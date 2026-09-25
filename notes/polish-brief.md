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
- **the recorded distance** → "how many letters differ", with the number. It counts differing letters in the rendered name, which is 36 letters for 18 syllables. Do not call it syllables; an agent checked this against `locus.Encoder.hamming` and the brief was wrong.
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

## FAILURE 0c — the opening must be one transcript, not an explanation

The pages do not express what is actually remarkable here. They explain a system. They never show the moment that makes someone sit up. Fix the opening of index.html, and put the same example wherever the other pages first make the claim.

### What is actually remarkable, stated once

Six AI systems, built by six different organisations, trained on different data, with different designs, no shared weights and no shared context, were each shown the same ordinary English paragraph describing a room. None of them saw the others. None was told what the others said. None was told that any other system existed.

Each returned a short nonsense-looking string.

**The strings for the same room matched.**

Nobody defined what a kitchen is. Nobody gave them a vocabulary of places, or a map, or a shared embedding. Two systems that share nothing looked at the same description and independently landed in the same neighbourhood. That is the thing. Everything else on these pages is the machinery that makes it checkable.

### The opening, exactly

Do not open with the kitchen anecdote as a rhetorical device. Open with the exchange itself, as a transcript, at the top of the page, before any explanation:

1. **One paragraph of plain English**, set in a bordered block and labelled as the input. Use a real one, verbatim from `marco/world.py`: the `kitchen_with_friend` description. It is about five sentences and mentions a window, a friend, labels on things, cooking, and that broken things stay broken.

2. **Two chat bubbles side by side or stacked**, labelled with two of the real model ids, each containing only the string that system returned. Use the real addresses from `evidence/lanes-summary.json` for `kitchen_with_friend`; two of the six families produced the identical string, so show that pair and let the identity land. Beneath each bubble, in small type, the model id and the fact that it was a separate call.

3. **One line under the pair**, in large type, stating the fact plainly: two systems built by different organisations, trained on different data, never in contact, and shown only the paragraph above, returned the same address for the same room.

4. **One line under that** giving the scale: the same thing held for eighty-seven of ninety comparisons across six such systems, and random answers would have scored sixteen.

5. **Then, and only then**, one sentence naming what the reader is about to find out: what the string is made of, why it is short, and how a stranger can check it without trusting anyone.

That is the whole opening. No headings, no preamble, no "imagine two programs meet". The transcript is the hook. The reader should be surprised before they are taught anything.

### Then, immediately after the opening, the same example worked in full

Before any general explanation, take that one room and walk it end to end with real values, in this order, each step on its own line with its value:

- the paragraph the systems were given
- the 45 statements, and the 19 that this room makes true, listed
- the distance from each of the 45 statements to the room, as numbers
- the ticks those distances produce
- the syllables those ticks produce
- **the address, which is the string in the transcript above**
- **the root**, and the fact that it is exact while the address is only near

Then say: that is one room, one address, and it took no shared map to produce. Everything after this point on the page explains why the string looks the way it does and why you can trust it.

Move the current general exposition, the seed section, and the controls to after this worked example. The page currently explains the machinery before showing the thing the machinery does.

### The rule for every page

Wherever a page makes its central claim, show the claim as a transcript or a worked instance first, and explain it second. proof.html: show the same room checked twice and matching, before explaining determinism. response.html: show the two organisations' addresses for the same job, before explaining nearness. whales.html: show one coda described, before explaining a phrase vector.

Do this in addition to FAILURE 0 (the register). The register makes the explanation followable; this makes it worth following.

## THE TARGET STANDARD — the form this publication is aiming at

Golden reference: `https://transformer-circuits.pub/2026/workspace/index.html`

Read it before finishing, and take its *form* rather than its subject. What that publication does, and what these pages must do:

1. **The figures are the explanation, not decoration for it.** A figure there is not a chart of a result; it is a small, self-contained, explorable object that teaches one idea by being looked at. Each of our fourteen static SVGs should be reworked in that spirit: a reader should be able to *read* a figure and understand the concept without the surrounding prose.

2. **One idea per figure, and the figure is where the reader learns it.** The prose introduces the figure and then gets out of the way. If a paragraph is doing the teaching and the figure is illustrating the paragraph, invert it.

3. **A step-by-step build-up in which every step is visible at once.** That publication shows you the small case, then the slightly larger case, then the real case, all on the page, so you can compare them. Not one at a time behind a control. Not "the animation shows". Every stage present, in order.

4. **Concrete before abstract, always, and the concrete thing is shown.** A real token, a real string, a real number, a real transcript. Never a schematic standing in for a real value when the real value exists.

5. **Annotations placed on the figure itself.** Labels, arrows and short callouts sit on the drawing, next to the thing they name. Not a legend below, not a caption that says "as shown". Point at the thing.

6. **Numbered figures referenced from the prose.** "Figure 3" appears in the sentence that needs it. The reader can find it. Captions say what the figure shows, in one sentence, and state the takeaway.

7. **Plain but precise prose, with no hype.** Confident, specific, unhurried. It never says something is remarkable; it shows the thing and lets the reader conclude it.

