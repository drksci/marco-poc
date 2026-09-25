# MARCO — where is it, though?

Two programs meet. Neither can say where it is.

Ask one and it will name a building. A building is not a place: it tells you
nothing about what the program can see, what it can reach, who is with it, or
what happens next. Every agent protocol in circulation describes the building.

This repo is a working answer to the other question. An agent answers 45 plain
yes/no statements about itself, and those answers become two objects:

```
⌁ ma.mo.ma.ma.ru·ma.me.ki.va.ki+ve.ki.va.tu.ru~ki.ru.ki     an address — fuzzy, nearby places read alike
!efe87ba9113b03473d9a657f01b994b88cd91bd0601d7131868d0bacbc6e9807...   a root   — exact, same place or nothing
```

The address says **near**. The root says **same**. Neither does the other's job,
and that separation is the design.

## What was measured

Six model families with entirely separate lineage — different training data,
different architectures, different organisations, no shared weights, no shared
embedding, no shared context, never shown each other's answers — were each shown
the same six places, one at a time, and asked which statements were true. Total
cost: **$0.05**.

| | result | control |
|---|---|---|
| Same place came out nearest | **87 / 90 (96.7%)** | 16.7% chance; 16.9% label-shuffle; 20.9% random vocabulary |
| Same root, byte-identical | **5 of 6 families** for two of the six places; 20 / 36 overall | a root is exact, not a score |
| Precision needed to name every place | **6 characters** (`⌁ ma.mo.ma`) | 1 character gives 3 groups from 6 places |
| Address ordering matches known distance | **rho = 0.9286** over all 15 pairs | shuffled null +0.0002 (sd 0.2704) |
| Solving two organisations' incompatible capability paths | **4 / 4 by nearness**, no mapping table | 1 / 4 by capability path |
| A live MARCO/POLO turn | **1 question, 1 model call, seal verified** | — |

## What it does not show

All six models were handed the same 45 statements. So this shows the frame is
usable by minds with nothing in common. It does **not** show that models with
different vocabularies would invent the same one. The models agreed on 88.8% of
their statement choices, and the addresses inherit that agreement. No claim is
made anywhere here about meaning or understanding.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # numpy only

python3 demo.py                           # the whole ladder, unrolled in one pass
python3 scripts/01_unroll.py              # the same, with every intermediate printed
python3 scripts/07_capability_nearness.py # two organisations, incompatible paths, no mapping table
python3 scripts/08_root_proof.py         # the exact root, at any grain, with folded-in attributes
python3 scripts/04_figure_lanes.py       # redraw the cross-model figure from the transcripts
python3 scripts/05_figure_gradient.py    # redraw the precision gradient
.venv/bin/python -m pytest tests/ -q      # 28 checks
python3 scripts/09_validate.py            # the validation bundle -> evidence/validation.json
python3 scripts/11_final_pass.py          # style, structure and claim checks
```

The model probe needs a key — any OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="https://<your-endpoint>/v1"
export OPENAI_API_KEY="<your-key>"
python3 scripts/02_probe_models.py --models <id> <id> <id> --jobs 4
python3 scripts/03_blind_match.py evidence/transcripts/*.jsonl --null-trials 400
python3 scripts/06_marco_polo.py --place kitchen_with_friend --hider-model <id>   # the live turn
```

`02_probe_models.py` writes every call verbatim to `evidence/transcripts/`: the
exact prompt, the exact reply, the parsed statements, latency and cost. Nothing
is post-processed away, and a failed call is recorded as a failure. Model ids
appear in the evidence; no vendor does.

## The articles

Published from this repo root. Start at `index.html`.

| file | what it is |
|---|---|
| `index.html` | the whole story, in plain language |
| `response.html` | a working response to `arXiv:2601.14567v2`, and the demonstration that solves its stated weakness |
| `proof.html` | how far this can be proved rather than asserted, and where proof stops |
| `whales.html` | mapping whale vocalisation structure onto the same geometry, and what a predictive mapping would require |
| `notes/whale-topologies.md` | the longer source note behind `whales.html` |
| `notes/transcript-excerpts.md` | every verbatim prompt and reply quoted on the site |
| `notes/style-references.md` | the two published style references applied, and how |

## Layout

```
primer.seed.json        the entire shared substrate: 3,300 bytes
marco/
  primer.py             seed -> frame. Landmarks, codebook, ladder, and an axis
                        order that is derived rather than transmitted
  locus.py              statements -> address. Distance vector, calibrated
                        partition, Gray-coded syllables, four-beat rendering
  world.py              the six places, in words anyone can read, plus every
                        place one answer away from each
  generator.py          the seed that asks its own questions. Holds no
                        questions and no situations
  assignment.py         Kuhn-Munkres, for the optimal one-to-one matching
scripts/                one script per result, each with its own docstring
evidence/               every number, including the failures
assets/
  site.css              component layer, shadcn/ui token contract
  viz.js                five interactive D3 views
  data.json             the data they bind to
  figures/              generated SVG, every value read from evidence/
```

## Two bugs worth keeping

Both are real, both were found by running the thing, and both are still in the
record because they are more instructive than a clean first attempt.

**The generator stalled with two candidates left.** It chose questions by
information gain, and a perfectly discriminating 1-vs-1 split has *zero*
information gain — both outcomes were already equally likely. So it asked
nothing, forever. Fixed by maximising `pos x neg`, which minimises the expected
number of survivors and behaves correctly at every n. Before: 0 questions, 0
resolutions. After: 64 of 64, mean 17.8 questions against a log2(204) = 7.67
floor.

**Reasoning models returned an empty string.** The completion budget was too
small; reasoning tokens consumed it and `finish_reason` came back as `length`
with empty content. The first probe recorded four "answers" that were an empty
string before this was spotted.

## The rule this repo is organised around

> In a space like this, the metric is more likely to be wrong than the model.

Every number here carries a null with the same information content, a
known-answer case whose result is already known, and a sweep of whatever
threshold was chosen. Where a measurement disagreed with the expectation that
was written down beforehand, the disagreement is reported rather than retuned.

Primer fingerprint: `df2f8b9972c40bfdd132366a58b4780f65f23feba1ef20a060c25d4eff2661ba`
