# Intimedev: creative directions

Three directions were developed from the discovery report. Each one answers the same brief: make Intimedev recognisable without its logo, and make "built on time, kept running" visible.

## A. The Turn

**Idea.** The current logo's hourglass, upright, is a deadline. Turned a quarter, it becomes ∞: long-term support. The whole site animates that turn. A working prototype of this direction was built first (kept outside the site, in `intimedev-v1-the-turn/`).

- Strengths: one clear gesture; reuses an asset clients may already know; strong scroll moment.
- Weaknesses: the hourglass is the most common "time" icon there is, and it also reads as "running out of time", the opposite of the promise. It keeps the indigo palette that every SaaS template uses. Hard to extend beyond the one turn.

## B. Commit Log

**Idea.** Software is built one commit at a time. The site reads like version history: monospace headlines, diff colours, timelines of releases, every section a "changeset".

- Strengths: honest about the work; very easy to build; developers recognise it instantly.
- Weaknesses: speaks to developers, not to the owners and operations leads who buy; green/red terminal styling is a cliché in this sector; no link to Egypt or to the name.

## C. Gnomon (recommended)

**Idea.** A gnomon is the part of a sundial that casts the shadow. The lowercase **i** of "intime" is already a gnomon: a stem with a sun above it. Light it from the side and its shadow falls along the ground; stem and shadow together are the two hands of a clock. The graphic language comes from one of the oldest known sundials, found in the Valley of the Kings: a semicircle divided into twelve sections.

- **Mark:** stem (ink), shadow (Egyptian blue), sun (solar orange). Reads as an i, a sundial and a clock at three o'clock.
- **Colour:** Egyptian blue, the first synthetic pigment, made in Egypt; deep ink for the shadow side; a single solar orange used only for the sun and for "now".
- **Signature devices:** the twelve-section dial; hard, directional shadows that follow the real position of the sun in Cairo; hour ticks as a layout ruler; time-zone overlap arcs.
- **Motion:** sunrise (things rise and their shadow lengthens), sweep (a dial hand moves to a new state), settle. Nothing floats or glows.
- Strengths: ownable (rooted in Egypt and in the name), works at every scale from favicon to hero, turns the "three markets" fact into a useful interactive tool, avoids every sector cliché.
- Weaknesses: needs disciplined execution so it stays technical rather than "ancient Egypt" themed; no hieroglyphs, papyrus textures or gold.

## Comparison (1 = weak, 5 = strong)

| Criterion | A. The Turn | B. Commit Log | C. Gnomon |
|---|---|---|---|
| Memorability | 4 | 3 | 5 |
| Distinctiveness | 2 | 2 | 5 |
| Relevance to business and audience | 4 | 2 | 5 |
| Scalability (social, decks, product) | 3 | 4 | 5 |
| Implementation feasibility | 4 | 5 | 4 |
| **Total** | **17** | **16** | **24** |

## Decision

**Direction C, Gnomon.** It is the only direction that is about the company's name, its origin and its promise at the same time, and it gives the site a useful hero (when will this team be working in my time zone?) instead of decoration.

Guardrails for C:

1. Technical, not themed: geometry, shadows and time. No pharaonic imagery.
2. Orange is the sun and only the sun: one small mark of "now" per view.
3. Shadows are hard and directional, never soft drop shadows.
4. Every live element degrades to a correct static state (no JavaScript, reduced motion, night time in Cairo).
