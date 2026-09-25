#!/usr/bin/env python3
"""Why agreement is possible at all: a shared manifold, and a chart laid over it.

The claim this figure exists to make
------------------------------------
Six model families were built by different organisations, on different data,
with different architectures. No shared weights, no shared embedding, no shared
context, and none of them saw another's answer. Their coordinates for the same
place still landed nearest each other in 87 of 90 comparisons.

A shared vocabulary cannot be the whole explanation. Handing someone a list of
45 questions tells them what to answer with; it does not tell them what the
answers mean, and it does not make two different systems place the same
situation in the same part of their own space. If that were all that was
happening, the addresses would be arbitrary but consistent, like two people
agreeing to call a colour "seven".

What the result implies is stronger. Situations appear to occupy a structure
that independently trained systems have in common, and the primer is a *chart*
laid over that structure rather than a substitute for it. A chart is how you
give names to places on a surface you did not build. Two cartographers using the
same grid will label the same mountain the same way, and that agreement is only
informative because the mountain was there first.

The two halves are different kinds of thing, and this figure keeps them apart:

    the manifold   shared, emergent, not ours. We did not build it and we
                   cannot see it directly. Its existence is inferred from the
                   fact that independent systems agree.
    the chart      ours, published, small. 45 statements, a codebook, an
                   ordering. It is what makes the shared structure addressable,
                   comparable and provable.

The parent project reached the same conclusion and recorded it, then corrected
itself on the follow-up question: the manifold is shared, and the chart is
shared too, *when the states are unambiguous*. When states are ambiguous the
charts diverge again. That distinction is why the six places here are described
in such plain, concrete English.

Output: assets/figures/shared-manifold.svg
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
SIGNAL, SIGNAL_SOFT = "#3f6b52", "#eaf0eb"
WARM, WARM_SOFT = "#9a6f2f", "#f8f2e6"
BLUE, BLUE_SOFT = "#3a4a6b", "#eef0f6"

W, H = 1220, 900
PAD = 30


def surface(cx, cy, w, h, rows=7, cols=9, colour=RULE, fill=None):
    """A curved surface drawn as a wireframe: a manifold, seen from the side."""
    out = []
    if fill:
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2:.0f}" ry="{h/2:.0f}" '
                   f'fill="{fill}" stroke="none"/>')
    for i in range(rows):
        t = i / (rows - 1)
        y = cy - h / 2 + t * h
        curve = (1 - (2 * t - 1) ** 2) * h * 0.16
        out.append(f'<path d="M {cx-w/2:.0f} {y:.0f} Q {cx:.0f} {y+curve:.0f} '
                   f'{cx+w/2:.0f} {y:.0f}" fill="none" stroke="{colour}" stroke-width="1"/>')
    for j in range(cols):
        t = j / (cols - 1)
        x = cx - w / 2 + t * w
        sag = (1 - (2 * t - 1) ** 2) * h * 0.16
        out.append(f'<path d="M {x:.0f} {cy-h/2:.0f} Q {x:.0f} {cy+sag:.0f} '
                   f'{x:.0f} {cy+h/2:.0f}" fill="none" stroke="{colour}" stroke-width="1"/>')
    return out


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {p: enc.encode(world.build(p).observations()) for p in places}

    # the recorded cross-family result, for the caption
    res = json.loads((ROOT / "evidence" / "RESULTS.json").read_text())
    cm = res["cross_model"]

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+22}" font-size="21" fill="{INK}" '
        f'font-family="Georgia, serif">A shared manifold, and a chart laid over it</text>',
        f'<text x="{PAD}" y="{PAD+44}" font-size="12" fill="{MUTED}">'
        f'Six families, {cm["n_models"]} independent systems, no shared weights and no shared '
        f'context: the same place came out nearest in '
        f'{cm["top1_strict"]*100:.1f}% of {cm["comparisons"]} comparisons.</text>',
    ]

    # ---- the three surfaces, and the same chart over each ----
    surf_y = 300
    specs = [
        ("family A", SIGNAL, SIGNAL_SOFT, 0.0),
        ("family B", BLUE, BLUE_SOFT, 0.9),
        ("family C", WARM, WARM_SOFT, 1.8),
    ]
    sw, sh = 340, 150
    for i, (name, colour, soft, phase) in enumerate(specs):
        cx = PAD + 60 + i * 400 + sw / 2 - 60
        o += surface(cx, surf_y, sw, sh, colour=colour, fill=None)
        o.append(f'<text x="{cx}" y="{surf_y - sh/2 - 26}" font-size="12.5" fill="{colour}" '
                 f'text-anchor="middle" font-weight="bold">{escape(name)}</text>')
        o.append(f'<text x="{cx}" y="{surf_y - sh/2 - 10}" font-size="10" fill="{MUTED}" '
                 f'text-anchor="middle">a different space, never compared</text>')

        # the same six places, charted on each surface at the same relative spots,
        # with a slight shear per family so the surfaces are visibly different
        for k, p in enumerate(places):
            fx = (k % 3) / 2 - 0.5
            fy = (k // 3) / 1 - 0.5
            px = cx + fx * sw * 0.34 + phase * 6
            py = surf_y + fy * sh * 0.30 + (1 - (2 * ((px - (cx - sw/2)) / sw) - 1) ** 2) * sh * 0.16
            o.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="5" fill="{colour}" '
                     f'stroke="#ffffff" stroke-width="1.5"/>')
            if i == 0:
                o.append(f'<text x="{px:.0f}" y="{py-10:.0f}" font-size="8.5" fill="{MUTED}" '
                         f'text-anchor="middle">{escape(p.split("_")[0])}</text>')

    o.append(f'<text x="{PAD}" y="{surf_y + sh/2 + 34}" font-size="12" fill="{INK}">'
             f'Three surfaces we did not build, and cannot see. Each family carries its own.</text>')
    o.append(f'<text x="{PAD}" y="{surf_y + sh/2 + 52}" font-size="12" fill="{MUTED}">'
             f'The same six places sit in the same relative positions on every one of them. '
             f'That is the thing being inferred.</text>')

    # ---- the chart, laid over all three ----
    cy2 = surf_y + sh / 2 + 96
    o.append(f'<rect x="{PAD}" y="{cy2}" width="{W-2*PAD}" height="150" rx="8" '
             f'fill="{GRID}" stroke="{RULE}"/>')
    o.append(f'<text x="{PAD+16}" y="{cy2+26}" font-size="13" fill="{INK}" font-weight="bold">'
             f'The chart: ours, published, and small</text>')
    o.append(f'<text x="{PAD+16}" y="{cy2+46}" font-size="11" fill="{MUTED}">'
             f'{len(frame.anchors)} statements, a {len(frame.syllables)}-syllable codebook, '
             f'an axis order derived over {len(frame.population)} places, and one hashing rule. '
             f'{frame.seed_bytes():,} bytes.</text>')
    o.append(f'<text x="{PAD+16}" y="{cy2+72}" font-size="12" fill="{INK}">'
             f'The chart does not create the positions. It gives them names, an order, and a '
             f'way to prove which one you are standing on.</text>')
    o.append(f'<text x="{PAD+16}" y="{cy2+92}" font-size="12" fill="{MUTED}">'
             f'Hand two cartographers the same grid and they label the same mountain the same '
             f'way. That agreement is only worth something because the mountain was there first.</text>')
    o.append(f'<text x="{PAD+16}" y="{cy2+118}" font-size="11.5" fill="{WARM}">'
             f'Where it stops: the chart is shared too, but only when the states are '
             f'unambiguous. Ambiguous states send the charts apart again, which is why the six '
             f'places here are described in plain, concrete English.</text>')
    o.append(f'<text x="{PAD+16}" y="{cy2+138}" font-size="11" fill="{MUTED}">'
             f'This is the parent project\'s finding, restated: the manifold is shared, and the '
             f'chart is shared when the situations are clear. It is inferred from agreement, '
             f'not observed directly.</text>')

    # ---- the emergent claim, in one line ----
    ey = cy2 + 176
    o.append(f'<line x1="{PAD}" y1="{ey-16}" x2="{W-PAD}" y2="{ey-16}" stroke="{RULE}"/>')
    o.append(f'<text x="{PAD}" y="{ey+8}" font-size="15" fill="{INK}" font-weight="bold">'
             f'What the numbers do and do not license</text>')
    lines = [
        ("shown", "Independent systems with separate lineage place the same situation in the "
                  "same part of their own space, and state it in a form another can check.",
         SIGNAL),
        ("implied", "Situations have a structure that independently trained systems share. "
                    "The primer charts it rather than inventing it.", BLUE),
        ("not shown", "That any of this is meaning. A coordinate is a description of a "
                      "position, and a shared position is not a shared understanding.", WARM),
    ]
    for i, (label, text, colour) in enumerate(lines):
        yy = ey + 34 + i * 34
        o.append(f'<rect x="{PAD}" y="{yy-14}" width="96" height="22" rx="11" '
                 f'fill="{colour}" opacity="0.12" stroke="{colour}"/>')
        o.append(f'<text x="{PAD+12}" y="{yy+2}" font-size="10.5" fill="{colour}" '
                 f'font-weight="bold">{escape(label.upper())}</text>')
        o.append(f'<text x="{PAD+112}" y="{yy+2}" font-size="12" fill="{INK}">'
                 f'{escape(text[:118])}</text>')

    o.append("</svg>")
    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "shared-manifold.svg").write_text("\n".join(o), encoding="utf-8")
    print("wrote assets/figures/shared-manifold.svg")
    print(f"  cross-family: {cm['top1_strict']*100:.1f}% strict over {cm['comparisons']} comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
