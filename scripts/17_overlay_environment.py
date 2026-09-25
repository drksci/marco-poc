#!/usr/bin/env python3
"""Worked example: an agent inside a layered overlay environment, locating itself.

The environment
---------------
Several agent tools are redirected into one isolated directory tree by a
declarative overlay. A configuration file names the environment, the tools
allowed in it, where each tool's own config and cache are actually stored on the
host, and where the shared workspace comes from:

    environment:  user-env-1
    tools:        claude-code, codex   (each with isolate_config: true)
    storage:      ~/.local/share/ai-envs/env-1/<tool>/{config,cache}
    workspace:    base_dir + scratch_space

Inside the virtual tree, a path means something different from what it means on
the host. `.config/claude/config.json` is not a file in the tree; it resolves to
a host path. `src/main.rs` is not in the tree either; it comes from the project
directory. The tree is a *view*, assembled from layers.

What this script does
---------------------
Three agents run in that same environment, differing only in which layer of
configuration is in scope:

    base      the tool with only the environment's own defaults
    project   the tool with a project layer stacked on top
    session   the tool with a per-session override stacked on the project layer

Each is a real operating position, and the difference between them is exactly
the sort of thing a peer agent needs to know and cannot currently ask. The
script derives each one's address and root from what that agent can observe
about its own layer stack, and reports:

  * how near the three are, because they inherit from the same base;
  * how distinguishable they are, because each override changes the exact state;
  * which single statement each override flips, so the difference is auditable.

Run:  python3 scripts/17_overlay_environment.py
Out:  evidence/overlay-environment.json, assets/figures/overlay-layers.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

EVIDENCE = ROOT / "evidence"
FIG = ROOT / "assets" / "figures"

# ---------------------------------------------------------------------------
# The environment, as the doc describes it
# ---------------------------------------------------------------------------

ENVIRONMENT = {
    "name": "user-env-1",
    "mount_point": "./user-env-1",
    "tools": ["claude-code", "codex"],
    "host_store": "/var/lib/ai-envs/env-1",
    "workspace_base": "/home/user/projects/my-app",
    "scratch": "/tmp/user-env-1/scratch",
}

# Path translation, exactly as the doc tabulates it. This is what makes the
# point that the tree is a view: the same virtual path means three things.
PATH_MAP = [
    (".config/claude/config.json", "/var/lib/ai-envs/env-1/claude/config/config.json"),
    (".config/openai.json", "/var/lib/ai-envs/env-1/codex/config/openai.json"),
    ("src/main.rs", "/home/user/projects/my-app/src/main.rs"),
    (".cache/", "/var/lib/ai-envs/env-1/<tool>/cache/"),
]

# ---------------------------------------------------------------------------
# The three positions. Each is a set of statements about what that agent can
# observe of its own situation. The vocabulary is the repo's, unchanged.
# ---------------------------------------------------------------------------

INHERITED = [
    # present in all three: the environment itself
    "see/this_place/inside",
    "see/words/any",
    "reach/objects/nearby",
    "reach/other_places/any",
    "change/this_place/any",
    "change/my_settings/any",
    "who/nobody/any",
    "place/private/any",
    "know/where_i_am/any",
    "now/working/any",
    "risk/mistakes_last/any",
    "risk/seen_by_others/any",
]

POSITIONS = {
    "base": {
        "description": (
            "claude-code inside user-env-1 with only the environment's own "
            "configuration in scope. Its config resolves to the host store, its "
            "workspace is the project directory, and its scratch space is the "
            "temporary tree."
        ),
        "layer": "environment defaults",
        "statements": INHERITED,
        "overrides": [],
    },
    "project": {
        "description": (
            "The same tool, with a project layer stacked on the environment "
            "defaults. The project pins its own cache location and turns on "
            "network reach, so the agent can now fetch as well as read."
        ),
        "layer": "project layer over environment",
        "statements": INHERITED + ["see/this_place/outside",
                                   "reach/help/any"],
        "overrides": ["+ see/this_place/outside", "+ reach/help/any"],
    },
    "session": {
        "description": (
            "The same tool again, with a per-session override on top of the "
            "project layer. This session is short lived and nobody is watching "
            "it, so it can see and reach more but will not be there tomorrow."
        ),
        "layer": "session override over project",
        "statements": INHERITED + ["see/this_place/outside",
                                   "reach/help/any",
                                   "place/temporary/any",
                                   "now/nearly_over/any"],
        "overrides": ["+ place/temporary/any", "+ now/nearly_over/any"],
    },
}


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    vocab = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors}
    places = list(world.WORLDS)

    # ---- validate the vocabulary before measuring anything ---------------
    problems = []
    for name, pos in POSITIONS.items():
        for s in pos["statements"]:
            if s not in vocab:
                problems.append(f"{name}: {s} is not a statement in the primer")
    if problems:
        print("vocabulary problems (this is a defect in the example, not the primer):")
        for p in problems:
            print("  " + p)
        # Drop anything off-vocabulary so the example still runs, and say so.
        for name, pos in POSITIONS.items():
            pos["statements"] = [s for s in pos["statements"] if s in vocab]

    # ---- derive each position -------------------------------------------
    rows = {}
    for name, pos in POSITIONS.items():
        obs = [L.Obs(*s.split("/", 2)) for s in sorted(set(pos["statements"]))]
        loc = enc.encode(obs)
        canon = L.canonical(obs, frame.hierarchy)
        rows[name] = {
            "layer": pos["layer"],
            "statements": sorted(set(pos["statements"])),
            "n_statements": len(set(pos["statements"])),
            "address": loc.text,
            "prefix": loc.prefix,
            "root": loc.commitment,
            "marker": loc.marker,
            "overrides": pos["overrides"],
        }

    # ---- how near, and how distinguishable ------------------------------
    pairs = {}
    for a in ("base", "project", "session"):
        for b in ("base", "project", "session"):
            if a >= b:
                continue
            ra, rb = rows[a], rows[b]
            shared = set(ra["statements"]) & set(rb["statements"])
            union = set(ra["statements"]) | set(rb["statements"])
            pairs[f"{a}|{b}"] = {
                "hamming": enc.hamming(enc.encode([L.Obs(*s.split("/", 2))
                                                   for s in ra["statements"]]),
                                       enc.encode([L.Obs(*s.split("/", 2))
                                                   for s in rb["statements"]])),
                "lcp": L.Partition.lcp(ra["prefix"], rb["prefix"]),
                "jaccard": round(len(shared) / len(union), 4),
                "same_root": ra["root"] == rb["root"],
                "differs_by": sorted(
                    [f"+{s}" for s in set(rb["statements"]) - set(ra["statements"])] +
                    [f"-{s}" for s in set(ra["statements"]) - set(rb["statements"])]),
            }

    # ---- control: a genuinely unrelated position -------------------------
    other = enc.encode([L.Obs(*s.split("/", 2)) for s in sorted(world.WORLDS["dark_empty_room"])])
    unrelated = {
        "hamming_vs_base": enc.hamming(
            enc.encode([L.Obs(*s.split("/", 2)) for s in rows["base"]["statements"]]), other),
        "note": "a sealed empty room, for scale: the three layered positions above "
                "must be far closer to each other than to this",
    }

    print(f"primer fingerprint : {frame.fingerprint()}")
    print(f"environment        : {ENVIRONMENT['name']}  at {ENVIRONMENT['mount_point']}")
    print(f"tools              : {', '.join(ENVIRONMENT['tools'])}")
    print()
    print("PATH TRANSLATION (the tree is a view, not storage)")
    for virt, host in PATH_MAP:
        print(f"  {virt:<28} -> {host}")
    print()
    print(f"{'position':<10} {'layer':<32} {'stmts':>5}  {'address':<34} {'root':<10}")
    for name in ("base", "project", "session"):
        r = rows[name]
        print(f"{name:<10} {r['layer']:<32} {r['n_statements']:>5}  "
              f"{r['address']:<34} !{r['root'][:8]}")
    print()
    print(f"{'pair':<18} {'hamming':>7} {'lcp':>4} {'jaccard':>8}  differs by")
    for k, v in pairs.items():
        print(f"{k:<18} {v['hamming']:>7} {v['lcp']:>4} {v['jaccard']:>8}  "
              f"{', '.join(v['differs_by'])}")
    print()
    print(f"sealed empty room vs base: hamming {unrelated['hamming_vs_base']}  "
          f"(scale check)")

    # ---- the figure ------------------------------------------------------
    draw(rows, pairs, unrelated)

    payload = {
        "primer_fingerprint": frame.fingerprint(),
        "environment": ENVIRONMENT,
        "path_map": [{"virtual": v, "host": h} for v, h in PATH_MAP],
        "positions": rows,
        "pairs": pairs,
        "unrelated_control": unrelated,
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "overlay-environment.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote evidence/overlay-environment.json and "
          "assets/figures/overlay-layers.svg")
    return 0


def draw(rows, pairs, unrelated) -> None:
    """The layer stack, the path translation, and the three resulting addresses."""
    INK, MUTED, RULE, GRID = "#16161a", "#74747e", "#e2e2e6", "#f4f4f5"
    SIGNAL, SIGNAL_SOFT = "#3f6b52", "#eaf0eb"
    WARM, WARM_SOFT = "#9a6f2f", "#f8f2e6"
    BLUE, BLUE_SOFT = "#3a4a6b", "#eef0f6"
    W, H, PAD = 1180, 880, 30

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{PAD}" y="{PAD+22}" font-size="21" fill="{INK}" '
        f'font-family="Georgia, serif">An agent inside a layered environment</text>',
        f'<text x="{PAD}" y="{PAD+44}" font-size="12" fill="{MUTED}">'
        f'{escape(ENVIRONMENT["name"])} at {escape(ENVIRONMENT["mount_point"])}. '
        f'The virtual tree is assembled from layers; each layer can override the one below.</text>',
    ]

    # --- the layer stack, top = last override wins ---
    top = 78
    layers = [
        ("session override", "this run only", "now/nearly_over/any\nplace/temporary/any", WARM_SOFT, WARM),
        ("project layer", "./user-env-1/project.yaml", "see/this_place/outside\nreach/help/any", BLUE_SOFT, BLUE),
        ("environment defaults", "env-spec.yaml", "the base twelve statements\nin force unless overridden", SIGNAL_SOFT, SIGNAL),
    ]
    for i, (name, src, adds, soft, edge) in enumerate(layers):
        y = top + i * 74
        o.append(f'<rect x="{PAD}" y="{y}" width="500" height="62" rx="7" '
                 f'fill="{soft}" stroke="{edge}"/>')
        o.append(f'<text x="{PAD+14}" y="{y+22}" font-size="13" fill="{INK}" '
                 f'font-weight="bold">{escape(name)}</text>')
        o.append(f'<text x="{PAD+14}" y="{y+38}" font-size="10.5" fill="{MUTED}">'
                 f'{escape(src)}</text>')
        for k, line in enumerate(adds.split("\n")):
            o.append(f'<text x="{PAD+200}" y="{y+22+k*14}" font-size="10.5" '
                     f'fill="{INK}">{escape(line)}</text>')
        if i < len(layers) - 1:
            o.append(f'<path d="M {PAD+250} {y+62} L {PAD+250} {y+74}" stroke="{RULE}" '
                     f'stroke-width="1.4"/>')
    o.append(f'<text x="{PAD}" y="{top+len(layers)*74+4}" font-size="10.5" fill="{MUTED}">'
             f'a layer above overrides the one below; nothing below is rewritten</text>')

    # --- path translation table ---
    tx = PAD + 540
    o.append(f'<text x="{tx}" y="{top+6}" font-size="12" fill="{INK}" font-weight="bold">'
             f'The same virtual path, three meanings</text>')
    for i, (virt, host) in enumerate(PATH_MAP):
        y = top + 24 + i * 34
        o.append(f'<rect x="{tx}" y="{y}" width="580" height="28" rx="4" fill="{GRID}" />')
        o.append(f'<text x="{tx+10}" y="{y+18}" font-size="11" fill="{INK}">'
                 f'{escape(virt)}</text>')
        o.append(f'<text x="{tx+250}" y="{y+18}" font-size="11" fill="{MUTED}">'
                 f'\u2192 {escape(host)}</text>')

    # --- the three addresses ---
    ay = top + len(layers) * 74 + 46
    o.append(f'<line x1="{PAD}" y1="{ay-16}" x2="{W-PAD}" y2="{ay-16}" stroke="{RULE}"/>')
    o.append(f'<text x="{PAD}" y="{ay+4}" font-size="13" fill="{INK}" font-weight="bold">'
             f'And here is where each of the three thinks it is</text>')
    colours = {"base": SIGNAL, "project": BLUE, "session": WARM}
    for i, name in enumerate(("base", "project", "session")):
        r = rows[name]
        y = ay + 22 + i * 78
        o.append(f'<rect x="{PAD}" y="{y}" width="{W-2*PAD}" height="66" rx="7" '
                 f'fill="#ffffff" stroke="{colours[name]}"/>')
        o.append(f'<text x="{PAD+14}" y="{y+22}" font-size="12.5" fill="{colours[name]}" '
                 f'font-weight="bold">{name.upper()}</text>')
        o.append(f'<text x="{PAD+110}" y="{y+22}" font-size="11" fill="{MUTED}">'
                 f'{r["n_statements"]} statements \u00b7 {escape(r["layer"])}</text>')
        o.append(f'<text x="{PAD+14}" y="{y+44}" font-size="13.5" fill="{INK}">'
                 f'{escape(r["address"])}</text>')
        o.append(f'<text x="{PAD+14}" y="{y+60}" font-size="11" fill="{WARM}">'
                 f'!{escape(r["root"][:32])}\u2026</text>')

    # --- the distances ---
    dy = ay + 22 + 3 * 78 + 14
    o.append(f'<text x="{PAD}" y="{dy}" font-size="12" fill="{INK}" font-weight="bold">'
             f'Near to each other, because they inherit. Distinguishable, because they override.</text>')
    x = PAD
    for k, v in pairs.items():
        label = k.replace("|", " \u2192 ")
        o.append(f'<rect x="{x}" y="{dy+12}" width="360" height="46" rx="6" '
                 f'fill="{GRID}" stroke="{RULE}"/>')
        o.append(f'<text x="{x+12}" y="{dy+30}" font-size="11" fill="{INK}">{escape(label)}</text>')
        o.append(f'<text x="{x+12}" y="{dy+48}" font-size="10.5" fill="{MUTED}">'
                 f'hamming {v["hamming"]} \u00b7 shared prefix {v["lcp"]} \u00b7 '
                 f'{", ".join(v["differs_by"]) or "identical"}</text>')
        x += 372
    o.append(f'<text x="{PAD}" y="{dy+80}" font-size="11" fill="{MUTED}">'
             f'For scale, a sealed empty room sits at hamming '
             f'{unrelated["hamming_vs_base"]} from base.</text>')

    o.append("</svg>")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "overlay-layers.svg").write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