8. **Generous whitespace and a calm typographic hierarchy.** One column, wide margins, large headings, short paragraphs. Nothing competes.

9. **Explorable where exploration teaches, static where it does not.** An interactive figure is acceptable when a reader dragging or stepping through it produces *insight* — seeing a space collapse, watching a value propagate. It is not acceptable as a way to hide information. Every value on these pages must be visible without interaction; exploration may only add.

Apply that form to all four pages in addition to FAILURE 0 (register), 0b (daisyUI) and 0c (open on the transcript). The figures are the largest remaining gap: they are currently charts that report, when they need to be diagrams that teach.

## FAILURE 0d — the proof must be runnable by the reader, not just reported

The strongest thing this project can offer is not a number. It is that a reader can check the central claim themselves, in about two minutes, with a phone, and no key, no terminal, and no understanding of the code.

Build this into proof.html as its own section, placed early, and reference it from index.html.

### The artefacts, which already exist

- `assets/figures/field-test-qr.svg` — a QR code holding a small self-contained primer: sixteen statements a person can honestly answer about a room, and one place described in plain English. Payload 1,062 bytes, QR version 27, medium error correction, so it scans from a screen and from paper. Show it at a size a phone can read, and say so.
- `assets/figures/field-test-card.svg` — the card to fill in: the sixteen numbered statements and two blank columns, plus what each possible outcome means.
- `evidence/field-test.json` — the whole fixture: the place text, the sixteen statements with their plain readings, which are true, the expected answer numbers, the address under the full primer, the address under the reduced primer, and the root.

### The section to write

State it as an instruction to the reader, in the register of FAILURE 0, and keep it short:

1. What to do. Scan the code into one assistant. Do not tell it what the code is for and do not explain the project. It will answer with a set of numbers. Do the same in a different app. Tick the answers on the card and compare.
2. Why it is a real test. The two assistants share no weights, no training data, no context and no contact. Neither is told the other exists. Neither is told what the place is called. If their answers agree, the frame is shared. If they differ, the claim on this page is wrong, and say so plainly.
3. What will happen. Most assistants answer the same way, because the sixteen statements are ordinary English about a room and the place is described so that a careful reader would answer the same way. Say that this is the honest shape of the result: the test is easy to pass, and it is a test because it could fail. Do not overclaim a low base rate.
4. What the reader can then check. Paste the numbers into the repository and get the address, or read it off: the expected answer is `1,2,4,5,6,11,14,16`, the library room's address under the full primer is `⌁ se.re.ni.ka.nu·re.ru.ki.va.sa+ru.ki.va.so.ru~ko.se.ta`, and the root of that answer is `!65bdc8219e4462894ea7bb2a54f9dff07545fd2c05e1baefd7a062329fbcb114`.
5. State the limit of the reduced primer honestly: the sixteen statements are cut from the same seed by the same rule, so it produces a genuine prefix of the full address, and the reduced address for the library room is `⌁ ma.ne.ti.ma`, which does not match the full address's prefix because a reduced vocabulary changes which statements carry the most weight. Say that rather than hiding it.

Do not claim the test has been run at scale by us. Say what it is, what it will show, and that the reader running it is what makes it evidence rather than a claim.

Also add a line to index.html's opening, after the transcript, offering the reader this test in one sentence with a pointer to the section.

## FAILURE 0e — the opening figure: two agents, one seed, then they check each other

The opening of index.html needs a figure that carries the whole discovery in one glance, and it must be drawn as two vertical chat columns read side by side.

### Layout

Two columns, equal width, side by side on wide screens and stacked on narrow ones. Left column headed with one real model id, right column with another. Use daisyUI `chat chat-start` for the left and `chat chat-end` for the right so the two sides are visually distinct. Give each column a `card` with a `card-title` naming the model.

**Rows must line up across the two columns**, so the reader can read straight across and compare. Use matched heights or a grid with aligned rows.

### The four turns

**Turn 1 — the seed is handed over.** Paste the same text into both columns, verbatim, so the reader sees that both received the identical thing. Keep it short enough to read: the sixteen-statement field primer from `evidence/field-test.json` is the right size, or a comparable reduced primer. Show it in `mockup-code` inside the bubble, or as a bubble followed by a full-width code block if it is too long for a bubble. Label the row across both columns: *the same seed, handed to both*. This is the moment the reader should understand that nothing else is shared.

**Turn 2 — the same question.** One row, both columns, each bubble containing the same question. Use the real one: the place description from `evidence/field-test.json`, asked as "which of these statements are true of this place?" Label the row: *the same question, asked separately*.

**Turn 3 — each answers.** Both columns, the answer each gave. Their answers are number sets. Show them. Label the row: *each answers alone*.

**Turn 4 — the cross-over.** This is the part that makes the figure. Each column is now shown the **other** one's answer and asked whether it recognises it. Left column receives the right column's answer, right column receives the left's. Each replies that it does. Label the row across both columns: *then each is shown the other's answer*. State in a line beneath that neither was told the other existed until this point, and neither was told the name of the place.

