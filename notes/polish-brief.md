# Polish four pages for a general reader. Two specific failures to fix.

Repo `/Users/blake/Projects/marco-poc`. Pages: `index.html`, `proof.html`, `response.html`, `whales.html`. You may rewrite all four. Do not touch `assets/site.css`, `assets/data.json`, `marco/`, `scripts/`, or `evidence/`.

## Read first
`evidence/RESULTS.json`, `evidence/validation.json`, `evidence/root-proof.json`, `evidence/capability-nearness.json`, `evidence/overlay-environment.json`, `evidence/marco-polo.json`, `primer.seed.json`, `assets/primer.seed.json`, `marco/world.py`, `marco/locus.py`, `marco/verify.py`, `notes/transcript-excerpts.md`, `notes/style-references.md`, `notes/whale-topologies.md`, `assets/figures/` (14 SVGs), and run `python3 demo.py`.

## FAILURE 1 — the seed is never actually shown or decomposed

This is the most important fix. The seed is the entire shared substrate, it is 3,300 bytes, and a reader never sees it. Fix that comprehensively:

1. **Print the whole file verbatim** in a `mockup-code` block with line numbers. Do not truncate, do not elide. It is 11 top-level keys: `primer_version, beats, commitment, markers, phonology, landmarks, distance, hierarchy, partition, similarity, population`.
2. **Decompose it visually, key by key.** Build a visual, not just a table. For each key draw a labelled block sized by how much of the file it occupies, then beside or beneath it, show what that key *becomes*: `landmarks` becomes 45 plain statements and their readings; `phonology` becomes the 32-syllable codebook; `markers` becomes the five-rung certainty ladder; `distance` becomes the four levels; `similarity` and `commitment` become the one hashing rule; `population` becomes the 204 places the ordering is calibrated on; `partition` contains only the *rule* for ordering, and produces the actual order. Mark each key STORED or DERIVED in a `badge`.
3. **Draw the size contrast to scale.** One figure: the 3,300-byte seed on the left, the frame it reconstructs on the right. Measured values: the seed is 3,300 bytes; the frame it serialises to is 4,532 bytes; the full set of landmarks, codebook and population that a registry-style exchange would have to ship is 67,561 bytes, which is 20.47 times the seed. Draw those three bars to scale so the reader sees it rather than reads it. Say the derived part is never transmitted, and that both sides recompute it and compare a fingerprint before anything else.
4. **Show the single most important line.** `partition` holds a rule, not a sequence. That one line is the difference between transmitting a frame and transmitting a generator, and it deserves its own callout.
5. Add a worked example: change one key in the seed and show what changes downstream. For instance change `similarity.minhash_seed` from 42 to 43: the fingerprint changes, the geometry becomes incommensurable, and the code refuses to compare addresses at all and will only compare exact roots. Quote the library's own refusal string from `marco/locus.py`.

## FAILURE 2 — "axis" and "bits" are meaningless to a general reader

These terms are everywhere and they are jargon. Remove them from the reader's path entirely.

- **axis** → call it a **question**, or a **thing you check**. The 45 axes are the 45 statements. There is no need for the word "axis" on any page. The ordering is "which questions get asked first", not "the axis order".
- **bits** → call them **ticks**, **marks**, or **answers**. "90 bits" becomes "90 ticks, one for each of the 45 questions, asked twice over in finer steps". Explain that each answer is a small piece of information and that 90 of them are enough to name any of the 204 places.
- **partition** → "how the questions are ordered", or "the order the questions are asked in".
- **Gray code** → never use the name. Explain the effect: neighbouring answers produce neighbouring sounds, so a small change in a place is a small change in its address, and the reader hears it.
- **manifold** → keep it only where it is the subject, and always glossed on first use in plain words: the shape of all possible situations, where nearness means likeness.
- **hamming distance** → "how many syllables differ", with the number.
- **canonical set** → "the statements that are true, in a fixed order".
- **encoding** → "turning the answers into an address".
- **deterministic** → "same input, same output, every time".
- **bootstrap** → "the seed asking its own questions".

Go through all four pages and remove every use of these terms that a reader would have to look up. Where a term is genuinely needed for precision, use it once, gloss it immediately in one short clause, and do not reuse it. Prefer the plain word every time.

