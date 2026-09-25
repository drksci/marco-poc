# Final polish pass: one agent, all four pages

This is a **single-agent** pass. One agent owns all four pages
(`index.html`, `proof.html`, `response.html`, `whales.html`) and works across
them together, comparing as it goes, so no page is left behind. No other writer
touches this repository while this pass runs.

Run it only after the four per-page integration workers have finished and their
output is committed or at least verified. If a page is mid-edit, stop.

## Mobile responsiveness (operator instruction, 25 Sep)

Every page must be genuinely usable on a phone, not merely not-broken. Audit at
360 px, 390 px and 768 px widths and fix what fails:

- **No horizontal overflow.** `document.scrollWidth` must equal the viewport
  width at each of those three widths. A wide table, a `mockup-code` block, a
  long coordinate string or an inline SVG is the usual cause. Artefacts get
  `w-full max-w-full overflow-x-auto` and wrap rather than push the page wide.
- **Long strings wrap.** Addresses, fingerprints and file paths must use
  `break-words` or `break-all` so a 64-character fingerprint cannot widen the
  page. A fingerprint must stay selectable and copyable when wrapped.
- **Two-column figures stack.** Anything built as two side-by-side columns must
  be `grid grid-cols-1` at phone width and `lg:grid-cols-2` (or `lg:grid-cols-12`)
  above it. Rows that line up across two columns on desktop must stack in
  reading order on a phone, and the labels that span both columns must still
  read correctly when stacked.
- **Tap targets** are at least 44 px high for anything a reader taps (the nav
  links).
- **Type sizes** stay legible: body text at least 16 px, captions and
  `mockup-code` at least 12 px, and no text smaller than 12 px anywhere.
- **No fixed pixel widths** on content containers. Use `max-w-*` and `w-full`.
- **Charts and diagrams** must either scale to the container or scroll inside
  their own box. Nothing may require pinching to read, and no label may be cut
  off at 360 px.
- Verify by measurement where you can (a headless check of `scrollWidth` against
  `clientWidth`, or a resize of the browser), and by inspection where you
  cannot. State in the report which you did.

## Creative latitude (operator instruction, 25 Sep)

This pass is authorised to **reauthor and redesign**, not merely to tidy.

- You may rewrite any prose on any of the four pages.
- You may **redesign every figure, or replace any figure outright**, including
  with a different visual form. `d3@7` is already loaded in every page head, so
  a data-driven or generated drawing is allowed and encouraged where it teaches
  better than a static one. Inline SVG, generated SVG, and D3 are all in scope.
- You may **rename the vocabulary** if a plainer or more accurate term exists.
  The operator's own suggestion is that a name like *content-based identifier*
  may be better than the current wording for what the string is. If you adopt a
  new term, define it on first use in ordinary words, and use it consistently
  across all four pages. Do not adopt the source notes' jargon instead.
- Keep the four pages distinct in what they deliver, and keep the result
  evidence-bound.

The only things that are not negotiable are the constraints in this file: the
golden-reference form, the register, the daisyUI-only rule, the flat rule, no
em dashes, the evidence bound on numbers, and the three required values.

## Source material to read in full

Read all of this before writing, and use it: `~/Downloads/marco1.md`,
`~/Downloads/marco2.md`, `~/Downloads/marco3.md`, `notes/polish-brief.md`,
`notes/integration-spec.md`, `notes/whale-topologies.md`,
`notes/transcript-excerpts.md`, `notes/style-references.md`, `README.md`,
`evidence/` (the whole directory), `assets/data.json`, `assets/figures/` (all
13 SVGs), `marco/` (the library), `demo.py`, and all four pages including the
parts you are not changing.

## What this pass is for

The four pages have been built up over many commits and then extended with the
concepts from `~/Downloads/marco1.md`, `marco2.md` and `marco3.md`. This pass is
the last one: raise all four to one standard together, and stop.

## The golden reference

`https://transformer-circuits.pub/2026/workspace/index.html`

Fetch it and read it before changing anything. Take its **form**, not its
subject. What it does that these pages must match:

1. **The figures are the explanation, not decoration for it.** A figure there is
   a small self-contained object that teaches one idea by being looked at. A
   reader should be able to read a figure and understand the concept without the
   surrounding prose.
2. **One idea per figure, and the figure is where the reader learns it.** The
   prose introduces the figure and gets out of the way. If a paragraph is doing
   the teaching and the figure is illustrating the paragraph, invert it.
3. **A step-by-step build-up with every stage visible at once.** The small case,
   then the slightly larger case, then the real case, all on the page, so the
   reader can compare them. Not one at a time behind a control.
4. **Concrete before abstract, and the concrete thing is shown.** A real string,
   a real number, a real transcript. Never a schematic standing in for a real
   value that exists.
5. **Annotations sit on the figure.** Labels, arrows and short callouts are on
   the drawing, next to the thing they name. Not a legend below, not a caption
   that says "as shown".
6. **Numbered figures referred to from the prose.** "Figure 3" appears in the
   sentence that needs it. The caption says what the figure shows in one
   sentence, then the takeaway.
7. **Plain but precise prose with no hype.** It never says something is
   remarkable; it shows the thing and lets the reader conclude it.
8. **Generous whitespace and a calm typographic hierarchy.** One column, wide
   margins, large headings, short paragraphs. Nothing competes.
9. **Explorable only where exploration teaches.** Every value must be visible
   without interaction; exploration may only add, never hide.

