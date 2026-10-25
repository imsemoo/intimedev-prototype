"""Build the Intimedev static site from tools/content.py.

Run from the project root:  python -I tools/build.py
Outputs HTML files in the project root and in services/.
"""
import html
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
V = "4"  # asset version: bump after CSS/JS changes
# The 404 page is served at any depth, so its links must be absolute to the Pages site root.
BASE404 = "/intimedev-prototype/"
NAV = [("services.html", "Services"), ("work.html", "Work"), ("about.html", "About"), ("contact.html", "Contact")]
SVC = {s["slug"]: s for s in C.SERVICES}
e = html.escape


def icon(name, cls="ico", r=""):
    return f'<svg class="{cls}" aria-hidden="true"><use href="{r}assets/icons/icons.svg#{name}"/></svg>'


# ---------------------------------------------------------------- dial

CX, CY, R_PLATE = 280, 280, 230
# The sun travels a circle just outside the plate, concentric with the dial.
SKY_RX, SKY_RY = 236, 236
BANDS = [("cairo", "CAI", 202), ("sydney", "SYD", 180), ("london", "LON", 158)]


def polar(r, deg):
    a = math.radians(deg)
    return CX + r * math.cos(a), CY - r * math.sin(a)


def shadow_angle(t):
    """Cairo hour (6..18) to the direction of the shadow on the plate, in degrees (math, y up)."""
    return -(t - 6) * 15


