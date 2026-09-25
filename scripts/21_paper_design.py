#!/usr/bin/env python3
"""Apply the paper design system to the four published pages.

This is a migration, not a rewrite. It touches the shell only:

    * adds `assets/paper.css`, the one design system, to every page
    * marks the body as `.paper`
    * replaces the nav with one shared, consistent nav
    * inserts a contents block built from the page's own section headings,
      and gives those headings anchor ids

Every section, figure, chat exchange, table and code block below the masthead is
left exactly as it was. The point of the design is to present that material, so
the migration must not be allowed to discard any of it.

It also carries two content fixes that were outstanding:

    * index.html rendered the address glyph as U+2319 (⌙). Every artefact in the
      repository, and the other three pages, use U+2301 (⌁).
    * proof.html quoted the field-test expectation as eight statement numbers.
      The corrected fixture, and the page's own table, both have nine.

Run:  python3 scripts/21_paper_design.py
"""

from __future__ import annotations

import html as H
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = ["index.html", "proof.html", "response.html", "whales.html"]

NAV_LINKS = [
    ("index.html", "overview"),
    ("response.html", "agent://"),
    ("proof.html", "evidence"),
    ("whales.html", "whales"),
]

WRONG_GLYPH = "\u2319"      # ⌙  what index.html had as a literal
WRONG_ENTITY = "&#8985;"    # ⌙  and as an HTML entity, 28 times
RIGHT_GLYPH = "\u2301"      # ⌁  what every artefact uses

STALE_EXPECT = "1, 2, 4, 5, 6, 11, 14, 16"
FIXED_EXPECT = "1, 2, 4, 5, 6, 10, 11, 14, 16"


def nav_html(current: str) -> str:
    links = []
    for href, label in NAV_LINKS:
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'    <a class="link link-hover" href="{href}"{cur}>{label}</a>')
    joined = "\n".join(links)
    return f"""<nav class="navbar" aria-label="Sections">
  <div>
{joined}
  </div>
</nav>"""


def heading_text(raw: str) -> str:
    """The visible text of a heading, with inline tags removed."""
    txt = re.sub(r"<[^>]+>", "", raw)
    return H.unescape(re.sub(r"\s+", " ", txt)).strip()


def add_ids_and_toc(body: str) -> tuple[str, str]:
    """Number the h2s, add anchor ids, and build the contents list."""
    entries: list[tuple[str, str]] = []
    counter = {"n": 0}

    def repl(m: re.Match) -> str:
        attrs, inner = m.group(1), m.group(2)
        counter["n"] += 1
        anchor = f"s{counter['n']}"
        label = heading_text(inner)
        entries.append((anchor, label))
        if re.search(r'\bid="', attrs):
            return m.group(0)
        return f'<h2 id="{anchor}"{attrs}>{inner}</h2>'

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, body, flags=re.S)

    items = "\n".join(
        f'      <li><a href="#{a}"><span class="n">{i}</span>{H.escape(label)}</a></li>'
        for i, (a, label) in enumerate(entries, 1))
    toc = f"""<nav class="paper-toc" aria-label="Contents">
    <p>Contents</p>
    <ol>
{items}
    </ol>
  </nav>"""
    return body, toc


def migrate(name: str) -> dict:
    path = ROOT / name
    src = path.read_text(encoding="utf-8")
    before = len(src)

    fixed = {"glyph": 0, "expect": 0}

    # --- the two content fixes -------------------------------------------
    n = src.count(WRONG_GLYPH) + src.count(WRONG_ENTITY)
    if n:
        src = src.replace(WRONG_GLYPH, RIGHT_GLYPH).replace(WRONG_ENTITY, RIGHT_GLYPH)
        fixed["glyph"] = n
    if name == "proof.html" and STALE_EXPECT in src:
        fixed["expect"] = src.count(STALE_EXPECT)
        src = src.replace(STALE_EXPECT, FIXED_EXPECT)

    # --- body marker (idempotent) ----------------------------------------
    if not re.search(r'<body class="[^"]*\bpaper\b', src):
        src = re.sub(r'<body class="([^"]*)"',
                     lambda m: f'<body class="{m.group(1)} paper"', src, count=1)

    # --- stylesheet, last in head so it wins over the utility defaults ----
    if "assets/paper.css" not in src:
        src = src.replace("</head>",
                          '<link href="assets/paper.css" rel="stylesheet" type="text/css" />\n</head>', 1)

    # --- one shared nav ---------------------------------------------------
    src = re.sub(r"<nav\b[^>]*>.*?</nav>", nav_html(name), src, count=1, flags=re.S)

    # --- contents block, right after the masthead (idempotent) ------------
    head_end = src.find("</header>")
    if head_end != -1:
        cut = head_end + len("</header>")
        body_part, toc = add_ids_and_toc(src[cut:])
        if 'class="paper-toc"' not in src:
            src = src[:cut] + "\n\n" + toc + "\n" + body_part
        else:
            src = src[:cut] + body_part
    else:
        src, _ = add_ids_and_toc(src)

    path.write_text(src, encoding="utf-8")
    return {"file": name, "before": before, "after": len(src), **fixed}


def main() -> int:
    for name in PAGES:
        r = migrate(name)
        print(f"{r['file']:15} {r['before']:>7,} -> {r['after']:>7,} bytes"
              f"   glyph fixes {r['glyph']:>2}   fixture fixes {r['expect']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
