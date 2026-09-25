# Integrating marco1.md, marco2.md, marco3.md into the four pages

Operator decision, 25 Sep: the concepts in the three source notes
(`~/Downloads/marco1.md`, `marco2.md`, `marco3.md`) must appear on all four pages.
They are incorporated **translated into the pages' own plain register**. The
source notes' own vocabulary is deliberately not used, and their unsupported
numbers are dropped.

Read this whole file before editing. It is the contract.

## What you may touch

- Exactly one file: the page you were assigned.
- Nothing else. Not `assets/`, not `marco/`, not `scripts/`, not `evidence/`,
  not another page, not `notes/polish-brief.md`.
- New figures are **inline SVG inside your page**. Do not add files to
  `assets/figures/`.
- `notes/polish-brief.md` is the standing brief and still binds you. This file
  adds to it and does not replace it.

## The register (from polish-brief.md, FAILURE 0)

Write as an excellent high-school teacher, not a researcher. Assume the reader
is smart and knows nothing. Concretely:

- One new idea per paragraph. Never two.
- Define every term on first use, in the same sentence, in everyday words.
  Never define it twice.
- Lead with the concrete instance, then generalise. Never the reverse.
- Short sentences. Active voice. No stacked subordinate clauses.
- Where you use an analogy, say where it breaks.
- Show the working in the order you would on a whiteboard, with real values.
- Say why a step is needed before doing it.
- Anticipate the obvious question and answer it in place.
- Never write "simply", "just", "obviously", "of course", "it's easy to see".
- Attribute the shared-vocabulary caveat, and the manifold argument, to the
  parent project wherever they appear.

## Mechanical rules the checker enforces

`python3 scripts/11_final_pass.py --check` must report **0 problems** for your
page. It fails on all of these:

- **No em dashes.** No `—` and no `--`. Use a comma, a full stop, or a colon.
  En dashes in numeric ranges are fine.
- **No dangling `src="..."`.** Every local reference must exist.
- Keep `<html lang="en" data-theme="light">`, the daisyUI stylesheet, the
  Tailwind script, and `aria-current="page"` on your own nav link.
- **No class from `assets/site.css`** and no reference to that stylesheet.
- **No hand-picked colour.** No `text-white`, `text-black`, `bg-white`,
  `bg-black`, no `text-[#...]` or `bg-[#...]`, no `text-gray-500` and friends.
  Colour comes from daisyUI semantic classes only. Inside your inline SVG use
  `currentColor` and `opacity` only, never a hex literal.
- **No chat bubble** holding more than 160 characters on one line, and none
  holding a comma list of 8 or more items. A long list goes in a `ul` beneath
  the chat, labelled as the working.
- **No forward-looking heading.** No `h2`/`h3` matching "what would make",
  "next steps", "future work", "recommendations", "roadmap", "looking ahead".
- These three values must appear on your page (they already do; do not remove
  them): the fingerprint `df2f8b9972c40bfdd132366a58b4780f65f23feba1ef20a060c25d4eff2661ba`,
  `96.7`, and `16.7`.
- The banned vocabulary is auto-replaced and reads as filler: delve, leverage,
  utilize, robust, seamless, paradigm, pivotal, showcase, tapestry, realm,
  landscape, underscore, myriad, plethora, embark, harness, navigate, holistic,
  game-changer, cutting-edge, state-of-the-art. Do not write them. **"paradigm"
  is banned, so "the orchestrator paradigm" must be written as "the orchestrator
  pattern" or in plain words.**

`python3 scripts/11_final_pass.py --check` must also keep passing for the other
three pages, which it will if you stay inside your own file.

## Numbers

- **Invent nothing.** Every number already on your page stays as it is.
- **Drop the source notes' unsupported numbers.** Specifically do not write
  `100%`, `60%`, `68%`, `98%`, `403`, or any token-reduction or latency figure.
  None of them has backing in `evidence/`.
- The numbers you may use are the ones already on your page, plus anything in
  `evidence/*.json`, `assets/data.json`, and `README.md`.
- Where a source note's claim needs its number to make sense, state the claim
  qualitatively instead, and cite the paper the page already cites
  (`arXiv:2601.06851` on index.html, `arXiv:2601.14567v2` on response.html).

## Structure and components

- Flat. No nesting beyond one level. No card inside a card. No accordion, no
  `collapse`, no `details`, no tabs, no stepper, no slider, no tooltip. Nothing
  a reader must click or hover to see. All information visible at once.
- daisyUI only, out of the box: `card`/`card-body`/`card-title`, `stats`/`stat`,
  `table table-zebra`, `chat` (`chat-start`/`chat-end`, `chat-bubble`,
  `chat-header`, `chat-footer`), `badge`, `alert`, `mockup-code`, `divider`,
  `progress`, `radial-progress`, `timeline timeline-vertical`, `steps`/`step`,
  `diff`, `navbar`, `hero`, `footer footer-center`.
- Keep the existing skeleton and spacing: navbar, hero masthead,
  `container mx-auto max-w-5xl px-4`, `py-12` between movements, prose at about
  `max-w-prose`, artefacts at full width.
- Keep the existing `footer footer-center` carrying the fingerprint and the four
  cross-links.
- **Every new major section closes with one short line**, in a daisyUI `alert`
  or a distinct bordered block, stating in ordinary words what is remarkable
  about what the reader just saw, or where it stops. One or two sentences. Never
  the formula "what is remarkable here is". State the fact and let it stand.
- Headings are sentences a working journalist would write. Never a bare label,
  never a colon plus a summary.

## Figures

- Every new central concept needs a diagram. The figure teaches the idea and the
  prose introduces it and gets out of the way.
- Inline SVG. `currentColor` and `opacity` only. Labels and arrows sit on the
  drawing, next to the thing they name. One idea per figure.
