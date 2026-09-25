#!/usr/bin/env python3
"""The unroll ladder, as a picture. Seed at the top, address and root at the bottom.

One tall diagram with two columns. The left column is the chain: each stage
derives from the one above it. The right column is the actual artefact that
stage produces, printed from the real seed.

Below the chain, a branch: what the two objects are then *used* for. Compare,
refine, verify, discover.

Everything shown is computed here from `primer.seed.json`. Nothing is drawn from
a description of what the code does.

Output: assets/figures/unroll-ladder.svg
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

INK, MUTED, RULE = "#16161a", "#74747e", "#e2e2e6"
SIGNAL, SIGNAL_SOFT = "#3f6b52", "#eaf0eb"
WARM, WARM_SOFT = "#9a6f2f", "#f8f2e6"
GRID = "#f4f4f5"

W, ROW, GAP = 1180, 74, 16
PAD, LX, RX = 30, 30, 400


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    seed = primer.load_seed()
    target = "kitchen_with_friend"
    w = world.build(target)
    obs = w.observations()
    canon = L.canonical(obs, frame.hierarchy)
    vec = L.anchor_vector(canon, frame.anchors, frame.distance)
    bits = frame.partition.bits(vec)
    syl = L.bits_to_syllables(bits, frame.syllables, per=5)
    loc = enc.encode(obs, timestamp=0)

    stages = [
        ("the seed", "primer.seed.json",
         f"{frame.seed_bytes():,} bytes. No situations, no questions, no axis order.",
         "primer_version, landmarks, phonology, markers, distance,\n"
         "hierarchy, partition, similarity, population"),
        ("landmarks", "namespace > relation > values",
         f"{len(frame.anchors)} statements, each with its plain reading inside the seed.",
         '  '.join(f"{k}/{r}/{v}" for (k, r, v) in frame.anchors[:3]) + "\n"
         f"  ... and {len(frame.anchors) - 3} more"),
        ("codebook", "boustrophedon walk over 6 consonants x 5 vowels",
         "32 syllables. Adjacent entries differ by exactly one phoneme: 31 of 31.",
         "  ".join(frame.syllables)),
        ("certainty ladder", "5 rungs, weakest wins",
         "Only = and |- may anchor a claim. Confidence cannot promote a marker.",
         "  ".join(f"{m} {v['rank']}" for m, v in frame.markers.items())),
        ("metric", "distance to each landmark",
         "Four levels, so quantisation keeps 0.0 distinct from 0.3.",
         "  ".join(f"{k} {v}" for k, v in frame.distance.items())),
        ("population", f"derived, depth {frame.population_params['depth']}",
         f"{len(frame.population)} concrete places. The only data the primer needs.",
         f"the {len(world.WORLDS)} shipped places, plus every place one answer away"),
        ("axis order", "descending variance over that population",
         "Not stored. Recovered identically on both sides. This is what a registry would ship.",
         f"first ten axes  {frame.partition.axes[:10]}\n"
         f"most important  #{frame.partition.axes[0]}  "
         f"{'/'.join(frame.anchors[frame.partition.axes[0]])}"),
        ("seal", "SHA-256 over the whole frame",
         "Two sides compare this before comparing anything else.",
         f"{frame.fingerprint()[:48]}\n{frame.fingerprint()[48:]}"),
    ]

    total_rows = len(stages) + 1  # + the two objects row
    H = PAD + 96 + total_rows * (ROW + GAP) + 300
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+24}" font-size="23" fill="{INK}" '
        f'font-family="Georgia, serif">The unroll ladder</text>',
        f'<text x="{PAD}" y="{PAD+48}" font-size="12.5" fill="{MUTED}">'
        f'Left: what is derived from what. Right: the artefact that stage produces, '
        f'printed from the real seed.</text>',
        f'<text x="{PAD}" y="{PAD+68}" font-size="12.5" fill="{MUTED}">'
        f'{frame.seed_bytes():,} bytes in, {frame.naive_transport_bytes():,} bytes of frame '
        f'reconstructed, {frame.compression()["reduction_factor"]}x, and none of the derived '
        f'part is ever sent.</text>',
    ]

    y = PAD + 96
    for i, (name, how, why, artefact) in enumerate(stages):
        # arrow from the previous stage
        if i:
            out.append(f'<path d="M {LX+22} {y-14} L {LX+22} {y-3}" stroke="{RULE}" '
                       f'stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(f'<rect x="{LX}" y="{y}" width="330" height="{ROW}" rx="6" '
                   f'fill="{GRID}" stroke="{RULE}"/>')
        out.append(f'<circle cx="{LX+22}" cy="{y+22}" r="12" fill="{INK}"/>')
        out.append(f'<text x="{LX+22}" y="{y+26}" font-size="11.5" fill="#ffffff" '
                   f'text-anchor="middle">{i+1}</text>')
        out.append(f'<text x="{LX+44}" y="{y+27}" font-size="14" fill="{INK}" '
                   f'font-weight="bold">{escape(name)}</text>')
        for k, line in enumerate(how.split("\n")):
            out.append(f'<text x="{LX+44}" y="{y+45+k*13}" font-size="10.5" '
                       f'fill="{MUTED}">{escape(line)}</text>')
        out.append(f'<text x="{LX+44}" y="{y+62}" font-size="10.5" fill="{MUTED}">'
                   f'{escape(why[:74])}</text>')
        # the artefact
        out.append(f'<rect x="{RX}" y="{y}" width="{W-RX-PAD}" height="{ROW}" rx="6" '
                   f'fill="#ffffff" stroke="{RULE}"/>')
        for k, line in enumerate(artefact.split("\n")):
            size = 12 if i in (0, 1, 2) else 10.5
            out.append(f'<text x="{RX+16}" y="{y+26+k*16}" font-size="{size}" '
                       f'fill="{INK}">{escape(line[:104])}</text>')
        y += ROW + GAP

    # the two objects produced
    y += 6
    out.append(f'<line x1="{LX}" y1="{y-8}" x2="{W-PAD}" y2="{y-8}" stroke="{RULE}"/>')
    out.append(f'<text x="{LX}" y="{y+16}" font-size="13" fill="{MUTED}">'
               f'and now one place: {target}, {len(canon)} statements reported</text>')
    yy = y + 28
    out.append(f'<rect x="{LX}" y="{yy}" width="560" height="96" rx="6" '
               f'fill="{SIGNAL_SOFT}" stroke="{SIGNAL}"/>')
    out.append(f'<text x="{LX+16}" y="{yy+24}" font-size="12" fill="{SIGNAL}" '
               f'font-weight="bold">THE ADDRESS - says near</text>')
    out.append(f'<text x="{LX+16}" y="{yy+48}" font-size="14" fill="{INK}">'
               f'{escape(loc.text[:58])}</text>')
    out.append(f'<text x="{LX+16}" y="{yy+68}" font-size="14" fill="{INK}">'
               f'{escape(loc.text[58:])}</text>')
    out.append(f'<text x="{LX+16}" y="{yy+86}" font-size="10.5" fill="{MUTED}">'
               f'similar places read alike. proves nothing.</text>')

    out.append(f'<rect x="{LX+580}" y="{yy}" width="{W-LX-580-PAD}" height="96" rx="6" '
               f'fill="{WARM_SOFT}" stroke="{WARM}"/>')
    out.append(f'<text x="{LX+596}" y="{yy+24}" font-size="12" fill="{WARM}" '
               f'font-weight="bold">THE ROOT - says same</text>')
    out.append(f'<text x="{LX+596}" y="{yy+46}" font-size="10.5" fill="{INK}">'
               f'{escape(loc.commitment[:52])}</text>')
    out.append(f'<text x="{LX+596}" y="{yy+62}" font-size="10.5" fill="{INK}">'
               f'{escape(loc.commitment[52:])}</text>')
    out.append(f'<text x="{LX+596}" y="{yy+86}" font-size="10.5" fill="{MUTED}">'
               f'one statement different, unrelated root. says nothing about nearness.</text>')

    # how they are used
    y = yy + 126
    out.append(f'<line x1="{LX}" y1="{y}" x2="{W-PAD}" y2="{y}" stroke="{RULE}"/>')
    out.append(f'<text x="{LX}" y="{y+22}" font-size="13" fill="{INK}" font-weight="bold">'
               f'And then what they are used for</text>')
    uses = [
        ("compare", "two addresses, one number",
         f"HAMMING(address, address) -> how close. No third party, no lookup."),
        ("refine", "stop wherever it matters",
         f"1 axis gives {len({enc.encode(world.build(p).observations(), precision=1).prefix for p in world.WORLDS})} groups from {len(world.WORLDS)} places; 6 axes names them all."),
        ("verify", "rebuild it yourself",
         "recompute the root from the statements. Equal or not equal."),
        ("discover", "find by situation, not by name",
         "path recall 1/4, nearness recall 4/4, with no mapping table."),
    ]
    uw = (W - PAD * 2 - 3 * 14) / 4
    for i, (name, sub, body) in enumerate(uses):
        x = LX + i * (uw + 14)
        out.append(f'<rect x="{x:.0f}" y="{y+34}" width="{uw:.0f}" height="92" rx="6" '
                   f'fill="#ffffff" stroke="{RULE}"/>')
        out.append(f'<text x="{x+14:.0f}" y="{y+56}" font-size="13" fill="{INK}" '
                   f'font-weight="bold">{escape(name)}</text>')
        out.append(f'<text x="{x+14:.0f}" y="{y+74}" font-size="10.5" fill="{MUTED}">'
                   f'{escape(sub)}</text>')
        words, line, lines = body.split(), "", []
        for wd in words:
            if len(line) + len(wd) + 1 > 34 and line:
                lines.append(line)
                line = wd
            else:
                line = f"{line} {wd}".strip()
        lines.append(line)
        for k, ln in enumerate(lines[:2]):
            out.append(f'<text x="{x+14:.0f}" y="{y+94+k*14}" font-size="10.5" fill="{INK}">'
                       f'{escape(ln)}</text>')

    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" '
               f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{RULE}"/></marker></defs>')
    out.append("</svg>")

    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "unroll-ladder.svg").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote assets/figures/unroll-ladder.svg  ({W}x{H})")
    print(f"  address {loc.text}")
    print(f"  root    {loc.commitment}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
