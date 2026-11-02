"""Generate the Nebe / Peklo / Ráj logo as SVG.

Each letter is a centre-line path drawn as a rounded "tube": the same path is
stroked many times, each pass thinner and lighter. The shading therefore follows
the stroke itself, including the bends (N, K, R ...), so a letter reads as one
continuous bent tube instead of flat overlapping pieces.

Run: python3 assets/logo/generate_logo.py   (writes the SVGs next to this file)
"""
import math
import os

H = 100          # cap height (centre-line runs 5..95, stroke caps fill 0..100)
W = 12           # stroke width
GAP = 7          # space between letters
LINE_GAP = 16    # space between words
ACCENT_SPACE = 14  # extra room above the line holding Á

# Centre-line paths. Each value: (path, advance width).
LETTERS = {
    "N": ("M5,95 V5 L29,95 V5", 34),
    "E": ("M28,5 H5 V95 H28 M5,50 H24", 33),
    "B": ("M5,50 H16 C30,50 30,95 16,95 H5 V5 H15 C27,5 27,50 15,50", 32),
    "P": ("M5,95 V5 H15 C29,5 29,56 15,56 H5", 31),
    "K": ("M5,5 V95 M28,5 L6,62 M15,40 L29,95", 34),
    "L": ("M5,5 V95 H27", 31),
    "O": ("M17,5 C31,5 31,5 31,30 V70 C31,95 31,95 17,95 C3,95 3,95 3,70 V30 C3,5 3,5 17,5 Z", 34),
    "R": ("M5,95 V5 H15 C29,5 29,56 15,56 H5 M15,56 L29,95", 34),
    "Á": ("M5,95 L19,5 L33,95 M10,64 H28 M17,-6 L25,-17", 38),
    "J": ("M25,5 V72 C25,99 5,99 5,76", 30),
}

# Colour per word: (edge / shadow, middle, highlight)
PALETTES = {
    "nebe":  ("#083a7a", "#1477d4", "#7cc8ff"),
    "peklo": ("#5e0a0a", "#d0261c", "#ffa04a"),
    "raj":   ("#16502a", "#2f9a45", "#a6e57a"),
}
WORDS = [("NEBE", "nebe"), ("PEKLO", "peklo"), ("RÁJ", "raj")]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    a, b = hex_to_rgb(a), hex_to_rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def shade(pal, t):
    """t = 0 at the tube edge, 1 at its centre."""
    edge, mid, light = pal
    if t < 0.75:
        return mix(edge, mid, (t / 0.75) ** 0.6)
    return mix(mid, light, ((t - 0.75) / 0.25) ** 1.5)


def tube_layers(pal, layers=28, light_shift=(0.0, 0.0)):
    """Return list of (width, colour, dx, dy) passes from outer to inner."""
    out = []
    for i in range(layers):
        r = 1 - i / layers                     # 1 = full width ... small = core
        t = math.sqrt(max(0.0, 1 - r * r))     # cylinder lighting
        k = 1 - r
        out.append((W * r, shade(pal, t), light_shift[0] * k, light_shift[1] * k))
    return out


def layout():
    """Place letters; returns list of (char, word_key, x, y) and total size."""
    rows = []
    for word, key in WORDS:
        width = sum(LETTERS[c][1] for c in word) + GAP * (len(word) - 1)
        rows.append((word, key, width))
    total_w = max(r[2] for r in rows)
    placed, y = [], 0
    for word, key, width in rows:
        if any(c in "Á" for c in word):
            y += ACCENT_SPACE
        x = (total_w - width) / 2
        for c in word:
            placed.append((c, key, x, y))
            x += LETTERS[c][1] + GAP
        y += H + LINE_GAP
    return placed, total_w, y - LINE_GAP


def build(style):
    placed, tw, th = layout()
    pad = 8
    parts = []
    for c, key, x, y in placed:
        path = LETTERS[c][0]
        g = [f'<g transform="translate({x:.1f},{y:.1f})" fill="none" '
             f'stroke-linecap="round" stroke-linejoin="round">']
        if style in ("tube", "tube-lit"):
            shift = (-1.6, -1.2) if style == "tube-lit" else (0, 0)
            for w, col, dx, dy in tube_layers(PALETTES[key], light_shift=shift):
                tr = f' transform="translate({dx:.2f},{dy:.2f})"' if (dx or dy) else ""
                g.append(f'<path d="{path}" stroke="{col}" stroke-width="{w:.2f}"{tr}/>')
        elif style == "flat":
            g.append(f'<path d="{path}" stroke="{PALETTES[key][1]}" stroke-width="{W}"/>')
        elif style == "mono":
            g.append(f'<path d="{path}" stroke="currentColor" stroke-width="{W}"/>')
        g.append("</g>")
        parts.append("".join(g))
    vb = f"{-pad} {-pad} {tw + 2 * pad:.1f} {th + 2 * pad:.1f}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'role="img" aria-label="Nebe Peklo Ráj">\n<title>Nebe Peklo Ráj</title>\n'
            + "\n".join(parts) + "\n</svg>\n")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for style in ("tube", "tube-lit", "flat", "mono"):
        with open(os.path.join(here, f"logo-{style}.svg"), "w", encoding="utf-8") as f:
            f.write(build(style))
    print("ok")