## Everything else that must hold

- Same voice on all four pages: plain sentences, one to three sentences per paragraph, each carrying a number, a literal string, or a pointer to the figure below it. No abstract phrasing. Headings are sentences a working journalist would write, never a label and never a colon-plus-summary.
- Same skeleton on all four: daisyUI `navbar` with the four links and `aria-current`, a `hero` masthead, `container mx-auto` main content, `footer footer-center`. Same spacing and heading sizes.
- Same illustration density: every page carries figures, not just index.html. If a section is prose or a table only, give it a visual. Reuse the 14 existing SVGs where they fit; build new static SVG or inline SVG where they do not.
- **Flat:** no nesting beyond one level. No card inside a card. No `mockup-window` or `mockup-browser` chrome. No accordion, no `collapse`, no `details`, no tabs, no stepper, no slider. Nothing a reader has to click or hover to see. All information visible at once.
- **Full width** for figures, tables, transcripts and code. Prose keeps a readable measure of about 68 characters; artefacts take the whole width.
- daisyUI components for every job: `card`, `stats`/`stat`, `table table-zebra`, `chat` (`chat-start`/`chat-end`, `chat-bubble`, `chat-header`, `chat-footer`) for every transcript, `badge`, `alert`, `mockup-code`, `divider`, `progress`/`radial-progress`. No page may reference a class from `assets/site.css`.
- Chat bubbles hold short messages. A 19-item list belongs in a full-width list beneath the chat, never inside a bubble.
- Include the shared-manifold argument on index.html and reference it from the other three: a shared vocabulary does not make two differently-built systems place the same situation in the same part of their own space, so the result implies situations occupy a structure independent systems have in common, and the primer is a chart laid over it. The manifold is shared, emergent and inferred; the chart is ours, published and 3,300 bytes. State the limit in the same breath: the chart is shared too, but only when the states are unambiguous. Attribute this to the parent project, not to this repo.
- Attribute the shared-vocabulary caveat to the parent project wherever it appears.
- No em dashes. No cost or latency figures. No forward-looking or proposal sections. No rhetorical-question openers. Ban: delve, leverage, robust, seamless, paradigm, showcase, pivotal, "it's worth noting", "in conclusion", "let's".
- Invent nothing. Every number must come from `evidence/` or `assets/data.json`.

## Verify, then report
Run `python3 scripts/11_final_pass.py --check` and `.venv/bin/python -m pytest tests/ -q`. Both clean. Then report per page: byte size, section count, figure count; confirm the seed block, the seed decomposition, and the size-contrast figure are present; list every jargon term you removed; and report any evidence conflict you found. Do not ask anything; finish and report.

## FAILURE 3 — no section says, in plain terms, what is remarkable about it

Every section currently explains *what* happens and never says *why anyone should care*. A reader finishes a section without knowing whether what they just read was ordinary or extraordinary. Fix that on all four pages.

The rule: **each major section ends with one short line, set in a daisyUI `alert` or a distinct bordered block, that states in ordinary words what is special about what they just saw.** One or two sentences. No hedging, no jargon, and no inflation. If a section genuinely has nothing remarkable in it, do not invent one; say what it establishes and what it does not.

Draw the wording from what the evidence actually shows. The genuinely striking things, in plain terms:

