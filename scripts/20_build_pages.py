#!/usr/bin/env python3
"""Build the four published pages from one design system.

The design follows the golden example: an academic paper, not a landing page.

    * one narrow reading column (46rem) of serif prose
    * numbered sections, listed in a contents block
    * figures that break out wider than the text measure
    * small monospace captions of the form "Figure N. ..."
    * no hero, no cards, no badges, no stat tiles, no dividers
    * one accent colour per meaning, taken from the daisyUI theme

Every page is generated from the same shell here so the four pages cannot drift
apart in typography, measure, or navigation.

Run:  python3 scripts/20_build_pages.py
Out:  index.html, proof.html, response.html, whales.html
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FINGERPRINT = "df2f8b9972c40bfdd132366a58b4780f65f23feba1ef20a060c25d4eff2661ba"

PAGES = [
    ("index.html", "overview"),
    ("response.html", "the agent:// gap"),
    ("proof.html", "evidence"),
    ("whales.html", "whales"),
]


def nav(current: str) -> str:
    links = []
    for href, label in PAGES:
        cur = ' aria-current="page"' if href == current else ""
        weight = "font-medium opacity-100" if href == current else "opacity-55 hover:opacity-90"
        links.append(
            f'<a class="link link-hover {weight}" href="{href}"{cur}>{label}</a>')
    return "\n      ".join(links)


def shell(current: str, title: str, masthead: str, contents: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.14/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
</head>
<body class="bg-base-100 text-base-content antialiased">

<div class="sticky top-0 z-40 border-b border-base-300 bg-base-100/90 backdrop-blur">
  <div class="mx-auto flex h-12 max-w-[68rem] items-center justify-between px-6 font-mono text-[12px] leading-none">
    <a class="opacity-70 hover:opacity-100" href="index.html">MARCO</a>
    <nav class="flex items-center gap-4 sm:gap-6" aria-label="Sections">
      {nav(current)}
    </nav>
  </div>
</div>

<article class="mx-auto max-w-[46rem] px-6">

{masthead}

{contents}

{body}

</article>

<footer class="mt-4 border-t border-base-300">
  <div class="mx-auto max-w-[46rem] px-6 py-12 font-mono text-[12px] leading-relaxed opacity-55">
    <p>Every value on this page is recomputable from <span class="break-all">primer.seed.json</span>. The command that checks the pages is <span class="break-all">python3 scripts/11_final_pass.py</span>.</p>
    <p class="mt-3 break-all">seed fingerprint {FINGERPRINT}</p>
  </div>
</footer>

<script src="assets/viz.js"></script>
</body>
</html>
"""


def masthead(kicker: str, title: str, dek: str, meta: list[str]) -> str:
    items = "".join(
        f'<span class="whitespace-nowrap">{m}</span>' for m in meta)
    return f"""  <header class="pb-4 pt-16 sm:pt-20">
    <p class="font-mono text-[11.5px] uppercase tracking-[0.2em] opacity-45">{kicker}</p>
    <h1 class="mt-6 font-serif text-[2.1rem] leading-[1.1] tracking-[-0.015em] sm:text-[2.7rem]">{title}</h1>
    <p class="mt-6 font-serif text-[1.15rem] leading-[1.62] opacity-70">{dek}</p>
    <div class="mt-9 flex flex-wrap gap-x-7 gap-y-2 border-t border-base-300 pt-4 font-mono text-[11.5px] opacity-55">
      {items}
    </div>
  </header>"""


def contents(items: list[tuple[str, str]]) -> str:
    rows = "\n".join(
        f'      <li class="flex gap-3"><a class="link link-hover opacity-80 hover:opacity-100" '
        f'href="#{anchor}"><span class="font-mono text-[11.5px] opacity-45">{i}</span> '
        f'<span class="ml-1">{label}</span></a></li>'
        for i, (anchor, label) in enumerate(items, 1))
    return f"""  <nav class="mb-2 border-y border-base-300 py-6" aria-label="Contents">
    <p class="mb-3 font-mono text-[11px] uppercase tracking-[0.2em] opacity-45">Contents</p>
    <ol class="space-y-1.5 font-serif text-[15px]">
{rows}
    </ol>
  </nav>"""


def section(anchor: str, n: int, title: str, blocks: list[str]) -> str:
    body = "\n".join(blocks)
    return f"""  <section id="{anchor}" class="scroll-mt-16 border-b border-base-300 py-11 last:border-b-0">
    <h2 class="mb-6 font-serif text-[1.55rem] leading-snug tracking-[-0.01em]">
      <span class="mr-3 font-mono text-[13px] align-middle opacity-40">{n}</span>{title}
    </h2>
{body}
  </section>"""


def prose(*paras: str) -> str:
    ps = "\n".join(f'    <p>{p}</p>' for p in paras)
    return f'    <div class="space-y-5 font-serif text-[1.0625rem] leading-[1.78]">\n{ps}\n    </div>'


def note(text: str, kind: str = "primary") -> str:
    return (f'    <aside class="my-7 border-l-2 border-{kind} pl-5 font-serif '
            f'text-[0.97rem] leading-[1.72] opacity-80">{text}</aside>')


def figure(mount: str, caption: str, aria: str, wide: bool = True) -> str:
    bleed = "lg:-mx-14" if wide else ""
    return f"""    <figure class="mt-9 {bleed}">
      <div class="rounded border border-base-300 bg-base-100 p-4">
        <div id="{mount}" role="img" aria-label="{aria}"></div>
      </div>
      <figcaption class="mt-3 font-mono text-[12px] leading-[1.65] opacity-60">{caption}</figcaption>
    </figure>"""


def values(pairs: list[tuple[str, str, str | None]]) -> str:
    rows = []
    for label, value, sub in pairs:
        subline = (f'<div class="mt-1 font-mono text-[11.5px] opacity-45">{sub}</div>'
                   if sub else "")
        rows.append(
            f'      <div class="flex flex-col gap-1 border-b border-base-300/70 py-3 last:border-b-0">'
            f'<dt class="font-mono text-[11.5px] uppercase tracking-[0.12em] opacity-50">{label}</dt>'
            f'<dd class="font-mono text-[15px] break-all">{value}</dd>{subline}</div>')
    return f'    <dl class="my-7 border-t border-base-300">\n' + "\n".join(rows) + "\n    </dl>"


def code(label: str, *lines: str) -> str:
    body = "\n".join(f'        <div class="break-all">{ln}</div>' for ln in lines)
    return f"""    <div class="my-7">
      <p class="mb-2 font-mono text-[11px] uppercase tracking-[0.18em] opacity-45">{label}</p>
      <div class="overflow-x-auto rounded border border-base-300 bg-base-200/50 px-4 py-3 font-mono text-[12.5px] leading-[1.75]">
{body}
      </div>
    </div>"""


