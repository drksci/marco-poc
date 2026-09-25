#!/usr/bin/env python3
"""Draw the gradient: one address that can be read at whatever precision you need.

The property being drawn
-----------------------
The address is not one string. It is a *path*, and you can stop anywhere along
it. Stop early and you have a coarse place — a neighbourhood, good enough to
find someone. Keep going and it narrows to a room. Keep going and it names the
room exactly. Nothing you read at step 3 is contradicted by step 7.

That is the dynamic part, and it is why this can be read by a person. A human
does not want eighteen syllables. A human wants "somewhere in the kitchen
region", and then, if it matters, "the one with the window and a friend in it".

Two panels, both measured:
  A. refinement curve — how many distinct places survive as you read more
  B. the same place, unfolded — the literal string at each precision

Output: assets/figures/precision-gradient.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L   # noqa: E402
from marco import primer, world  # noqa: E402

FIG = ROOT / "assets" / "figures"
EVIDENCE = ROOT / "evidence"
INK, MUTED, RULE = "#111111", "#6b6b6b", "#d8d8d8"
WARM, COOL = "#b08b4f", "#5d7a55"

W, H = 1240, 700
PAD = 30


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)

    # --- A. refinement curve, measured ---
    steps = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 45]
    curve = []
    for k in steps:
        seen = {}
        for p in places:
            loc = enc.encode(world.build(p).observations(), precision=k)
            seen.setdefault(loc.prefix, []).append(p)
        curve.append({"axes": k, "distinct": len(seen),
                      "syllables": k * int((frame.partition.branches).bit_length() - 1)
                                   if False else None,
                      "groups": sorted(v for v in seen.values() if len(v) > 1)})

    # --- B. one place, unfolded ---
    target = "kitchen_with_friend"
    obs = world.build(target).observations()
    full = enc.encode(obs)
    unfold = []
    for k in (1, 2, 4, 6, 12, 45):
        loc = enc.encode(obs, precision=k)
        n_syl = len(loc.text.replace("\u2301 ", "").replace(".", "").replace("\u00b7", "")
                    .replace("+", "").replace("~", "").replace(" ", "")) // 2
        unfold.append({"axes": k, "text": loc.text, "prefix": loc.prefix[:k],
                       "prefix_len": k, "syllables": n_syl})

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
               f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">')
    out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    y = PAD + 26
    out.append(f'<text x="{PAD}" y="{y}" font-size="24" fill="{INK}" '
               f'font-family="Georgia, serif">One address, many precisions</text>')
    y += 24
    for i, ln in enumerate([
        "You do not have to read the whole thing. Stop early and you have a region; keep going and",
        "you have a room. Every step narrows. No step contradicts the one before it.",
    ]):
        out.append(f'<text x="{PAD}" y="{y + i*17}" font-size="13.5" fill="{MUTED}">{escape(ln)}</text>')
    y += 48

    # ---------- Panel B: the unfolding string ----------
    out.append(f'<text x="{PAD}" y="{y}" font-size="13" fill="{MUTED}" letter-spacing="1">'
               f'B &#183; THE SAME PLACE, READ AT SIX PRECISIONS</text>')
    y += 18
    out.append(f'<text x="{PAD}" y="{y}" font-size="12" fill="{MUTED}">'
               f'{escape(target.replace("_", " "))} &#8212; {len(world.WORLDS[target])} of 45 statements true</text>')
    y += 20
    for row in unfold:
        out.append(f'<text x="{PAD}" y="{y+9}" font-size="11.5" fill="{MUTED}">'
                   f'{row["axes"]:>2} axes</text>')
        out.append(f'<text x="{PAD+80}" y="{y+9}" font-size="14" fill="{INK}">'
                   f'{escape(row["text"])}</text>')
        out.append(f'<text x="{PAD+880}" y="{y+9}" font-size="11.5" fill="{MUTED}">'
                   f'{row["prefix_len"]} hex digits</text>')
        y += 24
    y += 8

    # ---------- Panel A: the refinement curve ----------
    out.append(f'<text x="{PAD}" y="{y}" font-size="13" fill="{MUTED}" letter-spacing="1">'
               f'A &#183; HOW MANY PLACES STILL LOOK THE SAME</text>')
    y += 26
    plot_x, plot_w = PAD + 60, W - PAD * 2 - 120
    plot_h = 190
    n = len(places)
    out.append(f'<line x1="{plot_x}" y1="{y}" x2="{plot_x}" y2="{y+plot_h}" stroke="{RULE}"/>')
    out.append(f'<line x1="{plot_x}" y1="{y+plot_h}" x2="{plot_x+plot_w}" y2="{y+plot_h}" stroke="{RULE}"/>')
    out.append(f'<text x="{PAD-4}" y="{y+8}" font-size="11" fill="{MUTED}" text-anchor="end">{n} places</text>')
    out.append(f'<text x="{PAD-4}" y="{y+plot_h}" font-size="11" fill="{MUTED}" text-anchor="end">1 place</text>')

    pts = []
    for i, row in enumerate(curve):
        x = plot_x + plot_w * i / (len(curve) - 1)
        yy = y + plot_h * (1 - (row["distinct"] - 1) / (n - 1))
        pts.append((x, yy, row))
    for a, b in zip(pts, pts[1:]):
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{COOL}" stroke-width="2"/>')
    for x, yy, row in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="4" fill="{COOL}"/>')
        out.append(f'<text x="{x:.1f}" y="{yy-10:.1f}" font-size="10.5" fill="{INK}" '
                   f'text-anchor="middle">{row["distinct"]}</text>')
        out.append(f'<text x="{x:.1f}" y="{y+plot_h+16}" font-size="10.5" fill="{MUTED}" '
                   f'text-anchor="middle">{row["axes"]}</text>')
    out.append(f'<text x="{plot_x+plot_w/2:.0f}" y="{y+plot_h+38}" font-size="11.5" fill="{MUTED}" '
               f'text-anchor="middle">axes read (1 hex digit each) &#8594; sharper</text>')
    y += plot_h + 58

    out.append(f'<text x="{PAD}" y="{y}" font-size="12" fill="{MUTED}">'
               f'Coarse reading is not a failure: it is the honest answer "somewhere in this region". '
               f'The address never claims more precision than has been read.</text>')

    out.append("</svg>")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "precision-gradient.svg").write_text("\n".join(out), encoding="utf-8")
    (EVIDENCE / "precision-gradient.json").write_text(
        json.dumps({"curve": curve, "unfold": unfold,
                    "primer_fingerprint": frame.fingerprint()},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"{'axes':>5} {'digits':>7} {'distinct places':>16}  confusable groups")
    for row in curve:
        print(f"{row['axes']:>5} {row['axes']:>7} {row['distinct']:>16}  "
              f"{[g for g in row['groups']] if row['groups'] else ''}")
    print()
    for row in unfold:
        print(f"  {row['axes']:>2} axes  {row['text']}")
    print("\nwrote assets/figures/precision-gradient.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