- **One statement** — an agent can say one true thing about itself and it is checkable. Unremarkable alone, and worth saying so: this is the atom the rest is built from.
- **The 45 statements** — none of them is technical. They are questions a person could answer about a room. That is the surprise: a coordinate good enough to match across six unrelated systems is made of ordinary yes/no questions in plain English.
- **The certainty ladder** — a claim can only be as strong as its weakest input, and a model's confidence cannot promote it. Ordinary systems let a model assert. This one makes assertion impossible.
- **The seed** — 3,300 bytes produce everything both sides need, and 67,561 bytes of frame are reconstructed rather than sent. Two systems can share a coordinate system without either transmitting it.
- **The ordering of questions** — the order is not stored, it is worked out from the places themselves. A registry has to ship its structure and keep it versioned; this recomputes it and checks a fingerprint.
- **The address** — a place becomes something you can say out loud, and it is short: six characters already separate all six places, while the full address scales to far more. One form, read at whatever precision you need.
- **The root** — the exact half. Five of six independently built families produced byte-identical roots for the same place. That is not similarity, it is the same number.
- **The two objects together** — identity and location are deliberately kept apart. The address says near and proves nothing; the root says same and destroys nearness. Almost every system that tries to do both does neither well.
- **The shared manifold** — the deepest one. Six systems built by different organisations, on different data, with different designs, with no shared weights and no sight of each other, placed the same situation in the same part of their own space in 87 of 90 comparisons. The obvious explanation, that they were handed the same questions, does not survive contact with the numbers. Something about situations is common to systems that have nothing else in common.
- **The control that matters** — replacing each model's answers with random statements of the same length drops the result from 96.7% to 20.9%. What carries the signal is *which* statements they chose, not how many.
- **The MARCO/POLO turn** — the hider opens with one syllable, four of six places still fit, one question narrows it to two, and the seeker then checks the answer itself rather than accepting it. A stranger can find you without either side trusting the other.
- **The overlay environment** — three agents in the same layered environment read as near because they inherit, and stay distinguishable because they override. An agent can state which layer of its own configuration is in scope, which is something none of them can currently do.
- **The two organisations** — two companies name the same four capabilities with no words in common. Discovery by name finds one of four; discovery by position finds all four, with no mapping table to maintain and no curator to trust.
- **Where it stops** — say plainly that a shared position is not a shared understanding, that the statements were handed to the models rather than invented by them, and that the limit was already identified in the parent project.

Use those as the substance but write them in the page's own voice, tied to the specific values on that page. Never write "what is remarkable here is" as a formula; state the fact and let it stand. And where the honest reading is that something is modest, say that instead.

Then run the two checks and report.

## FAILURE 0 — the register. This is the most important one.

Everything else is secondary to this. The pages must read as though written by **an excellent high-school teacher**, not by a researcher summarising their own work.

What that means concretely:

1. **Assume the reader knows nothing and is smart.** Not a specialist. Someone who did well at school, is curious, and has never seen a coordinate system, a hash, or a model. Never assume a term. Never assume a concept.

2. **Define every term the first time, in the same sentence, in everyday words.** "A hash is a fingerprint for data: change one character and the fingerprint changes completely." Then use it freely. Never define something twice and never leave it undefined.

3. **One new idea per paragraph. Never two.** If a paragraph introduces a coordinate *and* a hashing rule, split it. A reader who has to hold two new things at once puts the page down.

4. **Lead with the concrete instance, then generalise.** Never the reverse. Not "a locus is a locality-preserving embedding" but "here is one place, here is what the agent notices about it, here is the short name it gets". The general statement comes after the reader has seen two or three instances.

5. **Use an everyday analogy for anything abstract, and say where the analogy breaks.** A coordinate is like a postcode: the first letters tell you the region, the whole thing tells you the street. Where it breaks: a postcode is assigned by a central authority, whereas this is worked out from what is around you. An analogy with its limit stated is teaching. An analogy without one is decoration.

6. **Numbers must be small and concrete before they are large or abstract.** Not "90 bits" but "45 questions, each answered yes or no. Ninety ticks in all." Not "20.47x" alone but "the seed is about the length of this paragraph; the thing it rebuilds is about the length of this page."

7. **Show the working, in the order you would do it on a whiteboard.** Every step written out, with the actual value, so the reader could reproduce it with a pen. No step skipped as obvious.

8. **Say why each step is needed before doing it.** A teacher says "we need a way to compare two places, so let's turn each one into a number" before introducing the number. Never introduce a mechanism without first saying what problem it solves.

9. **Anticipate the obvious question and answer it right there.** "You might ask why 45 questions and not 5. Here is what happens if you use 5." A teacher answers the question the class is about to ask. Do not save it for later and do not leave it.

10. **Short sentences. Active voice. No subordinate clauses stacked three deep.** If a sentence needs a comma to survive, split it.

11. **Warm, never patronising.** Do not say "simply", "just", "obviously", "of course", or "it's easy to see". Those words tell a struggling reader that they are the problem.

12. **Every section answers three questions, in this order:** what are we trying to do, how did we do it, and what did we get. Then, separately, what is interesting about it.