### What the figure has to make obvious without any prose

- The same seed going into both sides, visibly identical.
- The two answers coming out visibly alike.
- The cross-check at the end, where each side is handed the other's output and recognises it.

Draw the seed row with a horizontal bracket spanning both columns to show it is one object given twice. Draw a crossing pair of arrows between the columns on the final row, so the "x over" is literally visible.

### Honesty requirements

- If the real recorded answers for the two models you choose are not identical, show them as they are and say how far apart they are. Do not pick a pair that flatters the result without saying so.
- Do not claim this exchange was run as a single conversation. It was separate calls, and the cross-check is a reconstruction of what each model does when shown the other's output. Say that plainly in the caption.
- Do not claim the models understood anything. The claim is that they recognise the coordinate as describing the same place.

Use a real model id in each column heading, taken from `evidence/lanes-summary.json`, and take the answers from the same file. Nothing in this figure may be invented.

## FINAL PASS — bring all four pages to the same level, then stop

The four pages were built at different times by different agents and they show it. `whales.html` was rebuilt to the full standard: 20 sections, 6 figures, the seed printed and decomposed, every section closing with a plain statement of what is remarkable. `index.html` has the structure and the figures. `proof.html` and `response.html` are the thinnest.

Bring all four to one level. Work through them together, comparing as you go, so no page is left behind:

1. **Same section rhythm.** Each of the four reads: a `hero` masthead, then sections of comparable length, each closing with a plain statement of what is remarkable or where it stops. If one page has that and another does not, fix the one that does not.

2. **Same figure density.** Count the figures per page and bring the lowest up. Every page needs a diagram for each of its central concepts, drawn in the same visual language: labelled inline SVG, annotations on the drawing, currentColor and opacity only, no hex literals.

3. **Same treatment of the seed.** All four print it in full in a `mockup-code` block and decompose it. All four show the size contrast to scale.

4. **Same register.** The high-school-teacher standard from FAILURE 0. Read the four openings side by side; the one that is least followable gets rewritten to match the best.

5. **Same components.** The same daisyUI component is used for the same job on every page, and every page ends with the same `footer footer-center` carrying the fingerprint and the four cross-links.

6. **Encoded form in chat bubbles.** A bubble shows the coordinate an agent would actually transmit, never a bare list of tick numbers. The tick list is the working and belongs in a list beneath the chat, labelled as such. Example: `⌁ se.re.ni.ko.mu·mo.ru.ki.va.ke+ru.ki.va.so.ru~ki.ro.ta`.

7. **No page may be thinner than another in kind.** Length may differ. Completeness of treatment may not.

When you have finished, `python3 scripts/11_final_pass.py --check` must report zero problems and `.venv/bin/python -m pytest tests/ -q` must pass. Report per page: byte size, section count, figure count, and the single sentence you would use to describe what that page delivers.

## FAILURE 0e — corrections. Read these before drawing the figure.

Two defects in the cross-check figure as originally specified. Both must be fixed.

### 1. The crossing arrows must never pass over text

Arrows drawn from one column to the other currently run across the bubbles and the labels, which makes both unreadable. Rules:

- Route every connector through the **gutter between the two columns**, never across a bubble, a heading, or a line of text.
- Reserve a dedicated horizontal band for the cross-over. Give it its own vertical space between turn 3 and turn 4, so the arms have somewhere to travel that contains no text at all.
- Draw the arms as elbows, not diagonals: out from the source edge into the gutter, down or up within the gutter, then into the target edge. Right-angled routes can be checked at a glance for overlap; diagonals cannot.
- Put the arrowhead on the target edge, outside the bubble.
- If a route would still cross anything, move the row, not the text. Text never moves to accommodate a line.
- Verify by rendering: no connector path may intersect a text bounding box. If the figure is inline SVG, compute the boxes and assert no intersection before finishing.

### 2. The cross-over messages must carry the narrative and the coordinate

Turn 4 is the point of the figure and its bubbles are currently bare. Each bubble must contain the actual question being asked and the actual string being handed over.

Left column, receiving the right column's answer, says:

    Where is this coordinate {right model} shared?
    ⌁ se.re.ni.ko.mu·mo.ru.ki.va.ke+ru.ki.va.so.ru~ki.ro.ta

Right column, receiving the left column's answer, says:

    Where is this coordinate {left model} shared?
    ⌁ <that model's encoded coordinate>

Substitute the real model id in place of `{model}` and the real encoded coordinate, taken from `evidence/lanes-summary.json`. The coordinate goes in the bubble in a `font-mono` span so it is legible. Put the reply beneath it in the same bubble or in the chat footer: that this is the same place, or if the pair differs, what the difference is.

Keep the label across both columns at that row: *then each is shown the other's answer*. Keep the honesty caption: separate calls, the cross-over is a reconstruction, and nothing is claimed about understanding.

### The same treatment for every chat on every page

Wherever a bubble carries a coordinate, it carries the question or statement that goes with it, not the string alone. A bubble with only a string in it is a fragment; a bubble with the sentence and the string is a message.
