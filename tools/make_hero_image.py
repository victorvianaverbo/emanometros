"""
Gera images/hero-manometro.png:

1. Extrai o manometro da pagina 2 do PDF Diriflux (a foto institucional do
   manometro grande, limpa, sem logo).
2. Recorta apenas a area do manometro (descarta o "SUA LOGOMARCA AQUI"
   original que vinha baked na imagem).
3. Remove o fundo branco via chroma-key e suaviza borda.
4. Compoe a nossa propria flecha vermelha + texto "SUA LOGOMARCA AQUI".
5. Salva como PNG transparente.
"""
import io
import math
from pathlib import Path

import PyPDF2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PDF = Path(r"c:\Users\Victor\Desktop\Projetos\manometro\catalogo_diriflux.pdf")
OUT_DIR = ROOT / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_INDEX = 1  # institutional manometer page


def extract_page2_image() -> Image.Image:
    r = PyPDF2.PdfReader(str(PDF))
    page = r.pages[PAGE_INDEX]
    xobjs = page["/Resources"].get_object()["/XObject"].get_object()
    best = None
    best_area = 0
    for k in xobjs.keys():
        o = xobjs[k].get_object()
        if o.get("/Subtype") != "/Image":
            continue
        w = o.get("/Width", 0)
        h = o.get("/Height", 0)
        if w * h <= best_area:
            continue
        flt = o.get("/Filter")
        if isinstance(flt, list):
            flt = flt[0]
        if flt not in ("/DCTDecode", "/JPXDecode"):
            continue
        img = Image.open(io.BytesIO(o.get_data()))
        img.load()
        best = img
        best_area = w * h
    if best is None:
        raise RuntimeError("Could not extract manometer image from page 2")
    return best.convert("RGB")


def crop_manometer_region(img: Image.Image) -> Image.Image:
    """Crop the right portion of page 2 image where the manometer is,
    excluding the bottom-left 'SUA LOGOMARCA AQUI' red annotation."""
    w, h = img.size
    # Manometer occupies roughly right 65% horizontally, vertically centered.
    # Crop from x=30% of width to x=100%; keep full height.
    left = int(w * 0.30)
    return img.crop((left, 0, w, h))


def remove_white_background(img: Image.Image, threshold: int = 235) -> Image.Image:
    """Convert near-white pixels to transparent. Returns RGBA."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (255, 255, 255, 0)
    return img


def trim_transparent(img: Image.Image) -> Image.Image:
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    return img.crop(bbox) if bbox else img


def find_font(size=58, prefer_bold=True):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if prefer_bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if prefer_bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for f in candidates:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_arrow(draw, start, end, color, width=14):
    """Curved bezier arrow with triangular head."""
    sx, sy = start
    ex, ey = end
    mx = (sx + ex) / 2 - (ey - sy) * 0.35
    my = (sy + ey) / 2 + abs(ex - sx) * 0.25
    pts = []
    for t in [i / 32 for i in range(33)]:
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * ey
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=width)
    last = pts[-1]
    prev = pts[-4]
    angle = math.atan2(last[1] - prev[1], last[0] - prev[0])
    head_len = 42
    a1 = angle - math.radians(24)
    a2 = angle + math.radians(24)
    p1 = (last[0] - head_len * math.cos(a1), last[1] - head_len * math.sin(a1))
    p2 = (last[0] - head_len * math.cos(a2), last[1] - head_len * math.sin(a2))
    draw.polygon([last, p1, p2], fill=color)


def compose_hero(manometer: Image.Image) -> Image.Image:
    cw, ch = 1200, 1000
    canvas = Image.new("RGBA", (cw, ch), (255, 255, 255, 0))

    # Manometer on the right, large
    target_w = 700
    scale = target_w / manometer.width
    new_size = (target_w, int(manometer.height * scale))
    m = manometer.resize(new_size, Image.Resampling.LANCZOS)
    mx = cw - new_size[0] - 60
    my = (ch - new_size[1]) // 2
    canvas.paste(m, (mx, my), m)

    # Soft drop shadow under manometer
    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse(
        [(mx + 60, my + new_size[1] - 30), (mx + new_size[0] - 60, my + new_size[1] + 30)],
        fill=(0, 0, 0, 110),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    canvas = Image.alpha_composite(shadow, canvas)

    draw = ImageDraw.Draw(canvas)
    # Text "SUA LOGOMARCA AQUI" left of manometer
    font = find_font(size=72, prefer_bold=True)
    text_color = (255, 255, 255, 255)
    lines = ["SUA", "LOGOMARCA", "AQUI"]
    text_x = 60
    text_y = my + new_size[1] // 2 - 150
    line_spacing = 88
    # Subtle text shadow for legibility on navy
    for i, line in enumerate(lines):
        # Shadow
        for dx, dy in [(2, 2), (1, 2)]:
            draw.text((text_x + dx, text_y + i * line_spacing + dy), line,
                      font=font, fill=(0, 0, 0, 140))
        draw.text((text_x, text_y + i * line_spacing), line, font=font, fill=text_color)

    # Red curved arrow from below text to dial center
    arrow_color = (236, 72, 72, 255)
    start = (text_x + 380, text_y + 230)
    end = (mx + int(new_size[0] * 0.46), my + int(new_size[1] * 0.50))
    draw_arrow(draw, start, end, arrow_color, width=16)

    return canvas


def main():
    print(f"Extracting page-{PAGE_INDEX + 1} manometer image...")
    img = extract_page2_image()
    print(f"  Source size: {img.size}")

    img = crop_manometer_region(img)
    print(f"  After crop: {img.size}")

    img = remove_white_background(img, threshold=235)
    img = trim_transparent(img)
    print(f"  After bg-removal + trim: {img.size}")

    hero = compose_hero(img)
    out = OUT_DIR / "hero-manometro.png"
    hero.save(out, "PNG", optimize=True)
    size_kb = out.stat().st_size / 1024
    print(f"Saved: {out} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
