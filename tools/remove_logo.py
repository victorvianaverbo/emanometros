"""
Remove a marca antiga (oval vermelho) estampada no centro-inferior do mostrador
dos instrumentos, deixando o fundo limpo — sem tocar na escala/numeros.

Estrategia:
  1. Detecta o disco do mostrador (HoughCircles) -> centro (cx,cy) e raio R.
  2. Define uma ROI estreita central-inferior, onde so existe a marca
     (os numeros vermelhos da escala ficam no arco, fora dessa faixa).
  3. Mascara os pixels vermelhos saturados dentro da ROI = a marca.
  4. cv2.inpaint (Telea) reconstroi o fundo liso (branco/preto).

Saida NAO sobrescreve os originais: grava em tools/_clean/ (espelhando
images/) e gera comparacoes antes|depois em tools/_review/ para revisao.
Use --apply para copiar _clean sobre os originais depois de aprovado.

Rodar:
  cd framework-v20/emanometros
  python tools/remove_logo.py            # gera _clean + _review
  python tools/remove_logo.py --apply    # sobrescreve os originais
"""

import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
PRODUCTS = SITE / "images" / "products"
COVER = SITE / "images" / "manometro-cover.png"

CLEAN = HERE / "_clean"
REVIEW = HERE / "_review"

# Vermelho saturado em HSV (dois ranges, pois o vermelho cruza H=0/180).
RED1 = ((0, 80, 60), (12, 255, 255))
RED2 = ((168, 80, 60), (180, 255, 255))

# ROI da marca, em fracoes do raio do mostrador (relativo ao centro).
ROI_HALF_W = 0.34   # +/- em x
ROI_TOP = 0.30      # de cy + ROI_TOP*R
ROI_BOT = 0.82      # ate cy + ROI_BOT*R

# Casos especiais onde a deteccao do disco falha (perspectiva) ou o logo nao
# fica no centro-inferior. Retangulo manual em fracao da imagem (x0,y0,x1,y1).
# Dentro do retangulo ainda removemos so o vermelho (red_mask), entao pode ser
# generoso sem afetar a escala.
OVERRIDES = {
    "manovacuometro-di-a-vertical-100mm-p32-0": (0.36, 0.40, 0.64, 0.58),
    "termometro-dti-horizontal-bimetalico-analogico-100mm-p34-0": (0.30, 0.76, 0.66, 0.95),
    "termometro-dtic-vertical-capilar-100mm-p37-0": (0.09, 0.39, 0.43, 0.57),
}

# Overrides que removem TODO conteudo nao-branco no retangulo (logos com texto
# preto, ex. marca de outro fabricante). Fundo local precisa ser branco liso.
OVERRIDES_NONWHITE = {
    "manometro-dsia-vertical-para-prensas-100mm-p18-1": (0.37, 0.595, 0.67, 0.715),
}


def red_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, np.array(RED1[0]), np.array(RED1[1]))
    m2 = cv2.inRange(hsv, np.array(RED2[0]), np.array(RED2[1]))
    return cv2.bitwise_or(m1, m2)


def red_mask_loose(bgr, thr=18):
    """Pega vermelho/rosa por dominancia do canal R (inclui logo desbotado).
    Usar apenas dentro de retangulos/ROI controlados (sem numeros da escala)."""
    b, g, r = cv2.split(bgr.astype(np.int16))
    dom = (r - np.maximum(g, b)) > thr
    return (dom.astype(np.uint8)) * 255