def arc_points(r, t1, t2, steps=24):
    pts = [polar(r, shadow_angle(t1 + (t2 - t1) * i / steps)) for i in range(steps + 1)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def offsets_now():
    """Hours each city is ahead of Cairo, for the no-JavaScript dial only (time.js recomputes live,
    including daylight saving). Values for late October; Windows Python has no tz database without tzdata."""
    return {"cairo": 0, "sydney": 8, "london": -3}


def band_segments(delta):
    """Local 09:00-17:00 for a city `delta` hours ahead of Cairo, as Cairo hours clipped to the 06-18 plate."""
    segs = []
    for shift in (-24, 0, 24):
        a, b = 9 - delta + shift, 17 - delta + shift
        lo, hi = max(a, 6), min(b, 18)
        if hi > lo:
            segs.append((lo, hi))
    return segs


def dial_svg(t=10.0):
    a_sun = 180 - (t - 6) * 15
    sx, sy = sky(a_sun)
    hours = []
    for h in range(6, 19):
        x1, y1 = polar(40, shadow_angle(h))
        x2, y2 = polar(R_PLATE - 12, shadow_angle(h))
        major = " major" if h % 3 == 0 else ""
        hours.append(f'<line class="hour{major}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        if h % 3 == 0:
            # 06 and 18 sit just under the horizon so the line never strikes through them.
            lx, ly = polar(R_PLATE + 18, shadow_angle(h))
            if h in (6, 18):
                lx, ly = (CX + R_PLATE - 4, CY + 20) if h == 6 else (CX - R_PLATE + 4, CY + 20)
            anchor = "end" if h == 6 else "start" if h == 18 else "middle"
            hours.append(f'<text class="hour-label" x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="{anchor}">{h:02d}</text>')
    deltas = offsets_now()
    bands = []
    for key, _code, r in BANDS:
        segs = band_segments(deltas[key])
        d = " ".join(arc_points(r, a, b) for a, b in segs)
        bands.append(f'<path class="band-track" d="{arc_points(r, 6, 18)}"/>')
        bands.append(f'<path class="band{" is-cairo" if key == "cairo" else ""}" data-city="{key}" d="{d}"/>')
    sky_d = arc_points_sky()
    shadow = shadow_path(t)
    return f'''<svg class="dial" viewBox="30 30 500 512" role="group" aria-labelledby="dial-title dial-desc">
  <title id="dial-title">Working hours across Cairo, Sydney and London</title>
  <desc id="dial-desc">A sundial. The sun shows the time in Cairo; its shadow sweeps the plate. The arcs show typical business hours (09:00 to 17:00 local) in each city, drawn in Cairo time. Use the sun handle to move through the day.</desc>
  <path class="plate" d="M{CX - R_PLATE} {CY} A{R_PLATE} {R_PLATE} 0 0 0 {CX + R_PLATE} {CY} Z"/>
  {"".join(hours)}
  {"".join(bands)}
  <path class="sky" d="{sky_d}"/>
  <line class="horizon" x1="30" y1="{CY}" x2="530" y2="{CY}"/>
  <path class="shadow" d="{shadow}"/>
  <rect class="stem" x="{CX - 7}" y="{CY - 92}" width="14" height="92" rx="7"/>
  <circle class="sun" cx="{sx:.1f}" cy="{sy:.1f}" r="14"/>
  <circle class="sun-hit" cx="{sx:.1f}" cy="{sy:.1f}" r="30" tabindex="0" role="slider" aria-label="Time in Cairo" aria-valuemin="6" aria-valuemax="18" aria-valuenow="{t}"/>
  <circle class="sun-ring" cx="{sx:.1f}" cy="{sy:.1f}" r="22"/>
</svg>'''


def sky(deg):
    a = math.radians(deg)
    return CX + SKY_RX * math.cos(a), CY - SKY_RY * math.sin(a)


def arc_points_sky(steps=48):
    pts = [sky(180 - 180 * i / steps) for i in range(steps + 1)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def shadow_path(t):
    a = math.radians(shadow_angle(t))
    length = 120 + 100 * abs(math.cos(math.radians(180 - (t - 6) * 15)))
    ux, uy = math.cos(a), -math.sin(a)          # screen direction
    px, py = -uy, ux                            # perpendicular
    b1 = (CX + px * 7, CY + py * 7)
    b2 = (CX - px * 7, CY - py * 7)
    tip = (CX + ux * length, CY + uy * length)
    t1 = (tip[0] + px * 3, tip[1] + py * 3)
    t2 = (tip[0] - px * 3, tip[1] - py * 3)
    return (f"M{b1[0]:.1f} {b1[1]:.1f} L{t1[0]:.1f} {t1[1]:.1f} A3 3 0 0 1 {t2[0]:.1f} {t2[1]:.1f} "
            f"L{b2[0]:.1f} {b2[1]:.1f} Z")


def dial_block():
    cities = "".join(
        f'<div class="city" data-tz="{m["tz"]}" data-weekend="{m["weekend"]}"><span class="label"><span class="swatch is-{m["city"].lower()}" aria-hidden="true"></span>{m["city"]}</span>'
        f'<span class="time">--:--</span><span class="state">&nbsp;</span></div>' for m in C.MARKETS)
    return f'''<div class="dial-block" data-dial>
  {dial_svg()}
  <div class="dial-readout" aria-live="polite">{cities}</div>
  <p class="dial-note"><span data-dial-note>Drag the sun to compare working hours.</span> <button type="button" data-dial-now hidden>Back to now</button></p>
</div>'''


# ---------------------------------------------------------------- blueprints

def blueprint_svg(bp, uid):
    W, H = 640, 440
    cx, cy = W / 2, H / 2
    hub = {"business-platform": "Dashboard", "mobile-web-ecosystem": "API", "file-exchange": "Vault"}[bp["slug"]]
    parts = [p for p in bp["parts"] if p.lower() != hub.lower()]
    nodes, wires = [], []
    n = len(parts)
    for i, p in enumerate(parts):
        a = -math.pi / 2 + 2 * math.pi * i / n + (math.pi / n if n % 2 == 0 else 0)
        x, y = cx + 212 * math.cos(a), cy + 152 * math.sin(a)
        w = len(p) * 9.6 + 32
        wires.append((x, y))
        nodes.append(
            f'<rect class="node-shadow" x="{x - w / 2 + 5:.1f}" y="{y - 20 + 5:.1f}" width="{w:.1f}" height="40" rx="20"/>'
            f'<rect class="node" x="{x - w / 2:.1f}" y="{y - 20:.1f}" width="{w:.1f}" height="40" rx="20"/>'
            f'<text class="node-text" x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle">{e(p)}</text>')
    wire_d = " ".join(f"M{cx:.0f} {cy:.0f} L{x:.1f} {y:.1f}" for x, y in wires)
    hw = len(hub) * 11 + 48
    px, py = wires[0]
    return f'''<svg class="bp" viewBox="0 0 {W} {H}" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <path class="wire" d="{wire_d}"/>
  {"".join(nodes)}
  <rect class="node-shadow" x="{cx - hw / 2 + 6:.1f}" y="{cy - 28 + 6:.1f}" width="{hw:.1f}" height="56" rx="28"/>
  <rect class="hub" x="{cx - hw / 2:.1f}" y="{cy - 28:.1f}" width="{hw:.1f}" height="56" rx="28"/>
  <text class="hub-text" x="{cx:.1f}" y="{cy + 6:.1f}" text-anchor="middle">{e(hub)}</text>
  <circle class="pulse" r="5" style="offset-path: path('M{px:.1f} {py:.1f} L{cx:.0f} {cy:.0f}')"/>
</svg>'''


# ---------------------------------------------------------------- layout

def head(title, desc, r, extra_css=""):
    css = f'<link rel="stylesheet" href="{r}assets/css/tokens.css?v={V}"><link rel="stylesheet" href="{r}assets/css/site.css?v={V}">'
    if extra_css:
        css += f'<link rel="stylesheet" href="{r}assets/css/{extra_css}?v={V}">'
    org = {
        "@context": "https://schema.org", "@type": "Organization", "name": "Intimedev",
        "url": "https://intimedev.com/", "email": C.EMAIL, "telephone": C.PHONE,
        "areaServed": ["EG", "AU", "GB"],
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#1034a6">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{r}assets/brand/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/funnel-display.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}assets/fonts/funnel-sans.woff2" as="font" type="font/woff2" crossorigin>
{css}
<script>document.documentElement.classList.add("js");try{{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<script type="application/ld+json">{json.dumps(org)}</script>
</head>'''


def header(active, r):
    links = "".join(
        f'<li><a href="{r}{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a></li>' for href, label in NAV)
    mlinks = "".join(
        f'<li style="--i:{i}"><a href="{r}{href}"{" aria-current=\"page\"" if href == active else ""}>{label}{icon("arrow", r=r)}</a></li>'
        for i, (href, label) in enumerate([("index.html", "Home")] + NAV))
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-head" data-head>
  <div class="wrap">
    <a class="brand" href="{r}index.html" aria-label="Intimedev home">
      <img class="logo-light" src="{r}assets/brand/logo.svg" width="155" height="20" alt="Intimedev">
      <img class="logo-dark" src="{r}assets/brand/logo-dark.svg" width="155" height="20" alt="">
    </a>
    <nav class="nav" aria-label="Main"><ul>{links}</ul></nav>
    <span class="now-chip" title="Time in Cairo, where the team works">{icon("clock", r=r)}<span>Cairo <time data-now>--:--</time></span></span>
    <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-label="Switch colour theme">{icon("sun", "ico sun-i", r)}{icon("moon", "ico moon", r)}</button>
    <a class="btn btn-primary" href="{r}contact.html">Start a project</a>
    <button class="icon-btn menu-btn" type="button" data-menu-open aria-label="Open menu" aria-haspopup="dialog">{icon("menu", r=r)}</button>
  </div>
</header>
<dialog class="menu" data-menu aria-label="Menu">
  <div class="menu-top">
    <img class="logo-light" src="{r}assets/brand/logo.svg" width="155" height="20" alt="Intimedev" style="height:26px;width:auto">
    <img class="logo-dark" src="{r}assets/brand/logo-dark.svg" width="155" height="20" alt="" style="height:26px;width:auto">
    <button class="icon-btn" type="button" data-menu-close aria-label="Close menu">{icon("close", r=r)}</button>
  </div>
  <nav aria-label="Main"><ul>{mlinks}</ul></nav>
  <div class="menu-foot">
    <a class="btn btn-primary" href="{r}contact.html">Start a project</a>
    <button class="btn btn-line" type="button" data-theme-toggle>Switch colour theme</button>
  </div>
</dialog>'''


def footer(r):
    svcs = "".join(f'<li><a href="{r}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in C.SERVICES[:6])
    clocks = "".join(f'<li data-clock="{m["tz"]}"><span>{m["city"]}</span><time>--:--</time></li>' for m in C.MARKETS)
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true"></div>
    <div class="foot-grid">
      <div class="foot-brand">
        <img class="logo-light" src="{r}assets/brand/logo.svg" width="155" height="20" alt="Intimedev">
        <img class="logo-dark" src="{r}assets/brand/logo-dark.svg" width="155" height="20" alt="">
        <p>Software built on time and kept running. An Egyptian engineering team working with Australia, the UK and Egypt.</p>
      </div>
      <div><h2>Services</h2><ul>{svcs}<li><a href="{r}services.html">All services</a></li></ul></div>
      <div><h2>Company</h2><ul><li><a href="{r}work.html">Work</a></li><li><a href="{r}about.html">About</a></li><li><a href="{r}contact.html">Contact</a></li><li><a href="{r}brand.html">Brand guidelines</a></li></ul></div>
      <div><h2>Now</h2><ul class="foot-clocks">{clocks}</ul>
        <ul style="margin-top:20px"><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li><li><a href="tel:{C.PHONE_HREF}">{C.PHONE}</a></li></ul></div>
    </div>
    <div class="foot-base"><span>© <span data-year>2026</span> Intimedev</span><span>Egypt · Australia · United Kingdom</span></div>
  </div>
</footer>'''


def page(path, title, desc, active, body, extra_css="", base=None):
    depth = path.count("/")
    r = base if base is not None else "../" * depth
    doc = (head(title, desc, r, extra_css) + "\n<body>\n" + header(active, r) + f'\n<main id="main">\n{body}\n</main>\n'
           + footer(r) + f'\n<script src="{r}assets/js/time.js?v={V}" defer></script>\n<script src="{r}assets/js/site.js?v={V}" defer></script>\n</body>\n</html>\n')
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return path


def section_head(title, text="", label=""):
    lab = f'<p class="label">{label}</p>' if label else ""
    txt = f'<p class="copy">{text}</p>' if text else ""
    return f'<div class="section-head reveal">{lab}<h2>{title}</h2>{txt}</div>'


def closing(r, title="Tell us what needs to run.", text="Describe your requirements, your existing system or the problem in your way. We reply within one business day."):
    # A setting sundial on the horizon of the band; time.js puts the sun at the current hour in Cairo.
    rays = "".join(f'<line x1="500" y1="500" x2="{500 + 500 * math.cos(math.radians(d)):.1f}" y2="{500 - 500 * math.sin(math.radians(d)):.1f}"/>'
                   for d in range(15, 180, 15))
    art = (f'<svg class="horizon-art" viewBox="0 0 1000 520" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.2">'
           f'<path d="M0 500 A500 500 0 0 1 1000 500"/><path d="M110 500 A390 390 0 0 1 890 500" stroke-dasharray="2 9"/>{rays}'
           f'<line x1="-400" y1="500" x2="1400" y2="500"/></g>'
           f'<circle class="closing-sun" data-sun-arc data-cx="500" data-cy="500" data-r="500" cx="250" cy="67" r="16"/></svg>')
    return f'''<section class="closing" aria-labelledby="closing-title">
  {art}
  <div class="wrap">
    <div class="reveal"><h2 id="closing-title">{title}</h2><p>{text}</p></div>
    <div class="contact-lines reveal" style="--i:1">
      <a href="mailto:{C.EMAIL}">{icon("mail", r=r)}{C.EMAIL}</a>
      <a href="{C.WHATSAPP}" rel="noopener">{icon("chat", r=r)}WhatsApp {C.PHONE}</a>
      <a class="btn btn-primary" href="{r}contact.html">Start a project {icon("arrow", r=r)}</a>
    </div>
  </div>
</section>'''


def cap_groups(r):
    out = []
    for g, (name, text) in C.GROUPS.items():
        items = "".join(
            f'<li class="cap-item"><a href="{r}services/{s["slug"]}.html">{icon(s["icon"], r=r)}'
            f'<span><span class="name">{e(s["name"])}{" <span class=\"core\">Core</span>" if s["core"] else ""}</span>'
            f'<span class="short">{e(s["short"])}</span></span>{icon("arrow", "ico go", r)}</a></li>'
            for s in C.SERVICES if s["group"] == g)
        out.append(f'<div class="cap-group reveal"><header><h3>{name}</h3><p>{text}</p></header><ul class="cap-list">{items}</ul></div>')
    return f'<div class="cap-groups">{"".join(out)}</div>'


def day_path():
    items = "".join(f'<li class="reveal" style="--i:{i}"><h3>{e(n)}</h3><p>{e(d)}</p></li>'
                    for i, (n, d) in enumerate(C.PROCESS))
    return f'<ol class="day" data-day>{items}</ol>'


def stack_table():
    cols = "".join(f'<div class="reveal"><h3>{e(g)}</h3><ul>{"".join(f"<li>{e(t)}</li>" for t in items)}</ul></div>' for g, items in C.STACK)
    return f'<div class="stack">{cols}</div>'


def layers_section():
    rows = [("Interface", "Web portal, mobile app", "What your customers and staff use"),
            ("Application", "Laravel, CakePHP, Flutter", "Business logic, workflows, APIs"),
            ("Data", "MySQL, MariaDB, PostgreSQL", "Databases, reports, nightly backups"),
            ("Server", "Linux, Nginx, Apache, Docker", "Hardened, patched, monitored"),
            ("Connections", "Stripe, PayPal, Xero, AI APIs", "Payments, accounting, storage, email")]
    lis = "".join(f'<li class="layer reveal" style="--i:{i}"><span class="label">{a}</span><span><strong>{b}</strong><br><span>{c}</span></span></li>'
                  for i, (a, b, c) in enumerate(rows))
    return f'''<section class="section band layers-sec" aria-labelledby="layers-title">
  <div class="wrap">
    <div>
      <div class="section-head tight reveal" style="margin-top:0"><h2 id="layers-title">One team from the interface to the server.</h2>
      <p class="copy">Most agencies build the application and hand hosting to someone else. We write the code and run the servers it lives on, so when something breaks there is one team to call, and it already knows both sides.</p></div>
      <div class="claims">
        <div class="reveal"><strong>App + infra</strong><span>One team for the application code and the servers it runs on.</span></div>
        <div class="reveal" style="--i:1"><strong>Legacy welcome</strong><span>We maintain, upgrade and modernise systems others walked away from.</span></div>
      </div>
    </div>
    <div>
      <ol class="layers">{lis}</ol>
      <p class="layer-brace">Built, hosted and supported by Intimedev</p>
    </div>
  </div>
</section>'''


def blueprint_cards(r, lead=True):
    cards = []
    for i, bp in enumerate(C.BLUEPRINTS):
        cls = "is-lead" if i == 0 and lead else "is-wide"
        cards.append(f'''<a class="bp-card {cls} reveal" style="--i:{i}" href="{r}work.html#{bp["slug"]}">
  <div class="bp-figure">{blueprint_svg(bp, i)}</div>
  <div class="bp-text"><div class="meta"><span class="label">Blueprint</span>{icon("arrow", r=r)}</div>
  <h3>{e(bp["name"])}</h3><p>{e(bp["summary"])}</p></div></a>''')
    return f'<div class="blueprints">{"".join(cards)}</div>'


# ---------------------------------------------------------------- pages

def home():
    r = ""
    body = f'''<section class="hero" aria-labelledby="hero-title">
  <div class="wrap">
    <div class="hero-copy">
      <p class="label" style="--i:0">Software development and IT solutions</p>
      <h1 id="hero-title" style="--i:1">Software built on time. Kept running.</h1>
      <p class="lead" style="--i:2">One Egyptian team designs, builds and hosts your web, mobile and business systems, then supports them for years.</p>
      <div class="actions" style="--i:3">
        <a class="btn btn-primary" href="contact.html">Start a project {icon("arrow")}</a>
        <a class="text-link" href="services.html">What we build {icon("arrow")}</a>
      </div>
    </div>
    {dial_block()}
  </div>
  <div class="wrap">
    <ul class="hero-facts" aria-label="Intimedev in brief">
      <li><strong>14+ years</strong><span>building and supporting software</span></li>
      <li><strong>3 markets</strong><span>Egypt, Australia, United Kingdom</span></li>
      <li><strong>App to server</strong><span>code, hosting and support, one team</span></li>
      <li><strong>Years, not weeks</strong><span>most clients stay for years</span></li>
    </ul>
  </div>
</section>

<section class="section" aria-labelledby="cap-title" style="padding-top:0">
  <div class="wrap">
    {section_head('<span id="cap-title">We build it, connect it and keep it running.</span>', "Ten services, delivered by one experienced team for more than 14 years, for businesses in Egypt, Australia and the United Kingdom.")}
    {cap_groups(r)}
  </div>
</section>

{layers_section()}

<section class="section" aria-labelledby="bp-title">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true"></div>
    {section_head('<span id="bp-title">Systems we design, build and operate.</span>', "Representative blueprints of the platforms we deliver. They show the kind of work we do, not named client case studies.")}
    {blueprint_cards(r)}
  </div>
</section>

<section class="section band" aria-labelledby="day-title">
  <div class="wrap">
    {section_head('<span id="day-title">A clear path from idea to long-term support.</span>', "Six stages, from the first conversation to the years of support after launch.")}
    {day_path()}
  </div>
</section>

<section class="section" aria-labelledby="stack-title">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true"></div>
    {section_head('<span id="stack-title">Established tools, chosen to last.</span>', "We recommend maintainable technologies that suit each project, and we stay with them for the life of the system.")}
    {stack_table()}
  </div>
</section>

{closing(r)}'''
    return page("index.html", "Intimedev | Software built on time. Kept running.",
                "Custom web, mobile, ERP, infrastructure and AI solutions from one Egyptian team, for businesses in Egypt, Australia and the UK for more than 14 years.",
                "index.html", body)


def services_page():
    r = ""
    tiles = []
    for g, (name, text) in C.GROUPS.items():
        tiles.append(f'<div class="svc-group-title reveal"><h2>{name}</h2><p>{text}</p></div>')
        group = [x for x in C.SERVICES if x["group"] == g]
        # Fill every row: 3 per row, a short last row splits its width (no empty cells).
        full = len(group) - len(group) % 3 if len(group) % 3 else len(group)
        for i, s in enumerate(group):
            span = 4 if i < full else 12 // (len(group) - full)
            core = ' <span class="core">Core</span>' if s["core"] else ""
            tiles.append(f'<a class="svc-tile reveal" style="--i:{i};--span:{span}" href="services/{s["slug"]}.html">{icon(s["icon"])}'
                         f'<h3>{e(s["name"])}{core}</h3><p>{e(s["summary"])}</p><span class="text-link">Details {icon("arrow")}</span></a>')
    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="index.html">Home</a><span>/</span><span>Services</span></p>
      <h1 style="--i:1">What we build, connect and run.</h1>
      <p class="lead" style="--i:2">From custom applications to server infrastructure: designed, developed and supported by one experienced team.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true" style="margin-bottom:48px"></div>
    <div class="svc-grid">{"".join(tiles)}</div>
  </div>
</section>
{closing(r, "Not sure which service fits?", "Tell us what the system needs to do. We will recommend the right technical approach and an estimate.")}'''
    return page("services.html", "Services | Intimedev",
                "Custom web applications, mobile apps, ERP, e-commerce, e-learning, AI and API integrations, file systems, server administration and long-term support.",
                "services.html", body)


def service_page(i, s):
    r = "../"
    inds = "".join(f'<li><strong>{e(C.INDUSTRIES[k][0])}</strong><span>{e(C.INDUSTRIES[k][1])}</span></li>' for k in s["industries"])
    prev_s = C.SERVICES[i - 1]
    next_s = C.SERVICES[(i + 1) % len(C.SERVICES)]
    group = C.GROUPS[s["group"]][0]
    after = ""
    if s["slug"] != "maintenance-support":
        m = SVC["maintenance-support"]
        after = f'''<div class="after-launch reveal">{icon("support", r=r)}<div><h3>After launch, we stay.</h3><p class="copy">Every system we build can stay with us for upgrades, monitoring, backups and support, on the same servers we configured.</p></div>
      <a class="text-link" href="{m["slug"]}.html">{e(m["name"])} {icon("arrow", r=r)}</a></div>'''
    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="../index.html">Home</a><span>/</span><a href="../services.html">Services</a><span>/</span><span>{group}</span></p>
      <h1 style="--i:1">{e(s["name"])}.</h1>
      <p class="lead" style="--i:2">{e(s["summary"])}</p>
      <div class="actions" style="--i:3;margin-top:32px"><a class="btn btn-primary" href="../contact.html?service={s["slug"]}">Discuss this project {icon("arrow", r=r)}</a></div>
    </div>
    <svg class="head-mark" viewBox="0 0 24 24" aria-hidden="true"><use href="../assets/icons/icons.svg#{s["icon"]}"/></svg>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true" style="margin-bottom:56px"></div>
    <div class="svc-body">
      <div>
        <h2 class="reveal" style="font-size:clamp(1.5rem,2.4vw,2rem);margin-bottom:16px">What it includes</h2>
        <ol class="includes">{"".join(f'<li class="reveal" style="--i:{k}">{e(x)}</li>' for k, x in enumerate(s["includes"]))}</ol>
      </div>
      <div>
        <div class="aside-block reveal"><h2 class="label">Technologies we use</h2><ul class="chips">{"".join(f"<li>{e(t)}</li>" for t in s["stack"])}</ul></div>
        <div class="aside-block reveal"><h2 class="label">Where it is used</h2><ul class="ind-links">{inds}</ul></div>
      </div>
    </div>
  </div>
</section>
<section class="section band" aria-labelledby="how-title">
  <div class="wrap">
    {section_head('<span id="how-title">How the project runs.</span>')}
    {day_path()}
    <div style="margin-top:56px">{after}</div>
  </div>
</section>
<section class="section" style="padding-block:48px">
  <div class="wrap pager">
    <a href="{prev_s["slug"]}.html"><span class="label">Previous</span><strong>{e(prev_s["name"])}</strong></a>
    <a href="{next_s["slug"]}.html"><span class="label">Next</span><strong>{e(next_s["name"])}</strong></a>
  </div>
</section>
{closing(r, "Let's plan your project.", "Tell us what the system needs to do and what exists today. We reply within one business day.")}'''
    return page(f'services/{s["slug"]}.html', f'{s["name"]} | Intimedev', s["summary"], "services.html", body)


def work_page():
    r = ""
    feats = []
    for i, bp in enumerate(C.BLUEPRINTS):
        svcs = ", ".join(f'<a href="services/{k}.html">{e(SVC[k]["name"])}</a>' for k in bp["services"])
        inds = ", ".join(e(C.INDUSTRIES[k][0]) for k in bp["industries"])
        feats.append(f'''<article class="bp-feature" id="{bp["slug"]}">
  <div class="bp-figure reveal">{blueprint_svg(bp, 10 + i)}</div>
  <div class="reveal" style="--i:1">
    <p class="label">Blueprint</p>
    <h2 style="margin-top:12px">{e(bp["name"])}</h2>
    <p class="copy">{e(bp["summary"])}</p>
    <dl>
      <div><dt>Parts</dt><dd>{e(", ".join(bp["parts"]))}</dd></div>
      <div><dt>Services involved</dt><dd>{svcs}</dd></div>
      <div><dt>Typical industries</dt><dd>{inds}</dd></div>
    </dl>
  </div>
</article>''')
    inds = "".join(f'<div class="reveal" style="--i:{i % 4}"><h3>{e(n)}</h3><p>{e(d)}</p></div>' for i, (n, d) in enumerate(C.INDUSTRIES.values()))
    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="index.html">Home</a><span>/</span><span>Work</span></p>
      <h1 style="--i:1">Systems we design, build and operate.</h1>
      <p class="lead" style="--i:2">Three blueprints of the platforms we deliver, and the industries they serve. Ask us about projects similar to yours.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    {"".join(feats)}
    <p class="disclaimer">These are representative blueprints drawn for this site. They describe the kinds of systems we build; they are not screenshots of client projects or named case studies.</p>
  </div>
</section>
<section class="section band" aria-labelledby="ind-title">
  <div class="wrap">
    {section_head('<span id="ind-title">Built around how your business works.</span>')}
    <div class="ind-grid">{inds}</div>
  </div>
</section>
{closing(r, "Have a system that needs a new owner?", "We take over, upgrade and modernise existing systems as well as building new ones. Tell us what you run today.")}'''
    return page("work.html", "Work | Intimedev",
                "Representative systems Intimedev designs, builds and operates: business management platforms, mobile and web ecosystems and secure file exchange.",
                "work.html", body)


def origin_svg():
    lines = "".join(
        f'<line x1="150" y1="20" x2="{150 + 128 * math.cos(math.radians(a)):.1f}" y2="{20 + 128 * math.sin(math.radians(a)):.1f}" stroke="currentColor" stroke-width="1.5"/>'
        for a in [i * 15 for i in range(13)])
    return f'''<svg viewBox="0 0 300 170" role="img" aria-label="Drawing of a semicircle divided into twelve sections, with a peg at the top">
  <path d="M22 20 A128 128 0 0 0 278 20 Z" fill="var(--surface)" stroke="currentColor" stroke-width="2"/>
  {lines}
  <line x1="150" y1="20" x2="{150 + 120 * math.cos(math.radians(55)):.1f}" y2="{20 + 120 * math.sin(math.radians(55)):.1f}" stroke="var(--blue)" stroke-width="6" stroke-linecap="round"/>
  <circle cx="150" cy="20" r="7" fill="currentColor"/>
  <circle cx="60" cy="9" r="6" fill="var(--sun)"/>
</svg>'''


def about_page():
    r = ""
    facts = [("14+ years", "of practical software development"), ("3 markets", "Egypt, Australia and the United Kingdom"),
             ("App to server", "applications, servers, databases and integrations"), ("Years, not weeks", "most client relationships span years")]
    facts_html = "".join(f'<div class="reveal" style="--i:{i}"><strong>{a}</strong><span>{b}</span></div>' for i, (a, b) in enumerate(facts))
    principles = "".join(f'<div class="reveal" style="--i:{i % 3}"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(C.PRINCIPLES))
    markets = "".join(
        f'<div class="market reveal" style="--i:{i}" data-market="{m["tz"]}" data-weekend="{m["weekend"]}"><span class="state">&nbsp;</span>'
        f'<span class="time">--:--</span><h3>{m["country"]} <span class="label">{m["city"]}</span></h3><p>{e(m["note"])}</p></div>'
        for i, m in enumerate(C.MARKETS))
    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="index.html">Home</a><span>/</span><span>About</span></p>
      <h1 style="--i:1">An Egyptian engineering team that keeps time.</h1>
      <p class="lead" style="--i:2">For more than 14 years we have built, hosted and supported software for businesses in Egypt, Australia and the United Kingdom. We plan before we code and we stay after launch.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap"><div class="facts">{facts_html}</div></div>
</section>
<section class="section band" aria-labelledby="pr-title">
  <div class="wrap">
    {section_head('<span id="pr-title">How we work.</span>', "Six commitments that shape every project, taken from how we have worked with clients for over a decade.")}
    <div class="principles">{principles}</div>
  </div>
</section>
<section class="section" aria-labelledby="day2-title">
  <div class="wrap">
    <div class="hour-rule" aria-hidden="true"></div>
    {section_head('<span id="day2-title">From idea to long-term support.</span>')}
    {day_path()}
  </div>
</section>
<section class="section band" aria-labelledby="mk-title">
  <div class="wrap">
    {section_head('<span id="mk-title">Three markets. One dependable team.</span>', "Working across time zones taught us to communicate clearly, adapt to different business requirements and plan handovers around your day.")}
    <div class="markets">{markets}</div>
  </div>
</section>
<section class="section" aria-labelledby="or-title">
  <div class="wrap origin">
    <div class="reveal">{origin_svg()}</div>
    <div class="reveal" style="--i:1">
      <p class="label">Why a sundial</p>
      <h2 id="or-title" style="margin-top:12px">Our mark is a lowercase i casting its shadow.</h2>
      <p class="copy" style="margin-top:20px">One of the oldest known sundials was found in Egypt's Valley of the Kings: a limestone piece from the 13th century BC with a semicircle divided into twelve sections and a peg that cast the shadow. Our identity borrows that geometry. The i in our name is the peg, the dot is the sun, and its shadow and stem together read as the hands of a clock.</p>
      <p class="copy">It is a reminder of what we promise: software delivered on time, and kept running long after.</p>
      <p style="margin-top:24px"><a class="text-link" href="brand.html">Brand guidelines {icon("arrow")}</a></p>
    </div>
  </div>
</section>
<section class="section band" aria-labelledby="st2-title">
  <div class="wrap">
    {section_head('<span id="st2-title">Proven tools, organised by purpose.</span>')}
    {stack_table()}
  </div>
</section>
{closing(r)}'''
    return page("about.html", "About | Intimedev",
                "Intimedev is an Egyptian software team with more than 14 years of building, hosting and supporting software for businesses in Egypt, Australia and the UK.",
                "about.html", body)


def contact_page():
    r = ""
    opts = "".join(f'<option value="{s["slug"]}">{e(s["name"])}</option>' for s in C.SERVICES)
    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="index.html">Home</a><span>/</span><span>Contact</span></p>
      <h1 style="--i:1">Have a software project in mind?</h1>
      <p class="lead" style="--i:2">Tell us about your requirements, your existing system or your business challenge. We will help you define the right technical solution.</p>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap contact-wrap">
    <div class="contact-direct reveal">
      <ul class="direct-list">
        <li><a href="mailto:{C.EMAIL}">{icon("mail")}<span><strong>{C.EMAIL}</strong><span>Email us directly</span></span></a></li>
        <li><a href="tel:{C.PHONE_HREF}">{icon("phone")}<span><strong>{C.PHONE}</strong><span>Phone</span></span></a></li>
        <li><a href="{C.WHATSAPP}" rel="noopener">{icon("chat")}<span><strong>WhatsApp</strong><span>{C.PHONE}</span></span></a></li>
        <li><div>{icon("clock")}<span><strong>We reply within one business day</strong><span>Cairo <time data-now>--:--</time> right now</span></span></div></li>
      </ul>
      <p class="copy" style="font-size:var(--fs-small)">Serving Egypt, Australia and the United Kingdom.</p>
    </div>
    <form class="form reveal" style="--i:1" data-estimate novalidate aria-labelledby="form-title">
      <h2 id="form-title" class="full" style="grid-column:1/-1;font-size:clamp(1.4rem,2.2vw,1.8rem)">Request a project estimate</h2>
      <div class="field"><label for="f-name">Name <span class="req" aria-hidden="true">*</span></label><input id="f-name" name="name" autocomplete="name" required aria-describedby="e-name"><span class="error" id="e-name">Please tell us your name.</span></div>
      <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization"></div>
      <div class="field"><label for="f-email">Email <span class="req" aria-hidden="true">*</span></label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="e-email"><span class="error" id="e-email">Please enter a valid email address.</span></div>
      <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="field full"><label for="f-service">Service required</label><select id="f-service" name="service"><option value="">Select a service</option>{opts}<option value="other">Something else</option></select></div>
      <div class="field full"><label for="f-desc">Project description <span class="req" aria-hidden="true">*</span></label><textarea id="f-desc" name="description" required aria-describedby="h-desc e-desc"></textarea><span class="hint" id="h-desc">What should the system do? Is there an existing system?</span><span class="error" id="e-desc">A few lines about the project help us reply properly.</span></div>
      <div class="form-foot">
        <small>Sending opens your email app with this message addressed to {C.EMAIL}. Nothing is stored on this website.</small>
        <button class="btn btn-primary" type="submit">Prepare my email {icon("arrow")}</button>
      </div>
      <div class="form-done" data-done hidden tabindex="-1">
        <h3>Your email is ready.</h3>
        <p class="copy">Your email app should have opened with the message below. If it did not, copy it and send it to <a href="mailto:{C.EMAIL}">{C.EMAIL}</a>, or send it on WhatsApp.</p>
        <pre data-preview></pre>
        <div class="row">
          <button class="btn btn-line" type="button" data-copy>{icon("copy")}<span>Copy message</span></button>
          <a class="btn btn-line" data-wa href="{C.WHATSAPP}" rel="noopener">{icon("chat")}Send on WhatsApp</a>
          <button class="btn btn-line" type="button" data-edit>Edit</button>
        </div>
      </div>
    </form>
  </div>
</section>'''
    return page("contact.html", "Contact | Intimedev",
                "Request a project estimate from Intimedev by email, phone or WhatsApp. We reply within one business day.",
                "contact.html", body)


def not_found():
    body = f'''<section class="lost">
  <div class="wrap">
    <svg viewBox="0 0 300 170" aria-hidden="true" style="color:var(--text)">
      <path d="M22 20 A128 128 0 0 0 278 20 Z" fill="var(--surface)" stroke="currentColor" stroke-width="2"/>
      {"".join(f'<line x1="150" y1="20" x2="{150 + 128 * math.cos(math.radians(a)):.1f}" y2="{20 + 128 * math.sin(math.radians(a)):.1f}" stroke="var(--line-strong)" stroke-width="1.5"/>' for a in range(0, 181, 15))}
      <circle cx="150" cy="20" r="7" fill="currentColor"/>
    </svg>
    <div class="hero-copy">
      <p class="label" style="--i:0">404</p>
      <h1 style="--i:1;margin-top:12px">No shadow here.</h1>
      <p class="lead" style="--i:2;margin-top:20px">This page does not exist, or it has moved. The links below will get you back on time.</p>
      <div class="actions" style="--i:3;margin-top:32px;display:flex;flex-wrap:wrap;gap:20px;align-items:center"><a class="btn btn-primary" href="{BASE404}index.html">Back to home {icon("arrow", r=BASE404)}</a><a class="text-link" href="{BASE404}contact.html">Contact us {icon("arrow", r=BASE404)}</a></div>
    </div>
  </div>
</section>'''
    return page("404.html", "Page not found | Intimedev", "This page does not exist.", "", body, base=BASE404)


def brand_page():
    r = ""
    nav = [("strategy", "Strategy"), ("logo", "Logo"), ("colour", "Colour"), ("type", "Type"), ("grid", "Grid"),
           ("elements", "Elements"), ("icons", "Icons"), ("imagery", "Imagery"), ("motion", "Motion"), ("access", "Accessibility")]
    gnav = "".join(f'<li><a href="#{k}">{v}</a></li>' for k, v in nav)

    def g_head(key, num, title, text):
        return f'<div class="g-head reveal"><p class="label">{num} {dict(nav)[key]}</p><div><h2>{title}</h2><p class="copy">{text}</p></div></div>'

    # Logo construction drawing on the 64 grid
    grid = "".join(f'<line class="gridl" x1="{i}" y1="0" x2="{i}" y2="64"/><line class="gridl" x1="0" y1="{i}" x2="64" y2="{i}"/>' for i in range(0, 65, 4))
    construct = f'''<svg class="construct" viewBox="-6 -6 76 76" role="img" aria-label="The mark drawn on a 64 unit grid">
  {grid}
  <path d="M20 46L55 51.5A3 3 0 0 1 55 57.5L20 58Z" fill="#1034a6"/>
  <rect x="14" y="21" width="12" height="37" rx="6" fill="#0e1726"/>
  <circle cx="10" cy="10" r="7" fill="#ff5a1f"/>
  <path class="guide" d="M10 10 L26 58"/>
  <circle class="guide" cx="10" cy="10" r="7"/>
  <text x="-5" y="66">64 grid · stem 12 · sun 14</text>
</svg>'''
    sw = [("Ink", "#0e1726", "#fff", "The shadow side. Text, the stem of the mark, dark surfaces.", "17.6:1 on white"),
          ("Egyptian blue", "#1034a6", "#fff", "Primary brand colour. The cast shadow, primary buttons, links, the closing band.", "10.2:1 with white"),
          ("Solar", "#ff5a1f", "#0e1726", "The sun. Only for 'now': the sun in the mark, the dial, the hour-rule marker.", "Graphics only on light (3.1:1)"),
          ("Blue wash", "#e8ecfb", "#1034a6", "Blueprint grounds and soft cast shadows on panels.", "Blue text 8.6:1")]
    swatches = "".join(f'<div class="sw reveal"><div class="chip" style="background:{h};color:{fg}">{n}</div><dl><dt>Hex</dt><dd>{h.upper()}</dd><dt>Role</dt><dd>{role}</dd><dt>Contrast</dt><dd>{c}</dd></dl></div>' for n, h, fg, role, c in sw)
    neutrals = [("#ffffff", "bg"), ("#f2f4f7", "surface"), ("#e7eaf0", "surface-2"), ("#dde2e9", "line"), ("#808a9c", "line-input"), ("#5d6778", "text-3"), ("#475163", "text-2"), ("#0a101c", "night bg")]
    nrow = "".join(f'<div><b style="background:{h}"></b>{n}<br>{h}</div>' for h, n in neutrals)
    type_rows = [("Hero", "Funnel Display 700", "clamp(2.6rem, 6vw, 5.6rem) / 0.98, -0.035em", "Software built on time."),
                 ("Page title", "Funnel Display 700", "clamp(2.3rem, 4.8vw, 4.4rem) / 1.02", "Services"),
                 ("Section heading", "Funnel Display 700", "clamp(1.85rem, 3.3vw, 2.95rem) / 1.02", "One team, app to server"),
                 ("Card heading", "Funnel Display 700", "1.2 to 1.4rem / 1.2", "ERP and business systems"),
                 ("Lead", "Funnel Sans 400", "1.1 to 1.3rem / 1.5", "One team designs, builds and hosts"),
                 ("Body", "Funnel Sans 400", "1.0625rem / 1.6", "Secure, maintainable development"),
                 ("Button, navigation", "Funnel Sans 600 / 500", "1rem / 1", "Start a project"),
                 ("Label, metadata", "Geist Mono 500, uppercase", "0.75rem, +0.08em", "CAIRO 14:32"),
                 ("Case meta, stack", "Geist Mono 500", "0.88rem", "Laravel · PostgreSQL")]
    trows = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="mono">{c}</td><td>{d}</td></tr>' for a, b, c, d in type_rows)
    icons_html = "".join(f'<figure class="reveal"><svg aria-hidden="true"><use href="assets/icons/icons.svg#{s["icon"]}"/></svg><figcaption>{e(s["name"])}</figcaption></figure>' for s in C.SERVICES)
    contrast = [("Ink on white", "17.6:1", "Body and headings"), ("Text-2 #475163 on white", "8.0:1", "Secondary text"),
                ("Text-3 #5d6778 on surface", "5.2:1", "Labels and metadata"), ("White on Egyptian blue", "10.2:1", "Buttons, closing band"),
                ("Solar text #c2410c on white", "5.2:1", "Required-field marks"), ("Accent #7d95ff on night", "6.9:1", "Links and buttons in dark theme"),
                ("Form borders #808a9c on white", "3.5:1", "Meets 3:1 for controls")]
    crows = "".join(f'<tr><td>{a}</td><td class="pass">{b}</td><td>{c}</td></tr>' for a, b, c in contrast)
    spaces = [("--s-1", 4), ("--s-2", 8), ("--s-3", 12), ("--s-4", 16), ("--s-5", 24), ("--s-6", 32), ("--s-7", 48), ("--s-8", 64), ("--s-9", 96)]
    srows = "".join(f'<div><span>{n}</span><span>{v}px</span><b style="width:{v * 2}px"></b></div>' for n, v in spaces)

    body = f'''<section class="page-head">
  <div class="wrap">
    <div class="hero-copy">
      <p class="crumbs" style="--i:0"><a href="index.html">Home</a><span>/</span><span>Brand guidelines</span></p>
      <h1 style="--i:1">The Gnomon identity.</h1>
      <p class="lead" style="--i:2">How Intimedev looks, sounds and moves. A lowercase i casting its shadow: built on time, kept running.</p>
      <div class="downloads" style="--i:3">
        <a class="btn btn-line" href="assets/brand/logo.svg" download>Logo SVG</a>
        <a class="btn btn-line" href="assets/brand/logo-dark.svg" download>Logo for dark SVG</a>
        <a class="btn btn-line" href="assets/brand/mark.svg" download>Mark SVG</a>
        <a class="btn btn-line" href="assets/brand/app-icon.svg" download>App icon SVG</a>
      </div>
    </div>
    <img class="head-mark" src="assets/brand/mark.svg" width="64" height="64" alt="">
  </div>
</section>
<nav class="g-nav" aria-label="Guideline sections"><div class="wrap"><ul>{gnav}</ul></div></nav>

<section class="g-sec" id="strategy"><div class="wrap">
  {g_head("strategy", "01", "Built on time. Kept running.", "The Egyptian engineering team that builds your software on time and keeps it running for years: application, servers and support from one team.")}
  <div class="g-cols">
    <div class="tile g-span-4 reveal"><p class="label">Personality</p><p>Precise, steady, candid, quietly confident, hands-on. Never hyped, never cute.</p></div>
    <div class="tile g-span-4 reveal"><p class="label">Audience</p><p>Owners and operations leads in Australia, the UK and Egypt who run on custom systems and need one dependable team.</p></div>
    <div class="tile g-span-4 reveal"><p class="label">Differentiation</p><p>App and infrastructure from one team; legacy rescue; real time-zone overlap; an identity rooted in Egyptian timekeeping.</p></div>
    <div class="tile g-span-6 reveal"><p class="label">Write like this</p><p>"We write the code and run the servers it lives on." Short sentences. Specific nouns. Numbers only when verified.</p></div>
    <div class="tile g-span-6 reveal"><p class="label">Not like this</p><p>"Innovative, cutting-edge solutions that seamlessly empower your digital transformation."</p></div>
  </div>
  <p class="copy" style="margin-top:32px">Full research and the three directions considered: <span class="mono">docs/01-brand-discovery.md</span> and <span class="mono">docs/02-creative-direction.md</span>.</p>
</div></section>

<section class="g-sec" id="logo"><div class="wrap">
  {g_head("logo", "02", "A lowercase i casting its shadow.", "The stem is the gnomon, the dot is the sun, and the shadow falls to the right. Stem and shadow also read as the hands of a clock. The wordmark sets intime in bold and dev in regular, so the name never reads as one word.")}
  <div class="g-cols">
    <div class="tile is-light g-span-8 reveal"><div class="stage"><img src="assets/brand/logo.svg" width="155" height="20" alt="Intimedev logo"></div><p class="cap">Primary lockup. Clear space on every side equals the sun's diameter. Minimum width 96px on screen, 25mm in print.</p></div>
    <div class="tile is-light g-span-4 reveal"><div class="stage">{construct}</div><p class="cap">Construction on a 64-unit grid. The shadow tapers and dips so it reads as light, not as a letter L.</p></div>
    <div class="tile is-dark g-span-4 reveal"><div class="stage"><img src="assets/brand/logo-dark.svg" width="155" height="20" alt="Intimedev logo for dark backgrounds"></div><p class="cap">On dark: ink becomes near-white, the shadow a lighter blue. The sun never changes.</p></div>
    <div class="tile is-light g-span-4 reveal"><div class="stage"><img class="mark-lg" src="assets/brand/mark.svg" width="64" height="64" alt="Intimedev mark"></div><p class="cap">The mark alone: avatars, stamps, the corner of a slide. Minimum 20px.</p></div>
    <div class="tile is-blue g-span-4 reveal"><div class="stage"><img class="mark-lg" src="assets/brand/app-icon.svg" width="64" height="64" alt="Intimedev app icon" style="height:110px"></div><p class="cap">App icon and favicon on Egyptian blue. Works down to 16px.</p></div>
  </div>
  <h3 class="reveal" style="margin:56px 0 20px">Correct and incorrect use</h3>
  <div class="dont">
    <figure class="reveal"><div class="stage is-ok"><img src="assets/brand/logo.svg" width="155" height="20" alt=""></div><figcaption>Use the supplied files, on white, surface grey or night.</figcaption></figure>
    <figure class="reveal"><div class="stage"><img src="assets/brand/logo.svg" width="155" height="20" alt="" style="transform:scaleX(1.4)"></div><figcaption>Do not stretch or condense.</figcaption></figure>
    <figure class="reveal"><div class="stage"><img src="assets/brand/logo.svg" width="155" height="20" alt="" style="filter:hue-rotate(140deg)"></div><figcaption>Do not recolour. The sun is always solar orange.</figcaption></figure>
    <figure class="reveal"><div class="stage"><img src="assets/brand/logo.svg" width="155" height="20" alt="" style="transform:scaleX(-1)"></div><figcaption>Do not mirror: the light always comes from the upper left.</figcaption></figure>
    <figure class="reveal"><div class="stage" style="background:linear-gradient(135deg,#7c3aed,#ec4899)"><img src="assets/brand/logo.svg" width="155" height="20" alt=""></div><figcaption>Do not place on gradients or busy photos.</figcaption></figure>
    <figure class="reveal"><div class="stage"><img src="assets/brand/logo.svg" width="155" height="20" alt="" style="filter:drop-shadow(0 6px 10px rgba(0,0,0,.45))"></div><figcaption>Do not add effects. The mark already has its shadow.</figcaption></figure>
  </div>
</div></section>

<section class="g-sec" id="colour"><div class="wrap">
  {g_head("colour", "03", "Ink, Egyptian blue and one sun.", "Egyptian blue was the first synthetic pigment, made in Egypt. Ink is the shadow side. Solar orange is the sun, and the sun appears once per view at most.")}
  <div class="swatches">{swatches}</div>
  <div class="neutral-row reveal">{nrow}</div>
  <p class="copy" style="margin-top:24px">Tokens live in <span class="mono">assets/css/tokens.css</span>. Dark theme swaps surfaces to night blues and lifts the accent to #7D95FF; it follows the visitor's system setting and can be switched in the header.</p>
</div></section>

<section class="g-sec" id="type"><div class="wrap">
  {g_head("type", "04", "Funnel for words, Geist Mono for time.", "Funnel Display sets headlines: wide, firm, slightly technical. Funnel Sans sets everything people read at length. Geist Mono is the clock: times, labels and technologies. The site is English only; an Arabic version would need its own Arabic typeface chosen by comparison on real copy.")}
  <div class="table-scroll reveal"><table class="g-table"><thead><tr><th>Role</th><th>Face</th><th>Size / leading</th><th>Example</th></tr></thead><tbody>{trows}</tbody></table></div>
</div></section>

<section class="g-sec" id="grid"><div class="wrap">
  {g_head("grid", "05", "Twelve columns, one per daylight hour.", "The layout grid has twelve columns, the same as the twelve sections of the sundial. The hour rule at the top of a section draws those columns and marks the current hour in Cairo.")}
  <div class="grid-demo reveal" aria-hidden="true">{"".join(f"<span>{h:02d}</span>" for h in range(6, 18))}</div>
  <div class="hour-rule reveal" aria-hidden="true" style="margin-top:24px"></div>
  <div class="g-cols" style="margin-top:48px">
    <div class="g-span-6 reveal"><h3 style="margin-bottom:16px">Spacing scale</h3><div class="space-scale">{srows}</div></div>
    <div class="g-span-6 reveal"><h3 style="margin-bottom:16px">Shape</h3><p class="copy">Pills for things you press (from the stem of the mark), 14px for panels, 8px for inputs. Shadows are hard, offset and directional: never blurred.</p></div>
  </div>
</div></section>

<section class="g-sec" id="elements"><div class="wrap">
  {g_head("elements", "06", "Five devices, one sundial.", "Each device comes from the same object, so they never compete. Use two or three per page, not all five.")}
  <div class="g-cols">
    <div class="tile g-span-6 reveal"><p class="label">The dial</p><p>Sky arc, horizon, twelve-section plate. Used for the hero and for any comparison of time.</p></div>
    <div class="tile g-span-6 reveal"><p class="label">The hour rule</p><p>A section ruler with twelve ticks and the sun at the current hour in Cairo.</p></div>
    <div class="tile g-span-4 reveal"><p class="label">The cast shadow</p><p>Hard offset shadows on buttons and panels. Their direction follows the sun in Cairo through the day and disappears at night.</p></div>
    <div class="tile g-span-4 reveal"><p class="label">The blueprint</p><p>Systems drawn as nodes on a blue grid, each node casting a blue shadow, one orange grain of data moving.</p></div>
    <div class="tile g-span-4 reveal"><p class="label">The day path</p><p>Processes laid out as a line through the day, each step a point that fills in as you reach it.</p></div>
  </div>
</div></section>

<section class="g-sec" id="icons"><div class="wrap">
  {g_head("icons", "07", "Every icon casts a shadow.", "Drawn on a 24 grid with a 1.75 stroke and round ends. The object is in ink; its shadow on the lower right is in Egyptian blue, like the mark.")}
  <div class="icon-grid">{icons_html}</div>
</div></section>

<section class="g-sec" id="imagery"><div class="wrap">
  {g_head("imagery", "08", "Hard light, real places.", "Photography should show the real team, desks and city in strong directional daylight with clear shadows. No stock laptops, no glowing code, no handshakes. Until real photos exist, the site uses blueprints only and never presents them as client work.")}
  <div class="photo-rules">
    <figure class="reveal" style="margin:0"><div class="light-study" aria-hidden="true"><span class="sunp"></span><span class="obj"></span><span class="cast"></span></div><figcaption class="copy" style="margin-top:12px">Light from one side, low in the sky. Shadows long and crisp.</figcaption></figure>
    <div class="tile reveal"><p class="label">Shoot list (to commission)</p><p>The team at work in Cairo; hands on keyboards and server racks; whiteboard planning sessions; the office in morning light.</p></div>
    <div class="tile reveal"><p class="label">Screens</p><p>Real project screens only with client permission, set flat on the blue grid with a hard shadow, never in fake device mockups.</p></div>
  </div>
</div></section>

<section class="g-sec" id="motion"><div class="wrap">
  {g_head("motion", "09", "Rise, sweep, cast.", "Motion follows the sun: things rise and settle, dial hands sweep to a new state, shadows lengthen. Nothing floats, bounces or loops for decoration. All of it stops for visitors who ask for reduced motion.")}
  <div class="motion-demos">
    <div class="tile reveal"><div class="stage m-rise" aria-hidden="true"><div style="width:100%"><span></span><span></span><span></span></div></div><p class="label">Rise</p><p class="cap">Content enters from 24px below. 720ms, cubic-bezier(.3,0,.2,1), 60ms stagger.</p></div>
    <div class="tile reveal"><div class="stage m-sweep" aria-hidden="true"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50" fill="none" stroke="var(--line-strong)"/><path class="hand" d="M60 60 L60 16" stroke="var(--accent)" stroke-width="6" stroke-linecap="round"/><circle cx="60" cy="60" r="6" fill="var(--text)"/></svg></div><p class="label">Sweep</p><p class="cap">State changes rotate like a dial hand. cubic-bezier(.65,0,.35,1).</p></div>
    <div class="tile reveal"><div class="stage m-cast" aria-hidden="true"><span class="btn-demo">Start a project</span></div><p class="label">Cast</p><p class="cap">Hover lengthens the shadow; press shortens it. The direction follows Cairo time.</p></div>
  </div>
</div></section>

<section class="g-sec" id="access"><div class="wrap">
  {g_head("access", "10", "Readable first, clever second.", "Targets WCAG 2.2 AA. Every live element has a correct static state, a keyboard path and a text alternative.")}
  <div class="table-scroll reveal"><table class="g-table"><thead><tr><th>Pair</th><th>Contrast</th><th>Use</th></tr></thead><tbody>{crows}</tbody></table></div>
  <ul class="copy" style="margin-top:28px;display:grid;gap:8px;padding-inline-start:18px">
    <li>Solar orange is never used for text on light backgrounds; use #C2410C if orange text is unavoidable.</li>
    <li>The dial's sun is a keyboard slider (arrows, Page Up/Down, Home, End, Escape for now) with the three city times as its spoken value.</li>
    <li>Reduced motion removes the sunrise, reveals, pulses and page transitions; the dial still shows live time.</li>
    <li>Focus rings are 2px Egyptian blue (lighter blue on dark) with a 3px offset.</li>
  </ul>
</div></section>'''
    return page("brand.html", "Brand guidelines | Intimedev",
                "The Intimedev identity: logo, colour, typography, grid, graphic elements, icons, imagery, motion and accessibility.",
                "", body, extra_css="brand.css")


def build():
    out = [home(), services_page(), work_page(), about_page(), contact_page(), not_found(), brand_page()]
    out += [service_page(i, s) for i, s in enumerate(C.SERVICES)]
    print(f"built {len(out)} pages")


if __name__ == "__main__":
    build()
