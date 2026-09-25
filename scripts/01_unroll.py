#!/usr/bin/env python3
"""Walk the primer from seed to coordinate, printing every calculation.

Run this first. It is the whole mechanism, in order, with nothing skipped:

    seed  ->  landmarks  ->  codebook  ->  ladder  ->  metric  ->  population
          ->  axis order ->  seal
    then:  one world  ->  canonical set  ->  distance vector  ->  bits
          ->  syllables  ->  "⌁ ..."

Nothing here is hidden behind a library call. Every intermediate value is
printed, and every one of them is a pure function of the seed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L   # noqa: E402
from marco import primer, world  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> int:
    seed = primer.load_seed()

    rule("STEP 1  the seed")
    print(f"  file            primer.seed.json")
    print(f"  bytes           {len(json.dumps(seed, ensure_ascii=False).encode())}")
    print(f"  keys            {', '.join(seed)}")
    print()
    print("  This is the entire transmitted object. It contains no situations, no")
    print("  questions, no axis order. Everything below is derived from it.")

    frame = primer.expand()

    rule("STEP 2  landmarks  (the shared chart)")
    print(f"  expansion       namespace -> relation -> values, in seed order")
    print(f"  namespaces      {len(seed['landmarks'])}")
    print(f"  landmarks       {len(frame.anchors)}")
    for i in (0, 1, 6, 16, 22, 27, 37, 43):
        k, r, v = frame.anchors[i]
        print(f"    #{i:02d}  {k}/{r}/{v}")

    rule("STEP 3  codebook  (a place you can say out loud)")
    ph = seed["phonology"]
    print(f"  raw walk        {len(ph['consonants'])} consonants x "
          f"{len(ph['vowels'])} vowels = {len(ph['consonants'])*len(ph['vowels'])}")
    print(f"  ordering        {ph['syllable_order']} (snake), so a turn costs one phoneme")
    print(f"  padding         {ph['pad']} -> {len(frame.syllables)} syllables")
    print(f"  codebook        {' '.join(frame.syllables)}")
    adjacent = sum(1 for a, b in zip(frame.syllables, frame.syllables[1:])
                   if sum(1 for x, y in zip(a, b) if x != y) == 1
                   and abs(len(a) - len(b)) == 0)
    print(f"  check           {adjacent}/{len(frame.syllables)-1} adjacent pairs differ by "
          f"exactly one phoneme")

    rule("STEP 4  ladder  (what may anchor a claim)")
    for m, meta in frame.markers.items():
        verdict = "anchors" if meta["anchors"] else "does not anchor"
        print(f"  {m}  rank {meta['rank']}  {verdict:16s} {meta['desc']}")
    print()
    print("  A locus takes the weakest marker present. Confidence cannot promote it;")
    print("  only evidence can.")

    rule("STEP 5  metric  (what 'close' means)")
    for k, v in frame.distance.items():
        print(f"  {k:22s} {v}")

    rule("STEP 6  population  (the only data the primer needs)")
    pp = frame.population_params
    print(f"  spec            depth={pp['depth']}")
    print(f"  places          {len(frame.population)}")
    sizes = [len(p) for p in frame.population]
    print(f"  landmarks/place min {min(sizes)}  mean {np.mean(sizes):.2f}  max {max(sizes)}")
    print(f"  distinct        {len({tuple(p) for p in frame.population})}")
    print()
    print("  Every place is concrete and nameable: the six shipped worlds plus every")
    print("  place one landmark away from each. No synthetic random sets.")

    rule("STEP 7  axis order  (which question gets asked first)")
    print(f"  rule            {seed['partition']['order']}, over the population above")
    print(f"  branches        {seed['partition']['branches']}  (bits per axis: "
          f"{int(np.log2(seed['partition']['branches']))})")
    print(f"  axes            {len(frame.partition.axes)}")
    print(f"  first ten       {frame.partition.axes[:10]}")
    v0, v1 = frame.partition.axes[0], frame.partition.axes[-1]
    print(f"  most important  #{v0}  {frame.anchors[v0][0]}/{frame.anchors[v0][1]}/{frame.anchors[v0][2]}")
    print(f"  least important #{v1}  {frame.anchors[v1][0]}/{frame.anchors[v1][1]}/{frame.anchors[v1][2]}")
    print()
    print("  Not stored in the seed. Derived. This is the part a registry would have")
    print("  to ship and keep versioned; here both sides recompute it identically.")

    rule("STEP 8  seal  (proof the two sides agree)")
    print(f"  fingerprint     {frame.fingerprint()}")
    print()
    c = frame.compression()
    print(f"  transmitted     {c['seed_bytes']:,} bytes   (the seed)")
    print(f"  reconstructed   {c['naive_transport_bytes']:,} bytes   (landmarks, codebook, "
          f"axis order, population)")
    print(f"  ratio           {c['reduction_factor']}x fewer bytes, and nothing derived is "
          f"sent at all")

    # ------------------------------------------------------------------
    rule("NOW: one world becomes one coordinate")
    frame_world = world.build("kitchen_with_friend")
    check = frame_world.self_check(frame)
    print(f"  world           {frame_world.name}")
    print(f"  landmarks true  {check['n_landmarks']}")
    print(f"  marker floor    {check['marker_floor']}   (weakest marker present)")
    print(f"  self-check      {'ok' if check['ok'] else check['problems']}")

    obs = frame_world.observations()
    canon = L.canonical(obs, frame.hierarchy)
    print()
    print(f"  (a) canonical set        {len(obs)} observations -> {len(canon)} keys")
    print(f"      first six            {', '.join(canon[:6])}")
    print(f"      note                 hierarchical values expand: /src/tests also claims /src and /")

    vec = L.anchor_vector(canon, frame.anchors, frame.distance)
    print()
    print(f"  (b) distance vector      {len(vec)} numbers, one per landmark")
    uniq, counts = np.unique(vec, return_counts=True)
    print(f"      values present        {dict(zip([f'{u:.1f}' for u in uniq], counts))}")
    print(f"      first ten            {' '.join(f'{v:.1f}' for v in vec[:10])}")

    bits = frame.partition.bits(vec)
    print()
    print(f"  (c) partition bits       {len(bits)} bits "
          f"({int(np.log2(frame.partition.branches))} per axis x {len(frame.partition.axes)} axes)")
    print(f"      first forty-eigh     {''.join(str(b) for b in bits[:48])}")
    print(f"      prefix string        {frame.partition.prefix(vec)[:24]}...")

    syl = L.bits_to_syllables(bits, frame.syllables, per=5)
    print()
    print(f"  (d) syllables            {len(syl)}: {' '.join(syl)}")

    loc = L.Encoder(frame).encode(obs, timestamp=0)
    print()
    print(f"  (e) the coordinate       {loc.text}")
    print(f"      with its seal        {loc.short()}")
    print(f"      commitment           {loc.commitment}")
    print()
    print("  Read the four beats as: world . place + reach ~ now")
    print("  The commitment is the other half: it proves *exactly this* set of facts")
    print("  and nothing about nearness. Identity and location are separate objects.")

    # ------------------------------------------------------------------
    rule("AND NOW: two worlds, compared")
    enc = L.Encoder(frame)
    loci = {n: enc.encode(w.observations()) for n, w in world.build_all().items()}
    ordered = ["kitchen_with_friend", "kitchen_alone", "shared_workshop",
               "warehouse_alone", "locked_storeroom", "dark_empty_room"]
    print(f"  {'world':<20} {'landmarks':>9}  {'coordinate':<30} {'seal':<8}")
    for n in ordered:
        w = world.WORLDS[n]
        print(f"  {n:<20} {len(w):>9}  {loci[n].text:<30} {loci[n].commitment[:6]}")

    print()
    print("  Pre-registered relations, written down before looking at the geometry:")
    print(f"  {'expectation':<12} {'pair':<44} {'LCP':>4} {'hamming':>8} {'jaccard':>8}")
    for label, (a, b) in world.KNOWN_RELATIONS.items():
        A, B = set(world.WORLDS[a]), set(world.WORLDS[b])
        jac = len(A & B) / len(A | B)
        print(f"  {label:<12} {a + ' vs ' + b:<44} "
              f"{L.Partition.lcp(loci[a].prefix, loci[b].prefix):>4} "
              f"{enc.hamming(loci[a], loci[b]):>8} {jac:>8.3f}")

    rule("PROGRESSIVE PRECISION  (how much of the address do you need?)")
    axes = frame.partition.axes
    print(f"  {'axes kept':>9} {'prefix':>8} {'syllables':>10} {'worlds uniquely named':>22}")
    for k in (2, 4, 8, 12, 16, 24, 32, 45):
        prefixes = {}
        for n in ordered:
            loc = enc.encode(world.build(n).observations(), precision=k)
            prefixes.setdefault(loc.prefix, []).append(n)
        n_distinct = len(prefixes)
        n_syl = len(L.bits_to_syllables(
            L.Partition(axes=axes[:k], branches=frame.partition.branches).bits(
                L.anchor_vector(loci[n].canon, frame.anchors, frame.distance)),
            frame.syllables, per=5))
        print(f"  {k:>9} {k:>8} {n_syl:>10} {n_distinct:>10} of {len(ordered)}")
    print()
    print("  A short prefix is a coarse place; lengthening it narrows. Two worlds that")
    print("  share a prefix are, as far as the chart is concerned, in the same region.")
    print("  Where two *different* worlds collapse to one prefix, the primer is")
    print("  honestly saying: I cannot tell these apart at this resolution.")

    rule("CHECK THE ORDERING HOLDS")
    pairs = []
    names = list(world.WORLDS)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = set(world.WORLDS[a]), set(world.WORLDS[b])
            jac = 1.0 - len(A & B) / len(A | B)
            pairs.append((jac, enc.hamming(loci[a], loci[b]), f"{a} vs {b}"))
    pairs.sort()
    try:
        from scipy.stats import spearmanr
        rho, p = spearmanr([x[0] for x in pairs], [x[1] for x in pairs])
        print(f"  Spearman(known distance, locus hamming) over all {len(pairs)} pairs: "
              f"rho = {rho:.3f} (p = {p:.4f})")
    except ImportError:
        kn = np.argsort(np.argsort([x[0] for x in pairs]))
        lo = np.argsort(np.argsort([x[1] for x in pairs]))
        rho = float(np.corrcoef(kn, lo)[0, 1])
        print(f"  Spearman(known distance, locus hamming) over all {len(pairs)} pairs: "
              f"rho = {rho:.3f}   (scipy absent; rank correlation via numpy)")
    print()
    print("  Closest pair first:")
    for jac, ham, name in pairs[:3]:
        print(f"    hamming {ham:3d}   {name}")
    print("  Furthest pair last:")
    for jac, ham, name in pairs[-3:]:
        print(f"    hamming {ham:3d}   {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