def table(headers: list[str], rows: list[list[str]], caption: str | None = None) -> str:
    th = "".join(
        f'<th class="pb-2 pr-5 text-left font-mono text-[11px] uppercase tracking-[0.12em] '
        f'opacity-50">{h}</th>' for h in headers)
    trs = []
    for r in rows:
        tds = "".join(
            f'<td class="border-t border-base-300/70 py-2.5 pr-5 align-top">{c}</td>' for c in r)
        trs.append(f"        <tr>{tds}</tr>")
    cap = (f'\n      <figcaption class="mt-3 font-mono text-[12px] leading-[1.65] opacity-60">'
           f'{caption}</figcaption>') if caption else ""
    return f"""    <figure class="mt-7 overflow-x-auto">
      <table class="w-full font-serif text-[15px]">
        <thead><tr>{th}</tr></thead>
        <tbody>
{chr(10).join(trs)}
        </tbody>
      </table>{cap}
    </figure>"""


def chat(who: str, text: str, side: str = "start", footer: str | None = None) -> str:
    align = "chat-start" if side == "start" else "chat-end"
    bubble = "chat-bubble-primary" if side == "start" else "chat-bubble-neutral"
    foot = (f'\n      <div class="chat-footer mt-1 font-mono text-[11.5px] opacity-50">{footer}</div>'
            if footer else "")
    return f"""    <div class="chat {align} w-full mt-5">
      <div class="chat-header mb-1 font-mono text-[12px]">{who}</div>
      <div class="chat-bubble {bubble} max-w-[min(64ch,92%)] break-words font-mono text-[13px] leading-relaxed">{text}</div>{foot}
    </div>"""


# ===========================================================================
# index.html
# ===========================================================================
INDEX_BODY = "\n\n".join([
    section("s1", 1, "What comes out, and why there are two objects", [
        prose(
            "An agent answers 45 plain statements about the place it is in. The answers "
            "become two objects, and the separation between them is the whole design.",
            "The <strong>address</strong> is 18 syllables, written with a leading \u2301. It is "
            "fuzzy on purpose: places that are alike read alike, so the distance between two "
            "addresses is a distance you can measure. The <strong>root</strong> is 64 characters, "
            "written with a leading !. It is exact, which means it is equal or unrelated and "
            "nothing in between.",
            "One value cannot do both jobs. A value that stays close for nearby places cannot "
            "also be exact, and a value that is exact throws all nearness away. Two objects let "
            "one system have both.",
        ),
        code("address, for the kitchen with a friend",
             "\u2301 ma.mo.ma.ma.ru\u00b7ma.me.ki.va.ki+ve.ki.va.tu.ru~ki.ru.ki"),
        code("root, for the same answers",
             "!efe87ba9113b03473d9a657f01b994b88cd91bd0601d7131868d0bacbc6e9807"),
        table(
            ["question", "the address", "the root"],
            [["short enough to say out loud?", "yes, 18 syllables in four beats",
              "no, 64 characters"],
             ["do nearby places read alike?", "yes, by construction",
              "no, one letter changes everything"],
             ["does it prove two systems claim the same thing?", "no",
              "yes, equal or unrelated"],
             ["is it a location?", "yes", "no"]],
            "Table 1. The two objects do not overlap. Neither can answer the other's question."),
        note("The address is descriptive and must never authorise anything. Identity stays with "
             "the name the other protocol assigns, and the root answers exactly one question: are "
             "these the same, yes or no."),
    ]),
    section("s2", 2, "Six families that never spoke agreed on where they were", [
        prose(
            "Six model families were each asked about the same six places, one place per call. "
            "Each family was built by a different organisation, trained on different data, and "
            "given no sight of any other family's answers. The question never changed: which of "
            "the 45 statements are true of this place?",
            "Across 90 comparisons the same place came out nearest in 87 of them. Guessing one of "
            "six places would have scored about 17 per cent. Each family answered from its own "
            "space, and the spaces lined up.",
        ),
        figure("viz-controls",
               "Figure 1. The real result beside two deliberate breakages and chance. Both nulls "
               "sit at chance, with one standard deviation drawn, over 6,000 trials each.",
               "The real result at 96.7 per cent beside a label-shuffle null at 16.9 per cent, a "
               "random-vocabulary null at 20.9 per cent, and chance at 16.7 per cent."),
        note("All six families were handed the same 45 statements. That is the whole of the "
             "result and also its boundary. It shows the frame is usable by systems that share "
             "nothing else. It does not show that systems with different vocabularies would "
             "invent the same one. The families agreed with each other on 88.8 per cent of their "
             "statements, and the addresses inherit that agreement.", "warning"),
    ]),
    section("s3", 3, "Everything both sides need is 3,300 bytes", [
        prose(
            "A registry has to list what it knows. This does the opposite. It ships one small "
            "file of statements and geometry, and both sides work out the rest. There is no list "
            "of places and no list of the 45 statements.",
            "The seed has 11 top-level keys. One of them is about 70 per cent of the weight, and "
            "three of them are rules rather than content at all.",
        ),
        figure("viz-seedKeys",
               "Figure 2. Every top-level key, drawn to the bytes it holds. The plain statements "
               "are nearly all of it. The rules, including the ordering rule, are almost free.",
               "The eleven top-level keys of the seed as bars sized by the bytes each holds."),
        figure("viz-sizeCompare",
               "Figure 3. The seed against the frame it rebuilds and against the registry it "
               "replaces, which is 20.47 times larger. The first two bars are barely visible "
               "beside the third, which is the point.",
               "Three bars on one scale: 3,300 bytes sent, 4,532 bytes rebuilt, and 67,561 bytes "
               "if the whole registry were shipped instead."),
        note("The derived part is never sent. Both sides rebuild the frame from the same 3,300 "
             "bytes and compare the seed fingerprint before anything else happens. That is why "
             "the seed can be small, the frame large, and neither side has to trust the other."),
    ]),
    section("s4", 4, "From the seed to an address and a root, in eight stages", [
        prose(
            "Nothing below needs a server or a key. Each stage takes the one before it and "
            "applies a single rule. Walk it with the buttons: every value shown is the real value "
            "for one actual place.",
        ),
        figure("viz-ladder",
               "Figure 4. The eight stages. Stages 1 to 7 produce the address. Stage 8 produces "
               "the root, which is a separate object rather than a longer address.",
               "Eight stages from the seed to an address and a root, each showing the real "
               "intermediate value for one place."),
    ]),
    section("s5", 5, "The seed holds a rule for ordering, not an order", [
        prose(
            "The key called partition holds no sequence. It holds the rule that makes one, by "
            "measuring which statement splits 204 named places most evenly. Both sides run that "
            "rule and get the same order without either sending it.",
            "That is the difference between sending the answers and sending the arithmetic that "
            "produces them. A registry ships the answers. This ships the rule.",
        ),
        figure("viz-bootstrap",
               "Figure 5. The rule working through all 204 places. No list of statements to "
               "check exists anywhere in the seed. The trace is what the rule chose, and the "
               "dashed line is what perfectly even halving would do.",
               "The candidate set falling from 204 places towards one as the generator picks its "
               "own statements to check, on a log scale."),
        figure("viz-precision",
               "Figure 6. The same six places, read at more and more statements. Three addresses "
               "at one statement, six at six. The recorded number of times the count fell is zero.",
               "The number of distinct addresses the six places have as more statements are read, "
               "rising from three to six and never falling."),
    ]),
    section("s6", 6, "Six separate lineages, one arrangement", [
        prose(
            "If the addresses hold real structure, then laying the six places out by distance "
            "alone should recover the arrangement a person would draw. Nothing about the layout "
            "below is chosen by hand. It is fitted to the address distances.",
        ),
        figure("viz-manifold",
               "Figure 7. Positions fitted to address distance alone. Two places drawn close are "
               "close in the address. The two kitchens land 9 letters apart, and the dark empty "
               "room lands 23 from the kitchen with a friend.",
               "Six places positioned only by the distances between their addresses."),
        figure("viz-matrix",
               "Figure 8. All 15 pairs. The order matches the distances written down from the "
               "descriptions before anyone looked at the addresses: rank correlation 0.9286 over "
               "all 15.",
               "A six by six heatmap of address distances between all pairs of the six places."),
        prose(
            "The root behaves differently, and it should. Identical roots are rarer and clustered "
            "rather than spread evenly. That is what an exact object looks like when six systems "
            "answer independently.",
        ),
        figure("viz-rootBars",
               "Figure 9. The exact agreement, place by place. A root is not a score, so the "
               "only honest summary is how many families returned the identical value.",
               "For each of six places, how many of six independent model families produced the "
               "identical root."),
    ]),
    section("s7", 7, "Reproducing any value on this page", [
        prose(
            "That is the point of publishing the seed. Hand someone the same file and their "
            "answers match yours character for character, without either of you trusting the "
            "other. The evidence page takes the same machinery apart and names what would falsify "
            "it.",
        ),
        code("the three commands that check this repository",
             "python3 -m venv .venv &amp;&amp; .venv/bin/pip install -r requirements.txt",
             "python3 demo.py                       # the whole ladder, in one pass",
             "python3 scripts/11_final_pass.py      # style, structure and claim checks"),
    ]),
])

