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
W = 13           # stroke width
GAP = 8          # space between letters
LINE_GAP = 16    # space between words
ACCENT_SPACE = 14  # extra room above the line holding Á

# Centre-line paths. Each value: (path, advance width).
LETTERS = {
    "N": ("M7,94 V6 L45,94 V6", 52),
    "E": ("M42,6 H7 V94 H42 M7,50 H37", 49),
    "B": ("M7,50 H30 C46,50 46,94 30,94 H7 V6 H28 C43,6 43,50 28,50", 50),
    "P": ("M7,94 V6 H29 C46,6 46,56 29,56 H7", 50),
    "K": ("M7,6 V94 M43,6 L9,62 M22,44 L45,94", 52),
    "L": ("M7,6 V94 H41", 47),
    "O": ("M25,6 H29 C40,6 46,12 46,24 V76 C46,88 40,94 29,94 H25 "
          "C14,94 7,88 7,76 V24 C7,12 14,6 25,6 Z", 53),
    "R": ("M7,94 V6 H29 C46,6 46,56 29,56 H7 M28,56 L45,94", 52),
    "Á": ("M7,94 L27,6 L47,94 M14,64 H40 M25,-6 L33,-17", 54),
    "J": ("M38,6 V70 C38,98 7,98 7,74", 45),
}

# Colour per word: (edge, main, highlight). Edge + main are Tobias's colours.
PALETTES = {
    "nebe":  ("#194FA2", "#1963D1", "#4F8BE6"),
    "peklo": ("#B92A2A", "#EE2A2A", "#FF6A5C"),
    "raj":   ("#4DB21B", "#5DDA1F", "#8FEA5A"),
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
    # Soft shading: mostly the main colour, gentle edge, small highlight.
    if t < 0.6:
        return mix(edge, mid, (t / 0.6) ** 0.7)
    return mix(mid, light, ((t - 0.6) / 0.4) ** 2 * 0.85)


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
            shift = (-2.6, -2.0) if style == "tube-lit" else (0, 0)
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
