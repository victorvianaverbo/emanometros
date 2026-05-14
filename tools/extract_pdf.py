"""
Extrai produtos + imagens do Catalogo Diriflux para o site Press Control.

Saidas:
  ../data/products.json     -> lista estruturada dos produtos
  ../images/products/*.webp -> 1 imagem otimizada por produto

Rodar:
  cd framework-v20/emanometros/tools
  python extract_pdf.py
"""

import io
import json
import re
import unicodedata
from pathlib import Path

import PyPDF2
from PIL import Image

PDF_PATH = Path(r"c:\Users\Victor\Desktop\Projetos\manometro\catalogo_diriflux.pdf")
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
IMG_DIR = HERE.parent / "images" / "products"

DATA_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Slugify
# ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


# ---------------------------------------------------------------------------
# Classify product
# ---------------------------------------------------------------------------
def category_from_name(name: str) -> str:
    n = name.lower()
    if "manovacu" in n:
        return "manovacuometros"
    if "vacu" in n:
        return "vacuometros"
    if "term" in n:
        return "termometros"
    return "manometros"


def material_class(material: str) -> str:
    m = material.lower()
    if "total inox" in m:
        return "total-inox"
    if "inox" in m:
        return "inox-latao"
    return "aco-carbono"


def diametro_mm(diametro: str) -> int:
    m = re.search(r"(\d{2,3})\s*mm", diametro)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Parse one product block
# ---------------------------------------------------------------------------
SPEC_FIELDS = [
    ("material", r"(?:^|\n|\s{2,})\s*Material\s*:\s*"),
    ("sensor", r"(?:^|\n|\s{2,})\s*Elemento Sensor\s*:\s*"),
    ("diametro", r"(?:^|\n|\s{2,})\s*Di[aâ]metro do Visor\s*:\s*"),
    ("visor", r"(?<!do )(?:^|\n|\s{2,})\s*Visor\s*:\s*"),
    ("classe", r"(?:^|\n|\s{2,})\s*Classe de Exatid[aã]o\s*:\s*"),
    ("conexao", r"(?:^|\n|\s{2,})\s*Conex[aã]o\s*:\s*"),
    ("escalas", r"(?:^|\n|\s{2,})\s*Escalas\s*:\s*"),
    ("ponteiro", r"(?:^|\n|\s{2,})\s*Ponteiro\s*:\s*"),
    ("temperatura", r"(?:^|\n|\s{2,})\s*Temperatura\s+de\s+T\s*rabalho\s*:\s*"),
    ("haste", r"(?:^|\n|\s{2,})\s*Haste\s*:\s*"),
    ("faixa", r"(?:^|\n|\s{2,})\s*Faixa\s+de\s+Temperatura\s*:\s*"),
    ("capilar", r"(?:^|\n|\s{2,})\s*Capilar\s*:\s*"),
    ("aplicacao", r"(?:^|\n|\s{2,})\s*Aplica[cç][aã]o\s*:\s*"),
]


WORDBREAK_FIXES = [
    (r"\bpneum[aá]tic\s+os\b", "pneumáticos"),
    (r"\bI\s+ndicador\b", "Indicador"),
    (r"\bVacu\s+[oô]metro\b", "Vacuômetro"),
    (r"\bMan\s+ovacu\s+[oô]metro\b", "Manovacuômetro"),
    (r"\bTerm[oô]metro\s+indicado\b", "Termômetro indicado"),
    (r"\+\s*6\s*0\s*°C", "+60°C"),
    (r"\bT\s+rabalho\b", "Trabalho"),
    (r"\bar\s+-\s+condicionado\b", "ar-condicionado"),
    (r"\bBlow\s+-\s*out\b", "Blow-out"),
    (r"DSC\s{2,}Vertical", "DSC Vertical"),
    (r"DSI\s{2,}Vertical", "DSI Vertical"),
    (r"DSI\s+A\b", "DSIA"),
    (r"DI\s+A\b", "DIA"),
    (r"\s+\.\s*$", "."),
]