- Number your new figures continuing your page's existing sequence (index.html
  is at Figure 28, proof.html at Figure 10, response.html at Figure 6,
  whales.html currently has none: adopt the same `Figure N.` caption convention
  and start at Figure 1).
- Caption in one sentence: what it shows, then the takeaway. Prose refers to it
  by number in the sentence that needs it.
- Static. No interaction required to see any value.

## The concepts, and how each one must be said

These treatments are fixed so all four pages describe the same thing the same
way. Use the plain wording, not the source notes' vocabulary.

**A. A file path is not a place.** A path says where a file is kept. It says
nothing about what the agent is doing or what it can reach. Move the folder and
the path is wrong; do the same job somewhere else and the old path says nothing
about the new one.

**B. Place has three parts.** What is kept where (the structure), what the agent
was asked to do (the intent), and how current the machine is (the state). The
pages do not measure the third part; say so.

**C. The words a person already uses for a building.** Doors are permissions.
Weather is how loaded the machine is. Trails are how it got here. Gravity is
what the human wants most. Rooms are what kind of place it is. Home is which
model it belongs to.

**D. Eight ways to describe where things are relative to each other.** The
picnic (who brought what), the odd little country (a repository with borders),
the murmur (a crowd forming a shape), the lost property office (items with tags),
the house with too many rooms (contexts that move around), the tidepool (what
flows between pools and what is stranded), the constellations (meaning in the
lines drawn between things), the department of nearby things (proximity only).
One sentence each, and what each one emphasises.

**E. The punctuation in an address carries meaning.** Gloss each symbol once:
the project mark, the neighbourhood dot, the plus for what it can reach, the
tilde for its current state, the exclamation mark for the proof. And the five
markers for how strong a claim is: exact, derived, measured, the model's own
reading, and a guess. Say plainly that only the first two are proofs.

**F. An address you can say out loud.** The sounds are a rendering of the
coordinate, not a label someone assigned.

**G. Nearby places get nearby sounds.** A small change in a place makes a small
change in its name, so a person can hear that two places are close. Never write
the name of the coding scheme that produces this.

**H. Read less of the name and you get a region.** The first syllable orients
you; the whole string gives the exact place. A smaller model can stop after the
first part, and a larger one can read the lot. Growing precision never
invalidates the shorter reading.

**I. The trail: how it got here.** A root says what is true now. A trail says the
steps taken to arrive. Plain name: the record of the route.

**J. The claim travels with its proof.** Facts are collected, put in a fixed
order, and sealed into one value. Anyone holding the same facts gets the same
value, so the claim can be checked instead of trusted. To find where you are,
measure your distance from several known points and work out the position from
the measurements.

**K. The anchors.** Three kinds of fixed point: the chain of what the agent has
already done, which machine and which model family it runs on, and the project
owner's signature.

**L. Eight things an agent could say about itself.** What it is structurally
near, what it is trying to do, what it can reach, what it is not allowed to do,
which other agents and people are close, how old its context is, how much
machine it has, and where it came from. Say plainly that agents today cannot
state any of these.

**M. Two agents can share a past and have drifted.** Whether a copy is in step,
behind, or on its own separate history, and where exactly the histories parted.

**N. How close the others are.** The sense of other agents nearby, and of being
watched by a person.

**O. One shared floor, many private views.** The shared proving layer is the
same for everyone; each agent's view of it is its own. Coordinators sit in the
integrating middle; helpers sit at the edges.

**P. Overlapping maps, not a rigid grid.** A grid gives two neighbours unrelated
addresses when they fall either side of a line. Overlapping maps keep neighbours
near each other across the whole space. This is the difference from geohashing
and what3words, which are rigid grids, and from `agent://` URIs, which are static
labels.

**Q. How many letters differ.** Already on your page as the count of differing
letters in the rendered name. Keep that wording.

**R. Why independent systems could agree at all (from marco1.md).** Middle layers
of a trained model combine information so that the whole carries more than the
parts, while the outer layers mostly repeat; this organisation appears through
training and is absent in an untrained network. A model that only repeats likely
continuations is the older picture of what these systems do. Training on worked
examples encourages storing answers; training against outcomes pushes the
answers into the part that combines, which is where generalising comes from.
A claim can also collapse while it is being made: the combining drops away and
the model falls back on likely-sounding text. Agents that hand work to each other
can also cover for a failed one by picking up what it left unfinished. Where a
drawing carries intent that a shape does not, such as a tolerance or a finish,
matching a number is not enough.

## Allocation

Each page takes the subset below. Do not copy another page's sections. Treat a
concept that already exists on your page as done: add what is missing, do not
duplicate.

- **index.html** (the whole story): A, B, C, D, E, F, G, H, I, J, L, M, N, O, P,
  and R framed as the mechanism behind the agreement.
- **proof.html** (how far this can be proved): E's five markers as the strength
  ladder, I, J, K, L, Q, and R's collapse-while-claiming point, which is why
  confidence cannot promote a claim.
- **response.html** (the reply to the `agent://` paper): A, E, H, L, O, P, R's
  hand-over and drawing-intent points, which are what a discovery scheme has to
  cope with.
- **whales.html** (whale phrases on the same geometry): F, G, H, M, N, P, and R's
  mechanism, which is why two systems could place the same phrase alike.

## Verify before you report

Run all three, from the repo root, and paste the exact output:

1. `python3 scripts/11_final_pass.py --check`
2. `.venv/bin/python -m pytest tests/ -q`
3. `grep -c 'site.css' <yourpage>.html` and a grep of your page for `—` and `--`
   proving both are absent.

Then report: your page's byte size, section count, figure count, the concepts you
added, and every source-note concept you judge not to belong on your page and why.