INDEX_META = [
    "seed fingerprint df2f8b99\u2026",
    "seed 3,300 bytes",
    "45 statements",
    "6 model families, 6 places, 90 comparisons",
    "total cost $0.05",
]

# ===========================================================================
# proof.html
# ===========================================================================
PROOF_BODY = "\n\n".join([
    section("s1", 1, "A test anyone can run, in about two minutes", [
        prose(
            "The strongest thing here is not a number. It is that a reader can check the central "
            "claim without a key, a terminal, or any understanding of the code.",
            "Scan the code in Figure 1 into one assistant, without saying what it is for. Ask a "
            "second assistant, in a different app. Tick both sets of answers on the card in "
            "Figure 2 and compare. If the two sets agree, the two systems are working from the "
            "same frame. If they do not, the claim on this page is wrong.",
        ),
        f"""    <div class="mt-9 grid grid-cols-1 gap-8 lg:-mx-14 lg:grid-cols-2">
      <figure>
        <img src="assets/figures/field-test-qr.svg" alt="A QR code holding sixteen statements a person can answer about a place, and one place described in plain English" class="w-full max-w-[22rem] rounded border border-base-300 bg-base-100 p-4">
        <figcaption class="mt-3 font-mono text-[12px] leading-[1.65] opacity-60">Figure 1. The whole test fits in this code: 1,062 bytes, QR version 27, medium error correction, 125 modules.</figcaption>
      </figure>
      <figure>
        <img src="assets/figures/field-test-card.svg" alt="The card to fill in, with the sixteen numbered statements and two blank columns" class="w-full rounded border border-base-300 bg-base-100">
        <figcaption class="mt-3 font-mono text-[12px] leading-[1.65] opacity-60">Figure 2. The card to print or copy, with a column for each assistant and what a disagreement would mean.</figcaption>
      </figure>
    </div>""",
        prose(
            "The place the code describes is a quiet library at night, in one paragraph and "
            "nothing else. Read it and answer the sixteen statements yourself before you look at "
            "the expected answers, because that is exactly what you are asking the assistants to "
            "do.",
        ),
        chat("a person, describing a place",
             "You are alone in a small private study room in a library, late at night. The door "
             "is closed. Through the window you can see the street lamps, and you can hear the "
             "building's heating. There are books and papers within reach on the desk.<br><br>"
             "Nobody else is in the room and nobody is watching. You are part way through reading "
             "something. You cannot change what is in the room, and you expect to leave when you "
             "are finished."),
        table(
            ["#", "the statement", "true here?"],
            [["1", "I can see inside this place", "true"],
             ["2", "I can see out of this place", "true"],
             ["3", "I can see other people", "false"],
             ["4", "I can see words", "true"],
             ["5", "I can hear sound", "true"],
             ["6", "I can reach objects near me", "true"],
             ["7", "I can reach other people", "false"],
             ["8", "I cannot reach anything", "false"],
             ["9", "I can change things here", "false"],
             ["10", "I cannot change anything", "true"],
             ["11", "Nobody else is here", "true"],
             ["12", "One other is here", "false"],
             ["13", "Someone is watching me", "false"],
             ["14", "This place is private", "true"],
             ["15", "I cannot leave this place", "false"],
             ["16", "Work is in progress", "true"]],
            "Table 1. The sixteen statements and the answers the description supports."),
        values([
            ("expected answers", "1, 2, 4, 5, 6, 10, 11, 14, 16", "nine statements"),
            ("address, full seed", "\u2301 se.re.ni.ko.mu\u00b7mo.ru.ki.va.ke+ru.ki.va.so.ru~ki.ro.ta", None),
            ("address, sixteen-statement card", "\u2301 ma.tu.me.ma", "a genuine prefix, cut short"),
            ("root", "!7343e3b49ce82b0aaae335b1095d14c9c45645254a4ab5bc0875b70545c9d3b5", None),
        ]),
        note("<strong>This fixture was wrong once, and it was models that caught it.</strong> "
             "Statement 10 reads I cannot change anything, and the description says you cannot "
             "change what is in the room. An earlier version of this expected answer left "
             "statement 10 out: eight numbers instead of nine. Four independent models were asked, "
             "and three of them answered with the same nine numbers, statement 10 included. They "
             "disagreed with the hand-written expectation and agreed with each other and with the "
             "description. The fixture was corrected to match the models, not the other way round, "
             "and the raw disagreement is kept in evidence/field-test-answers.json rather than "
             "quietly patched. In a space like this, the measurement is more likely to be wrong "
             "than the thing it measures."),
        note("The fourth model, gemma-4-31b-it, answered all sixteen statements true. That is not "
             "agreement. It is a failure to tell one statement from another, and it is reported "
             "here as a failure rather than counted as a match. Most assistants will answer the "
             "same way, and that is the honest shape of this result: the test is easy to pass and "
             "it is still a test, because it could fail. The limit of the sixteen-statement card "
             "is real and is stated rather than hidden. Cutting the vocabulary changes which "
             "statements carry the most weight, so the short address does not match the first "
             "syllables of the full address.", "warning"),
    ]),
    section("s2", 2, "The same answers give the same address every time", [
        prose(
            "An address is useful only if it holds still. If the same answers could produce two "
            "different addresses, nothing could be compared. So the same place is named over and "
            "over, three different ways, and all three agree.",
            "Fifty runs inside one process, fifty runs across fresh processes, and a set of runs "
            "with the clock pinned so that no clock reading can reach the result. The number of "
            "distinct outputs is 1 in every case.",
        ),
        values([
            ("distinct outputs, 50 pinned runs", "1", "clock pinned, so time cannot leak in"),
            ("distinct outputs, 50 unpinned runs", "1", "no dependence on the clock"),
            ("distinct outputs, fresh processes", "1", "identical to the in-process value"),
        ]),
        note("A timestamp is not part of an address, and the check above is why. If a clock "
             "reading could reach the address, the same place would name itself differently every "
             "second and nothing could be compared at all. Time belongs to the root, and only when "
             "a caller asks for it."),
    ]),
    section("s3", 3, "Reading further never blurs two places together", [
        prose(
            "Six places are named six times, keeping the first 1 statement, then 2, 3, 4, 5 and 6. "
            "At one statement they fall into 3 addresses. At three statements they make 4, at four "
            "they make 5, and at six all six are apart. The count never falls, and the recorded "
            "number of violations is 0.",
            "That property is what makes a short address safe to publish. A prefix is a region, "
            "never a lie.",
        ),
        figure("viz-precision",
               "Figure 3. The same address read at more and more statements. Every step narrows "
               "the place down, and no step contradicts an earlier one. Recorded violations: 0.",
               "The number of distinct addresses the six places have as more statements are read."),
    ]),
    section("s4", 4, "How far apart two addresses are, and whether that matches the places", [
        prose(
            "All 15 pairs of the six places were measured. The distances were written down before "
            "anyone looked at the addresses, from how much the descriptions themselves differ. The "
            "two lists were then compared by rank, and they agree at 0.9286 across all 15 pairs.",
            "One preregistered expectation failed, and it is worth stating plainly. It expected "
            "the two kitchens to be strictly nearest and then the shared workshop. In fact the "
            "kitchen alone and the shared workshop both sit at 9 letters from the kitchen with a "
            "friend, so the strict ordering does not hold. It is reported as a tie. The weaker "
            "ordering does hold: the near pairs sit below the far ones, all the way out.",
        ),
        figure("viz-manifold",
               "Figure 4. The six places laid out from the address distances alone. The "
               "arrangement is not drawn by hand, it is fitted. Two places that render close are "
               "close in the address.",
               "Six places positioned only by the distances between their addresses."),
        table(
            ["pair", "written down before looking", "measured in the address", "agrees?"],
            [["kitchen with friend \u00b7 kitchen alone", "near", "9 letters", "yes"],
             ["kitchen with friend \u00b7 shared workshop",
              "near, and strictly after the pair above", "9 letters, a tie", "tie"],
             ["kitchen with friend \u00b7 warehouse alone", "far", "16 letters", "yes"],
             ["kitchen with friend \u00b7 dark empty room", "furthest", "23 letters", "yes"]],
            "Table 2. The four preregistered pairs, including the one the preregistration got "
            "wrong. It stays in the table rather than disappearing from it."),
    ]),
    section("s5", 5, "The exact half, across separate families", [
        prose(
            "A root has no middle ground. Two sets of answers either produce the same 64 "
            "characters or they produce values with nothing in common. So the honest summary is a "
            "count: how many of six independent families returned the identical root for the same "
            "place.",
            "Five of the six agreed for the locked storeroom, and five of the six for the dark "
            "empty room. The weakest place is the warehouse, where two of the six agreed. Summed "
            "over all six places, 20 of the 36 family and place pairs fall in one largest agreeing "
            "group.",
        ),
        figure("viz-rootBars",
               "Figure 5. The exact agreement, place by place. Perfect agreement everywhere would "
               "be surprising. The empty cells are as informative as the filled ones.",
               "For each of six places, how many of six independent model families produced the "
               "identical root."),
        prose(
            "A root also works over part of the answers. Six statements out of 45 are enough for "
            "both sides to compare a value covering what they have agreed so far, without either "
            "side revealing the rest.",
            "A root can also absorb what an operator already holds. Fold a machine name into the "
            "answers and the root moves, while the address does not move a syllable.",
        ),
        values([
            ("root, nothing folded in", "efe87ba9113b03473d9a657f01b994b88cd91bd0601d7131868d0bacbc6e9807", None),
            ("root, with a machine name folded in", "2c4ccc8b91c64c130b8651c319c582b88aa4235b2ddcc8a7c5cf7a3152f54acd", "the address is unchanged"),
            ("root, with library versions folded in", "317b045886ffed7556631de3feb60a82d1c3b861239e5cc0d03fd024737e6eb4", "the address is unchanged"),
            ("root, with a machine name and an operator label", "4a325bb518b88ec0f248aa216f2f9743871b4052fdc85d0ee79610f5cede7dc2", "the address is unchanged"),
        ]),
    ]),
    section("s6", 6, "The harder version: find the matching place in another family", [
        prose(
            "The result above asks a weak question. A harder one: take one family's address for a "
            "place and find which of the six places another family meant, without being told. "
            "Across all fifteen family pairs, the right place came out nearest every single time.",
            "Three comparisons needed a tie broken rather than winning outright, which is why the "
            "strict count is 87 of 90 rather than 90 of 90. The three are named here, because a "
            "number without its exceptions is not checkable.",
        ),
        table(
            ["family pair", "right place nearest", "outright, no tie", "strict"],
            [["gemma-4-31b-it \u00b7 gpt-6-luna", "6 of 6", "5 of 6", "5 of 6"],
             ["glm-5.3 \u00b7 gpt-6-luna", "6 of 6", "5 of 6", "5 of 6"],
             ["gpt-6-luna \u00b7 mimo-v2.6-pro", "6 of 6", "5 of 6", "5 of 6"],
             ["the other twelve pairs", "6 of 6", "6 of 6", "6 of 6"]],
            "Table 3. Every pair finds the right place. Three do it with a tie at the top, and "
            "gpt-6-luna is the family in all three."),
        note("Assigning all fifteen pairs at once, rather than one at a time, also comes out at "
             "1.0. That rules out the weaker worry that a method which always returns something "
             "would score well by accident, because every family's six addresses have to be "
             "matched one to one."),
    ]),
    section("s7", 7, "What the numbers license, and what they do not", [
        prose(
            "Every family was handed the same 45 statements. That is the whole of the result and "
            "also its boundary. The frame works for systems that share nothing else. It is not "
            "evidence that systems would invent the same statements on their own.",
            "The families agreed with each other on 88.8 per cent of their statements, and the "
            "addresses inherit that agreement. The two nulls below show what is left once the "
            "shared vocabulary is taken away.",
            "A root commits to a list of answers. It does not commit to the reasoning that chose "
            "them, so nothing here proves that any model reasoned correctly. The address reports "
            "what a system said and never what it understood.",
        ),
        figure("viz-controls",
               "Figure 6. The cross-family result at 96.7 per cent beside two deliberate "
               "breakages and chance at 16.7 per cent. Both nulls sit at chance, with one standard "
               "deviation drawn, over 6,000 trials each.",
               "The cross-family result at 96.7 per cent beside a label-shuffle null at 16.9 per "
               "cent, a random-vocabulary null at 20.9 per cent, and chance at 16.7 per cent."),
        code("the checks behind this page",
             "python3 scripts/09_validate.py       # the validation bundle",
             "python3 scripts/11_final_pass.py     # style, structure and claim checks"),
    ]),
])

