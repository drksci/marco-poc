#!/usr/bin/env python3
"""The card you fill in while running the blind test.

Sixteen numbered statements and two blank columns. Scan the code into one
assistant, read out the numbers it chose, tick them in the A column. Do the same
in a different app for the B column. Then compare the columns.

That comparison is the test. Two systems with no shared weights, no shared
context and no contact either chose the same statements or they did not.

Output: assets/figures/field-test-card.svg
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from marco import primer  # noqa: E402

INK, MUTED, RULE, GRID = "#16161a", "#74747e", "#e2e2e6", "#f4f4f5"
SIG, SIGSOFT, WARM, WARMSOFT = "#3f6b52", "#eaf0eb", "#9a6f2f", "#f8f2e6"


def main() -> int:
    d = json.loads((ROOT / "evidence" / "field-test.json").read_text())
    st = d["statements"]
    W, RH, PAD = 900, 30, 28
    H = 300 + RH * len(st) + 190

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+22}" font-size="21" fill="{INK}" '
        f'font-family="Georgia, serif">The blind test, on paper</text>',
        f'<text x="{PAD}" y="{PAD+46}" font-size="12" fill="{MUTED}">'
        f'Scan the code on the left into one assistant. Do it again in a different app. '
        f'Tick what each one chose.</text>',
        # column heads
        f'<text x="{PAD}" y="{220}" font-size="11" fill="{MUTED}">STATEMENT</text>',
        f'<text x="{W-190}" y="{220}" font-size="11" fill="{SIG}" text-anchor="middle">'
        f'ASSISTANT A</text>',
        f'<text x="{W-90}" y="{220}" font-size="11" fill="{WARM}" text-anchor="middle">'
        f'ASSISTANT B</text>',
        f'<line x1="{PAD}" y1="{230}" x2="{W-PAD}" y2="{230}" stroke="{RULE}"/>',
    ]
    for i, s in enumerate(st):
        y = 252 + i * RH
        if i % 2 == 0:
            o.append(f'<rect x="{PAD}" y="{y-16}" width="{W-2*PAD}" height="{RH}" fill="#fbfbfc"/>')
        o.append(f'<text x="{PAD}" y="{y+3}" font-size="12" fill="{MUTED}">{s["n"]:>2}</text>')
        o.append(f'<text x="{PAD+34}" y="{y+3}" font-size="12.5" fill="{INK}">'
                 f'{escape(s["plain"])}</text>')
        for cx, col in ((W - 190, SIG), (W - 90, WARM)):
            o.append(f'<rect x="{cx-13}" y="{y-13}" width="26" height="26" rx="4" '
                     f'fill="none" stroke="{col}"/>')
    y = 252 + len(st) * RH + 24
    o.append(f'<line x1="{PAD}" y1="{y-16}" x2="{W-PAD}" y2="{y-16}" stroke="{RULE}"/>')
    o.append(f'<text x="{PAD}" y="{y+8}" font-size="13" fill="{INK}" font-weight="bold">'
             f'What the comparison means</text>')
    lines = [
        ("the answers agree", "Two systems that share no weights, no context and no contact "
                              "placed the same room in the same part of their own space.",
         SIGSOFT, SIG),
        ("the answers differ", "The frame is not shared, and the claim on this site is wrong. "
                               "That is a result too, and worth reporting.", WARMSOFT, WARM),
        ("the first few agree", "The outside of an address is the coarse part. Agreement there "
                                "means the region matches even when the detail does not.",
         GRID, MUTED),
    ]
    for i, (lab, txt, soft, edge) in enumerate(lines):
        yy = y + 28 + i * 34
        o.append(f'<rect x="{PAD}" y="{yy-14}" width="150" height="24" rx="12" fill="{soft}" '
                 f'stroke="{edge}"/>')
        o.append(f'<text x="{PAD+12}" y="{yy+3}" font-size="10.5" fill="{edge}" '
                 f'font-weight="bold">{escape(lab.upper())}</text>')
        o.append(f'<text x="{PAD+166}" y="{yy+3}" font-size="11.5" fill="{INK}">'
                 f'{escape(txt[:96])}</text>')
    o.append(f'<text x="{PAD}" y="{H-PAD-24}" font-size="11" fill="{MUTED}">'
             f'The expected answer for the library room is a set of eight numbers. It is recorded '
             f'in the repository so you can check whether your two assistants found it.</text>')
    o.append(f'<text x="{PAD}" y="{H-PAD-6}" font-size="11" fill="{MUTED}">'
             f'Primer {escape(d["primer_fingerprint"][:32])}\u2026 \u00b7 '
             f'payload {d["qr_payload_bytes"]} bytes \u00b7 full address for this place '
             f'{escape(d["address_full_primer"])}</text>')
    o.append("</svg>")

    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "field-test-card.svg").write_text("\n".join(o), encoding="utf-8")
    print(f"wrote assets/figures/field-test-card.svg ({W}x{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
