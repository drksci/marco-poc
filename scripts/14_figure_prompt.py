#!/usr/bin/env python3
"""The exact prompt a model received, annotated. Plus the exact reply.

Nothing here is a summary. The left column is the literal prompt text, copied
out of `evidence/transcripts/*.jsonl`, with each part labelled and measured.
The right column is the literal reply.

The point of the figure is to make it impossible to be vague about what was
asked. A reader can see every one of the 45 statements, see that nothing else
was said, and see that no other model's answer was in the room.

Output: assets/figures/prompt-anatomy.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import primer  # noqa: E402

INK, MUTED, RULE = "#16161a", "#74747e", "#e2e2e6"
SIGNAL, SIGNAL_SOFT = "#3f6b52", "#eaf0eb"
WARM, WARM_SOFT = "#9a6f2f", "#f8f2e6"
GRID = "#f4f4f5"

W = 1180
PAD = 30
LEFT_W = 700
RIGHT_X = PAD + LEFT_W + 36
RIGHT_W = W - RIGHT_X - PAD
LH = 15          # line height for prompt text at 10.5px
LH_BIG = 17


def wrap(text, cols, prefix=""):
    lines, line = [], prefix
    for word in text.split():
        if len(line) + len(word) + 1 > cols and line.strip() != prefix.strip():
            lines.append(line)
            line = prefix + word
        else:
            line = f"{line} {word}".strip() if prefix else f"{line} {word}".strip()
    lines.append(line)
    return lines


def main() -> int:
    frame = primer.expand()
    recs = [json.loads(l)
            for p in sorted((ROOT / "evidence" / "transcripts").glob("probe-*.jsonl"))
            for l in p.read_text().splitlines() if l.strip()]
    # the same place seen by two families, so the agreement is visible
    place = "shared_workshop"
    a = next(r for r in recs if r["situation_id"] == place
             and r["model"] == "deepseek-v4.1-flash" and r.get("ok"))
    b = next(r for r in recs if r["situation_id"] == place
             and r["model"] == "gpt-6-luna" and r.get("ok"))

    prompt_lines = a["prompt"].split("\n")

    # ---- measure the prompt into labelled parts -------------------------
    n_vocab = len(frame.anchors)
    parts = [
        ("role", 1, "one sentence. the model is told what kind of object the list is."),
        ("the 45 statements", None,
         f"{n_vocab} numbered lines, each a key and its plain reading. This is the whole "
         f"vocabulary."),
        ("the place", None,
         "one paragraph of ordinary English. It is the only thing that differs between calls."),
        ("the instruction", None,
         "four lines: choose only what the description supports, do not choose what merely "
         "sounds plausible, reply with JSON only, use the keys exactly as written."),
        ("the reply schema", 1,
         '{"true_statements": [...]}. The model is told the shape of the answer.'),
    ]

    body_h = len(prompt_lines) * LH
    H = 150 + body_h + 150 + 70
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+24}" font-size="22" fill="{INK}" '
        f'font-family="Georgia, serif">What the model was actually given</text>',
        f'<text x="{PAD}" y="{PAD+48}" font-size="12.5" fill="{MUTED}">'
        f'The complete prompt, verbatim, for one place. {len(prompt_lines)} lines, '
        f'{len(a["prompt"])} characters, {a.get("usage",{}).get("prompt_tokens","?")} prompt tokens.</text>',
        f'<text x="{PAD}" y="{PAD+68}" font-size="12.5" fill="{MUTED}">'
        f'Nothing else was sent. No other model\'s answer, no naming of the place, no mention '
        f'that other models exist.</text>',
        f'<text x="{PAD}" y="{PAD+88}" font-size="12.5" fill="{MUTED}">'
        f'Prompt sha256 {escape(a["prompt_sha256"][:40])}\u2026 \u00b7 the same bytes went to '
        f'every family.</text>',
    ]

    # ---- the prompt, line by line ---------------------------------------
    top = 130
    out.append(f'<rect x="{PAD}" y="{top}" width="{LEFT_W}" height="{body_h+28}" rx="6" '
               f'fill="{GRID}" stroke="{RULE}"/>')
    out.append(f'<text x="{PAD+14}" y="{top+18}" font-size="10.5" fill="{MUTED}">'
               f'THE PROMPT, LINE FOR LINE</text>')

    # annotate the regions
    y = top + 32
    marks = []
    for i, line in enumerate(prompt_lines):
        stripped = line.rstrip()
        colour = INK
        weight = "normal"
        if stripped.startswith("STATEMENTS"):
            colour, weight = SIGNAL, "bold"
            marks.append(("the 45 statements begin", y))
        elif stripped.startswith("Here is the place"):
            colour, weight = WARM, "bold"
            marks.append(("the place begins", y))
        elif stripped.startswith("Which statements"):
            colour, weight = SIGNAL, "bold"
            marks.append(("the instruction begins", y))
        elif stripped.startswith('{"true_statements"'):
            colour, weight = WARM, "bold"
            marks.append(("the reply schema", y))
        out.append(f'<text x="{PAD+14}" y="{y+11}" font-size="10.5" fill="{colour}" '
                   f'font-weight="{weight}">{escape(stripped[:104])}</text>')
        y += LH

    # ---- annotation markers on the right edge of the prompt box ---------
    for label, yy in marks:
        out.append(f'<line x1="{PAD+LEFT_W-6}" y1="{yy+7}" x2="{PAD+LEFT_W+10}" y2="{yy+7}" '
                   f'stroke="{WARM}" stroke-width="1.2"/>')
        out.append(f'<text x="{PAD+LEFT_W+16}" y="{yy+11}" font-size="10" fill="{WARM}">'
                   f'{escape(label)}</text>')

    # ---- the replies -----------------------------------------------------
    ry = top
    for label, rec, colour, soft in [
        (f"{a['model']} replied", a, SIGNAL, SIGNAL_SOFT),
        (f"{b['model']} replied", b, WARM, WARM_SOFT),
    ]:
        raw = json.dumps(json.loads(rec["raw_response"]), indent=1)
        lines = raw.split("\n")
        h = 34 + len(lines) * 13 + 44
        out.append(f'<rect x="{RIGHT_X}" y="{ry}" width="{RIGHT_W}" height="{h}" rx="6" '
                   f'fill="{soft}" stroke="{colour}"/>')
        out.append(f'<text x="{RIGHT_X+14}" y="{ry+20}" font-size="10.5" fill="{colour}" '
                   f'font-weight="bold">{escape(label.upper())}</text>')
        for k, line in enumerate(lines):
            out.append(f'<text x="{RIGHT_X+14}" y="{ry+40+k*13}" font-size="10.5" '
                       f'fill="{INK}">{escape(line[:60])}</text>')
        out.append(f'<text x="{RIGHT_X+14}" y="{ry+h-26}" font-size="10" fill="{MUTED}">'
                   f'{rec.get("n_selected")} statements chosen</text>')
        out.append(f'<text x="{RIGHT_X+14}" y="{ry+h-12}" font-size="10" fill="{MUTED}">'
                   f'root !{escape(rec["raw_response"] and "")}'
                   f'{"same place, so the roots are compared below" if False else ""}</text>')
        ry += h + 16

    # ---- the comparison --------------------------------------------------
    import hashlib
    def root_of(stmts):
        payload = json.dumps({"statements": sorted(stmts), "extra": []},
                             separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    ra, rb = root_of(a["landmarks"]), root_of(b["landmarks"])
    same = set(a["landmarks"]) == set(b["landmarks"])
    fy = max(y, ry) + 14
    out.append(f'<line x1="{PAD}" y1="{fy}" x2="{W-PAD}" y2="{fy}" stroke="{RULE}"/>')
    verdict = ("identical statement sets, so identical roots" if same
               else "different statement sets, so different roots")
    out.append(f'<text x="{PAD}" y="{fy+24}" font-size="13" fill="{INK}" '
               f'font-weight="bold">{escape(verdict)}</text>')
    out.append(f'<text x="{PAD}" y="{fy+46}" font-size="11" fill="{MUTED}">'
               f'{escape(a["model"])}  !{ra[:32]}\u2026</text>')
    out.append(f'<text x="{PAD}" y="{fy+64}" font-size="11" fill="{MUTED}">'
               f'{escape(b["model"])}  !{rb[:32]}\u2026</text>')
    out.append("</svg>")

    FIG = ROOT / "assets" / "figures"
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "prompt-anatomy.svg").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote assets/figures/prompt-anatomy.svg ({W}x{H})")
    print(f"  {a['model']}: {a['n_selected']} statements, root {ra[:16]}")
    print(f"  {b['model']}: {b['n_selected']} statements, root {rb[:16]}")
    print(f"  identical roots: {same}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
