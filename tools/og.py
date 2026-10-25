"""Render the Open Graph images (1200 x 630) for every page into assets/og/.

Run from the project root:  python tools/og.py
Needs Python Playwright with Chrome installed (channel="chrome").
"""
import html
import math
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og"
FONTS = (ROOT / "assets" / "fonts").as_uri()
LOGO = (ROOT / "assets" / "brand" / "logo.svg").as_uri()

PAGES = [
    ("index", "Home", "Software built on time. Kept running."),
    ("services", "Services", "What we build, connect and run."),
    ("work", "Work", "Systems we design, build and operate."),
    ("about", "About", "An Egyptian engineering team that keeps time."),
    ("contact", "Contact", "Have a software project in mind?"),
    ("brand", "Brand guidelines", "The Gnomon identity."),
] + [(f"services-{s['slug']}", "Service", s["name"] + ".") for s in C.SERVICES]


def dial(t=10.5):
    """The hero sundial, simplified: plate, twelve hour lines, stem, shadow, sun."""
    cx, cy, r = 300, 300, 230
    lines = "".join(
        f'<line x1="{cx + 40 * math.cos(math.radians(-(h - 6) * 15)):.1f}" y1="{cy - 40 * math.sin(math.radians(-(h - 6) * 15)):.1f}" '
        f'x2="{cx + (r - 14) * math.cos(math.radians(-(h - 6) * 15)):.1f}" y2="{cy - (r - 14) * math.sin(math.radians(-(h - 6) * 15)):.1f}" '
        f'stroke="{"#5d6778" if h % 3 == 0 else "#b9c1cd"}" stroke-width="{1.6 if h % 3 == 0 else 1.2}"/>' for h in range(6, 19))
    a_sun = math.radians(180 - (t - 6) * 15)
    sx, sy = cx + 250 * math.cos(a_sun), cy - 250 * math.sin(a_sun)
    a_sh = math.radians(-(t - 6) * 15)
    ux, uy = math.cos(a_sh), -math.sin(a_sh)
    px, py = -uy, ux
    ln = 120 + 100 * abs(math.cos(a_sun))
    tip = (cx + ux * ln, cy + uy * ln)
    shadow = (f"M{cx + px * 8:.1f} {cy + py * 8:.1f} L{tip[0] + px * 3:.1f} {tip[1] + py * 3:.1f} "
              f"L{tip[0] - px * 3:.1f} {tip[1] - py * 3:.1f} L{cx - px * 8:.1f} {cy - py * 8:.1f} Z")
    sky = " ".join(f"{cx + 250 * math.cos(math.radians(d)):.1f},{cy - 250 * math.sin(math.radians(d)):.1f}" for d in range(180, -1, -4))
    return f'''<svg viewBox="40 30 520 520" width="470" height="470">
  <path d="M{cx - r} {cy} A{r} {r} 0 0 0 {cx + r} {cy} Z" fill="#f2f4f7"/>
  {lines}
  <polyline points="{sky}" fill="none" stroke="#b9c1cd" stroke-width="1.6" stroke-dasharray="2 8" stroke-linecap="round"/>
  <line x1="40" y1="{cy}" x2="560" y2="{cy}" stroke="#0e1726" stroke-width="2"/>
  <path d="{shadow}" fill="#1034a6"/>
  <rect x="{cx - 8}" y="{cy - 100}" width="16" height="100" rx="8" fill="#0e1726"/>
  <circle cx="{sx:.1f}" cy="{sy:.1f}" r="17" fill="#ff5a1f"/>
</svg>'''


def card(label, title):
    size = 76 if len(title) < 34 else 64 if len(title) < 46 else 56
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Funnel Display"; src: url("{FONTS}/funnel-display.woff2") format("woff2"); font-weight: 300 800; }}
@font-face {{ font-family: "Geist Mono"; src: url("{FONTS}/geist-mono.woff2") format("woff2"); font-weight: 400 600; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: 1200px; height: 630px; background: #fff; overflow: hidden; position: relative; font-family: "Funnel Display", sans-serif; color: #0e1726; }}
.logo {{ position: absolute; left: 72px; top: 64px; height: 40px; }}
.label {{ position: absolute; left: 72px; top: 190px; font: 500 18px/1 "Geist Mono", monospace; letter-spacing: .1em; text-transform: uppercase; color: #5d6778; }}
h1 {{ position: absolute; left: 72px; top: 232px; width: 620px; font-weight: 700; font-size: {size}px; line-height: 1.02; letter-spacing: -0.035em; }}
.dial {{ position: absolute; right: 40px; top: 44px; }}
.rule {{ position: absolute; left: 72px; right: 72px; bottom: 64px; height: 10px; border-top: 1.5px solid #dde2e9;
  background: repeating-linear-gradient(90deg, #b9c1cd 0 1.5px, transparent 1.5px calc(100% / 12)) top left / calc(100% + 1.5px) 9px no-repeat; }}
.rule i {{ position: absolute; top: -6px; left: 37.5%; width: 11px; height: 11px; border-radius: 50%; background: #ff5a1f; }}
.url {{ position: absolute; right: 72px; top: 76px; font: 500 18px/1 "Geist Mono", monospace; color: #5d6778; }}
</style></head><body>
<img class="logo" src="{LOGO}" alt="">
<p class="label">{html.escape(label)}</p>
<h1>{html.escape(title)}</h1>
<div class="dial">{dial()}</div>
<p class="url">intimedev.com</p>
<div class="rule"><i></i></div>
</body></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        tmp = OUT / "_card.html"   # a file:// page, so fonts and the logo load from disk
        for name, label, title in PAGES:
            tmp.write_text(card(label, title), encoding="utf-8")
            page.goto(tmp.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(150)
            page.screenshot(path=str(OUT / f"{name}.png"))
        browser.close()
    tmp.unlink()
    print(f"rendered {len(PAGES)} images into {OUT}")


if __name__ == "__main__":
    main()
