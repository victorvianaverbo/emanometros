"""
Remove o fundo branco de manometro-bare.png usando flood-fill a partir
das bordas — preserva o branco INTERNO (mostrador, escala, kgf/cm²) e
mantém o texto preto + flecha vermelha intactos.

Saida: ../images/hero-manometro.png (transparente)
"""
from pathlib import Path
from collections import deque
from PIL import Image

HERE = Path(__file__).resolve().parent
IMAGES = HERE.parent / "images"
SRC = IMAGES / "manometro-bare.png"
DEST = IMAGES / "hero-manometro.png"

# tolerance: how close to (255,255,255) counts as background-white
TOLERANCE = 18


def is_bg_pixel(r, g, b, tol=TOLERANCE):
    return r >= 255 - tol and g >= 255 - tol and b >= 255 - tol


def flood_remove_bg(img: Image.Image, tol=TOLERANCE) -> Image.Image:
    """BFS from all 4 borders; mark all reachable near-white pixels as
    transparent. Internal white islands stay opaque."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()

    visited = bytearray(w * h)  # 0 = not visited, 1 = bg
    q = deque()

    # Seed: every border pixel that is near-white
    def maybe_push(x, y):
        i = y * w + x
        if visited[i]:
            return
        r, g, b, _ = px[x, y]
        if is_bg_pixel(r, g, b, tol):
            visited[i] = 1
            q.append((x, y))

    for x in range(w):
        maybe_push(x, 0)
        maybe_push(x, h - 1)
    for y in range(h):
        maybe_push(0, y)
        maybe_push(w - 1, y)

    # BFS 4-connectivity
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                if not visited[i]:
                    r, g, b, _ = px[nx, ny]
                    if is_bg_pixel(r, g, b, tol):
                        visited[i] = 1
                        q.append((nx, ny))

    # Apply transparency
    out = img.copy()
    out_px = out.load()
    for y in range(h):
        for x in range(w):
            if visited[y * w + x]:
                out_px[x, y] = (255, 255, 255, 0)

    return out


def feather_edges(img: Image.Image, radius: int = 1) -> Image.Image:
    """Light feather on the alpha channel to soften halos."""
    from PIL import ImageFilter
    alpha = img.split()[-1].filter(ImageFilter.GaussianBlur(radius=radius))
    out = img.copy()
    out.putalpha(alpha)
    return out


def trim_transparent(img: Image.Image) -> Image.Image:
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    return img.crop(bbox) if bbox else img


def main():
    print(f"Loading {SRC.name}...")
    img = Image.open(SRC)
    print(f"  Source: {img.size}, mode={img.mode}")

    # Crop right portion only — exclude the "SUA LOGOMARCA AQUI" text + arrow
    # that live on the left side of the page-2 composition.
    w, h = img.size
    crop_left = int(w * 0.48)  # keep right ~52% (manometer area)
    img = img.crop((crop_left, 0, w, h))
    print(f"  After left-crop: {img.size}")

    img = flood_remove_bg(img, tol=TOLERANCE)
    print(f"  After flood-fill bg removal: alpha applied")

    img = feather_edges(img, radius=0.8)
    img = trim_transparent(img)
    print(f"  After feather + trim: {img.size}")

    img.save(DEST, "PNG", optimize=True)
    print(f"Saved {DEST.name} ({DEST.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
