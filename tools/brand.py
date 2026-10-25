"""Generate the Intimedev logo files (SVG) from the mark geometry and the Funnel Display outlines.

Run: python -I tools/brand.py   (from the project root)
Writes assets/brand/*.svg
"""
import os
import tempfile
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "brand"
FONT = ROOT / "assets" / "fonts" / "funnel-display.woff2"

INK = "#0e1726"
BLUE = "#1034a6"
SUN = "#ff5a1f"
NIGHT_INK = "#eef1f6"
NIGHT_BLUE = "#7d95ff"

# The gnomon mark on a 64 grid: stem (the i), its shadow on the ground, the sun as the dot.
# Light comes from the upper left, so the shadow falls to the right along the baseline.
STEM = dict(x=14, y=21, w=12, h=37, r=6)
# Shadow: a wedge that thins and dips slightly as it leaves the stem, so it reads as cast light, not a letter L.
SHADOW_D = "M20 46L55 51.5A3 3 0 0 1 55 57.5L20 58Z"
SUN_C = dict(cx=10, cy=10, r=7)


def mark_shapes(ink, blue, sun, dx=0.0, dy=0.0, s=1.0):
    def rect(d, fill):
        return (f'<rect x="{dx + d["x"] * s:.2f}" y="{dy + d["y"] * s:.2f}" width="{d["w"] * s:.2f}" '
                f'height="{d["h"] * s:.2f}" rx="{d["r"] * s:.2f}" fill="{fill}"/>')
    return "".join([
        f'<path d="{SHADOW_D}" fill="{blue}" transform="translate({dx:.2f} {dy:.2f}) scale({s:.4f})"/>',
        rect(STEM, ink),
        f'<circle cx="{dx + SUN_C["cx"] * s:.2f}" cy="{dy + SUN_C["cy"] * s:.2f}" r="{SUN_C["r"] * s:.2f}" fill="{sun}"/>',
    ])


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" role="img" aria-label="{title}">'
            f"<title>{title}</title>{body}</svg>\n")


def instance(weight):
    font = TTFont(FONT)
    return instancer.instantiateVariableFont(font, {"wght": weight})


def outline(font, text, x0):
    """Return (svg path d, advance end x, bounds) for text at font units, y flipped (baseline at 0)."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    parts, x = [], x0
    bp = BoundsPen(gs)
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        gs[name].draw(TransformPen(bp, (1, 0, 0, -1, x, 0)))
        parts.append(pen.getCommands())
        x += hmtx[name][0]
    return " ".join(parts), x, bp.bounds


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    bold, regular = instance(700), instance(400)
    upm = bold["head"].unitsPerEm
    xh = bold["OS/2"].sxHeight

    d_in, end_in, b1 = outline(bold, "intime", 0)
    d_dev, end_dev, b2 = outline(regular, "dev", end_in + upm * 0.004)
    top = min(b1[1], b2[1])          # ascender of d / i-dot (negative y)

    # Scale the mark so its stem sits on the baseline and its sun reaches the ascender.
    mark_h = 58 - 3                   # stem bottom (58) to sun top (3) on the 64 grid
    s = (-top) / mark_h
    mark_w = 58 * s
    gap = upm * 0.16
    text_x = mark_w + gap
    pad = upm * 0.02
    width = text_x + end_dev + pad
    height = -top + pad * 2
    dy = pad + (-top) - 58 * s        # put the stem bottom on the baseline

    def lockup(ink, blue, sun, title):
        body = mark_shapes(ink, blue, sun, dx=0, dy=dy, s=s)
        body += (f'<g transform="translate({text_x:.2f} {pad + -top:.2f})" fill="{ink}">'
                 f'<path d="{d_in}"/><path d="{d_dev}"/></g>')
        return svg(width, height, body, title)

    files = {
        "logo.svg": lockup(INK, BLUE, SUN, "Intimedev"),
        "logo-dark.svg": lockup(NIGHT_INK, NIGHT_BLUE, SUN, "Intimedev"),
        "logo-mono.svg": lockup(INK, INK, INK, "Intimedev"),
        "logo-mono-white.svg": lockup("#ffffff", "#ffffff", "#ffffff", "Intimedev"),
        "mark.svg": svg(64, 64, mark_shapes(INK, BLUE, SUN, dx=-1, dy=0), "Intimedev mark"),
        "mark-dark.svg": svg(64, 64, mark_shapes(NIGHT_INK, NIGHT_BLUE, SUN, dx=-1), "Intimedev mark"),
        "mark-mono.svg": svg(64, 64, mark_shapes(INK, INK, INK, dx=-1), "Intimedev mark"),
        # App icon / favicon: mark on an Egyptian blue tile, shadow in white so it survives at 16px.
        "app-icon.svg": svg(64, 64, '<rect width="64" height="64" rx="14" fill="%s"/>' % BLUE
                            + mark_shapes("#ffffff", "#8fa3ff", SUN, dx=4.6, dy=4.6, s=0.86), "Intimedev"),
        "favicon.svg": svg(64, 64, '<rect width="64" height="64" rx="14" fill="%s"/>' % BLUE
                           + mark_shapes("#ffffff", "#8fa3ff", SUN, dx=4.6, dy=4.6, s=0.86), "Intimedev"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"lockup {width:.0f}x{height:.0f} units, mark scale {s:.2f}, x-height {xh}")


if __name__ == "__main__":
    build()