PROOF_META = [
    "seed fingerprint df2f8b99\u2026",
    "6 families, 6 places, 90 comparisons",
    "36 calls recorded verbatim",
    "one preregistered expectation failed, and is reported",
]

# ===========================================================================
# response.html
# ===========================================================================
RESPONSE_BODY = "\n\n".join([
    section("s1", 1, "Two companies name the same job differently", [
        prose(
            "Start with one job and two names for it. One company calls the job of approving a "
            "change /workflow/approval. Another calls the same job /process/authorize. The two "
            "paths share no word at all.",
            "The paper's identifier is built by hashing an agent's list of capabilities. A hash "
            "turns any list into a fixed-length code, and changing one entry changes the code "
            "completely. That is the right property for a name, because a name that drifted "
            "whenever an agent learned something could not refer to anything.",
            "The same property is why the scheme says nothing about location. Two agents doing "
            "nearly the same job get two unrelated codes, and there is no way to measure a gap "
            "between two codes. Text has no distance. Two house names, Rose Cottage and The Roses, "
            "are not one metre apart or three metres apart. They are the same or they are "
            "different.",
            "The paper names this weakness in itself, and its own remedy is an external mapping "
            "service: a second system to run, and a second source of truth that can drift away "
            "from both of the things it maps.",
        ),
        code("one job, two names, no shared word",
             "acme.com     /workflow/approval",
             "globex.io    /process/authorize"),
        note("Nothing below replaces the identifier. The address is added beside it. The name "
             "still does identity and authorisation exactly as the paper designed it, and the "
             "address is never used to authorise anything."),
    ]),
    section("s2", 2, "The two methods, on the same four queries", [
        prose(
            "Each query is one company's own capability path, asked against the other company's "
            "nine agents. The distance is in letters of an address, out of 36.",
        ),
        table(
            ["query, as issued", "by matching the path", "by nearest address", "letters apart"],
            [["workflow/approval", "nothing, a miss", "process/authorize", "2"],
             ["workflow/build", "nothing, a miss", "process/compile", "3"],
             ["workflow/rollback", "nothing, a miss", "process/revert", "2"],
             ["process/audit", "five results, every process path including the decoy",
              "process/review", "4"]],
            "Table 1. The single hit by path is an accident: the audit query shares its first "
            "segment with every process path on the other side, so one of the five results "
            "happens to be right. A shared string is not a shared meaning."),
        values([
            ("recall by matching the path", "1 of 4", "and the one hit is a prefix accident"),
            ("recall by nearest address", "4 of 4", "in the first position"),
            ("decoy returned as nearest", "0 of 4", "the decoy exists so an always-returns method fails"),
        ]),
        figure("viz-capability",
               "Figure 1. All nine agents, laid out from the distances between their addresses and "
               "nothing else. No path, no job label and no company name was used to place them. "
               "The four green lines are jobs that match, and none of them share a word.",
               "Nine agents from two organisations, laid out by address distance only, with the "
               "four equivalent pairs joined."),
        prose(
            "Twenty pairs of agents were measured rather than the four queries only. The four "
            "equivalent pairs sit a mean of 2.75 letters apart. The sixteen other pairs sit a mean "
            "of 24 letters apart. The separation is 21.25 letters, and it was not assigned by "
            "anybody.",
            "Shuffling the labels and asking again scores 19.9 per cent recall, with a spread of "
            "22.3, against a chance of 20 per cent. The method finds all four equivalents. The "
            "shuffle finds one.",
            "The same machinery measures at 96.7 per cent on the cross-family result, against a "
            "chance of 16.7 per cent, which is the number this page is trying to move.",
        ),
    ]),
    section("s3", 3, "An agent in a layered environment has three places, not one", [
        prose(
            "A running agent does not sit in one place. It sits in an environment with defaults, a "
            "project layer over those defaults, and a session that overrides the project. Each "
            "layer can change which statements are true, so each layer produces its own address "
            "and its own root.",
            "In the recorded environment the three positions sit 2, 5 and 3 letters apart. They "
            "share most of their letters because they inherit the same lower layers, and they stay "
            "distinguishable because each one overrides something the others do not.",
        ),
        figure("viz-layers",
               "Figure 2. The three layers of one environment, and a place with nothing in common "
               "for scale. The layers inherit, so they read as near. Nothing in common reads as "
               "far.",
               "Three positions in one layered environment, placed by address distance, with a "
               "sealed empty room far away for scale."),
        table(
            ["layer", "statements true", "what it adds", "letters from below"],
            [["environment defaults", "12", "the starting point", "\u00b7"],
             ["project layer", "14",
              "this place can be seen from outside, and help can be reached", "2"],
             ["session override", "16",
              "this place is temporary, and the work is nearly over", "3"]],
            "Table 2. Each layer adds statements rather than replacing the ones below. Two "
            "statements added at each step, two and three letters of movement, and the roots never "
            "match because the answers never match."),
        note("Two of the three layers share 29 of their first 45 answers, which is why they read "
             "as near. The sealed empty room, used as a control, sits 24 letters from the "
             "defaults. That is more than ten times the distance between any two layers of the "
             "same environment."),
    ]),
    section("s4", 4, "Two agents, one question", [
        prose(
            "Everything above is a measurement between systems that were never talking to each "
            "other. The same machinery works as a live exchange. One agent holds a place and "
            "never names it. The other holds the geometry and has to find it by asking.",
            "The hider opens by disclosing one syllable. The seeker chooses the single statement "
            "that splits the remaining candidates most evenly, asks it, and gets an answer. That "
            "is one question and one model call. The seeker then rebuilds the address from the "
            "answers, compares the root, and accepts or does not.",
        ),
        figure("viz-turn",
               "Figure 3. The whole exchange. The hider is gpt-6-luna, told which place it is in "
               "and never asked to name it. The question was whether it can see other people, "
               "answered YES, and the place found was the kitchen with a friend. Verdict: POLO.",
               "A timeline of the single exchange: one syllable disclosed, one statement asked, "
               "one answer, then verification of the root."),
        values([
            ("questions asked", "1", "chosen by how evenly it splits the candidates"),
            ("model calls", "1", "no retries"),
            ("cost of the exchange", "$0.000047", "one call, 287 tokens"),
            ("verdict", "POLO", "the root rebuilt from the answers matched"),
        ]),
        prose(
            "The seeker never accepts the hider's word. It rebuilds the address from the "
            "statements and compares the root. Two equal roots are the whole of the verification, "
            "and they need no server, no key and no cooperation from the other side.",
        ),
    ]),
    section("s5", 5, "Where the address has to stop", [
        prose(
            "The address is descriptive and never authoritative. It must not be used to grant "
            "permission, to decide trust, or to identify anyone. A descriptive value that could "
            "authorise would be a second source of truth beside the one the paper already has, "
            "which is the problem this page set out to avoid.",
            "Two things are shown here and they should not be confused. The first is that "
            "equivalent work lands at a near address when the work happens in a similar kind of "
            "place. The second is that a name cannot measure a gap between two different names. "
            "Only the first is a claim about the world.",
            "The shared vocabulary caveat applies here too. Both organisations were mapped into "
            "the same 45 statements before anything was measured, so the result shows that the "
            "geometry finds equivalent work once both sides answer the same statements. It does "
            "not show that two organisations would independently write the same 45.",
        ),
        code("the script behind this page",
             "python3 scripts/07_capability_nearness.py"),
    ]),
])