Go through all four pages and rewrite to this register. This will make the pages longer. That is correct and expected: the current pages are too short for the ideas in them, not too long. Density is not the same as brevity, and the current density is what makes them unreadable.

## FAILURE 0b — rebuild as standard daisyUI. No custom layer.

Final structural requirement, and it supersedes the flat-override approach.

The pages are currently a hybrid: daisyUI classes, plus a hand-rolled stylesheet (`assets/site.css`) with its own tokens and components, plus an override layer appended to that stylesheet. That hybrid is the source of the contrast faults and the nested layout. Two component systems on one page will always drift.

Rebuild all four pages as **standard daisyUI**:

1. **Use no class from `assets/site.css`.** Not one. The classes to stop using: `card` is fine because daisyUI has it, but drop `wrap`, `masthead`, `kicker`, `title`, `standfirst`, `lede`, `rung`, `rung__num`, `rung__title`, `figure`, `figcaption`, `takeaway`, `meta-strip`, `stat-grid`, `stat`, `stat-label`, `stat-value`, `stat-note`, `locus-block`, `root-block`, `ladder`, `ladder-row`, `ladder-glyph`, `workings`, `step`, `step-n`, `step-title`, `step-body`, `transcript`, `turn`, `turn-who`, `turn-said`, `table-wrap`, `prose-block`, `pull`, `aside`, `honest`, `alert-signal`, `alert-warm`, `site-nav`, `site-footer`, `page-grid`, `col-main`, `col-wide`, `col-side`, `col-full`, `col-half`, `col-third`, `measure`, `measure-tight`, `lanes-note`, `quote`, `mono`.

2. **Use daisyUI's own component for each job, out of the box, unmodified.** No extra CSS to make them look a particular way.
   - page shell: `navbar`, `hero`, `footer footer-center`, `divider`
   - grouped content: `card` + `card-body` + `card-title`
   - numbers: `stats` + `stat` + `stat-title` + `stat-value` + `stat-desc`
   - steps: `steps` + `step` + `step-primary` (this replaces the hand-rolled ladder and the numbered workings)
   - sequences and turns: `timeline timeline-vertical` + `timeline-start`/`timeline-middle`/`timeline-end`
   - transcripts: `chat` + `chat-start`/`chat-end` + `chat-bubble` + `chat-header` + `chat-footer` + `chat-image avatar`
   - comparison and contrast: `diff` + `diff-item-1` + `diff-item-2` + `diff-resizer`
   - warnings and limits: `alert alert-warning`; confirmations: `alert alert-success`
   - literal content: `mockup-code` for code and the seed; `mockup-window` for figures that need a frame
   - labels and statuses: `badge badge-outline` and `badge badge-primary`
   - comparisons: `table table-zebra`
   - progress and proportion: `progress` and `radial-progress`
   - interaction-free emphasis: `tooltip` is forbidden, since nothing may require hover
   - buttons and controls: only where a reader genuinely acts, which on these pages is nowhere

3. **Colour comes only from the theme.** Use daisyUI semantic classes: `bg-base-100`, `bg-base-200`, `bg-base-300`, `text-base-content`, `text-primary`, `bg-primary text-primary-content`, `text-secondary`, `text-accent`, `text-warning`, `text-success`, `border-base-300`. No hardcoded hex, no arbitrary Tailwind colour values like `text-[#333]` or `bg-gray-100`, and no `text-white` or `text-black` anywhere. Each of daisyUI's pairings is contrast-checked; hand-picked colours are where the contrast faults came from.

4. **One theme, declared once.** Keep `<html lang="en" data-theme="light">`. The figures are drawn on white, so a light theme is required for them to be legible. Do not add a dark variant and do not use `prefers-color-scheme`.

5. **Load order:** the daisyUI stylesheet, then nothing else. Delete the `<link rel="stylesheet" href="assets/site.css">` tag. I will remove the file itself once all four pages stop referencing it, and I will verify that with a check.

6. **Layout with Tailwind utilities only.** `container mx-auto max-w-5xl px-4`, `grid grid-cols-1 gap-6`, `lg:grid-cols-12` for two-column sections where a figure genuinely needs a caption beside it, `py-12` between movements. Artefacts full width. Prose about 68 characters.

When you report, state explicitly that the page contains zero references to `assets/site.css`, and list the daisyUI components you used per section.
