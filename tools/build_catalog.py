"""
Gera o catalogo proprio da Press Control em PDF.

Le ../data/products.json + imagens em ../images/products/ e produz
../catalogo-presscontrol.pdf — com branding Press Control, sem qualquer
referencia a marca de origem.

Rodar:
  cd framework-v20/emanometros/tools
  python build_catalog.py
"""

import json
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
SITE_ROOT = HERE.parent
DATA = SITE_ROOT / "data" / "products.json"
HERO_IMAGE = SITE_ROOT / "images" / "manometro-bare.png"          # com seta/texto — usar na pag. Sobre
HERO_COVER = SITE_ROOT / "images" / "manometro-cover.png"         # limpo, transparente — capa
OUTPUT = SITE_ROOT / "catalogo-presscontrol.pdf"
FONTS_DIR = HERE / "fonts"

# Brand colors (matching style.css)
NAVY = HexColor("#0A1628")
NAVY_LIGHT = HexColor("#152238")
STEEL = HexColor("#1E3A5F")
ELECTRIC = HexColor("#0078D4")
CYAN = HexColor("#00B4D8")
ACCENT = HexColor("#0078D4")
SLATE_50 = HexColor("#F8FAFC")
SLATE_100 = HexColor("#F1F5F9")
SLATE_200 = HexColor("#E2E8F0")
SLATE_300 = HexColor("#CBD5E1")
SLATE_400 = HexColor("#94A3B8")
SLATE_600 = HexColor("#475569")
SLATE_700 = HexColor("#334155")
SLATE_900 = HexColor("#0F172A")
WHATSAPP = HexColor("#25D366")

VIOLET = HexColor("#7C3AED")
AMBER = HexColor("#F59E0B")

CAT_LABEL = {
    "manometros": "MANÔMETROS",
    "manovacuometros": "MANOVACUÔMETROS",
    "vacuometros": "VACUÔMETROS",
    "termometros": "TERMÔMETROS",
}

# Acentos de categoria (Design System Press Control)
CAT_COLOR = {
    "manometros": ELECTRIC,   # #0078D4
    "manovacuometros": CYAN,  # #00B4D8
    "vacuometros": VIOLET,    # #7C3AED
    "termometros": AMBER,     # #F59E0B
}
CAT_NUM = {
    "manometros": "01",
    "manovacuometros": "02",
    "vacuometros": "03",
    "termometros": "04",
}
CAT_LEDE = {
    "manometros": "Medição de pressão com máxima exatidão para as mais diversas "
                  "aplicações industriais — ar comprimido, hidráulica, vapor, "
                  "processos químicos e alimentícios.",
    "manovacuometros": "Pressão e vácuo num único instrumento. Ideal para sistemas "
                       "que operam acima e abaixo da pressão atmosférica.",
    "vacuometros": "Monitoramento de vácuo com total confiabilidade para bombas, "
                   "câmaras, embalagem e processos de sucção.",
    "termometros": "Controle de temperatura robusto e preciso — bimetálicos, de "
                   "haste e capilares à distância para os ambientes mais exigentes.",
}


def cat_color(cat):
    return CAT_COLOR.get(cat, ELECTRIC)

SPECS_LEFT = [
    ("material", "Material:"),
    ("sensor", "Elemento Sensor:"),
    ("diametro", "Diâmetro do Visor:"),
    ("visor", "Visor:"),
    ("classe", "Classe de Exatidão:"),
    ("conexao", "Conexão:"),
]
SPECS_RIGHT = [
    ("escalas", "Escalas:"),
    ("ponteiro", "Ponteiro:"),
    ("temperatura", "Temperatura de Trabalho:"),
    ("haste", "Haste:"),
    ("faixa_temperatura", "Faixa de Temperatura:"),
    ("capilar", "Capilar:"),
]

COMPANY = "Press Control"
ADDRESS = "Rua Platina, 693 - Prado, Belo Horizonte/MG"
PHONE = "(31) 9571-3196"
EMAIL = "contato@presscontrol.com.br"
SITE = "www.presscontrol.com.br"
INSTAGRAM = "@presscontrol"


# ---------------------------------------------------------------------------
# Fonts — mesmas do site (Plus Jakarta Sans + DM Sans)
# ---------------------------------------------------------------------------
class Fonts:
    display = "Helvetica-Bold"
    display_bold = "Helvetica-Bold"
    display_xbold = "Helvetica-Bold"
    body = "Helvetica"
    body_bold = "Helvetica-Bold"


