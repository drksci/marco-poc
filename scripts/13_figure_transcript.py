#!/usr/bin/env python3
"""The MARCO/POLO turn as a vertical transcript. Turn by turn, nothing skipped.

Two lanes down the page: the hider on the left, the seeker on the right. Every
bubble is the literal text of that turn, taken from `evidence/marco-polo.json`.
A column on the far right shows how many places are still possible after each
turn, so the collapse is visible as you read down.

The hider is a real model. It was told which place it was in, in plain English,
and was never asked to name it. The seeker owns the geometry and decides which
question is worth spending.

Output: assets/figures/marco-polo-transcript.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

INK, MUTED, RULE = "#16161a", "#74747e", "#e2e2e6"
HIDER, SEEKER = "#3f6b52", "#9a6f2f"
HIDER_SOFT, SEEKER_SOFT = "#eaf0eb", "#f8f2e6"
GRID = "#f4f4f5"

W = 1120
LEFT_LANE, RIGHT_LANE = 60, 600
BUBBLE_W = 470
PAD = 30
TOP = 132
ROW = 96
BOTTOM = 210


def wrap(text: str, cols: int, max_lines: int = 6) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > cols and line:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: cols - 1] + "\u2026"
    return lines


def main() -> int:
    p = json.loads((ROOT / "evidence" / "marco-polo.json").read_text())
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {n: enc.encode(world.build(n).observations()) for n in places}
    target = p["place_under_test"]

    # A turn list: (lane, label, lines, candidate count)
    turns: list[tuple[str, str, list[str], int]] = []

    # opening disclosure
    first_axes = p["disclosure_steps"][0]
    d0 = enc.encode(world.build(target).observations(), precision=first_axes)
    fits0 = [n for n in places if loci[n].prefix[:first_axes] == d0.prefix[:first_axes]]
    turns.append(("hider", "opens with one syllable", [f'MARCO   "{d0.text}"',
                  f"{first_axes} of {len(frame.partition.axes)} axes disclosed"], len(fits0)))

    # then each recorded turn
    seen_disclosures = 1
    for ev in p["trace"]:
        if ev["kind"] == "answer":
            n_after = sum(1 for n in places
                          if (ev["statement"] in world.WORLDS[n]) == ev["answer"])
            turns.append(("seeker", "asks one yes/no question",
                          [f'"{ev["question"]}"', f'hider answers  {ev["raw"]!r}'.replace("'", '"')],
                          n_after))
        elif ev["kind"] == "disclosure" and seen_disclosures < len(p["disclosure_steps"]):
            k = ev["axes"]
            fits = [n for n in places if loci[n].prefix[:k] == ev["prefix"]]
            turns.append(("hider", f"releases {k} axes",
                          [f'MARCO   "{ev["address"]}"', f"{len(fits)} of {len(places)} places still fit"],
                          len(fits)))
            seen_disclosures += 1

    # the catch
    turns.append(("seeker", "names it, then checks the seal",
                  ["\"you are in " + target.replace("_", " ") + "\"",
                   "rebuilds the address itself, compares the root"], 1))
    turns.append(("hider", "seal",
                  [f'!{enc.encode(world.build(target).observations()).commitment[:44]}',
                   f"POLO  {p['verdict']}   \u00b7   {p['hider_calls']} model call   \u00b7   "
                   f"${p['cost_usd']:.6f}"], 0))

    H = TOP + ROW * len(turns) + BOTTOM
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+24}" font-size="22" fill="{INK}" '
        f'font-family="Georgia, serif">One turn, from one syllable</text>',
        f'<text x="{PAD}" y="{PAD+48}" font-size="12.5" fill="{MUTED}">'
        f'The hider is {escape(p["hider_model"])}, told which place it is in and never asked to '
        f'name it. The seeker owns the geometry.</text>',
        f'<text x="{PAD}" y="{PAD+68}" font-size="12.5" fill="{MUTED}">'
        f'Left lane: what the hider disclosed. Right lane: what the seeker spent. '
        f'Far right: places still possible.</text>',
        f'<text x="{PAD}" y="{PAD+88}" font-size="12.5" fill="{MUTED}">'
        f'Every bubble is the literal text of that turn, from evidence/marco-polo.json.</text>',
        # lane headers
        f'<line x1="{LEFT_LANE}" y1="{TOP-14}" x2="{LEFT_LANE}" y2="{H-BOTTOM+30}" '
        f'stroke="{RULE}" stroke-dasharray="3 4"/>',
        f'<line x1="{RIGHT_LANE}" y1="{TOP-14}" x2="{RIGHT_LANE}" y2="{H-BOTTOM+30}" '
        f'stroke="{RULE}" stroke-dasharray="3 4"/>',
        f'<text x="{PAD}" y="{TOP-28}" font-size="11" fill="{HIDER}">HIDER \u2014 a model</text>',
        f'<text x="{RIGHT_LANE+BUBBLE_W-40}" y="{TOP-28}" font-size="11" fill="{SEEKER}" '
        f'text-anchor="end">SEEKER \u2014 the geometry</text>',
        f'<text x="{W-PAD}" y="{TOP-28}" font-size="11" fill="{MUTED}" '
        f'text-anchor="end">PLACES POSSIBLE</text>',
    ]

    y = TOP - 4
    for i, (lane, label, lines, count) in enumerate(turns):
        x = LEFT_LANE if lane == "hider" else RIGHT_LANE
        soft = HIDER_SOFT if lane == "hider" else SEEKER_SOFT
        edge = HIDER if lane == "hider" else SEEKER
        lines = sum((wrap(l, 60) or [""] for l in lines), [])
        h = 26 + 16 * len(lines)
        out.append(f'<rect x="{x}" y="{y}" width="{BUBBLE_W}" height="{h}" rx="8" '
                   f'fill="{soft}" stroke="{edge}"/>')
        out.append(f'<text x="{x+14}" y="{y+18}" font-size="10" fill="{edge}">'
                   f'{escape(label.upper())}</text>')
        for k, line in enumerate(lines):
            size = 13 if k == 0 else 10.5
            colour = INK if k == 0 else MUTED
            out.append(f'<text x="{x+14}" y="{y+38+k*16}" font-size="{size}" '
                       f'fill="{colour}">{escape(line)}</text>')

        # the narrowing column
        cx, cw = W - PAD - 250, 250
        out.append(f'<rect x="{cx}" y="{y+8}" width="{cw}" height="20" rx="4" fill="{GRID}"/>')
        if count:
            out.append(f'<rect x="{cx}" y="{y+8}" width="{cw*count/len(places):.0f}" '
                       f'height="20" rx="4" fill="{HIDER}" opacity="0.8"/>')
        else:
            out.append(f'<rect x="{cx}" y="{y+8}" width="{cw}" height="20" rx="4" '
                       f'fill="{HIDER}"/>')
        label_txt = f"{count} of {len(places)}" if count else f"seal matches"
        out.append(f'<text x="{cx+10}" y="{y+23}" font-size="11.5" fill="#ffffff" '
                   f'font-weight="bold">{escape(label_txt)}</text>')

        # connector between lanes
        if i:
            mx = (LEFT_LANE + BUBBLE_W + RIGHT_LANE) / 2 if lane == "seeker" else \
                 (RIGHT_LANE + BUBBLE_W + LEFT_LANE) / 2
            out.append(f'<path d="M {mx:.0f} {y-10} L {mx:.0f} {y-2}" stroke="{RULE}" '
                       f'stroke-width="1.2"/>')
        y += h + 22

    fy = H - BOTTOM + 40
    out.append(f'<line x1="{PAD}" y1="{fy-16}" x2="{W-PAD}" y2="{fy-16}" stroke="{RULE}"/>')
    out.append(f'<text x="{PAD}" y="{fy+6}" font-size="12.5" fill="{INK}">'
               f'The opening is one syllable. That is {first_axes} of {len(frame.partition.axes)} axes, '
               f'and {len(fits0)} of {len(places)} places still fit.</text>')
    out.append(f'<text x="{PAD}" y="{fy+26}" font-size="12.5" fill="{MUTED}">'
               f'Everything after it was earned: {p["questions_asked"]} question, '
               f'{p["hider_calls"]} model call, ${p["cost_usd"]:.6f}. The seeker never accepted the '
               f'hider\'s word for the place.</text>')
    out.append(f'<text x="{PAD}" y="{fy+46}" font-size="12.5" fill="{MUTED}">'
               f'It rebuilt the address from the statements and compared the root. '
               f'{escape(p["verdict"])}.</text>')
    out.append("</svg>")

    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "marco-polo-transcript.svg").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote assets/figures/marco-polo-transcript.svg ({W}x{H}) with {len(turns)} turns")
    for lane, label, lines, count in turns:
        print(f"  {lane:<7} {label:<30} -> {count} places")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
