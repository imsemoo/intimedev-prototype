# Intimedev: QA report

Tested 25 October 2026 on the local build (`python -m http.server 8193`), Chrome 14x via Playwright and Lighthouse 12.8.2.

## Pages delivered (17)

Home, Services, 10 service pages, Work, About, Contact, Brand guidelines, 404.

## Responsive

- All 17 pages probed at 320, 375, 768, 1024, 1280 and 1920 px wide: **no horizontal overflow, no clipped text, no broken images, one h1 per page, no skipped heading levels, no console errors, no failed requests.**
- Fixed during QA: lead blueprint forced a 553 px layout on phones (aspect-ratio plus min-height); the brand page's grid demo overflowed at 320 px; breadcrumb links were under 24 px tall.
- Screens reviewed by eye at 375 and 1280 (light and dark).

## Functional (automated, 20 checks pass)

| Area | Result |
|---|---|
| Dial keyboard: Home, Page Up, Escape back to live | Pass; the spoken value lists the three city times |
| Dial drag with a pointer | Pass |
| Theme toggle, persists after reload | Pass |
| Cast-shadow offsets set from Cairo time | Pass |
| Internal links (21 unique) | All return 200 |
| Contact: `?service=` preselects the service | Pass |
| Contact: empty submit shows 3 inline errors and focuses the first | Pass |
| Contact: invalid email caught | Pass |
| Contact: valid submit composes the email, shows the preview, prefills WhatsApp | Pass |
| Mobile menu: native modal dialog, Escape closes, focus returns | Pass |

**The form does not post to a server.** On submit it opens the visitor's email app with the message addressed to info@intimedev.com and offers copy and WhatsApp. The page says this next to the button. A real endpoint is still needed.

## Lighthouse (local, simulated throttling)

| Page | Mobile perf | Desktop perf | Accessibility | Best practices | Mobile LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|
| Home | 98 | 100 | 100 | 100 | 2.1 s | 0 | 80 ms |
| Contact | 99 | 100 | 100 | 100 | 1.9 s | 0 | 0 ms |
| ERP service | 98 | 100 | 100 | 100 | 1.9 s | 0 | 50 ms |
| Work | 99 | 100 | 100 | 100 | 2.1 s | 0 | 0 ms |

SEO scores 63 only because every page carries `noindex` while this is a prototype. Remove the meta tag at launch. These are lab numbers from a local server, not field data.

Weight: no images, three self-hosted fonts (about 58 KB total), two small scripts, no third-party requests.

## Accessibility

- Contrast checked for every text and control pair (table in brand.html#access).
- Reduced motion turns off the sunrise, reveals, pulses and page transitions. The dial still shows live time.
- The dial is a labelled group with a description; its sun is a keyboard slider.
- NOT VERIFIED: screen reader pass with NVDA or VoiceOver (not available in this environment); Safari and Firefox (only Chrome tested); iOS Safari zoom behaviour.

## Known limitations and remaining work

1. No real portfolio, testimonials, team photos or founding year: the site uses verified facts and clearly labelled blueprints only (see docs/01, section 7).
2. Contact form needs a backend or form service.
3. Privacy policy and terms pages are not written (legal text must come from the company).
4. `noindex` must be removed, and canonical URLs and an Open Graph image added, at launch.
5. The new logo replaces the current one: needs the company's approval.
6. English only. An Arabic version needs an Arabic typeface chosen on real copy, plus RTL review.
7. The no-JavaScript dial uses late-October time-zone offsets; with JavaScript it is always live.