def setup_fonts():
    """Registra Plus Jakarta Sans (display) e DM Sans (body). Fallback p/ Helvetica."""
    try:
        pdfmetrics.registerFont(TTFont("Jakarta", str(FONTS_DIR / "PlusJakartaSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("Jakarta-Bold", str(FONTS_DIR / "PlusJakartaSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("Jakarta-XBold", str(FONTS_DIR / "PlusJakartaSans-ExtraBold.ttf")))
        pdfmetrics.registerFont(TTFont("DMSans", str(FONTS_DIR / "DMSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("DMSans-Bold", str(FONTS_DIR / "DMSans-Bold.ttf")))
        Fonts.display = "Jakarta-Bold"
        Fonts.display_bold = "Jakarta-Bold"
        Fonts.display_xbold = "Jakarta-XBold"
        Fonts.body = "DMSans"
        Fonts.body_bold = "DMSans-Bold"
        print("Fonts: Plus Jakarta Sans + DM Sans (mesmas do site)")
    except Exception as e:
        print(f"AVISO: falha ao carregar fontes customizadas ({e}). Usando Helvetica.")
    return Fonts


# ---------------------------------------------------------------------------
# SVG Aperture Mark — vetorial, mesmo desenho do site (viewBox 100x100)
# ---------------------------------------------------------------------------
def draw_aperture_mark(c, cx, cy, size, body_color=white, needle_color=None):
    """Desenha o 'pc-mark' do site centrado em (cx, cy) com diâmetro `size`."""
    if needle_color is None:
        needle_color = CYAN

    scale = size / 100.0

    def X(v): return cx + (v - 50) * scale
    def Y(v): return cy - (v - 50) * scale  # PDF y inverted vs SVG
    def W(v): return v * scale

    c.saveState()
    c.setStrokeColor(body_color)
    c.setLineCap(1)

    # Circle r=46
    c.setLineWidth(W(3.5))
    c.circle(cx, cy, W(46), stroke=1, fill=0)

    # Tick marks (cardinal + minor) — replicates SVG
    ticks_major = [(50, 20, 50, 10), (80, 50, 90, 50), (50, 80, 50, 90), (20, 50, 10, 50)]
    ticks_strong = [(73.33, 26.67, 78.28, 21.72), (73.33, 73.33, 78.28, 78.28),
                    (26.67, 73.33, 21.72, 78.28), (26.67, 26.67, 21.72, 21.72)]
    ticks_minor = [
        (59.06, 16.19, 60.35, 11.36), (67.5, 19.69, 70, 15.36),
        (80.31, 32.5, 84.64, 30), (83.81, 40.94, 88.64, 39.65),
        (83.81, 59.06, 88.64, 60.35), (80.31, 67.5, 84.64, 70),
        (67.5, 80.31, 70, 84.64), (59.06, 83.81, 60.35, 88.64),
        (40.94, 83.81, 39.65, 88.64), (32.5, 80.31, 30, 84.64),
        (19.69, 67.5, 15.36, 70), (16.19, 59.06, 11.36, 60.35),
        (16.19, 40.94, 11.36, 39.65), (19.69, 32.5, 15.36, 30),
        (32.5, 19.69, 30, 15.36), (40.94, 16.19, 39.65, 11.36),
    ]
    c.setLineWidth(W(2.4))
    for x1, y1, x2, y2 in ticks_major:
        c.line(X(x1), Y(y1), X(x2), Y(y2))
    c.setLineWidth(W(1.4))
    for x1, y1, x2, y2 in ticks_strong:
        c.line(X(x1), Y(y1), X(x2), Y(y2))
    c.setStrokeColor(_with_alpha(body_color, 0.45))
    for x1, y1, x2, y2 in ticks_minor:
        c.line(X(x1), Y(y1), X(x2), Y(y2))

    # Needle
    c.setStrokeColor(needle_color)
    c.setLineWidth(W(4))
    c.line(X(44.8), Y(53), X(74.25), Y(36))

    # Center dot
    c.setFillColor(body_color)
    c.circle(cx, cy, W(4), stroke=0, fill=1)
    c.setFillColor(white)
    c.circle(cx, cy, W(1.6), stroke=0, fill=1)

    c.restoreState()


def _with_alpha(color, alpha):
    """Retorna nova cor com transparência aproximada via mistura com branco."""
    # ReportLab colors podem ter alpha. Se for HexColor sem alpha, criamos cor com alpha.
    try:
        r, g, b = color.rgb()
        from reportlab.lib.colors import Color
        return Color(r, g, b, alpha=alpha)
    except Exception:
        return color


# ---------------------------------------------------------------------------
# Logo (mark + wordmark) — exato como no site
# ---------------------------------------------------------------------------
def draw_logo(c, x, y, size=22, light_bg=False):
    """Desenha 'mark + Press Control' começando em (x, y baseline do texto)."""
    mark_size = size * 1.25
    body_color = SLATE_900 if light_bg else white
    needle = ELECTRIC if light_bg else CYAN

    mark_cx = x + mark_size / 2
    mark_cy = y + size * 0.32  # alinhar com baseline do texto

    draw_aperture_mark(c, mark_cx, mark_cy, mark_size, body_color=body_color, needle_color=needle)

    text_x = x + mark_size + size * 0.35
    c.setFont(Fonts.display_bold, size)
    c.setFillColor(body_color)
    c.drawString(text_x, y, "Press")
    w = c.stringWidth("Press ", Fonts.display_bold, size)
    c.setFillColor(needle)
    c.drawString(text_x + w, y, "Control")


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
def draw_header_strip(c):
    width, height = A4
    c.setFillColor(white)
    c.rect(0, height - 14 * mm, width, 14 * mm, fill=1, stroke=0)
    draw_logo(c, 16 * mm, height - 10 * mm, size=10, light_bg=True)
    c.setFillColor(SLATE_400)
    c.setFont(Fonts.body, 8)
    c.drawRightString(width - 16 * mm, height - 9.5 * mm, f"{SITE}  ·  {PHONE}")
    c.setStrokeColor(SLATE_200)
    c.setLineWidth(0.5)
    c.line(16 * mm, height - 14 * mm, width - 16 * mm, height - 14 * mm)


def draw_footer_strip(c, page_num=None, total_pages=None):
    width, _ = A4
    c.setStrokeColor(SLATE_200)
    c.setLineWidth(0.5)
    c.line(16 * mm, 13 * mm, width - 16 * mm, 13 * mm)
    c.setFillColor(SLATE_400)
    c.setFont(Fonts.body, 8)
    c.drawString(16 * mm, 8 * mm, f"{COMPANY}  ·  Catálogo de Produtos · Edição 2026")
    if page_num and total_pages:
        c.drawRightString(width - 16 * mm, 8 * mm, f"{page_num:02d} / {total_pages:02d}")


def wrap_text(c, text, font, size, max_width):
    if not text:
        return []
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(c, x, y, text, font, size, max_width, line_height=None, color=SLATE_600):
    if line_height is None:
        line_height = size * 1.55
    c.setFillColor(color)
    c.setFont(font, size)
    cur = y
    for line in wrap_text(c, text, font, size, max_width):
        c.drawString(x, cur, line)
        cur -= line_height
    return cur


# ---------------------------------------------------------------------------
# Ícones de especificação — vetoriais, viewBox 24×24 (vocabulário do Design System)
# ---------------------------------------------------------------------------
def draw_spec_icon(c, key, x, y, size, color):
    """Desenha o ícone da spec `key` no canto inferior-esquerdo (x, y), lado `size`."""
    s = size / 24.0

    def X(v):
        return x + v * s

    def Y(v):
        return y + (24 - v) * s  # PDF y invertido vs SVG

    def W(v):
        return v * s

    def arch(x1, y1, cx1, cy1, cx2, cy2, x2, y2):
        p = c.beginPath()
        p.moveTo(X(x1), Y(y1))
        p.curveTo(X(cx1), Y(cy1), X(cx2), Y(cy2), X(x2), Y(y2))
        c.drawPath(p, stroke=1, fill=0)

    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(max(W(2), 0.6))
    c.setLineCap(1)
    c.setLineJoin(1)

    try:
        if key == "diametro":
            c.circle(X(12), Y(12), W(8), stroke=1, fill=0)
            c.line(X(4), Y(12), X(20), Y(12))
            c.line(X(6), Y(10), X(4), Y(12)); c.line(X(4), Y(12), X(6), Y(14))
            c.line(X(18), Y(10), X(20), Y(12)); c.line(X(20), Y(12), X(18), Y(14))
        elif key == "conexao":
            c.rect(X(3), Y(14), W(6), W(4), stroke=1, fill=0)
            c.rect(X(13), Y(15), W(3), W(6), stroke=1, fill=0)
            c.line(X(9), Y(12), X(13), Y(12)); c.line(X(16), Y(12), X(21), Y(12))
        elif key in ("escalas", "faixa_temperatura"):
            arch(4, 16, 6, 6, 18, 6, 20, 16)
            c.line(X(12), Y(16), X(16), Y(10))
            c.circle(X(12), Y(16), W(1.4), stroke=0, fill=1)
        elif key == "ponteiro":
            c.circle(X(12), Y(12), W(8), stroke=1, fill=0)
            c.line(X(12), Y(12), X(16), Y(8))
            c.circle(X(12), Y(12), W(1.6), stroke=0, fill=1)
        elif key == "classe":
            p = c.beginPath()
            p.moveTo(X(12), Y(3)); p.lineTo(X(20), Y(6)); p.lineTo(X(20), Y(12))
            p.curveTo(X(20), Y(17), X(16), Y(20), X(12), Y(21))
            p.curveTo(X(8), Y(20), X(4), Y(17), X(4), Y(12))
            p.lineTo(X(4), Y(6)); p.close()
            c.drawPath(p, stroke=1, fill=0)
            c.line(X(9), Y(12), X(11), Y(14)); c.line(X(11), Y(14), X(15), Y(10))
        elif key == "material":
            c.circle(X(12), Y(12), W(8), stroke=1, fill=0)
            c.circle(X(12), Y(12), W(4), stroke=1, fill=0)
            c.line(X(4), Y(12), X(6), Y(12)); c.line(X(18), Y(12), X(20), Y(12))
        elif key == "sensor":
            arch(4, 18, 4, 10, 12, 4, 16, 5)
            arch(16, 5, 20, 6, 20, 11, 14, 12)
            c.circle(X(4), Y(18), W(1.5), stroke=0, fill=1)
        elif key == "temperatura":
            p = c.beginPath()
            p.moveTo(X(10), Y(6)); p.lineTo(X(10), Y(15))
            c.drawPath(p, stroke=1, fill=0)
            c.line(X(14), Y(4), X(14), Y(15))
            c.line(X(10), Y(4), X(14), Y(4))
            c.circle(X(12), Y(17), W(4), stroke=1, fill=0)
        elif key == "haste":
            c.line(X(12), Y(3), X(12), Y(16))
            c.rect(X(9), Y(21), W(6), W(5), stroke=1, fill=0)
        elif key == "capilar":
            arch(3, 12, 6, 8, 9, 16, 12, 12)
            arch(12, 12, 15, 8, 18, 16, 21, 12)
        elif key == "visor":
            c.roundRect(X(4), Y(18), W(16), W(12), W(2), stroke=1, fill=0)
            c.line(X(4), Y(10), X(20), Y(10))
        else:  # fallback
            c.circle(X(12), Y(12), W(8), stroke=1, fill=0)
            c.line(X(9), Y(12), X(15), Y(12)); c.line(X(12), Y(9), X(12), Y(15))
    except Exception:
        pass
    c.restoreState()


# ---------------------------------------------------------------------------
# COVER — Industrial elegant
# ---------------------------------------------------------------------------
def page_cover(c):
    width, height = A4

    # Fundo navy escuro
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Gradient simulado via blocos sutis (linhas finas horizontais ao topo)
    for i in range(0, 60):
        alpha = 1 - i / 60
        from reportlab.lib.colors import Color
        c.setFillColor(Color(0.06, 0.14, 0.23, alpha=alpha * 0.4))
        c.rect(0, height - 50 * mm - i * 1.0, width, 1.0, fill=1, stroke=0)

    # Pattern: linhas verticais finas (tipo grade industrial) na lateral direita
    c.setStrokeColor(_with_alpha(CYAN, 0.10))
    c.setLineWidth(0.4)
    for i in range(20):
        gx = width - 95 * mm + i * 5 * mm
        c.line(gx, 22 * mm, gx, height - 22 * mm)

    # Marca d'agua: aperture mark atras da foto do manometro (canto inferior direito)
    draw_aperture_mark(
        c, width - 62 * mm, 76 * mm, 170 * mm,
        body_color=_with_alpha(CYAN, 0.05),
        needle_color=_with_alpha(CYAN, 0.08),
    )

    # ─── Top band com logo ───
    draw_logo(c, 20 * mm, height - 22 * mm, size=14)
    c.setFillColor(_with_alpha(white, 0.55))
    c.setFont(Fonts.body, 8.5)
    c.drawRightString(width - 20 * mm, height - 18.5 * mm, "INSTRUMENTAÇÃO INDUSTRIAL")
    c.setFillColor(_with_alpha(white, 0.35))
    c.drawRightString(width - 20 * mm, height - 23 * mm, "BELO HORIZONTE  ·  MG  ·  BRASIL")

    # Linha cyan separadora
    c.setFillColor(CYAN)
    c.rect(20 * mm, height - 28 * mm, width - 40 * mm, 0.4, fill=1, stroke=0)

    # ─── Badge "EDIÇÃO 2026" ───
    badge_y = height - 50 * mm
    badge_w = 52 * mm
    c.setFillColor(_with_alpha(CYAN, 0.12))
    c.setStrokeColor(_with_alpha(CYAN, 0.35))
    c.setLineWidth(0.6)
    c.roundRect(20 * mm, badge_y, badge_w, 7 * mm, 3.5 * mm, fill=1, stroke=1)
    c.setFillColor(CYAN)
    c.circle(24 * mm, badge_y + 3.5 * mm, 1.1 * mm, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.setFont(Fonts.body_bold, 8)
    c.drawString(28.5 * mm, badge_y + 2.4 * mm, "EDIÇÃO 2026  ·  CATÁLOGO")

    # ─── Título principal: CATÁLOGO / DE / PRODUTOS ───
    c.setFillColor(white)
    c.setFont(Fonts.display_xbold, 68)
    c.drawString(20 * mm, height - 78 * mm, "Catálogo")

    # gradiente simulado: desenhamos "de Produtos" em duas cores (cyan->electric)
    c.setFillColor(ELECTRIC)
    c.setFont(Fonts.display_xbold, 68)
    c.drawString(20 * mm, height - 108 * mm, "de Produtos")

    # Subtítulo
    c.setFillColor(_with_alpha(white, 0.75))
    c.setFont(Fonts.body, 12)
    c.drawString(20 * mm, height - 122 * mm,
                 "Manômetros · Manovacuômetros · Vacuômetros · Termômetros")
    c.setFillColor(_with_alpha(white, 0.45))
    c.setFont(Fonts.body, 10)
    c.drawString(20 * mm, height - 130 * mm,
                 "Pronta entrega · Personalização com sua marca · Envio para todo Brasil")

    # ─── Imagem do manometro (canto inferior direito, fundo navy) ───
    hero = HERO_COVER if HERO_COVER.exists() else HERO_IMAGE
    if hero.exists():
        img_w = 78 * mm
        img_h = 92 * mm
        img_x = width - img_w - 22 * mm
        img_y = 32 * mm
        # halo cyan suave atrás da foto
        c.saveState()
        from reportlab.lib.colors import Color
        for i in range(10):
            rr = (max(img_w, img_h) / 2 + 22) - i * 2.4
            c.setFillColor(Color(0, 0.706, 0.847, alpha=0.03))
            c.circle(img_x + img_w / 2, img_y + img_h / 2, rr, fill=1, stroke=0)
        c.restoreState()
        c.drawImage(
            str(hero),
            img_x, img_y, img_w, img_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ─── Lista de categorias com índice tipo industrial (esquerda baixa) ───
    cats = [
        ("01", "MANÔMETROS"),
        ("02", "MANOVACUÔMETROS"),
        ("03", "VACUÔMETROS"),
        ("04", "TERMÔMETROS"),
    ]
    cat_y = 100 * mm
    c.setFillColor(_with_alpha(white, 0.5))
    c.setFont(Fonts.body_bold, 7.5)
    c.drawString(20 * mm, cat_y + 10, "CATEGORIAS  /  CONTEÚDO")
    c.setStrokeColor(_with_alpha(white, 0.15))
    c.setLineWidth(0.4)
    c.line(20 * mm, cat_y + 5, 95 * mm, cat_y + 5)
    for i, (num, name) in enumerate(cats):
        y = cat_y - 5 - i * 9 * mm
        c.setFillColor(CYAN)
        c.setFont(Fonts.body_bold, 9)
        c.drawString(20 * mm, y, num)
        c.setFillColor(white)
        c.setFont(Fonts.display_bold, 10.5)
        c.drawString(31 * mm, y, name)

    # ─── Faixa inferior com endereço/contato ───
    c.setFillColor(NAVY_LIGHT)
    c.rect(0, 0, width, 22 * mm, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(0, 22 * mm, width, 0.4, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.setFont(Fonts.body_bold, 8.5)
    c.drawString(20 * mm, 13.5 * mm, ADDRESS)
    c.setFillColor(_with_alpha(white, 0.65))
    c.setFont(Fonts.body, 8.5)
    c.drawString(20 * mm, 7 * mm, f"{PHONE}  ·  {EMAIL}  ·  {SITE}")
    # Direita: ano grande
    c.setFillColor(_with_alpha(CYAN, 0.7))
    c.setFont(Fonts.display_xbold, 18)
    c.drawRightString(width - 20 * mm, 8.5 * mm, "2026")

    c.showPage()


# ---------------------------------------------------------------------------
# SOBRE
# ---------------------------------------------------------------------------
def page_sobre(c):
    width, height = A4
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    draw_header_strip(c)

    # Eyebrow
    c.setFillColor(ELECTRIC)
    c.setFont(Fonts.body_bold, 8.5)
    c.drawString(20 * mm, height - 26 * mm, "SOBRE A EMPRESA")
    # Linha curta cyan
    c.setFillColor(CYAN)
    c.rect(20 * mm, height - 29 * mm, 14 * mm, 0.6, fill=1, stroke=0)

    # Titulo
    c.setFillColor(SLATE_900)
    c.setFont(Fonts.display_xbold, 30)
    c.drawString(20 * mm, height - 42 * mm, "Press Control")
    c.setFillColor(SLATE_600)
    c.setFont(Fonts.body, 12)
    c.drawString(20 * mm, height - 51 * mm, "Instrumentação industrial · Pronta entrega · Personalização")

    paragraphs = [
        "A Press Control é uma empresa especializada em instrumentação industrial de medição, "
        "atendendo indústrias, oficinas, revendedores e profissionais técnicos em todo o Brasil.",
        "Trabalhamos com manômetros, manovacuômetros, vacuômetros e termômetros de alta confiabilidade, "
        "selecionados para resistir aos ambientes mais exigentes — químico, alimentício, petroquímico, "
        "siderúrgico e refrigeração.",
        "Mantemos estoque amplo para pronta entrega e enviamos para todas as regiões do país. "
        "Nossa equipe técnica orienta a escolha do instrumento correto para cada aplicação.",
        "Nossa missão é fazer com que você seja sempre atendido da melhor maneira possível, "
        "com agilidade, qualidade e suporte técnico especializado.",
    ]

    text_x = 20 * mm
    text_max = width / 2 - 28 * mm
    y = height - 65 * mm
    for para in paragraphs:
        y = draw_paragraph(c, text_x, y, para, Fonts.body, 10.5, text_max, line_height=15.5, color=SLATE_700)
        y -= 8

    # Highlight box
    y -= 4
    box_h = 34 * mm
    c.setFillColor(NAVY)
    c.roundRect(text_x, y - box_h, text_max, box_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(text_x, y - box_h, 1.6 * mm, box_h, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.setFont(Fonts.body_bold, 8)
    c.drawString(text_x + 6 * mm, y - 7 * mm, "PERSONALIZAÇÃO")
    c.setFillColor(white)
    c.setFont(Fonts.display_bold, 13)
    c.drawString(text_x + 6 * mm, y - 13.5 * mm, "Sua marca em cada medição.")
    c.setFillColor(_with_alpha(white, 0.75))
    c.setFont(Fonts.body, 9.5)
    cur = y - 19 * mm
    for line in wrap_text(c, "Personalizamos manômetros com logomarca, cores e escalas customizadas para sua empresa.", Fonts.body, 9.5, text_max - 12 * mm):
        c.drawString(text_x + 6 * mm, cur, line)
        cur -= 13

    # Lado direito: imagem do manômetro
    if HERO_IMAGE.exists():
        img_w = 90 * mm
        img_h = 90 * mm
        # fundo cinza claro elegante
        c.setFillColor(SLATE_50)
        c.roundRect(width - img_w - 22 * mm, height - 140 * mm, img_w + 8 * mm, img_h + 8 * mm, 3 * mm, fill=1, stroke=0)
        c.drawImage(
            str(HERO_IMAGE),
            width - img_w - 18 * mm,
            height - 136 * mm,
            img_w,
            img_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Diferenciais (4 cards na parte inferior)
    y_box = 30 * mm
    box_w = width - 40 * mm
    box_h = 42 * mm
    c.setFillColor(SLATE_50)
    c.setStrokeColor(SLATE_200)
    c.setLineWidth(0.5)
    c.roundRect(20 * mm, y_box, box_w, box_h, 3 * mm, fill=1, stroke=1)

    diferenciais = [
        ("Pronta Entrega", "Estoque amplo · Envio em até 24h"),
        ("Personalização", "Logo + cores + escalas customizadas"),
        ("Consultoria Técnica", "Especialistas para cada aplicação"),
        ("NF-e e Suporte", "Documentação e atendimento pós-venda"),
    ]
    col_w = box_w / 4
    for i, (titulo, desc) in enumerate(diferenciais):
        cx = 20 * mm + i * col_w + 5 * mm
        # icon dot
        c.setFillColor(CYAN)
        c.circle(cx + 2, y_box + box_h - 11 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(SLATE_900)
        c.setFont(Fonts.display_bold, 10)
        c.drawString(cx + 9, y_box + box_h - 13 * mm, titulo)
        c.setFillColor(SLATE_600)
        c.setFont(Fonts.body, 8.2)
        for j, line in enumerate(wrap_text(c, desc, Fonts.body, 8.2, col_w - 10)):
            c.drawString(cx, y_box + box_h - 21 * mm - j * 11, line)
        if i < 3:
            c.setStrokeColor(SLATE_200)
            c.setLineWidth(0.4)
            c.line(20 * mm + (i + 1) * col_w, y_box + 6 * mm, 20 * mm + (i + 1) * col_w, y_box + box_h - 6 * mm)

    draw_footer_strip(c, page_num=2)
    c.showPage()


# ---------------------------------------------------------------------------
# INDEX
# ---------------------------------------------------------------------------
def page_index(c, products, product_pages):
    width, height = A4
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    draw_header_strip(c)

    c.setFillColor(ELECTRIC)
    c.setFont(Fonts.body_bold, 8.5)
    c.drawString(20 * mm, height - 26 * mm, "SUMÁRIO")
    c.setFillColor(CYAN)
    c.rect(20 * mm, height - 29 * mm, 14 * mm, 0.6, fill=1, stroke=0)
    c.setFillColor(SLATE_900)
    c.setFont(Fonts.display_xbold, 30)
    c.drawString(20 * mm, height - 42 * mm, "Índice")
    c.setFillColor(SLATE_600)
    c.setFont(Fonts.body, 11)
    c.drawString(20 * mm, height - 50 * mm, f"{len(products)} produtos organizados por categoria")

    groups = {}
    for p in products:
        groups.setdefault(p["categoria"], []).append(p)

    y = height - 65 * mm

    col_x = [20 * mm, width / 2 + 4 * mm]
    col_widths = [width / 2 - 28 * mm] * 2
    col = 0
    y_start_row = y

    for cat in ("manometros", "manovacuometros", "vacuometros", "termometros"):
        items = groups.get(cat, [])
        if not items:
            continue
        if col == 1:
            y = max(y, y_start_row)
            col = 0
            y_start_row = y
        accent = cat_color(cat)
        # marcador da categoria na cor do acento
        c.setFillColor(accent)
        c.rect(col_x[col], y - 0.5, 2.4 * mm, 2.4 * mm, fill=1, stroke=0)
        c.setFillColor(accent)
        c.setFont(Fonts.display_bold, 11.5)
        c.drawString(col_x[col] + 4 * mm, y, CAT_LABEL[cat])
        c.setFillColor(SLATE_400)
        c.setFont(Fonts.body, 9)
        c.drawRightString(col_x[col] + col_widths[col], y, f"{len(items)} produtos")
        y -= 5
        c.setStrokeColor(accent)
        c.setLineWidth(0.8)
        c.line(col_x[col], y, col_x[col] + col_widths[col], y)
        y -= 9

        c.setFont(Fonts.body, 8.6)
        for p in items:
            if y < 25 * mm:
                if col == 0:
                    col = 1
                    y = y_start_row
                else:
                    draw_footer_strip(c, page_num=3)
                    c.showPage()
                    c.setFillColor(white)
                    c.rect(0, 0, width, height, fill=1, stroke=0)
                    draw_header_strip(c)
                    y = height - 30 * mm
                    y_start_row = y
                    col = 0
            c.setFillColor(SLATE_900)
            name = p["nome"]
            max_name_w = col_widths[col] - 15 * mm
            if c.stringWidth(name, Fonts.body, 8.6) > max_name_w:
                while c.stringWidth(name + "…", Fonts.body, 8.6) > max_name_w and len(name) > 8:
                    name = name[:-1]
                name = name + "…"
            c.drawString(col_x[col], y, name)
            c.setFillColor(SLATE_400)
            c.drawRightString(col_x[col] + col_widths[col], y, f"pág. {product_pages.get(p['id'], '—')}")
            y -= 11
        y -= 8

    draw_footer_strip(c, page_num=3)
    c.showPage()


# ---------------------------------------------------------------------------
# PRODUCT PAGE
# ---------------------------------------------------------------------------
def page_product(c, product, page_num, total_pages):
    width, height = A4
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    draw_header_strip(c)

    cat = CAT_LABEL.get(product["categoria"], product["categoria"].upper())
    accent = cat_color(product["categoria"])
    c.setFillColor(accent)
    c.setFont(Fonts.body_bold, 8.5)
    c.drawString(20 * mm, height - 26 * mm, f"{CAT_NUM.get(product['categoria'], '')} · {cat}".strip(" ·"))
    c.setFillColor(accent)
    c.rect(20 * mm, height - 29 * mm, 14 * mm, 0.6, fill=1, stroke=0)

    c.setFillColor(SLATE_900)
    c.setFont(Fonts.display_xbold, 18)
    title = product["nome"]
    if product.get("glicerina") is True:
        title += " — PREPARADO PARA GLICERINA"
    elif product.get("glicerina") is False:
        title += " — NÃO LEVA GLICERINA"
    title_lines = wrap_text(c, title, Fonts.display_xbold, 18, width - 40 * mm)
    ty = height - 40 * mm
    for line in title_lines:
        c.drawString(20 * mm, ty, line)
        ty -= 22

    # Photos
    photos_y = ty - 5 * mm
    photo_w = (width - 40 * mm - 8 * mm) / 2
    photo_h = 75 * mm
    photos_box_y = photos_y - photo_h
    if photos_box_y < 110 * mm:
        photo_h = photos_y - 110 * mm
        photos_box_y = photos_y - photo_h

    front_path = SITE_ROOT / product.get("imagem", "")
    back_path = SITE_ROOT / product.get("imagem_verso", "") if product.get("imagem_verso") else None

    # Sutil fundo cinza atrás das fotos
    c.setFillColor(SLATE_50)
    c.setStrokeColor(SLATE_200)
    c.setLineWidth(0.4)
    c.roundRect(20 * mm, photos_box_y - 2 * mm, photo_w, photo_h + 4 * mm, 2 * mm, fill=1, stroke=1)
    if back_path and back_path.exists() and back_path.is_file():
        c.roundRect(20 * mm + photo_w + 8 * mm, photos_box_y - 2 * mm, photo_w, photo_h + 4 * mm, 2 * mm, fill=1, stroke=1)

    if front_path.exists() and front_path.is_file():
        c.drawImage(
            str(front_path),
            20 * mm,
            photos_box_y,
            photo_w,
            photo_h,
            preserveAspectRatio=True,
            mask="auto",
        )
    if back_path and back_path.exists() and back_path.is_file():
        c.drawImage(
            str(back_path),
            20 * mm + photo_w + 8 * mm,
            photos_box_y,
            photo_w,
            photo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Specs
    specs = product.get("specs", {})
    aplicacao = product.get("aplicacao", "")

    specs_y = photos_box_y - 10 * mm
    col_x = [20 * mm, width / 2 + 4 * mm]
    col_w = width / 2 - 28 * mm
    label_color = accent
    value_color = SLATE_900
    icon_sz = 4.2 * mm
    text_off = icon_sz + 2.2 * mm  # recuo do texto p/ caber o ícone

    def draw_specs_column(col, items, top_y):
        y = top_y
        x0 = col_x[col]
        tx = x0 + text_off
        avail_w = col_w - text_off
        for key, label in items:
            value = specs.get(key, "")
            if not value:
                continue
            # ícone da spec na cor da categoria, alinhado à linha do label
            draw_spec_icon(c, key, x0, y - 0.6 * mm, icon_sz, accent)
            c.setFillColor(label_color)
            c.setFont(Fonts.body_bold, 9.5)
            c.drawString(tx, y, label)
            lbl_w = c.stringWidth(label + " ", Fonts.body_bold, 9.5)
            c.setFillColor(value_color)
            c.setFont(Fonts.body, 9.5)
            avail = avail_w - lbl_w
            if c.stringWidth(value, Fonts.body, 9.5) <= avail:
                c.drawString(tx + lbl_w, y, value)
                y -= 14
            else:
                y -= 12
                for line in wrap_text(c, value, Fonts.body, 9.5, avail_w):
                    c.drawString(tx, y, line)
                    y -= 12
                y -= 2
        return y

    y_left = draw_specs_column(0, SPECS_LEFT, specs_y)
    y_right = draw_specs_column(1, SPECS_RIGHT, specs_y)
    y_after = min(y_left, y_right) - 4

    if aplicacao:
        c.setFillColor(label_color)
        c.setFont(Fonts.body_bold, 9.5)
        c.drawString(20 * mm, y_after, "Aplicação:")
        c.setFillColor(SLATE_900)
        c.setFont(Fonts.body, 9.5)
        y = y_after - 14
        for line in wrap_text(c, aplicacao, Fonts.body, 9.5, width - 40 * mm):
            c.drawString(20 * mm, y, line)
            y -= 13

    c.setFillColor(SLATE_400)
    c.setFont(Fonts.body, 8)
    c.drawString(20 * mm, 30 * mm, "* Escalas e configurações personalizáveis sob consulta.")

    cta_y = 18 * mm
    c.setFillColor(WHATSAPP)
    c.roundRect(20 * mm, cta_y, width - 40 * mm, 9 * mm, 2 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(Fonts.body_bold, 10)
    c.drawCentredString(width / 2, cta_y + 3 * mm, f"Orçamento via WhatsApp  ·  {PHONE}  ·  {EMAIL}")

    draw_footer_strip(c, page_num=page_num, total_pages=total_pages)
    c.showPage()


# ---------------------------------------------------------------------------
# CATEGORY OPENER — banda colorida + número grande (template do Design System)
# ---------------------------------------------------------------------------
def page_category_opener(c, cat, items, page_num, total_pages):
    width, height = A4
    accent = cat_color(cat)
    band_h = height * 0.36

    # fundo branco
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # banda de cor no terço superior
    c.setFillColor(accent)
    c.rect(0, height - band_h, width, band_h, fill=1, stroke=0)

    # número grande translúcido no canto direito da banda
    c.saveState()
    c.setFillColor(_with_alpha(white, 0.16))
    c.setFont(Fonts.display_xbold, 150)
    c.drawRightString(width - 16 * mm, height - band_h + 14 * mm, CAT_NUM.get(cat, ""))
    c.restoreState()

    # eyebrow + nome da categoria (sobre a banda, base inferior)
    c.setFillColor(_with_alpha(white, 0.85))
    c.setFont(Fonts.body_bold, 9)
    c.drawString(20 * mm, height - band_h + 30 * mm, f"CATEGORIA {CAT_NUM.get(cat, '')}")
    c.setFillColor(white)
    c.setFont(Fonts.display_xbold, 34)
    c.drawString(20 * mm, height - band_h + 14 * mm, CAT_LABEL[cat].title())

    # corpo: lede + contagem
    y = height - band_h - 22 * mm
    y = draw_paragraph(c, 20 * mm, y, CAT_LEDE.get(cat, ""), Fonts.body, 12,
                       width - 40 * mm, line_height=18, color=SLATE_700)

    # destaque de contagem
    y -= 10 * mm
    c.setFillColor(accent)
    c.setFont(Fonts.display_xbold, 28)
    c.drawString(20 * mm, y, str(len(items)))
    c.setFillColor(SLATE_600)
    c.setFont(Fonts.body, 11)
    c.drawString(20 * mm + c.stringWidth(str(len(items)), Fonts.display_xbold, 28) + 4 * mm, y + 2,
                 "produtos nesta categoria")

    # linha de acento
    c.setFillColor(accent)
    c.rect(20 * mm, y - 8 * mm, 30 * mm, 0.8, fill=1, stroke=0)

    draw_footer_strip(c, page_num=page_num, total_pages=total_pages)
    c.showPage()


# ---------------------------------------------------------------------------
# BACK COVER
# ---------------------------------------------------------------------------
def page_back(c):
    width, height = A4
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Marca d'agua
    draw_aperture_mark(
        c, width - 70 * mm, height - 90 * mm, 160 * mm,
        body_color=_with_alpha(CYAN, 0.06),
        needle_color=_with_alpha(CYAN, 0.08),
    )

    # Logo no topo
    draw_logo(c, 20 * mm, height - 22 * mm, size=16)
    c.setFillColor(CYAN)
    c.rect(20 * mm, height - 28 * mm, width - 40 * mm, 0.4, fill=1, stroke=0)

    # Eyebrow
    c.setFillColor(CYAN)
    c.setFont(Fonts.body_bold, 8.5)
    c.drawString(20 * mm, height - 50 * mm, "VAMOS CONVERSAR?")

    # Big title
    c.setFillColor(white)
    c.setFont(Fonts.display_xbold, 40)
    c.drawString(20 * mm, height - 75 * mm, "Estamos prontos")
    c.setFillColor(ELECTRIC)
    c.drawString(20 * mm, height - 95 * mm, "para o seu projeto.")
    c.setFillColor(_with_alpha(white, 0.7))
    c.setFont(Fonts.body, 12)
    c.drawString(20 * mm, height - 105 * mm, "Consultoria, orçamento e suporte técnico em instrumentação industrial.")

    # Contact card
    box_y = 60 * mm
    box_h = 80 * mm
    c.setFillColor(NAVY_LIGHT)
    c.setStrokeColor(_with_alpha(CYAN, 0.25))
    c.setLineWidth(0.6)
    c.roundRect(20 * mm, box_y, width - 40 * mm, box_h, 4 * mm, fill=1, stroke=1)
    c.setFillColor(CYAN)
    c.rect(20 * mm, box_y, 1.6 * mm, box_h, fill=1, stroke=0)

    # Layout em grade 2 colunas; endereço ocupa linha inteira (largo)
    info_grid = [
        # (label, value, full_row?)
        [("WHATSAPP", PHONE, False), ("EMAIL", EMAIL, False)],
        [("SITE", SITE, False), ("INSTAGRAM", INSTAGRAM, False)],
        [("ENDEREÇO", ADDRESS, True)],
        [("ATENDIMENTO", "Seg–Sex 8h–18h  ·  Sáb 8h–12h", True)],
    ]
    col_x = [28 * mm, width / 2 + 4 * mm]
    row_y_start = box_y + box_h - 14 * mm
    row_step = 16 * mm
    for row_idx, row in enumerate(info_grid):
        y = row_y_start - row_idx * row_step
        for col_idx, item in enumerate(row):
            label, value, full = item
            x = col_x[col_idx]
            c.setFillColor(CYAN)
            c.setFont(Fonts.body_bold, 7.5)
            c.drawString(x, y, label)
            c.setFillColor(white)
            c.setFont(Fonts.display_bold, 11)
            c.drawString(x, y - 10, value)

    c.setFillColor(_with_alpha(white, 0.4))
    c.setFont(Fonts.body, 8.5)
    c.drawCentredString(width / 2, 38 * mm, f"© 2026 {COMPANY}. Todos os direitos reservados.")
    c.drawCentredString(width / 2, 30 * mm, "Catálogo de Produtos · Edição 2026")

    # Linha cyan inferior
    c.setFillColor(CYAN)
    c.rect(20 * mm, 22 * mm, width - 40 * mm, 0.4, fill=1, stroke=0)
    c.setFillColor(_with_alpha(white, 0.35))
    c.setFont(Fonts.body, 8)
    c.drawString(20 * mm, 16 * mm, ADDRESS)
    c.drawRightString(width - 20 * mm, 16 * mm, SITE)

    c.showPage()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    with DATA.open(encoding="utf-8") as f:
        products = json.load(f)

    cat_order = {"manometros": 0, "manovacuometros": 1, "vacuometros": 2, "termometros": 3}
    products.sort(key=lambda p: (cat_order.get(p["categoria"], 9), p["nome"]))

    # Ordem das categorias presentes
    ordered_cats = sorted(
        {p["categoria"] for p in products},
        key=lambda cat: cat_order.get(cat, 9),
    )
    groups = {}
    for p in products:
        groups.setdefault(p["categoria"], []).append(p)

    # Pré-cálculo da paginação: cover(1) sobre(2) índice(3),
    # depois para cada categoria: 1 abertura + N produtos; por fim contracapa.
    product_pages = {}
    page = 4
    for cat in ordered_cats:
        page += 1  # página de abertura da categoria
        for p in groups[cat]:
            product_pages[p["id"]] = page
            page += 1
    total_pages = page  # número da contracapa = última página

    setup_fonts()

    tmp_out = OUTPUT.with_suffix(".tmp.pdf")
    c = canvas.Canvas(str(tmp_out), pagesize=A4)
    c.setTitle("Catálogo Press Control 2026")
    c.setAuthor("Press Control")
    c.setSubject("Catálogo de Produtos")

    page_cover(c)
    page_sobre(c)
    page_index(c, products, product_pages)

    page_num = 4
    for cat in ordered_cats:
        page_category_opener(c, cat, groups[cat], page_num, total_pages)
        page_num += 1
        for p in groups[cat]:
            page_product(c, p, page_num, total_pages)
            page_num += 1

    page_back(c)
    c.save()

    try:
        if OUTPUT.exists():
            OUTPUT.unlink()
        tmp_out.rename(OUTPUT)
    except PermissionError:
        print(f"AVISO: nao consegui sobrescrever {OUTPUT.name}. PDF salvo em {tmp_out.name}")
        size_mb = tmp_out.stat().st_size / (1024 * 1024)
        print(f"Generated {tmp_out}  ({size_mb:.2f} MB)")
        return

    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"Generated {OUTPUT}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