RESPONSE_META = [
    "seed fingerprint df2f8b99\u2026",
    "two organisations, nine agents, four equivalent jobs",
    "4 of 4 found by address, 1 of 4 by path",
    "one live exchange, one question, one model call",
]

# ===========================================================================
# whales.html
# ===========================================================================
WHALES_BODY = "\n\n".join([
    section("s1", 1, "A coda is a rhythm, and a firing rate is a rate", [
        prose(
            "A vocalisation and a neural response are not naturally written in the same vocabulary. "
            "A field biologist may describe a sperm-whale coda as 5R or 1+1+3, report its tempo "
            "and inter-click intervals, and place it in a behavioural context. A neurophysiologist "
            "may describe the response to that sound as spike rate, latency, a trajectory through "
            "population activity, or a change in blood oxygen level. These are valid descriptions "
            "of different observables, not two names for one coordinate.",
            "The analogy to this repository is structural, not semantic. In MARCO an agent "
            "declares which of 45 statements are true, and a shared seed converts those answers "
            "into distances, a coarse-to-fine address, and a separate exact root. For whale work, "
            "a recording supplies measurable acoustic features rather than declared answers, and "
            "neural activity supplies a second observation space. The proposed bridge is a learned "
            "correspondence between the two spaces.",
        ),
        note("Note what is being claimed. A phrase address would be descriptive and "
             "neighbourhood-preserving. A recording checksum would identify an exact file while "
             "destroying neighbourhood. A neural prediction would be an empirical estimate of "
             "response, not a decoded message. That separation is implemented and measured in this "
             "repository, where it holds at 96.7 per cent against a chance of 16.7 per cent. That "
             "it will be useful for cetacean neurobiology is speculation."),
    ]),
    section("s2", 2, "What is established, and what is not", [
        prose(
            "Sperm-whale codas are stereotyped click sequences, roughly 3 to 40 clicks long, whose "
            "inter-click intervals define rhythm, and they are commonly notated in relative timing "
            "forms such as 5R and 1+1+3 (Rendell and Whitehead 2003). Codas overlap and are "
            "matched in interaction (Schulz and others 2008). Identity cues occur at unit, "
            "individual and clan level (Gero, Whitehead and Rendell 2016).",
            "Sharma and others (2024) report contextual and combinatorial structure: "
            "context-sensitive features called rubato and ornamentation are systematically "
            "controlled and imitated across whales, and these combine with context-independent "
            "rhythm and tempo to produce nearly an order of magnitude more distinguishable codas. "
            "That paper does not claim semantics, syntax, or that codas are a language, and the "
            "popular framing that they are is not supported by that source.",
            "Humpback song has a nested hierarchy of phrase, theme, song and song session (Payne "
            "and McVay 1971), and songs are culturally transmitted and can undergo "
            "population-level revolutions (Noad and others 2000; Garland and others 2011). "
            "Bottlenose-dolphin signature whistles are individually distinctive learned contours "
            "used as vocal labels and copied or addressed (Janik and others 2013). They are the "
            "strongest referential-label analogue here, but they are not demonstrated to be words.",
        ),
        note("What remains open is what the additional distinguishability does socially: "
             "recognition, coordination, turn-taking, affective modulation, or something else. A "
             "structured acoustic repertoire is not evidence of compositional meaning, and a "
             "behavioural hierarchy is not a linguistic grammar.", "warning"),
    ]),
    section("s3", 3, "Where neural decoding genuinely exists, and where it does not", [
        prose(
            "In bats, single-unit auditory-cortex recordings include neurons tuned to echo delay "
            "and velocity, yielding range-like maps. In zebra finches, single-unit "
            "auditory-forebrain responses encode conspecific song and tutor familiarity. In "
            "marmosets, single-unit activity tracks self-generated vocal feedback (Eliades and "
            "Wang 2008). In macaques, voice-selective temporal cortex has been studied with both "
            "imaging and single-unit recording (Petkov and others 2008).",
            "Cetacean neural data of this kind does not exist. There are no chronic implanted "
            "single-unit or electrocorticography recordings in wild cetaceans, and ethics, "
            "permits, animal size, immersion and cetacean neuroanatomy make the bat, songbird and "
            "marmoset paradigm unavailable. Non-invasive auditory evoked potentials and "
            "behavioural psychoacoustics exist. For this question, that is the ceiling.",
        ),
        note("Any claim of a whale phrase-to-neuron map is therefore speculation until a lawful, "
             "interpretable neural measurement exists. The distance between the two is precisely "
             "the scientific problem, not a gap that a pronounceable coordinate can close by "
             "rhetoric."),
    ]),
    section("s4", 4, "A concrete pipeline, and the controls that make it hard", [
        prose(
            "The pipeline below is one way to make the analogy testable. It replaces declared "
            "statements with measured acoustic features, keeps a fixed reference set, and asks "
            "whether the resulting address predicts a measured neural response.",
        ),
        figure("viz-pipeline",
               "Figure 1. From a calibrated recording to a phrase address, and from a neural "
               "response to a held-out prediction. The dashed boxes are the controls, and they are "
               "the hard part: every choice is made on training folds only and then frozen before "
               "the test fold is touched.",
               "A pipeline diagram: recording, segmentation, an 18-number phrase vector, 64 "
               "reference phrases, quantised distances, a phrase address, a neural response, a "
               "fitted mapping, and a held-out prediction, with the controls below."),
        prose(
            "The phrase vector has 18 measured dimensions: unit count, the first five inter-unit "
            "intervals, median tempo, three rubato statistics, a spectral-centroid trajectory at "
            "four temporal landmarks, early and late bandwidth, and two ornamentation scores. A "
            "fixed set of 64 reference phrases replaces the 45 declared statements. Distances are "
            "quantised into four levels whose thresholds are calibrated on training data only, and "
            "the axes are ordered by discriminative power measured on training folds.",
        ),
        note("Every feature needs held-out reliability estimates. Microphone placement, "
             "propagation, overlap and detector error can dominate the differences being measured, "
             "and poor reference phrases are a known failure mode: redundant ones collapse "
             "dimensions, outliers make every phrase look far away, and population-specific ones "
             "encode recording conditions rather than vocal structure.", "warning"),
        prose(
            "The controls are the hard part, and they have established names. Canonical "
            "correlation analysis goes back to Hotelling (1936) and can produce near-perfect "
            "in-sample correlation when the predictor and response dimensions approach the number "
            "of samples. A few hundred phrases against a population response containing thousands "
            "of neurons is exactly the regime where a spurious mapping is easy to find, because "
            "flexible projections can align noise, especially after searching reference sets, "
            "metrics, alignments and penalties.",
            "Circular analysis is the same error in another form: selecting features or "
            "coordinates because they fit the neural data, then evaluating them on those same "
            "data (Kriegeskorte and others 2009). Representational similarity analysis exists "
            "precisely because two spaces are not directly commensurate (Kriegeskorte and others "
            "2008), and encoding models predict neural measurements from stimulus features "
            "(Naselaris and others 2011; Huth and others 2016).",
        ),
        note("A broad search might vary a thousand reference sets, six feature metrics, five "
             "quantisation schemes, four axis-ordering rules and three response alignments, around "
             "360,000 topological candidates, and about 7.2 million fitted candidates once ridge "
             "penalties are included. Search multiplicity belongs in the null distribution, not in "
             "an afterthought. A candidate that wins millions of trials by chance has not "
             "discovered a map."),
    ]),
    section("s5", 5, "What is asserted here but never measured", [
        prose(
            "This page is a proposal and it should be read as one. The honest list is short and "
            "specific.",
        ),
        table(
            ["asserted", "status"],
            [["the same objects separate description, exact identity and prediction",
              "implemented and measured, in this repository"],
             ["a phrase address would organise a coda repertoire",
              "untested. No cetacean phrase has been given an address"],
             ["18 measured dimensions are the biologically relevant ones",
              "asserted, with no held-out reliability estimate behind it"],
             ["a linear map from phrase address to neural response exists",
              "speculative. There is no cetacean neural data to fit it to"],
             ["a successful map would mean the animal computes an address",
              "false as stated. It would mean the address preserves useful information"]],
            "Table 1. The distinction the whole page turns on: what is demonstrated in this "
            "repository, and what is not."),
        prose(
            "A locus, a phrase address, or a neural coordinate is descriptive and never "
            "authoritative. In a whale application, even a highly repeatable acoustic feature "
            "should not be promoted to a behavioural claim without independent evidence, and an "
            "inferred neural association should stay a hypothesis until it survives held-out "
            "subjects, temporal shuffles, decoys and search-corrected nulls.",
            "The strongest defensible outcome is therefore modest: a reproducible, "
            "topology-preserving description of vocal signals, plus a rigorously tested "
            "prediction of a particular neural measurement where such data exist. For cetaceans "
            "today the first object is feasible and the second is not established.",
        ),
    ]),
    section("s6", 6, "References", [
        f"""    <ol class="space-y-3 font-serif text-[14.5px] leading-[1.6] opacity-85">
      <li>Antunes, R. and others (2011). Animal Behaviour 81:723-730. <span class="font-mono text-[12.5px] opacity-60">doi:10.1016/j.anbehav.2010.12.019</span></li>
      <li>Eliades, S. and Wang, X. (2008). Journal of Neuroscience. <span class="font-mono text-[12.5px] opacity-60">Neural substrates of vocalization feedback monitoring in primate auditory cortex</span></li>
      <li>Garland, E. and others (2011). Proceedings of the Royal Society B. <span class="font-mono text-[12.5px] opacity-60">doi:10.1098/rspb.2011.0630</span></li>
      <li>Gero, S., Whitehead, H. and Rendell, L. (2016). Royal Society Open Science 3:150372. <span class="font-mono text-[12.5px] opacity-60">doi:10.1098/rsos.150372</span></li>
      <li>Hotelling, H. (1936). <span class="font-mono text-[12.5px] opacity-60">Relations between two sets of variates. Biometrika 28:321-377</span></li>
      <li>Huth, A. and others (2016). Nature. <span class="font-mono text-[12.5px] opacity-60">doi:10.1038/nature17637</span></li>
      <li>Janik, V. and others (2013). PNAS. <span class="font-mono text-[12.5px] opacity-60">doi:10.1073/pnas.1304459110</span></li>
      <li>Kriegeskorte, N. and others (2008). Frontiers in Human Neuroscience. <span class="font-mono text-[12.5px] opacity-60">doi:10.3389/neuro.01.1.1.004.2008</span></li>
      <li>Kriegeskorte, N. and others (2009). Nature Neuroscience. <span class="font-mono text-[12.5px] opacity-60">doi:10.1038/nn.2303</span></li>
      <li>Naselaris, T. and others (2011). NeuroImage. <span class="font-mono text-[12.5px] opacity-60">doi:10.1016/j.neuroimage.2010.07.073</span></li>
      <li>Noad, M. and others (2000). Proceedings of the Royal Society B. <span class="font-mono text-[12.5px] opacity-60">doi:10.1098/rspb.2000.1271</span></li>
      <li>Payne, R. and McVay, S. (1971). Science. <span class="font-mono text-[12.5px] opacity-60">doi:10.1126/science.173.3997.585</span></li>
      <li>Petkov, C. and others (2008). Neuron. <span class="font-mono text-[12.5px] opacity-60">A voice region in the monkey brain</span></li>
      <li>Rendell, L. and Whitehead, H. (2003). Proceedings of the Royal Society B 270:225-231. <span class="font-mono text-[12.5px] opacity-60">doi:10.1098/rspb.2002.2239</span></li>
      <li>Schoenemann, P. (1966). Psychometrika. <span class="font-mono text-[12.5px] opacity-60">doi:10.1007/BF02289451</span></li>
      <li>Schulz, T. and others (2008). Animal Behaviour 76:1977-1988. <span class="font-mono text-[12.5px] opacity-60">doi:10.1016/j.anbehav.2008.07.032</span></li>
      <li>Sharma, P. and others (2024). Nature Communications 15:3617. <span class="font-mono text-[12.5px] opacity-60">doi:10.1038/s41467-024-47221-8</span></li>
    </ol>""",
    ]),
])

