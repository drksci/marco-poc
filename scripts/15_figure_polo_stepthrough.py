#!/usr/bin/env python3
"""The MARCO/POLO exchange as an annotated grid.

Column per participant. Row per turn. Inside each row, three sub-rows: what was
literally said, the same thing in plain English, and what changed in the
computation.

The far-right column carries the only number that matters at each step: how many
places are still consistent with everything disclosed so far. It starts knowing
nothing, and it ends at one.

Every string in the grid is copied out of `evidence/marco-polo.json`. Every
count is recomputed here from the primer.

Output: assets/figures/polo-stepthrough.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

INK, MUTED, RULE, GRID = "#16161a", "#74747e", "#e2e2e6", "#f4f4f5"
HIDER, HIDER_SOFT = "#3f6b52", "#eaf0eb"
SEEKER, SEEKER_SOFT = "#9a6f2f", "#f8f2e6"
GEO, GEO_SOFT = "#3a4a6b", "#eef0f6"

W = 1280
PAD = 28
COL_LABEL = 118                      # turn number + label
COL_W = 296                          # three participant columns
STATE_W = 152
SUB = 30                             # sub-row height
SUB_SMALL = 22
GAP = 14


def wrap(text, cols, limit=4):
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > cols and line:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    if len(lines) > limit:
        lines = lines[:limit]
        lines[-1] = lines[-1][:cols - 1] + "\u2026"
    return lines


def main() -> int:
    p = json.loads((ROOT / "evidence" / "marco-polo.json").read_text())
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {n: enc.encode(world.build(n).observations()) for n in places}
    target = p["place_under_test"]
    steps = list(p["disclosure_steps"])

    # ---- build the turns -------------------------------------------------
    turns = []

    k0 = steps[0]
    d0 = enc.encode(world.build(target).observations(), precision=k0)
    fits0 = [n for n in places if loci[n].prefix[:k0] == d0.prefix[:k0]]
    turns.append({
        "label": "opens",
        "hider": [f'MARCO  "{d0.text}"', f"{k0} of {len(frame.partition.axes)} axes", "nothing else offered"],
        "seeker": ["waits", "the opening is a bearing, not an answer", ""],
        "geo": [f"prefix[:{k0}] = {escape(d0.prefix[:k0])}",
                f"{len(fits0)} of {len(places)} places share it",
                "no question spent yet"],
        "count": len(fits0),
    })

    seen = 1
    for ev in p["trace"]:
        if ev["kind"] == "answer":
            truth = [n for n in places if (ev["statement"] in world.WORLDS[n]) == ev["answer"]]
            turns.append({
                "label": "asks",
                "hider": [f'"{ev["question"]}"', "answered from the place it is in",
                          f'replied {ev["raw"]!r}'.replace("'", '"')],
                "seeker": [f'"{ev["question"]}"', "the one question with the most even split",
                           "chosen by the primer, not by the model"],
                "geo": [f'statement {ev["statement"]}',
                        f'is it true here? {ev["answer"]}',
                        f'keeps {len(truth)} of {len(places)}'],
                "count": len(truth),
            })
        elif ev["kind"] == "disclosure" and seen < len(steps):
            k = ev["axes"]
            fits = [n for n in places if loci[n].prefix[:k] == ev["prefix"]]
            turns.append({
                "label": "widens",
                "hider": [f'MARCO  "{ev["address"]}"', f"now {k} of {len(frame.partition.axes)} axes",
                          "still not naming the place"],
                "seeker": ["narrows", f"{len(fits)} place(s) left", ""],
                "geo": [f"prefix[:{k}] = {ev['prefix'][:k]}",
                        f"{len(fits)} of {len(places)} places",
                        "arithmetic on the address"],
                "count": len(fits),
            })
            seen += 1

    full = loci[target]
    turns.append({
        "label": "names it",
        "hider": ["says nothing yet", "has not named the place at any point", ""],
        "seeker": [f'"you are in {target.replace("_", " ")}"',
                   "rebuilds the address itself from the statements",
                   "does not take the hider's word"],
        "geo": ["recompute root from the statements",
                f"!{full.commitment[:24]}",
                "compare with the hider's root"],
        "count": 1,
    })
    turns.append({
        "label": "checks",
        "hider": [f'!{full.commitment[:28]}', "the seal it holds", f'{p["hider_calls"]} model call'],
        "seeker": [f'POLO  {p["verdict"]}', "equal or not equal. no threshold",
                   f'{p["questions_asked"]} question spent'],
        "geo": ["sha256 over {statements, extra}",
                "one hashing rule for the whole project",
                "adjacency deliberately destroyed"],
        "count": 1,
    })

    # ---- geometry --------------------------------------------------------
    x_label = PAD
    x_hider = x_label + COL_LABEL
    x_seeker = x_hider + COL_W + GAP
    x_geo = x_seeker + COL_W + GAP
    x_state = x_geo + COL_W + GAP
    row_h = lambda t: SUB + 3 * SUB_SMALL + 12
    H = 172 + sum(row_h(t) for t in turns) + 96

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+24}" font-size="22" fill="{INK}" '
        f'font-family="Georgia, serif">One exchange, broken down</text>',
        f'<text x="{PAD}" y="{PAD+48}" font-size="12.5" fill="{MUTED}">'
        f'A column per participant, a row per turn, and under each turn the same thing three ways: '
        f'what was said, what it means, and what it changed.</text>',
        f'<text x="{PAD}" y="{PAD+68}" font-size="12.5" fill="{MUTED}">'
        f'The hider is {escape(p["hider_model"])}, told which place it is in and never asked to name '
        f'it. The seeker owns the geometry and decides which question to spend.</text>',
        f'<text x="{PAD}" y="{PAD+88}" font-size="12.5" fill="{MUTED}">'
        f'The opening is one syllable. Everything after it is earned: '
        f'{p["questions_asked"]} question, {p["hider_calls"]} model call.</text>',
    ]

    # ---- header ----------------------------------------------------------
    hy = 146
    heads = [
        (x_hider, "HIDER", f"a model, {p['hider_model']}", HIDER),
        (x_seeker, "SEEKER", "owns the geometry", SEEKER),
        (x_geo, "WHAT IT CHANGES", "arithmetic on the primer", GEO),
        (x_state, "PLACES", "still possible", MUTED),
    ]
    for x, name, sub, colour in heads:
        width = STATE_W if x == x_state else COL_W
        out.append(f'<rect x="{x}" y="{hy-24}" width="{width}" height="44" rx="5" '
                   f'fill="{GRID}" stroke="{RULE}"/>')
        out.append(f'<text x="{x+12}" y="{hy-6}" font-size="11.5" fill="{colour}" '
                   f'font-weight="bold">{escape(name)}</text>')
        out.append(f'<text x="{x+12}" y="{hy+10}" font-size="9.5" fill="{MUTED}">'
                   f'{escape(sub)}</text>')

    # ---- rows ------------------------------------------------------------
    y = hy + 34
    for i, t in enumerate(turns):
        h = row_h(t)
        if i % 2 == 0:
            out.append(f'<rect x="{PAD}" y="{y}" width="{W-2*PAD}" height="{h}" fill="#fbfbfc"/>')

        # turn label
        out.append(f'<text x="{x_label}" y="{y+24}" font-size="11" fill="{MUTED}">'
                   f'TURN {i}</text>')
        out.append(f'<text x="{x_label}" y="{y+40}" font-size="12.5" fill="{INK}" '
                   f'font-weight="bold">{escape(t["label"])}</text>')

        # three participant cells, each with the same three sub-rows
        for x, key, soft, edge in ((x_hider, "hider", HIDER_SOFT, HIDER),
                                   (x_seeker, "seeker", SEEKER_SOFT, SEEKER),
                                   (x_geo, "geo", GEO_SOFT, GEO)):
            out.append(f'<rect x="{x}" y="{y+6}" width="{COL_W}" height="{h-16}" rx="5" '
                       f'fill="{soft}" stroke="{edge}" opacity="0.55"/>')
            for sub_i, (sub_label, line) in enumerate(zip(
                    ("said", "meaning", "changed"), t[key])):
                ly = y + 24 + sub_i * SUB_SMALL
                out.append(f'<text x="{x+10}" y="{ly}" font-size="8.5" fill="{MUTED}">'
                           f'{escape(sub_label.upper())}</text>')
                for k, wl in enumerate(wrap(line, 40, limit=1)):
                    size = 12 if sub_i == 0 else 10.5
                    colour = INK if sub_i == 0 else MUTED
                    out.append(f'<text x="{x+52}" y="{ly+k*12}" font-size="{size}" '
                               f'fill="{colour}">{escape(wl)}</text>')

        # the state column
        frac = t["count"] / len(places) if t["count"] else 0
        out.append(f'<rect x="{x_state}" y="{y+22}" width="{STATE_W}" height="22" rx="4" '
                   f'fill="{GRID}"/>')
        if t["count"]:
            out.append(f'<rect x="{x_state}" y="{y+22}" width="{STATE_W*frac:.0f}" height="22" '
                       f'rx="4" fill="{HIDER}" opacity="0.8"/>')
        else:
            out.append(f'<rect x="{x_state}" y="{y+22}" width="{STATE_W}" height="22" rx="4" '
                       f'fill="{HIDER}"/>')
        txt = f'{t["count"]} of {len(places)}' if t["count"] else "sealed"
        out.append(f'<text x="{x_state+10}" y="{y+38}" font-size="12" fill="#ffffff" '
                   f'font-weight="bold">{escape(txt)}</text>')
        out.append(f'<text x="{x_state}" y="{y+h-18}" font-size="9.5" fill="{MUTED}">'
                   f'{"candidate set" if i else "no information yet"}</text>')

        y += h

    # ---- footer ----------------------------------------------------------
    fy = y + 26
    out.append(f'<line x1="{PAD}" y1="{fy-14}" x2="{W-PAD}" y2="{fy-14}" stroke="{RULE}"/>')
    out.append(f'<text x="{PAD}" y="{fy+8}" font-size="12.5" fill="{INK}">'
               f'The opening is {steps[0]} of {len(frame.partition.axes)} axes, and '
               f'{len(fits0)} of {len(places)} places still fit. One question takes it to two.</text>')
    out.append(f'<text x="{PAD}" y="{fy+28}" font-size="12.5" fill="{MUTED}">'
               f'The seeker never accepted the hider\'s word for the place. It rebuilt the address '
               f'from the statements and compared the root: {escape(p["verdict"])}.</text>')
    out.append(f'<text x="{PAD}" y="{fy+48}" font-size="12.5" fill="{MUTED}">'
               f'A name would have been a claim. A root is a check, and it costs nothing to run.</text>')
    out.append("</svg>")

    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "polo-stepthrough.svg").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote assets/figures/polo-stepthrough.svg ({W}x{H}) with {len(turns)} turns")
    for t in turns:
        print(f"  {t['label']:<9} places={t['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
