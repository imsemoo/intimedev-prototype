# Intimedev: brand identity and website

A static site for Intimedev built on the "Gnomon" identity: a lowercase i casting its shadow.

## Read first

- `docs/01-brand-discovery.md`: research, verified facts, gaps, strategy
- `docs/02-creative-direction.md`: three directions compared, and why Gnomon won
- `docs/03-qa-report.md`: testing, Lighthouse, limitations
- `brand.html`: the brand guidelines, live

## Structure

```
tools/content.py   all copy and facts (edit here, not in HTML)
tools/build.py     generates every .html page from content.py
tools/brand.py     generates the logo SVGs in assets/brand/
assets/css/tokens.css   colour, type, space and motion tokens (light and dark)
assets/css/site.css     components and pages
assets/css/brand.css    brand guidelines page only
assets/js/time.js       Cairo time: dial, cast shadows, hour rules, clocks
assets/js/site.js       header, theme, menu dialog, reveals, contact form
assets/icons/icons.svg  icon sprite (service icons cast a blue shadow)
```

## Build

```bash
python -I tools/build.py
```

After changing CSS or JS, bump `V` in `tools/build.py` and rebuild so browsers fetch the new files. Regenerate logos with `python -I tools/brand.py` (needs fontTools and brotli).

## Preview

```bash
python -m http.server 8193
```

Then open http://localhost:8193/.