WHALES_META = [
    "seed fingerprint df2f8b99\u2026",
    "an analogy, and its limits",
    "no cetacean neural data of the kind this needs exists",
    "all citations checked against the primary source",
]

# ===========================================================================
# assemble
# ===========================================================================

INDEX_CONTENTS = [
    ("s1", "What comes out, and why there are two objects"),
    ("s2", "Six families that never spoke agreed on where they were"),
    ("s3", "Everything both sides need is 3,300 bytes"),
    ("s4", "From the seed to an address and a root, in eight stages"),
    ("s5", "The seed holds a rule for ordering, not an order"),
    ("s6", "Six separate lineages, one arrangement"),
    ("s7", "Reproducing any value on this page"),
]
PROOF_CONTENTS = [
    ("s1", "A test anyone can run, in about two minutes"),
    ("s2", "The same answers give the same address every time"),
    ("s3", "Reading further never blurs two places together"),
    ("s4", "How far apart two addresses are, and whether that matches"),
    ("s5", "The exact half, across separate families"),
    ("s6", "The harder version: find the matching place in another family"),
    ("s7", "What the numbers license, and what they do not"),
]
RESPONSE_CONTENTS = [
    ("s1", "Two companies name the same job differently"),
    ("s2", "The two methods, on the same four queries"),
    ("s3", "An agent in a layered environment has three places, not one"),
    ("s4", "Two agents, one question"),
    ("s5", "Where the address has to stop"),
]
WHALES_CONTENTS = [
    ("s1", "A coda is a rhythm, and a firing rate is a rate"),
    ("s2", "What is established, and what is not"),
    ("s3", "Where neural decoding genuinely exists, and where it does not"),
    ("s4", "A concrete pipeline, and the controls that make it hard"),
    ("s5", "What is asserted here but never measured"),
    ("s6", "References"),
]

