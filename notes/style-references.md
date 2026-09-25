# Style references applied to this site

Two published references were used while writing the four pages. Both are
recorded here because "we checked the writing" is a claim, and a claim without a
reference is just an assertion.

## 1. Avoiding AI-writing patterns

<https://github.com/conorbronsdon/avoid-ai-writing> — a pattern catalogue plus a
bundled detector (`avoid-ai-writing-detector` on npm, version 3.36.0 at the time
of writing).

The catalogue lists 56 patterns across content, language, structure,
communication, meta, structural, fingerprint and register categories. The
mechanically fixable ones were applied to the prose here:

- em dashes replaced with commas or full stops, since the catalogue lists them
  as a structural tell
- tier-1 vocabulary removed: *leverage*, *robust*, *seamless*, *utilize*,
  *showcase*, *pivotal*, *paradigm* and the rest
- filler phrases removed: *in order to*, *due to the fact that*, *it is worth
  noting that*, *furthermore*, *moreover*, *in conclusion*
- no promotional language, no significance inflation, no rhetorical-question
  openers, no "let's" constructions, no generic conclusions
- headings in sentence case, not title case
- no inline-header lists, no numbered-list inflation

The judgement-only patterns were applied by hand: uniform paragraph length,
uniform sentence length, hollow intensifiers, self-labelling significance
("this is the interesting part"), and narrated candor ("two caveats I would
rather flag than let you discover later").

The detector's verdict on the four pages is recorded in
`evidence/writing-scan.json`. Run `python3 scripts/11_final_pass.py` to
re-apply the mechanical fixes and re-run the scan, or `--check` to report only.

## 2. Data visualisation

<https://github.com/aj-geddes/useful-ai-prompts/blob/main/skills/data-visualization/SKILL.md>

The guidance there is chart-type-by-data, minimise ink relative to data, label
completely, keep scales consistent, and use colour purposefully. Applied as:

- a heatmap for the distance matrix rather than six separate bar charts
- bars with error whiskers for the control comparison, so the null's spread is
  visible rather than asserted
- a line chart with a log scale for the candidate-set collapse, because the
  quantity spans two orders of magnitude
- one colour means one thing throughout: green for agreement and anchoring,
  ochre for caveats and controls, grey for context
- every figure carries its units, its ranges and its labels in the figure
  itself, and an `alt` attribute and `<figcaption>` in the page

## Where these live in the repo

| file | what it is |
|---|---|
| `scripts/11_final_pass.py` | applies the mechanical style fixes, checks structure, claims, leftovers, forward-looking headings, and that only one root value is quoted |
| `evidence/writing-scan.json` | the detector's output over the four pages |
| `assets/figures/*.svg` | generated figures, every value read from `evidence/` |
| `assets/viz.js` | the five interactive D3 v7 views |
| `assets/data.json` | the data those views bind to |