def clean_spaces(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace(" ,", ",").replace(" .", ".")
    for pat, repl in WORDBREAK_FIXES:
        t = re.sub(pat, repl, t)
    # Collapse double spaces again after fixes
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_value(block: str, pattern: str) -> str:
    """Extracts text after `pattern:` up to next field marker.

    Stop markers may appear either after a newline OR after 2+ spaces inline
    (PDF text sometimes concatenates two fields on the same line).
    """
    sep = r"(?:\n\s*|\s{2,})"
    next_markers = (
        rf"(?:{sep}Material\s*:|{sep}Elemento Sensor\s*:|{sep}Di[aâ]metro do Visor\s*:|"
        rf"{sep}Visor\s*:|{sep}Classe de Exatid[aã]o\s*:|{sep}Conex[aã]o\s*:|"
        rf"{sep}Escalas?\s*:|{sep}Ponteiro\s*:|{sep}Temperatura\s+de\s+T\s*rabalho\s*:|"
        rf"{sep}Haste\s*:|{sep}Faixa\s+de\s+Temperatura\s*:|{sep}Capilar\s*:|"
        rf"{sep}Aplica[cç][aã]o\s*:|{sep}Montagem\s*:|{sep}Sistema\s*:|{sep}Caixa\s*:|"
        r"\*[A-Z]+|\n\s*(?:Man[oô]metro|Vacu[oô]metro|Manovacu[oô]metro|Term[oô]metro)\s+[A-Z]|$)"
    )
    m = re.search(pattern + r"(.+?)" + next_markers, block, re.S | re.I)
    if not m:
        return ""
    return clean_spaces(m.group(1))


PRODUCT_TITLE_RE = re.compile(
    r"^(Man[oô]metro|Vacu[oô]metro|Manovacu[oô]metro|Term[oô]metro)\s+[A-Z0-9].+?$",
    re.M | re.I,
)


def parse_page(page_text: str, page_num: int):
    """Returns list of (title, raw_block) for this page."""
    # Strip header lines (WWW.DIRIFLUX, DIRIFLUX MERCANTIL, address, phone)
    lines = page_text.split("\n")
    cleaned = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if re.match(r"^\d+\s*$", s):  # page number
            continue
        if "DIRIFLUX" in s.upper():
            continue
        if "Rua Mesquita" in s:
            continue
        if re.match(r"^\(31\)", s):
            continue
        if "WWW." in s.upper():
            continue
        cleaned.append(s)

    text = "\n".join(cleaned)

    # Find product title lines
    titles = []
    for m in PRODUCT_TITLE_RE.finditer(text):
        titles.append((m.start(), m.group(0).strip()))

    if not titles:
        return []

    products = []
    for i, (start, title) in enumerate(titles):
        end = titles[i + 1][0] if i + 1 < len(titles) else len(text)
        block = text[start:end]
        products.append((title, block))
    return products


def block_to_product(title: str, block: str, page_num: int, idx_on_page: int) -> dict:
    # Title may have trailing variant info: "Manometro DSA Horizontal - NAO LEVA GLICERINA"
    glicerina = None
    title_clean = title
    if re.search(r"PREPARADO PARA GLICERINA", title, re.I):
        glicerina = True
        title_clean = re.sub(
            r"[-–]?\s*PREPARADO PARA GLICERINA.*$", "", title_clean, flags=re.I
        ).strip()
    elif re.search(r"N[AÃ]O LEVA GLICERINA", title, re.I):
        glicerina = False
        title_clean = re.sub(
            r"[-–]?\s*N[AÃ]O LEVA GLICERINA.*$", "", title_clean, flags=re.I
        ).strip()
    # Termometros may have suffix like "Bimetalico Analogico" or "Tipo Capela Analogico"
    # Keep title clean (drop the closing dashes/em-dashes)
    title_clean = re.sub(r"\s*[-–]\s*$", "", title_clean).strip()

    INVALID_PREFIXES = (
        "Classe", "Conex", "Escalas", "Ponteiro", "Temperatura",
        "Aplica", "Montagem", "Sistema", "Faixa", "Haste",
    )
    specs = {}
    for key, pat in SPEC_FIELDS:
        v = extract_value(block, pat)
        if v:
            v = re.sub(r"\*+.*$", "", v).strip()
            # Reject captures that bled into next field (started with another field name)
            if v.startswith(INVALID_PREFIXES):
                continue
            if ":" in v and key != "aplicacao":
                v = v.split(":")[0].rsplit(" ", 1)[0].strip()
                if not v or len(v) < 2:
                    continue
            specs[key] = v

    diametro = specs.get("diametro", "")
    dia_mm = diametro_mm(diametro)

    # Add nominal diameter to displayed title (helps differentiate variants)
    nome_display = title_clean
    if dia_mm and str(dia_mm) not in nome_display:
        nome_display = f"{title_clean} {dia_mm}mm"

    slug_parts = [title_clean]
    if dia_mm:
        slug_parts.append(f"{dia_mm}mm")
    slug_parts.append(f"p{page_num}-{idx_on_page}")
    slug = slugify(" ".join(slug_parts))

    material = specs.get("material", "")
    return {
        "id": slug,
        "nome": nome_display,
        "categoria": category_from_name(title_clean),
        "material_class": material_class(material),
        "diametro_mm": dia_mm,
        "glicerina": glicerina,
        "imagem": f"images/products/{slug}.webp",
        "imagem_verso": f"images/products/{slug}-verso.webp",
        "specs": {
            "material": specs.get("material", ""),
            "sensor": specs.get("sensor", ""),
            "diametro": specs.get("diametro", ""),
            "visor": specs.get("visor", ""),
            "classe": specs.get("classe", ""),
            "conexao": specs.get("conexao", ""),
            "escalas": specs.get("escalas", "") or "A consultar",
            "ponteiro": specs.get("ponteiro", ""),
            "temperatura": specs.get("temperatura", ""),
            "haste": specs.get("haste", ""),
            "faixa_temperatura": specs.get("faixa", ""),
            "capilar": specs.get("capilar", ""),
        },
        "aplicacao": specs.get("aplicacao", ""),
        "_page": page_num,
        "_idx_on_page": idx_on_page,
    }


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------
def _decode_image(obj, w, h, flt):
    """Decode a PDF image XObject into a PIL Image."""
    data = obj.get_data()
    if flt == "/DCTDecode" or flt == "/JPXDecode":
        return Image.open(io.BytesIO(data))
    if flt == "/FlateDecode":
        mode = "RGB" if obj.get("/ColorSpace") == "/DeviceRGB" else "L"
        return Image.frombytes(mode, (w, h), data)
    return None


def extract_page_images(page) -> list:
    """Return list of PIL.Image (RGB, white-flattened), in order, only product-sized."""
    images = []
    if "/Resources" not in page:
        return images
    resources = page["/Resources"].get_object()
    if "/XObject" not in resources:
        return images
    xobjs = resources["/XObject"].get_object()
    for name in sorted(xobjs.keys(), key=lambda k: int(re.sub(r"\D", "", k) or 0)):
        obj = xobjs[name].get_object()
        if obj.get("/Subtype") != "/Image":
            continue
        w = obj.get("/Width", 0)
        h = obj.get("/Height", 0)
        if w < 200 or h < 200:
            continue
        try:
            flt = obj.get("/Filter")
            if isinstance(flt, list):
                flt = flt[0]
            img = _decode_image(obj, w, h, flt)
            if img is None:
                continue
            img.load()

            # Apply SMask (soft mask = alpha channel) if present
            if "/SMask" in obj:
                sm_obj = obj["/SMask"].get_object()
                sm_flt = sm_obj.get("/Filter")
                if isinstance(sm_flt, list):
                    sm_flt = sm_flt[0]
                try:
                    sm = _decode_image(sm_obj, sm_obj.get("/Width"), sm_obj.get("/Height"), sm_flt)
                    if sm is not None:
                        sm = sm.convert("L")
                        if sm.size != img.size:
                            sm = sm.resize(img.size, Image.Resampling.LANCZOS)
                        img = img.convert("RGB")
                        img.putalpha(sm)
                except Exception as e:
                    print(f"  ! SMask decode failed for {name}: {e}")

            images.append(img)
        except Exception as e:
            print(f"  ! could not decode image {name}: {e}")
    return images


def flatten_on_white(img: Image.Image) -> Image.Image:
    """Composite RGBA image over white; pass through if no alpha."""
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


def save_webp(img: Image.Image, dest: Path, max_size: int = 600, quality: int = 86):
    img = flatten_on_white(img)
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    img.save(dest, "WEBP", quality=quality, method=6)


def center_brightness(img: Image.Image) -> float:
    """Mean brightness of center 40% region (used to detect front vs back).

    Front (dial face) is brighter (white/cream face), back is darker (metal).
    """
    g = img.convert("L")
    w, h = g.size
    box = (w * 2 // 5, h * 2 // 5, w * 3 // 5, h * 3 // 5)
    crop = g.crop(box)
    pixels = list(crop.getdata())
    return sum(pixels) / max(1, len(pixels))


def pick_front_back(img_a, img_b):
    """Return (front, back) tuple by comparing center brightness."""
    if img_a is None:
        return img_b, None
    if img_b is None:
        return img_a, None
    ba = center_brightness(img_a)
    bb = center_brightness(img_b)
    return (img_a, img_b) if ba >= bb else (img_b, img_a)


FRONT_BRIGHTNESS_THRESHOLD = 110


def classify_and_pair(imgs, n_prods):
    """Pair images to products by classifying each image as front (bright
    dial) or back (dark mount).

    Diriflux often lays out a page in two rows: top row = all fronts,
    bottom row = all backs. So pairing imgs[2i]+imgs[2i+1] groups wrong.
    Instead: classify ALL images by center-brightness. Take the top-N
    brightest as fronts (preserving page order); remainder go to backs.

    If a candidate "front" is below FRONT_BRIGHTNESS_THRESHOLD it is rejected
    (likely all images are back-views), and that product gets a None front
    rather than a misleading back shown as its main image.
    """
    if not imgs or n_prods == 0:
        return [(None, None) for _ in range(n_prods)]

    indexed = list(enumerate(imgs))
    by_brightness = sorted(indexed, key=lambda x: -center_brightness(x[1]))
    n_pick = min(n_prods, len(imgs))
    front_indices = {idx for idx, _ in by_brightness[:n_pick]}

    fronts, backs = [], []
    for idx, img in indexed:
        if idx in front_indices and center_brightness(img) >= FRONT_BRIGHTNESS_THRESHOLD:
            fronts.append(img)
        else:
            backs.append(img)

    pairs = []
    for i in range(n_prods):
        f = fronts[i] if i < len(fronts) else None
        b = backs[i] if i < len(backs) else None
        pairs.append((f, b))
    return pairs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Reading {PDF_PATH}")
    reader = PyPDF2.PdfReader(str(PDF_PATH))

    all_products = []
    pages_with_products = range(6, 38)  # pages 7..38 (0-indexed 6..37)

    for page_idx in pages_with_products:
        page = reader.pages[page_idx]
        page_num = page_idx + 1
        text = page.extract_text() or ""
        parsed = parse_page(text, page_num)
        if not parsed:
            print(f"P{page_num}: NO PRODUCTS")
            continue

        imgs = extract_page_images(page)
        print(f"P{page_num}: {len(parsed)} product(s), {len(imgs)} image(s)")

        # Pair images to products using per-page brightness classification.
        # See classify_and_pair() for rationale.
        n_prods = len(parsed)
        pairs = classify_and_pair(imgs, n_prods)

        for i, (title, block) in enumerate(parsed):
            product = block_to_product(title, block, page_num, i)
            front, back = pairs[i]

            if front is not None:
                save_webp(front, IMG_DIR / f"{product['id']}.webp")
            else:
                product["imagem"] = ""
            if back is not None:
                save_webp(back, IMG_DIR / f"{product['id']}-verso.webp")
            else:
                product["imagem_verso"] = ""
            all_products.append(product)

    # Strip internal keys
    for p in all_products:
        p.pop("_page", None)
        p.pop("_idx_on_page", None)

    # Dedupe by name (keep entry with most populated specs)
    def spec_score(p):
        return sum(1 for v in p["specs"].values() if v)

    by_name = {}
    for p in all_products:
        existing = by_name.get(p["nome"])
        if existing is None or spec_score(p) > spec_score(existing):
            by_name[p["nome"]] = p
    deduped = list(by_name.values())
    removed = len(all_products) - len(deduped)
    if removed:
        print(f"\nDeduped: removed {removed} duplicate-name entries")
    all_products = deduped

    out = DATA_DIR / "products.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(all_products)} products -> {out}")
    print(f"Wrote images -> {IMG_DIR}")

    # Quick category breakdown
    from collections import Counter
    cats = Counter(p["categoria"] for p in all_products)
    print("\nBy category:")
    for k, v in cats.most_common():
        print(f"  {k:20s} {v}")


if __name__ == "__main__":
    main()