## What each page delivers

Keep these distinct. They are four views of one result, not four drafts of it.

- `index.html` — the whole story in plain language.
- `proof.html` — how far the result can be proved rather than asserted, and
  where proof stops.
- `response.html` — a working reply to `arXiv:2601.14567v2`, and the
  demonstration that answers its stated weakness.
- `whales.html` — whale vocalisation structure mapped onto the same geometry,
  and what a predictive mapping would require.

## Accessibility (the part most likely to be thin)

Do this as an audit, not an assertion. Check every page and fix what fails:

- **Every `<img>` has a meaningful `alt`.** Not a filename, not "figure". The
  alt says what the figure shows. A purely decorative element gets `alt=""`.
- **Every inline `<svg>` that carries meaning has `role="img"` and a `<title>`
  (first child) or `aria-label`,** so a screen reader announces it. Decorative
  SVG gets `aria-hidden="true"`.
- **Heading order.** One `h1` per page, then `h2` for sections and `h3` only
  inside an `h2`. No level skipped. Run a check, do not eyeball it.
- **No meaning carried by colour alone.** Anything distinguished by colour is
  also distinguished by a label, a shape, or text.
- **Tables** have a `<caption>` and `<th scope="col">` on the header row.
- **Transcripts** built from `chat` bubbles are readable as text in order, and
  the speaker is named in text, not only by left/right position.
- **Links** are descriptive. "This paper", not "click here" or a bare URL.
- **Nothing requires hover or click** to be read (`tooltip` is forbidden).
- **Contrast** comes only from daisyUI's own pairings: `bg-base-100`,
  `bg-base-200`, `bg-base-300`, `text-base-content`, `text-primary`,
  `bg-primary text-primary-content`, `text-secondary`, `text-accent`,
  `text-warning`, `text-success`, `border-base-300`. No hex, no arbitrary
  Tailwind colour, no `text-white` or `text-black`.
- Keep `lang="en"`, the `aria-current="page"` marker on the current nav link,
  and a real page `<title>`.

## The register that must hold on every page

From `notes/polish-brief.md`, FAILURE 0, and it still binds:

- An excellent high-school teacher, not a researcher. Assume a smart reader who
  knows nothing.
- One new idea per paragraph, never two.
- Define every term on first use, in the same sentence, in everyday words. Never
  define it twice.
- Concrete instance first, general statement after.
- Where an analogy is used, say where it breaks.
- Short sentences, active voice. Never "simply", "just", "obviously", "of
  course", "it's easy to see".
- Attribute the shared-vocabulary caveat, and the manifold argument, to the
  parent project.
- Every major section closes with one short line, in an `alert` or a distinct
  bordered block, saying in ordinary words what is remarkable about what the
  reader just saw, or where it stops. Never the formula "what is remarkable
  here is".
- Headings are sentences a working journalist would write. Never a bare label,
  never a colon plus a summary.
- No em dashes anywhere. No forward-looking or proposal sections.

## Hard constraints

- **Flat.** No nesting beyond one level, no card inside a card, no `collapse`,
  `details`, tabs, stepper, slider, or `tooltip`. Everything visible at once.
- **daisyUI only**, unmodified, out of the box. Zero classes from
  `assets/site.css`, and no reference to that stylesheet. The shared vocabulary
  is `navbar`, `hero`, `footer footer-center`, `divider`, `card`, `stats`,
  `steps`, `timeline`, `chat`, `diff`, `alert`, `mockup-code`, `badge`, `table
  table-zebra`, `progress`, `radial-progress`.
- **Numbers:** invent nothing. Every number must already appear on the page or
  exist in `evidence/*.json`, `assets/data.json` or `README.md`. Do not add
  `100%`, `60%`, `68%`, `98%`, `403`, or any cost, token-reduction or latency
  figure.
- Do not touch `assets/`, `marco/`, `scripts/`, `evidence/`, or
  `notes/polish-brief.md`. New figures are inline SVG inside the pages.
- These three values must remain on every page: the fingerprint
  `df2f8b9972c40bfdd132366a58b4780f65f23feba1ef20a060c25d4eff2661ba`, `96.7`,
  and `16.7`.
- Banned vocabulary is auto-stripped and reads as filler: delve, leverage,
  utilize, robust, seamless, paradigm, pivotal, showcase, tapestry, realm,
  landscape, underscore, myriad, plethora, embark, harness, navigate, holistic,
  game-changer, cutting-edge, state-of-the-art.

## Measure it, do not assert it

Run all of these from the repo root and paste the exact output in the report.

1. `python3 scripts/11_final_pass.py --check` — must report **0 problems**.
2. `.venv/bin/python -m pytest tests/ -q` — must pass.
3. Em dash and double hyphen sweep over all four pages; must be zero.
4. `grep -c 'site.css' index.html proof.html response.html whales.html` — all 0.
5. An accessibility audit you run and paste: count of `<img>` without `alt`,
   count of meaningful `<svg>` without `role="img"`/`<title>`, heading levels in
   document order per page, and `<table>` without a `<caption>`.
6. Per page: byte size, section count, figure count.

## Report

Per page: byte size, section count, figure count, and the single sentence you
would use to describe what that page delivers. Then list, across all four pages,
every accessibility defect you found and fixed, every figure you added or
reworked, and any evidence conflict or unresolved gap you hit. If a page still
has a gap you could not close, say which and why.
