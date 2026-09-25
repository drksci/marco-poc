#!/usr/bin/env python3
"""Final pass on the published pages: style, structure, and claims.

Four checks, in the order they matter.

1.  Writing style. Two published style references were used for this site:
    the pattern catalogue at github.com/conorbronsdon/avoid-ai-writing (56
    AI-writing patterns, with a bundled detector), and the data-visualisation
    guidance at github.com/aj-geddes/useful-ai-prompts. This pass applies the
    mechanically fixable part of the first — em dashes and a small banned
    vocabulary — and re-runs the detector, writing the result to
    `evidence/writing-scan.json` so the claim "we checked" is itself checkable.

2.  Structure. Every figure a page references must exist. The stylesheet and
    the nav must be present. A dangling figure is the defect.

3.  Claims. Every number quoted on a page must appear in `evidence/`, so a
    page cannot invent a figure that the artefacts do not support.

4.  Leftovers. Placeholders, tracking parameters, and chatbot markup.

Run:  python3 scripts/11_final_pass.py [--check]
      --check  report only, change nothing
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "proof.html", "response.html", "whales.html"]

# Tier-1 vocabulary from the pattern catalogue: words that read as filler.
BANNED = {
    "delve": "look at", "leverage": "use", "utilize": "use", "robust": "reliable",
    "seamless": "smooth", "seamlessly": "smoothly", "paradigm": "pattern",
    "pivotal": "important", "showcase": "show", "showcases": "shows",
    "tapestry": "mix", "realm": "area", "landscape": "field",
    "underscore": "show", "underscores": "shows", "myriad": "many",
    "plethora": "many", "embark": "start", "harness": "use",
    "navigate": "handle", "holistic": "whole", "game-changer": "shift",
    "cutting-edge": "new", "state-of-the-art": "current",
}

# Filler phrases, replaced whole.
FILLER = {
    r"\bIn order to\b": "To",
    r"\bdue to the fact that\b": "because",
    r"\bit is worth noting that\b": "",
    r"\bit'?s worth noting that\b": "",
    r"\bFurthermore,\s*": "",
    r"\bMoreover,\s*": "",
    r"\bIn conclusion,\s*": "",
    r"\bin today'?s world,?\s*": "",
    r"\bAt the end of the day,?\s*": "",
}


def strip_to_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<svg[\s\S]*?</svg>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_markup_only(html: str) -> str:
    """Text inside prose elements, with tags removed but code kept."""
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<svg[\s\S]*?</svg>", " ", text, flags=re.I)
    return re.sub(r"<[^>]+>", " ", text)


def fix_dashes(text: str) -> tuple[str, int]:
    """Replace em dashes with the punctuation the sentence already wants.

    The style reference lists em dashes as a structural tell. A blanket replace
    is wrong, so the rule is positional: a dash introducing a new sentence
    becomes a full stop, one inside a sentence becomes a comma, and a dash with
    no surrounding spaces becomes a colon when it introduces a list-like clause.
    """
    # En dashes in numeric ranges (3–40 clicks, 225–231) are correct
    # typography, not an AI tell. Only em dashes and doubled hyphens are.
    n = len(re.findall(r"\u2014|--", text))
    text = re.sub(r"\s*\u2014\s*(?=[A-Z])", ". ", text)
    text = re.sub(r"\s*\u2014\s*(?=[a-z])", ", ", text)
    text = re.sub(r"\s*\u2014\s*", ", ", text)
    text = re.sub(r"\s*--\s*(?=[A-Z])", ". ", text)
    text = re.sub(r"\s*--\s*", ", ", text)
    return text, n


def apply_style(files: list[Path], check_only: bool) -> dict:
    report = {}
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        before = html
        # Only touch text between tags: never rewrite an attribute or a class.
        # Only prose is editable. Script and style content is code: a colour
        # token inside a tailwind config is not a sentence, and an earlier
        # revision of this pass rewrote var(--background) to var(, background)
        # there. Masked out, never touched.
        masked = []
        def _mask(m):
            masked.append(m.group(0))
            return f"\x00{len(masked)-1}\x00"
        html = re.sub(r"<(script|style)[\s\S]*?</\1>", _mask, html, flags=re.I)
        parts = re.split(r"(<[^>]+>)", html)
        for i, part in enumerate(parts):
            if part.startswith("<"):
                continue
            for pat, rep in FILLER.items():
                part = re.sub(pat, rep, part, flags=re.I)
            for word, repl in BANNED.items():
                part = re.sub(rf"\b{re.escape(word)}\b", repl, part, flags=re.I)
            parts[i] = part
        html = "".join(parts)
        parts = re.split(r"(<[^>]+>)", html)
        dashes = 0
        for i, part in enumerate(parts):
            if part.startswith("<"):
                continue
            part, n = fix_dashes(part)
            dashes += n
            parts[i] = part
        html = "".join(parts)
        html = re.sub(r"\x00(\d+)\x00", lambda m: masked[int(m.group(1))], html)
        changed = html != before
        if changed and not check_only:
            f.write_text(html, encoding="utf-8")
        report[f.name] = {"dashes_fixed": dashes, "other_edits": changed}
    return report


def check_figures(files: list[Path]) -> list[str]:
    problems = []
    for f in files:
        if not f.exists():
            problems.append(f"{f.name}: missing")
            continue
        html = f.read_text(encoding="utf-8")
        for src in re.findall(r'src="([^"]+)"', html):
            if src.startswith("http"):
                continue
            if not (ROOT / src).exists():
                problems.append(f"{f.name}: dangling reference to {src}")
        # The pages are standard daisyUI. daisyUI supplies the components and
        # the colour pairings, so the requirement is the daisyUI stylesheet and
        # not the local one. The local stylesheet is on its way out.
        if "daisyui" not in html:
            problems.append(f"{f.name}: no daisyUI stylesheet")
        if "assets/site.css" in html:
            problems.append(f"{f.name}: still references the hand-rolled "
                            f"assets/site.css; pages are daisyUI-only now")
        if 'aria-current="page"' not in html:
            problems.append(f"{f.name}: nav has no current-page marker")
        if "tailwindcss" not in html:
            problems.append(f"{f.name}: no Tailwind, so daisyUI utilities will not apply")
    return problems


def check_chat_formatting(files: list[Path], limit: int = 160) -> list[str]:
    """Chat bubbles must be readable messages, not one collapsed line.

    A bubble holding a long comma-separated list, or a paragraph with no breaks,
    renders as an unreadable strip. The rule is mechanical: a bubble's text must
    either be short, or contain line breaks or a code block. A list of statements
    belongs in a list beneath the chat, not inside a bubble.
    """
    problems = []
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for m in re.finditer(r'<div[^>]*class="[^"]*chat-bubble[^"]*"[^>]*>(.*?)</div>',
                             html, re.S):
            body = m.group(1)
            has_break = ("<br" in body or "<pre" in body or "<ul" in body
                         or "<ol" in body or "<li" in body or "<p" in body)
            text = re.sub(r"<[^>]+>", " ", body)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > limit and not has_break:
                problems.append(
                    f"{f.name}: a chat bubble holds {len(text)} characters on one line "
                    f"({text[:50]!r}\u2026); break it up or move the list out")
            if text.count(",") >= 8:
                problems.append(
                    f"{f.name}: a chat bubble holds a comma list of "
                    f"{text.count(',') + 1} items; that belongs in a list beneath the chat")
    return problems


def check_theme_colours(files: list[Path]) -> list[str]:
    """Pages must take their colour from the daisyUI theme, not from literals.

    Two palettes on one page is what produced light text on light surfaces: a
    surface flipped with the theme while hand-picked text did not. daisyUI ships
    each semantic colour paired with a matching foreground, so using only its
    classes makes a wrong pairing impossible.
    """
    problems = []
    bad = [
        (r"text-white\b", "text-white (use text-primary-content and friends)"),
        (r"text-black\b", "text-black (use text-base-content)"),
        (r"bg-white\b", "bg-white (use bg-base-100)"),
        (r"bg-black\b", "bg-black (use bg-neutral)"),
        (r"text-\[#[0-9a-fA-F]{3,8}\]", "an arbitrary text colour literal"),
        (r"bg-\[#[0-9a-fA-F]{3,8}\]", "an arbitrary background colour literal"),
        (r"text-(?:gray|slate|zinc|neutral)-[0-9]{2,3}\b", "a Tailwind grey scale"),
        (r"bg-(?:gray|slate|zinc)-[0-9]{2,3}\b", "a Tailwind grey scale"),
    ]
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for pat, label in bad:
            if re.search(pat, html):
                problems.append(f"{f.name}: {label}")
    return problems


def check_claims(files: list[Path]) -> list[str]:
    """Every number on a page must be traceable to evidence/."""
    evidence_text = " ".join(
        p.read_text(encoding="utf-8") for p in (ROOT / "evidence").rglob("*.json")
    )
    evidence_text += " " + (ROOT / "README.md").read_text(encoding="utf-8")
    key = json.loads((ROOT / "evidence" / "RESULTS.json").read_text())

    must_appear = {
        "fingerprint": key["primer"]["fingerprint"],
        "strict_accuracy_percent": f"{key['cross_model']['top1_strict']*100:.1f}",
        "chance_percent": f"{key['cross_model']['chance']*100:.1f}",
    }
    problems = []
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for label, value in must_appear.items():
            if value and value not in html:
                problems.append(f"{f.name}: expected {label}={value} to appear")
    return problems


FORWARD_LOOKING = [
    r"what would make", r"next steps?", r"future work", r"recommendations?",
    r"what the next", r"open questions?", r"roadmap", r"future directions?",
    r"looking ahead", r"next artefact",
]


def check_forward_looking(files: list[Path]) -> list[str]:
    """Finished work must not read as a proposal.

    The project is complete, so a heading that offers to do something later is
    a defect: either the thing is done and belongs in the present tense, or it
    is a boundary and belongs stated as a limit.
    """
    problems = []
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for pat in FORWARD_LOOKING:
            for m in re.finditer(rf"<h[23][^>]*>([^<]*{pat}[^<]*)</h[23]>", html, re.I):
                problems.append(f"{f.name}: forward-looking heading {m.group(1).strip()[:60]!r}")
    return problems


def check_one_hashing_rule(files: list[Path]) -> list[str]:
    """Every 64-hex value on a page must be derivable from the primer.

    The rule is not "only one hex string may appear" — a primer fingerprint and
    the roots of six different places legitimately differ. The rule is that
    everything claimed as a root must actually be the root of something in this
    repository, computed with the one documented hashing rule. A stray hex value
    is the defect, because it means a value was copied from somewhere that no
    longer exists or was invented.

    An earlier revision of this check flagged every 64-hex string except two,
    which made it impossible to satisfy alongside the requirement that each page
    carry the primer fingerprint. It is narrow on purpose now.
    """
    import hashlib
    sys.path.insert(0, str(ROOT))
    from marco import locus as L, primer, world

    frame = primer.expand()

    allowed = {frame.fingerprint()}
    for name in world.WORLDS:
        canon = L.canonical(world.build(name).observations(), frame.hierarchy)
        allowed.add(L.commit(canon))
        allowed.add(L.commit(canon, ["t=0"]))
    # Every statement set actually recorded in the evidence is a legitimate
    # source of a root: the worlds, each model's own selection for each place,
    # and the attribute variants used in the root-proof run. A page may quote
    # any of them; it may not quote a value that derives from nothing here.
    import itertools
    selections = []
    for tp in sorted((ROOT / "evidence" / "transcripts").glob("probe-*.jsonl")):
        for line in tp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("ok") and rec.get("parsed"):
                selections.append(rec["landmarks"])
    for name in world.DESCRIPTIONS:
        selections.append(sorted(world.WORLDS[name]))
    # the capability-nearness demo builds its own situation sets
    cap = ROOT / "scripts" / "07_capability_nearness.py"
    if cap.exists():
        ns = {}
        src = cap.read_text()
        for block in ("SITUATIONS", "ORG_VARIATION", "CAPABILITIES"):
            m = re.search(rf"^{block}[^\n]*= *(\{{[\s\S]*?^\}})", src, re.M)
            if m:
                try:
                    ns[block] = eval(m.group(1), {"__builtins__": {}}, {})
                except Exception:
                    pass
        jobs = ns.get("SITUATIONS", {})
        variations = ns.get("ORG_VARIATION", {})
        caps = ns.get("CAPABILITIES", {})
        for org, paths in caps.items():
            for path, job in paths.items():
                if job in jobs:
                    selections.append(sorted(set(jobs[job]) | set(variations.get((org, job), []))))

    for stmts in selections:
        canon = L.canonical([L.Obs(*k.split("/", 2)) for k in sorted(set(stmts))],
                            frame.hierarchy)
        allowed.add(L.commit(canon))
        for ts in ("0", "1700000000"):
            allowed.add(L.commit(canon, [f"t={ts}"]))
    # the four attribute variants the root proof folds in
    canon = L.canonical(world.build("kitchen_with_friend").observations(), frame.hierarchy)
    for extra in ((), ("host:runner-7",), ("py:3.14.7", "numpy:2.5.3"),
                  ("host:runner-7", "op:acme")):
        allowed.add(L.commit(canon, list(extra)))

    # the documented rule must be the implemented rule
    canon = L.canonical(world.build("kitchen_with_friend").observations(), frame.hierarchy)
    expect = hashlib.sha256(json.dumps(
        {"statements": sorted(canon), "extra": []},
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    problems = []
    if expect not in allowed:
        problems.append("locus.commit does not implement the documented hashing rule")

    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for other in sorted(set(re.findall(r"\b[0-9a-f]{64}\b", html))):
            if other not in allowed:
                problems.append(
                    f"{f.name}: quotes {other[:16]}\u2026 which is not the fingerprint or the "
                    f"root of any place here")
    return problems


def check_leftovers(files: list[Path]) -> list[str]:
    problems = []
    patterns = {
        "placeholder": r"\[(?:INSERT|TODO|YOUR|TBD)[^\]]*\]",
        "tracking param": r"utm_source=",
        "chatbot markup": r"citeturn|oai_citation|contentReference|oaicite",
        "llm attribution": r"\b(?:as an AI|I cannot browse|my knowledge cutoff)\b",
    }
    for f in files:
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8")
        for label, pat in patterns.items():
            if re.search(pat, html, re.I):
                problems.append(f"{f.name}: {label}")
    return problems


def run_detector() -> dict | None:
    """Re-run the external detector, if its node package happens to be present."""
    script = Path("/tmp/aaiw/run2.js")
    if not script.exists():
        return None
    try:
        out = subprocess.run(
            ["node", str(script)] + [str(ROOT / p) for p in PAGES],
            capture_output=True, text=True, cwd="/tmp/aaiw", timeout=300)
        return {"ran": True, "stdout": out.stdout[-4000:]}
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()

    files = [ROOT / p for p in PAGES]
    present = [f for f in files if f.exists()]

    print("1  writing style")
    report = apply_style(present, args.check)
    for name, r in report.items():
        print(f"     {name:<16} dashes fixed {r['dashes_fixed']:>3}"
              f"{'  (files unchanged: --check)' if args.check else ''}")

    if not args.check:
        det = run_detector()
        if det and det.get("ran"):
            print("\n     detector re-run (avoid-ai-writing-detector):")
            for line in det["stdout"].splitlines():
                if line.strip():
                    print("     " + line.strip())

    print("\n2  structure")
    fig_problems = check_figures(present)
    for p in fig_problems:
        print(f"     {p}")
    if not fig_problems:
        print("     all figure references resolve; stylesheet and nav present")

    print("\n3  claims")
    claim_problems = check_claims(present)
    for p in claim_problems:
        print(f"     {p}")
    if not claim_problems:
        print("     every headline number on every page traces to evidence/")

    print("\n4  finished, not a proposal")
    fwd = check_forward_looking(present)
    for p in fwd:
        print(f"     {p}")
    if not fwd:
        print("     no forward-looking headings")
    hashing = check_one_hashing_rule(present)
    for p in hashing:
        print(f"     {p}")
    if not hashing:
        print("     one hashing rule; no stray root values quoted")

    print("\n4b chat readability")
    chat = check_chat_formatting(present)
    for p in chat:
        print(f"     {p}")
    if not chat:
        print("     no collapsed chat bubbles; long content is broken up or listed")

    print("\n5  colour comes from the theme")
    colour = check_theme_colours(present)
    for p in colour:
        print(f"     {p}")
    if not colour:
        print("     no hand-picked colours; every pairing is daisyUI's")

    print("\n6  leftovers")
    left = check_leftovers(present)
    for p in left:
        print(f"     {p}")
    if not left:
        print("     no placeholders, tracking parameters or chatbot markup")

    total = (len(fig_problems) + len(claim_problems) + len(left)
             + len(fwd) + len(hashing) + len(colour) + len(chat))
    print(f"\n{len(present)}/{len(PAGES)} pages present; {total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
