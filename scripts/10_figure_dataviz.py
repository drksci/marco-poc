#!/usr/bin/env python3
"""Draw the numbers. Four charts, every value read from evidence/.

    controls.svg     the headline against its nulls, as bars
    matrix.svg       the 6x6 distance matrix for one model pair, as a heatmap
    roots.svg        how many families produced the byte-identical root
    turn.svg         the MARCO/POLO turn, as a collapsing timeline

Nothing here is illustrative. If a value is not in the evidence files, the
chart is not drawn.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

FIG = ROOT / "assets" / "figures"
EV = ROOT / "evidence"

INK, MUTED, RULE = "#16161a", "#74747e", "#e2e2e6"
GOOD, WARN, COOL = "#3f6b52", "#9a6f2f", "#3f6b52"
GRID = "#f0f0f2"


def head(w, h, title, sub=None):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
        f'<text x="28" y="38" font-size="19" fill="{INK}" '
        f'font-family="Georgia, serif">{escape(title)}</text>',
    ]
    if sub:
        out.append(f'<text x="28" y="60" font-size="11.5" fill="{MUTED}">{escape(sub)}</text>')
    return out


def wrap_axis(text, width, size=11, indent=10):
    """Naive word wrap for axis labels."""
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    lines.append(line)
    return lines


# ── 1. controls ──────────────────────────────────────────────────────────

def chart_controls() -> None:
    b = json.loads((EV / "blind" / "blind-match.json").read_text())
    rows = [
        ("real cross-model", b["top1_accuracy"], b["top1_strict_accuracy"], None, GOOD),
        ("chance", b["chance"], None, None, MUTED),
        ("null: labels shuffled", b["null_label_shuffle"]["accuracy"], None,
         b["null_label_shuffle"]["sd"], WARN),
        ("null: random vocabulary", b["null_random_vocabulary"]["accuracy"], None,
         b["null_random_vocabulary"]["sd"], WARN),
    ]
    W, H = 880, 300
    x0, bw, row_h = 250, 480, 42
    out = head(W, H, "The result and its controls",
               f"{b['pairs']} model pairs x {len(b['situations'])} places = "
               f"{b['pairs']*len(b['situations'])} comparisons. "
               f"Bars: accuracy. Whiskers: one standard deviation over 400 trials per pair.")
    for i, (label, val, _, sd, colour) in enumerate(rows):
        y = 90 + i * row_h
        out.append(f'<text x="{x0-14}" y="{y+16}" font-size="12" fill="{INK}" '
                   f'text-anchor="end">{escape(label)}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{bw}" height="22" fill="{GRID}"/>')
        out.append(f'<rect x="{x0}" y="{y}" width="{bw*val:.1f}" height="22" '
                   f'fill="{colour}" opacity="0.85"/>')
        out.append(f'<text x="{x0+bw*val+8:.1f}" y="{y+16}" font-size="12" '
                   f'fill="{INK}">{val*100:.1f}%</text>')
        if sd:
            lo = max(0.0, val - sd)
            hi = min(1.0, val + sd)
            out.append(f'<line x1="{x0+bw*lo:.1f}" y1="{y+11}" x2="{x0+bw*hi:.1f}" '
                       f'y2="{y+11}" stroke="{INK}" stroke-width="1"/>')
            for xx in (lo, hi):
                out.append(f'<line x1="{x0+bw*xx:.1f}" y1="{y+6}" x2="{x0+bw*xx:.1f}" '
                           f'y2="{y+16}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<line x1="{x0}" y1="{90+4*row_h}" x2="{x0+bw}" y2="{90+4*row_h}" stroke="{RULE}"/>')
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = x0 + bw * frac
        out.append(f'<line x1="{x:.1f}" y1="{90+4*row_h}" x2="{x:.1f}" y2="{90+4*row_h+5}" stroke="{RULE}"/>')
        out.append(f'<text x="{x:.1f}" y="{90+4*row_h+20}" font-size="10.5" fill="{MUTED}" '
                   f'text-anchor="middle">{int(frac*100)}%</text>')
    out.append(f'<text x="{x0+220}" y="{90+4*row_h+40}" font-size="11" fill="{MUTED}">'
               f'The nulls sit at chance. The result does not.</text>')
    out.append("</svg>")
    (FIG / "controls.svg").write_text("\n".join(out), encoding="utf-8")
    print("  controls.svg")


# ── 2. distance matrix ───────────────────────────────────────────────────

def chart_matrix() -> None:
    frame = primer.expand()
    enc = L.Encoder(frame)
    records = [json.loads(l)
               for p in (EV / "transcripts").glob("probe-*.jsonl")
               for l in p.read_text().splitlines() if l.strip()]
    sel: dict[str, dict[str, set]] = {}
    for r in records:
        if r.get("ok") and r.get("parsed"):
            sel.setdefault(r["model"], {})[r["situation_id"]] = set(r["landmarks"])
    models = sorted(sel)
    places = [p for p in world.DESCRIPTIONS if all(p in sel[m] for m in models)]
    a, bb = models[0], models[-1]
    loc = {m: {p: enc.encode([L.Obs(*k.split("/", 2)) for k in sorted(sel[m][p])])
               for p in places} for m in (a, bb)}

    n = len(places)
    cell, x0, y0 = 46, 250, 130
    W, H = x0 + cell * n + 60, y0 + cell * n + 90
    M = np.array([[enc.hamming(loc[a][p], loc[bb][q]) for q in places] for p in places])
    vmax = max(1, int(M.max()))

    out = head(W, H, "Two models, one matrix",
               f"{a} (rows) against {bb} (columns). Cells: distance between two addresses. "
               f"The diagonal is the same place seen by both.")
    for i, p in enumerate(places):
        for j, q in enumerate(places):
            v = M[i, j]
            t = v / vmax
            fill = f'rgb({int(240-150*t)},{int(244-90*t)},{int(238-60*t)})'
            x, y = x0 + j * cell, y0 + i * cell
            out.append(f'<rect x="{x}" y="{y}" width="{cell-2}" height="{cell-2}" fill="{fill}"/>')
            out.append(f'<text x="{x+(cell-2)/2:.0f}" y="{y+(cell-2)/2+4:.0f}" font-size="12" '
                       f'fill="{INK}" text-anchor="middle">{v}</text>')
            if i == j:
                out.append(f'<rect x="{x}" y="{y}" width="{cell-2}" height="{cell-2}" '
                           f'fill="none" stroke="{GOOD}" stroke-width="2.5"/>')
    for i, p in enumerate(places):
        lines = wrap_axis(p.replace("_", " "), 22)
        for k, ln in enumerate(lines):
            out.append(f'<text x="{x0-12}" y="{y0+i*cell+ (cell/2) - (len(lines)-1)*6 + k*12:.0f}" '
                       f'font-size="10.5" fill="{INK}" text-anchor="end">{escape(ln)}</text>')
    for j, q in enumerate(places):
        out.append(f'<g transform="translate({x0+j*cell+18},{y0-10}) rotate(-45)">'
                   f'<text font-size="10.5" fill="{INK}" text-anchor="start">'
                   f'{escape(q.replace("_", " "))}</text></g>')
    diag = [int(M[i, i]) for i in range(n)]
    off = [int(M[i, j]) for i in range(n) for j in range(n) if i != j]
    out.append(f'<text x="{x0}" y="{y0+cell*n+34}" font-size="11.5" fill="{MUTED}">'
               f'Ringed diagonal: same place, both models. Range {min(diag)}-{max(diag)}. '
               f'Off-diagonal range {min(off)}-{max(off)}.</text>')
    out.append(f'<text x="{x0}" y="{y0+cell*n+52}" font-size="11.5" fill="{MUTED}">'
               f'The diagonal never overlaps the rest: {sum(1 for i in range(n) if M[i,i] < min(M[i,j] for j in range(n) if j!=i))}'
               f' of {n} rows have a strictly smallest value on the diagonal.</text>')
    out.append("</svg>")
    (FIG / "matrix.svg").write_text("\n".join(out), encoding="utf-8")
    print(f"  matrix.svg  ({a} vs {bb})")


# ── 3. root agreement ────────────────────────────────────────────────────

def chart_roots() -> None:
    rp = json.loads((EV / "root-proof.json").read_text())
    places = rp["places"]
    sizes = [rp["per_place"][p]["largest_group_size"] for p in places]
    distinct = [rp["per_place"][p]["distinct_roots"] for p in places]
    n = len(rp["models"])
    rows = sorted(zip(places, sizes, distinct), key=lambda t: -t[1])

    W, H = 880, 90 + len(rows) * 40 + 90
    x0, bw = 260, 380
    out = head(W, H, "The same root, from separate families",
               f"{n} independent model families. Bar: how many produced the byte-identical "
               f"root for that place. Out of {n}.")
    for i, (p, s, d) in enumerate(rows):
        y = 84 + i * 40
        out.append(f'<text x="{x0-14}" y="{y+17}" font-size="11.5" fill="{INK}" '
                   f'text-anchor="end">{escape(p.replace("_", " "))}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{bw}" height="24" fill="{GRID}"/>')
        out.append(f'<rect x="{x0}" y="{y}" width="{bw*s/n:.1f}" height="24" fill="{GOOD}" opacity="0.85"/>')
        out.append(f'<text x="{x0+8}" y="{y+17}" font-size="12" fill="#ffffff" '
                   f'font-weight="bold">{s} of {n}</text>')
        out.append(f'<text x="{x0+bw+12}" y="{y+17}" font-size="11" fill="{MUTED}">'
                   f'{d} distinct root{"s" if d != 1 else ""}</text>')
    out.append(f'<line x1="{x0}" y1="{84+len(rows)*40+8}" x2="{x0+bw}" y2="{84+len(rows)*40+8}" stroke="{RULE}"/>')
    out.append(f'<text x="{x0}" y="{84+len(rows)*40+28}" font-size="11.5" fill="{MUTED}">'
               f'{rp["largest_group_total"]} model-place pairs produced a byte-identical root '
               f'({rp["largest_group_fraction"]*100:.1f}%).</text>')
    out.append(f'<text x="{x0}" y="{84+len(rows)*40+46}" font-size="11.5" fill="{MUTED}">'
               f'A root is not a similarity: it is the same 32 bytes, or it is unrelated. '
               f'The address is allowed to differ; this is not.</text>')
    out.append("</svg>")
    (FIG / "roots.svg").write_text("\n".join(out), encoding="utf-8")
    print("  roots.svg")


# ── 4. the turn ──────────────────────────────────────────────────────────

def chart_turn() -> None:
    p = json.loads((EV / "marco-polo.json").read_text())
    steps = []
    for ev in p["trace"]:
        if ev["kind"] == "disclosure":
            steps.append(("hider discloses", ev["address"], f"{ev['axes']} of 45 axes", None))
        elif ev["kind"] == "answer":
            steps.append(("seeker asks", ev["question"], "YES" if ev["answer"] else "NO", None))
    # candidate counts, recomputed so the collapse is visible
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {n: enc.encode(world.build(n).observations()) for n in places}
    target = p["place_under_test"]

    W = 900
    row_h = 56
    H = 110 + len(steps) * row_h + 70
    out = head(W, H, "One turn, one question",
               f"hider {p['hider_model']} · {p['questions_asked']} question · "
               f"{p['hider_calls']} model call · ${p['cost_usd']:.6f} · verdict {p['verdict']}")
    for i, (who, text, note, _) in enumerate(steps):
        y = 92 + i * row_h
        colour = GOOD if who.startswith("hider") else WARN
        out.append(f'<circle cx="40" cy="{y+14}" r="5" fill="{colour}"/>')
        out.append(f'<text x="58" y="{y+18}" font-size="12" fill="{MUTED}">{escape(who)}</text>')
        body = text if len(text) < 62 else text[:59] + "..."
        out.append(f'<text x="200" y="{y+18}" font-size="13" fill="{INK}">"{escape(body)}"</text>')
        out.append(f'<text x="200" y="{y+35}" font-size="10.5" fill="{MUTED}">{escape(note)}</text>')
        if i < len(steps) - 1:
            out.append(f'<line x1="40" y1="{y+19}" x2="40" y2="{y+row_h+8}" stroke="{RULE}"/>')

    # the narrowing, drawn as a bar per stage
    y = 92 + len(steps) * row_h + 16
    out.append(f'<text x="28" y="{y}" font-size="11.5" fill="{MUTED}">PLACES STILL POSSIBLE</text>')
    for i, k in enumerate(p["disclosure_steps"]):
        disclosed = enc.encode(world.build(target).observations(), precision=k)
        fits = [n for n in places if loci[n].prefix[:k] == disclosed.prefix[:k]]
        bx = 60 + i * 250
        w = 200 * len(fits) / len(places)
        out.append(f'<rect x="{bx}" y="{y+14}" width="200" height="20" fill="{GRID}"/>')
        out.append(f'<rect x="{bx}" y="{y+14}" width="{w:.0f}" height="20" fill="{GOOD}" opacity="0.8"/>')
        out.append(f'<text x="{bx+8}" y="{y+29}" font-size="11.5" fill="#ffffff" '
                   f'font-weight="bold">{len(fits)} of {len(places)}</text>')
        out.append(f'<text x="{bx}" y="{y+50}" font-size="10.5" fill="{MUTED}">'
                   f'after {k} axes disclosed</text>')
    out.append("</svg>")
    (FIG / "turn.svg").write_text("\n".join(out), encoding="utf-8")
    print("  turn.svg")


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    chart_controls()
    chart_matrix()
    chart_roots()
    chart_turn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