def detect_dial(bgr):
    """Retorna (cx, cy, R) do mostrador, ou None se nao detectar."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    h, w = gray.shape
    md = min(h, w)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=md,
        param1=100, param2=40,
        minRadius=int(0.18 * md), maxRadius=int(0.62 * md),
    )
    if circles is None:
        return None
    circles = np.uint16(np.around(circles[0]))
    # maior raio
    c = max(circles, key=lambda x: x[2])
    return int(c[0]), int(c[1]), int(c[2])


def build_logo_mask(bgr, dial):
    """Mascara so a marca (vermelho central-inferior), descartando numeros da
    escala que sejam vermelhos: funde as letras num blob via dilatacao
    horizontal e mantem apenas componentes com centroide perto do eixo vertical
    do mostrador (a marca e centralizada; os numeros 0/max ficam nas laterais).
    """
    h, w = bgr.shape[:2]
    cx, cy, R = dial
    roi = np.zeros((h, w), np.uint8)
    x0 = max(0, int(cx - ROI_HALF_W * R))
    x1 = min(w, int(cx + ROI_HALF_W * R))
    y0 = max(0, int(cy + ROI_TOP * R))
    y1 = min(h, int(cy + ROI_BOT * R))
    roi[y0:y1, x0:x1] = 255
    red = cv2.bitwise_and(red_mask_loose(bgr, thr=11), roi)

    # funde D-F-X (e asas) horizontalmente
    kw = max(5, int(0.10 * R))
    glue = cv2.dilate(red, cv2.getStructuringElement(cv2.MORPH_RECT, (kw, 3)))
    n, labels, stats, cent = cv2.connectedComponentsWithStats(glue, connectivity=8)
    keep = np.zeros((h, w), np.uint8)
    tol_x = 0.20 * R
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 12:
            continue
        if abs(cent[i][0] - cx) <= tol_x:
            keep[labels == i] = 255
    mask = cv2.bitwise_and(red, keep)
    return mask, (x0, y0, x1, y1)


def process(path):
    """Retorna (clean_bgr_or_bgra, mask, dial, roi, n_pixels) ou None."""
    raw = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if raw is None:
        return None
    alpha = None
    if raw.ndim == 3 and raw.shape[2] == 4:
        alpha = raw[:, :, 3]
        bgr = raw[:, :, :3].copy()
    else:
        bgr = raw if raw.ndim == 3 else cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)

    h, w = bgr.shape[:2]

    nw = OVERRIDES_NONWHITE.get(path.stem)
    if nw is not None:
        fx0, fy0, fx1, fy1 = nw
        roi_box = (int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h))
        roi = np.zeros((h, w), np.uint8)
        x0, y0, x1, y1 = roi_box
        roi[y0:y1, x0:x1] = 255
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        nonwhite = (gray < 195).astype(np.uint8) * 255
        mask = cv2.bitwise_and(cv2.bitwise_or(nonwhite, red_mask_loose(bgr)), roi)
        n = int(cv2.countNonZero(mask))
        mask_d = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
        clean = cv2.inpaint(bgr, mask_d, 5, cv2.INPAINT_TELEA)
        return ("clean", clean, alpha, None, roi_box, n)

    override = OVERRIDES.get(path.stem)
    if override is not None:
        fx0, fy0, fx1, fy1 = override
        roi_box = (int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h))
        roi = np.zeros((h, w), np.uint8)
        x0, y0, x1, y1 = roi_box
        roi[y0:y1, x0:x1] = 255
        mask = cv2.bitwise_and(red_mask_loose(bgr), roi)
        n = int(cv2.countNonZero(mask))
        if n < 20:
            return ("nologo", bgr, alpha, None, roi_box, n)
        mask_d = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
        clean = cv2.inpaint(bgr, mask_d, 4, cv2.INPAINT_TELEA)
        return ("clean", clean, alpha, None, roi_box, n)

    dial = detect_dial(bgr)
    if dial is None:
        return ("nodial", bgr, alpha, None, None, 0)

    mask, roi = build_logo_mask(bgr, dial)
    n = int(cv2.countNonZero(mask))
    if n < 30:  # sem marca relevante na ROI (ex: verso)
        return ("nologo", bgr, alpha, dial, roi, n)

    # dilatar para cobrir bordas/antialias do logo
    mask_d = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=2)
    clean = cv2.inpaint(bgr, mask_d, 5, cv2.INPAINT_TELEA)
    return ("clean", clean, alpha, dial, roi, n)


def recompose(clean_bgr, alpha):
    if alpha is None:
        return clean_bgr
    return np.dstack([clean_bgr, alpha])


def save_like(src_path, out_path, img):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if src_path.suffix.lower() == ".webp":
        cv2.imwrite(str(out_path), img, [cv2.IMWRITE_WEBP_QUALITY, 95])
    else:
        cv2.imwrite(str(out_path), img)


def make_compare(orig_bgr, clean_bgr, dial, roi):
    """antes|depois lado a lado, com circulo+ROI desenhados no 'antes'."""
    a = orig_bgr.copy()
    if dial:
        cx, cy, R = dial
        cv2.circle(a, (cx, cy), R, (0, 255, 0), 2)
    if roi:
        x0, y0, x1, y1 = roi
        cv2.rectangle(a, (x0, y0), (x1, y1), (255, 0, 255), 2)
    h = max(a.shape[0], clean_bgr.shape[0])

    def pad(im):
        return cv2.copyMakeBorder(im, 0, h - im.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(40, 40, 40))
    sep = np.full((h, 6, 3), (40, 40, 40), np.uint8)
    return np.hstack([pad(a), sep, pad(clean_bgr)])


def main():
    apply = "--apply" in sys.argv

    targets = sorted(PRODUCTS.glob("*.webp")) + [COVER]

    if apply:
        n = 0
        for src in targets:
            rel = src.relative_to(SITE / "images")
            cand = CLEAN / rel
            if cand.exists():
                # so sobrescreve os que realmente mudaram (estao em _clean)
                img = cv2.imread(str(cand), cv2.IMREAD_UNCHANGED)
                save_like(src, src, img)
                n += 1
        print(f"Aplicado: {n} imagens sobrescritas a partir de tools/_clean/")
        return

    CLEAN.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    stats = {"clean": 0, "nologo": 0, "nodial": 0}
    cleaned, nodial = [], []

    for src in targets:
        res = process(src)
        if res is None:
            print(f"  ERRO ao ler {src.name}")
            continue
        kind, img, alpha, dial, roi, n = res
        stats[kind] += 1
        rel = src.relative_to(SITE / "images")

        if kind == "clean":
            cleaned.append(src.name)
            out = recompose(img, alpha)
            save_like(src, CLEAN / rel, out)
            orig = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
            ob = orig[:, :, :3] if orig.ndim == 3 and orig.shape[2] == 4 else orig
            cmp = make_compare(ob, img, dial, roi)
            cv2.imwrite(str(REVIEW / f"{src.stem}__cmp.png"), cmp)
        elif kind == "nodial":
            nodial.append(src.name)

    print(f"\nResumo: {stats['clean']} limpas | {stats['nologo']} sem logo (versos) "
          f"| {stats['nodial']} sem disco detectado")
    if nodial:
        print("\nSEM DISCO DETECTADO (verificar manualmente):")
        for nm in nodial:
            print(f"  - {nm}")
    print(f"\n_clean/ e _review/ gerados em {HERE}")
    print("Revise as comparacoes em tools/_review/ e rode com --apply para aplicar.")


if __name__ == "__main__":
    main()
