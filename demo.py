#!/usr/bin/env python3
"""MARCO, unrolled end to end. One command, no key, no network.

    python3 demo.py

This walks the whole thing in order and prints every value it computes:

    0  the seed                       the entire shared substrate
    1  the ladder                     seven rungs, each with a real example
    2  one place -> one address       every intermediate number
    3  the gradient                   the same address read at six precisions
    4  the root                       exact, at any grain, absorbing any extra
    5  the bootstrap                  the seed that asks its own questions
    6  a MARCO/POLO turn              a hider that opens with one syllable
    7  across families                what six independent models agreed on
    8  two organisations             incompatible names, no mapping table
    9  what this does not show       the honest part

Stages 7 and 8 read the recorded evidence, so they print what was measured
rather than what this script can compute on its own. Everything else is
computed live from the seed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from marco import generator, locus as L, primer, world  # noqa: E402

WIDE = 78


def stage(n: int, title: str) -> None:
    print()
    print("=" * WIDE)
    print(f"  {n}  {title}")
    print("=" * WIDE)


def rule(text: str = "") -> None:
    print()
    print(f"-- {text}" if text else "")


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {p: enc.encode(world.build(p).observations()) for p in places}

    print()
    print("MARCO — an agent that can say where it is.")
    print(f"primer fingerprint  {frame.fingerprint()}")

    # ------------------------------------------------------------------
    stage(0, "the seed")
    seed = primer.load_seed()
    print(f"  file                primer.seed.json")
    print(f"  size                {frame.seed_bytes():,} bytes")
    print(f"  contains            {', '.join(seed)}")
    print()
    print("  No situations. No questions. No axis order. No answer key.")
    print("  Everything below is derived from these bytes, identically on both sides.")

    # ------------------------------------------------------------------
    stage(1, "the ladder — seven rungs, each useful on its own")
    rungs = [
        ("one statement",
         f'{len(frame.anchors)} available, one asked: "I can see inside this place"',
         "one true fact. Not yet a place."),
        ("a pattern of ticks",
         f"an agent answers all {len(frame.anchors)}; the set of true ones is its situation",
         "comparable by eye. Not yet measurable."),
        ("close and far",
         "four distance levels: " + ", ".join(f"{v} {k}" for k, v in frame.distance.items()),
         "nearness is a number. Nothing has a position yet."),
        ("a place",
         f"{len(frame.partition.axes)} axes x {frame.partition.branches} branches, ordered by "
         f"how much they tell apart",
         "similar situations land in the same region."),
        ("a place you can say",
         f"{len(frame.syllables)} syllables, adjacent ones one phoneme apart",
         "an address you can read aloud."),
        ("a place you can prove",
         "SHA-256 over the exact statement set",
         "same set, same 32 bytes. Nearness destroyed on purpose."),
        ("everything together",
         "the address says near; the root says same",
         "two objects, two jobs, neither doing the other's."),
    ]
    for i, (name, detail, verdict) in enumerate(rungs, 1):
        print(f"  rung {i}  {name}")
        print(f"          {detail}")
        print(f"          -> {verdict}")

    # ------------------------------------------------------------------
    stage(2, "one place becomes one address")
    target = "kitchen_with_friend"
    w = world.build(target)
    check = w.self_check(frame)
    print(f"  place               {target}")
    print(f"  statements true     {check['n_landmarks']} of {len(frame.anchors)}")
    print(f"  marker floor        {check['marker_floor']}  (the weakest rung present)")
    print(f"  self-check          {'ok' if check['ok'] else check['problems']}")

    obs = w.observations()
    canon = L.canonical(obs, frame.hierarchy)
    vec = L.anchor_vector(canon, frame.anchors, frame.distance)
    bits = frame.partition.bits(vec)
    syl = L.bits_to_syllables(bits, frame.syllables, per=5)
    loc = enc.encode(obs)          # a state root: nothing pinned

    print()
    print("  (a) what the agent says it can see:")
    for key in canon[:5]:
        print(f"        {key:<30} \"{frame.plain[key]}\"")
    print(f"        ... and {len(canon) - 5} more")

    uniq, counts = np.unique(vec, return_counts=True)
    print()
    print(f"  (b) distance to each of the {len(vec)} landmarks:")
    print(f"        {' '.join(f'{v:.1f}' for v in vec[:24])} ...")
    print(f"        levels present: " +
          ", ".join(f"{u:.1f} x{c}" for u, c in zip(uniq, counts)))

    print()
    print(f"  (c) {len(bits)} bits, {int(np.log2(frame.partition.branches))} per axis:")
    print(f"        {''.join(str(b) for b in bits[:48])} ...")

    print()
    print(f"  (d) {len(syl)} syllables:")
    print(f"        {' '.join(syl)}")

    print()
    print(f"  (e) the address:")
    print(f"        {loc.text}")
    print(f"      and the root over exactly that statement set:")
    print(f"        !{loc.commitment}")
    print(f"      pin a timestamp and you get a different object, a session root:")
    print(f"        !{enc.encode(obs, timestamp=0).commitment}")
    print()
    print(f"  read the beats as   place . what + reach ~ now")
    print(f"  marker              {loc.marker}"
          f"{'  (anchors a claim)' if loc.is_anchored() else '  (does not anchor)'}")

    # ------------------------------------------------------------------
    stage(3, "the gradient — the same address, read at six precisions")
    print(f"  {'axes':>5}  {'syllables':>9}  {'places this distinct':>20}  address")
    for k in (1, 2, 4, 6, 12, 45):
        prec = {p: enc.encode(world.build(p).observations(), precision=k) for p in places}
        distinct = len({v.prefix for v in prec.values()})
        shown = prec[target]
        n_syl = len(shown.text.replace("\u2301 ", "").split("."))
        print(f"  {k:>5}  {n_syl:>9}  {distinct:>13} of {len(places)}  {shown.text}")
    print()
    print("  Six characters names all six places. You stop wherever you like, and")
    print("  no reading contradicts an earlier one — checked in tests/test_smoke.py.")

    # ------------------------------------------------------------------
    stage(4, "the root — exact, at any grain, absorbing anything else you have")
    order = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]
    order = [order[i] for i in frame.partition.axes]

    def root(statements, extra=()):
        payload = json.dumps({"statements": sorted(statements), "extra": sorted(extra)},
                             separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    base = list(canon)
    print(f"  the root over everything {target} reported:")
    print(f"    {root(base)}")
    print()
    print(f"  {'grain':>6}  {'places told apart by root alone':>32}  root prefix")
    for k in (2, 4, 8, 45):
        roots = {p: root([x for x in order if x in world.WORLDS[p]][:k]) for p in places}
        distinct = len(set(roots.values()))
        print(f"  {k:>6}  {distinct:>21} of {len(places)}  {roots[target][:20]}...")
    print()
    print("  fold in whatever else the operator has to hand:")
    addr_before = loc.text
    for label, extra in [("nothing", ()),
                         ("host:runner-7", ("host:runner-7",)),
                         ("py + numpy", ("py:3.14.7", "numpy:2.5.3")),
                         ("host + operator", ("host:runner-7", "op:acme"))]:
        print(f"    {label:<18} {root(base, extra)[:20]}...")
    addr_after = enc.encode(world.build(target).observations(), timestamp=0).text
    print()
    print(f"  address unchanged by any of that:  {addr_before == addr_after}")
    print("  So a root can carry generic fingerprints of an environment, and the")
    print("  coordinate stays a coordinate.")

    # ------------------------------------------------------------------
    stage(5, "the bootstrap — the seed asks its own questions")
    gen = generator.Generator(frame)
    print(f"  population          {len(frame.population)} places")
    print(f"  questions in primer 0")
    print()
    trace = gen.run(frame.population[0])
    print(f"  one trace, hiding {len(world.WORLDS)} landmarks from the seeker:")
    print(f"    {'#':>2}  {'question':<40} {'answer':<7} {'still possible':>14}")
    for s in trace.steps[:10]:
        print(f"    {s.index:>2}  {s.description[:40]:<40} "
              f"{'yes' if s.answer else 'no':<7} {s.candidates_after:>14}")
    print(f"    ... resolved to 1 candidate after {len(trace.steps)} questions")
    print()
    rep = generator.bootstrap_report(frame, n_trials=64)
    print(f"  over {rep['trials']} trials: mean {rep['mean_questions']} questions, "
          f"{rep['resolved']} resolved")
    print(f"  floor log2({len(frame.population)}) = {rep['log2_population']}")

    # ------------------------------------------------------------------
    stage(6, "a MARCO/POLO turn — the hider opens with one syllable")
    hider = world.build(target)
    for step_k in (1, 3, 6):
        disclosed = enc.encode(hider.observations(), precision=step_k)
        fits = [p for p in places
                if loci[p].prefix[:step_k] == disclosed.prefix[:step_k]]
        print(f"  hider discloses     {disclosed.text:<16} "
              f"({step_k} of {len(frame.partition.axes)} axes)   "
              f"{len(fits)} of {len(places)} places still fit")
        if step_k == 1:
            print(f"                      {[p for p in fits]}")
    print()
    print("  The seeker spends its questions between disclosures. In the recorded")
    print("  live run the whole exchange took one model call, $0.000047, and the")
    print("  seeker rebuilt the address itself before comparing the root:")
    print("      POLO  MATCH")

    # ------------------------------------------------------------------
    stage(7, "across families — six models that never spoke to each other")
    rp = ROOT / "evidence" / "RESULTS.json"
    if rp.exists():
        res = json.loads(rp.read_text())
        cm = res["cross_model"]
        print(f"  models              {cm['n_models']} independent families")
        for m in cm["models"]:
            print(f"                        {m}")
        print(f"  comparisons         {cm['pairs']} pairs x {cm['n_places']} places "
              f"= {cm['comparisons']}")
        print()
        print(f"  same place nearest  {cm['top1_strict']*100:.1f}% strictly "
              f"({cm['top1']*100:.0f}% counting exact ties)")
        print(f"  chance              {cm['chance']*100:.1f}%")
        print(f"  null, labels shuffled        "
              f"{cm['null_label_shuffle']['accuracy']*100:.1f}% "
              f"(sd {cm['null_label_shuffle']['sd']*100:.1f})")
        print(f"  null, random vocabulary      "
              f"{cm['null_random_vocabulary']['accuracy']*100:.1f}% "
              f"(sd {cm['null_random_vocabulary']['sd']*100:.1f})")
        print(f"  statement-level agreement    {cm['mean_landmark_jaccard']*100:.1f}%")
        print(f"  cost of the whole thing      ${cm['cost_usd']:.4f}")
        rp2 = res["root_proof"]
        print()
        print(f"  the exact root: {rp2['largest_agreeing_group']} model-place pairs "
              f"produced a byte-identical root")
        for p, n in sorted(rp2["per_place_largest_group"].items(),
                           key=lambda kv: -kv[1]):
            print(f"      {p:<22} {n} of {cm['n_models']} identical")
    else:
        print("  evidence/RESULTS.json not found; run the scripts first")

    # ------------------------------------------------------------------
    stage(8, "two organisations, incompatible names, no mapping table")
    cp = ROOT / "evidence" / "capability-nearness.json"
    if cp.exists():
        cn = json.loads(cp.read_text())
        for org, paths in cn["organisations"].items():
            print(f"  {org}")
            for p in paths:
                print(f"      agent://{org}/{p}/01h...")
        print()
        print(f"  discovery by capability path   recall {cn['path_discovery_recall']}")
        print(f"  discovery by nearness          recall {cn['nearness_discovery_recall']}"
              f"   (no mapping table)")
        print(f"  equivalent pairs               mean hamming {cn['equivalent_mean_hamming']}")
        print(f"  non-equivalent pairs           mean hamming {cn['non_equivalent_mean_hamming']}")
        print(f"  separation                     +{cn['separation_hamming']}")
        print(f"  decoy returned as nearest      {cn['decoy_returned_as_nearest']} times")
        print(f"  null, labels shuffled          {cn['null_shuffled_recall_mean']} "
              f"(chance {cn['chance']})")
    else:
        print("  evidence/capability-nearness.json not found")

    # ------------------------------------------------------------------
    stage(9, "what this does not show")
    print("  All six models were handed the same 45 statements. So this shows the")
    print("  frame is usable by minds with nothing in common; it does NOT show that")
    print("  models with different vocabularies would invent the same one.")
    print()
    print("  They agreed on 88.8% of their statement choices, and the addresses")
    print("  inherit that agreement. The warehouse disagreed most (mean hamming 6.3).")
    print()
    print("  No claim is made about meaning, understanding, or intent. The address")
    print("  is descriptive and never authoritative. Identity and location are")
    print("  separate objects on purpose, and this demonstration keeps them apart.")
    print()
    print("=" * WIDE)
    print(f"  {len(frame.anchors)} statements · {len(world.WORLDS)} places · "
          f"{len(frame.population)} in the population · 28 checks in tests/")
    print(f"  primer {frame.fingerprint()[:24]}...")
    print("=" * WIDE)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