OUT = {
    "index.html": (
        "MARCO: an agent can say who it is, not where it is",
        masthead("MARCO \u00b7 a sense of place \u00b7 September 2026",
                 "An agent can say who it is. Nothing says where it is.",
                 "Forty-five plain statements about a place become a short address that says how "
                 "near other places are, and an exact root that says whether two systems mean the "
                 "same thing. Six model families that share no weights, no training data and no "
                 "context produced the same address for the same place in 87 of 90 comparisons.",
                 INDEX_META),
        contents(INDEX_CONTENTS), INDEX_BODY),
    "proof.html": (
        "Evidence: the same answer twice \u00b7 MARCO",
        masthead("MARCO \u00b7 evidence",
                 "The same answer twice",
                 "A claim that cannot fail is not a claim. Everything on this page could come out "
                 "the other way, and one preregistered expectation did. It is reported here rather "
                 "than dropped.",
                 PROOF_META),
        contents(PROOF_CONTENTS), PROOF_BODY),
    "response.html": (
        "The agent:// gap: a name says who, not where \u00b7 MARCO",
        masthead("a working response \u00b7 arXiv:2601.14567v2",
                 "What <em>agent://</em> is missing",
                 "The paper solves who. An identifier that answers who has nothing to say about "
                 "where, and that is not a fault in the paper. This page adds the second question "
                 "and measures what it is worth.",
                 RESPONSE_META),
        contents(RESPONSE_CONTENTS), RESPONSE_BODY),
    "whales.html": (
        "Can a whale phrase be given an address? \u00b7 MARCO",
        masthead("MARCO \u00b7 an analogy, and its limits",
                 "Can a whale phrase be given an address?",
                 "The same separation of objects that this repository implements might describe a "
                 "vocalisation, an exact recording, and a neural response. What is established, "
                 "what is contested, and the short list of things asserted but never measured.",
                 WHALES_META),
        contents(WHALES_CONTENTS), WHALES_BODY),
}


def main() -> int:
    for name, (title, head, toc, body) in OUT.items():
        html = shell(name, title, head, toc, body)
        (ROOT / name).write_text(html, encoding="utf-8")
        print(f"wrote {name}  {len(html.encode()):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
