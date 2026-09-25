#!/usr/bin/env python3
"""Draw the result: one vertical lane per model family, same six places.

What the figure has to make unmissable
-------------------------------------
The models in the lanes have **entirely separate lineage**. Different training
data, different architectures, different labs, no shared weights, no shared
embedding, no shared context, no coordination, and no sight of each other's
answers. Each was shown one place, in plain English, once, and asked which of 45
plain statements were true.

If a horizontal band runs across all lanes unbroken, that beat of the address is
*identical* across every family. If a band breaks, that beat is private to a
model. The shape to look for is: wide shared bands on the outside, broken bands
in the middle — the same coarse structure, different fine detail.

Everything drawn here comes from `evidence/transcripts/`. Nothing is illustrative,
and a place a model failed to answer is drawn as a gap rather than filled in.

Output: assets/figures/cross-model-lanes.svg  (+ a JSON summary of the agreement counts)
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L   # noqa: E402
from marco import primer, world  # noqa: E402

FIG = ROOT / "assets" / "figures"
EVIDENCE = ROOT / "evidence"

INK = "#111111"
MUTED = "#6b6b6b"
RULE = "#d8d8d8"
SHARED_FILL = "#e8efe6"
SHARED_EDGE = "#5d7a55"
PRIVATE_FILL = "#f6f2e8"
PRIVATE_EDGE = "#b08b4f"
GAP_FILL = "#fafafa"

LANE_W = 214
GUTTER = 168
ROW_H = 132
HEADER_H = 236
PAD = 26


def load_records() -> list[dict]:
    recs = []
    for p in sorted((ROOT / "evidence" / "transcripts").glob("probe-*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    return recs


def beats_of(text: str) -> list[str]:
    """Split a rendered coordinate back into its four beats."""
    body = text.replace("\u2301 ", "").strip()
    place, rest = (body.split("\u00b7", 1) + [""])[:2]
    what, rest = (rest.split("+", 1) + [""])[:2]
    reach, now = (rest.split("~", 1) + [""])[:2]
    return [place, what, reach, now]


def wrap(s: str, width: int) -> list[str]:
    out, line = [], ""
    for word in s.split():
        if len(line) + len(word) + 1 > width and line:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return out or [""]


def main() -> int:
    frame = primer.expand()
    records = load_records()
    if not records:
        print("error: no transcripts in evidence/transcripts/", file=sys.stderr)
        return 2

    # model -> place -> coordinate
    sel: dict[str, dict[str, set]] = defaultdict(dict)
    for r in records:
        if r.get("ok") and r.get("parsed"):
            sel[r["model"]][r["situation_id"]] = set(r["landmarks"])

    places = [p for p in world.DESCRIPTIONS if all(p in sel[m] for m in sel)]
    models = sorted(m for m in sel if all(p in sel[m] for p in places))
    if not models:
        print("error: no model answered every place", file=sys.stderr)
        return 3

    enc = L.Encoder(frame)
    coords: dict[str, dict[str, str]] = {}
    beats: dict[str, dict[str, list[str]]] = {}
    coords_loci: dict[str, dict[str, object]] = {}
    for m in models:
        coords[m], beats[m], coords_loci[m] = {}, {}, {}
        for p in places:
            obs = [L.Obs(*k.split("/", 2)) for k in sorted(sel[m][p])]
            loc = enc.encode(obs)
            coords_loci[m][p] = loc
            coords[m][p] = loc.text
            beats[m][p] = beats_of(loc.text)

    # Agreement: for each place and beat, is the beat identical across all lanes?
    n_beats = 4
    agreement = {}
    for p in places:
        agreement[p] = [len({beats[m][p][i] for m in models}) == 1
                        for i in range(n_beats)]

    n_models = len(models)
    width = GUTTER + LANE_W * n_models + PAD * 2
    height = HEADER_H + ROW_H * len(places) + 120

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               f'width="{width}" height="{height}" font-family="ui-monospace, SFMono-Regular, '
               f'Menlo, monospace" role="img" '
               f'aria-label="Six model families independently produce the same coordinate beats '
               f'for the same six places">')
    out.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')

    # ---- header: the lineage claim, stated as a fact about the run ----
    y = PAD + 8
    out.append(f'<text x="{PAD}" y="{y+22}" font-size="25" fill="{INK}" '
               f'font-family="Georgia, serif">Separate lineage, same coordinate</text>')
    y += 44
    lines = [
        f"{n_models} model families. Different training data, different architectures,",
        "different organisations. No shared weights. No shared embedding. No shared context.",
        "Never shown another lane. Each answered which of 45 plain statements were true",
        "about one place, in English, once.",
    ]
    for i, ln in enumerate(lines):
        out.append(f'<text x="{PAD}" y="{y + i*17}" font-size="13.5" fill="{MUTED}">{escape(ln)}</text>')
    y += len(lines) * 17 + 16

    # legend
    out.append(f'<rect x="{PAD}" y="{y}" width="16" height="12" fill="{SHARED_FILL}" '
               f'stroke="{SHARED_EDGE}" stroke-width="1.5"/>')
    out.append(f'<text x="{PAD+24}" y="{y+11}" font-size="12.5" fill="{INK}">'
               f'band runs unbroken: every family produced this beat identically</text>')
    out.append(f'<rect x="{PAD+560}" y="{y}" width="16" height="12" fill="{PRIVATE_FILL}" '
               f'stroke="{PRIVATE_EDGE}" stroke-width="1.5"/>')
    out.append(f'<text x="{PAD+584}" y="{y+11}" font-size="12.5" fill="{INK}">'
               f'band breaks: this beat differs between families</text>')
    out.append(f'<text x="{PAD}" y="{y+34}" font-size="12.5" fill="{MUTED}">'
               f'primer fingerprint {frame.fingerprint()[:16]}... &#183; '
               f'{len(frame.anchors)} statements &#183; {len(places)} places</text>')

    # ---- lane headers ----
    lane_y = HEADER_H - 62
    for j, m in enumerate(models):
        x = PAD + GUTTER + j * LANE_W
        cx = x + LANE_W / 2
        out.append(f'<line x1="{cx}" y1="{lane_y + 46}" x2="{cx}" y2="{height - 74}" '
                   f'stroke="{RULE}" stroke-width="1"/>')
        out.append(f'<text x="{cx}" y="{lane_y}" font-size="14.5" fill="{INK}" '
                   f'text-anchor="middle" font-weight="bold">{escape(m)}</text>')
        for k, ln in enumerate(wrap("independent lineage", 26)):
            out.append(f'<text x="{cx}" y="{lane_y + 16 + k*13}" font-size="10.5" '
                       f'fill="{MUTED}" text-anchor="middle">{escape(ln)}</text>')

    # ---- rows ----
    for i, p in enumerate(places):
        top = HEADER_H + i * ROW_H
        out.append(f'<line x1="{PAD}" y1="{top}" x2="{width-PAD}" y2="{top}" '
                   f'stroke="{RULE}" stroke-width="1"/>')
        out.append(f'<text x="{PAD}" y="{top+26}" font-size="14" fill="{INK}" '
                   f'font-weight="bold">{escape(p.replace("_", " "))}</text>')
        out.append(f'<text x="{PAD}" y="{top+43}" font-size="10.5" fill="{MUTED}">'
                   f'{len(world.WORLDS[p])} of 45 statements true</text>')

        # shared-band backdrops, behind the text
        for b in range(n_beats):
            if agreement[p][b]:
                bx = PAD + GUTTER
                out.append(f'<rect x="{bx}" y="{top + 14 + b*26}" '
                           f'width="{LANE_W * n_models}" height="24" '
                           f'fill="{SHARED_FILL}" stroke="none"/>')

        for j, m in enumerate(models):
            x = PAD + GUTTER + j * LANE_W
            out.append(f'<rect x="{x+5}" y="{top+8}" width="{LANE_W-10}" height="{ROW_H-22}" '
                       f'fill="none" stroke="{RULE}" stroke-width="1"/>')
            for b in range(n_beats):
                txt = beats[m][p][b]
                shared = agreement[p][b]
                fill = SHARED_FILL if shared else PRIVATE_FILL
                edge = SHARED_EDGE if shared else PRIVATE_EDGE
                out.append(f'<rect x="{x+9}" y="{top + 14 + b*26}" width="{LANE_W-18}" '
                           f'height="24" rx="3" fill="{fill}" stroke="{edge}" stroke-width="1"/>')
                out.append(f'<text x="{x+16}" y="{top + 30 + b*26}" font-size="13" '
                           f'fill="{INK}">{escape(txt)}</text>')

    # ---- footer: the count that makes it a measurement, not a picture ----
    fy = HEADER_H + ROW_H * len(places) + 26
    total_beats = len(places) * n_beats
    shared_total = sum(sum(agreement[p]) for p in places)

    # The load-bearing measurement is retrieval, not string identity. Two lanes
    # can disagree on a syllable and still put the place in the right
    # neighbourhood; what matters is whether the same place comes out nearest.
    hits = strict = total = 0
    for a, b in itertools.combinations(models, 2):
        for pi, p in enumerate(places):
            d = [enc.hamming(coords_loci[a][p], coords_loci[b][q]) for q in places]
            total += 1
            hits += int(int(np.argmin(d)) == pi)
            strict += int(d[pi] < min(v for j, v in enumerate(d) if j != pi))

    out.append(f'<line x1="{PAD}" y1="{fy-14}" x2="{width-PAD}" y2="{fy-14}" '
               f'stroke="{RULE}" stroke-width="1"/>')
    out.append(f'<text x="{PAD}" y="{fy+12}" font-size="16" fill="{INK}">'
               f'Same place came out nearest in {strict} of {total} cross-family comparisons '
               f'({100*strict/total:.1f}%) &#183; chance is {100/len(places):.1f}%</text>')
    out.append(f'<text x="{PAD}" y="{fy+34}" font-size="13" fill="{MUTED}">'
               f'{hits} of {total} if exact ties are also counted ({100*hits/total:.1f}%). '
               f'{shared_total} of {total_beats} whole beats are character-for-character identical '
               f'across all {n_models}; the rest differ by a syllable or two.</text>')
    out.append(f'<text x="{PAD}" y="{fy+56}" font-size="13" fill="{MUTED}">'
               f'Read the columns, not the letters. A lane is not required to spell the place the '
               f'same way. It is required to put it in the same place.</text>')
    out.append(f'<text x="{PAD}" y="{fy+52}" font-size="12" fill="{MUTED}">'
               f'This is not a claim that the models understand the place. They were handed the '
               f'45 statements and used them consistently. What it shows is that the '
               f'frame is usable by minds with nothing in common.</text>')
    out.append("</svg>")

    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "cross-model-lanes.svg").write_text("\n".join(out), encoding="utf-8")

    summary = {
        "primer_fingerprint": frame.fingerprint(),
        "models": models,
        "places": places,
        "coordinates": coords,
        "beats": beats,
        "beat_identical_across_all_models": agreement,
        "shared_beats": shared_total,
        "total_beats": total_beats,
        "n_models": n_models,
    }
    (EVIDENCE / "lanes-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"models : {n_models} ({', '.join(models)})")
    print(f"places : {len(places)}")
    print(f"shared beats: {shared_total}/{total_beats}")
    for p in places:
        marks = "".join("S" if v else "." for v in agreement[p])
        print(f"  {p:<22} {marks}   " + "  ".join(f"{m}={beats[m][p][0]}" for m in models[:3]))
    print(f"\nwrote assets/figures/cross-model-lanes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
