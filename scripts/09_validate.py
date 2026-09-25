#!/usr/bin/env python3
"""One audit: everything this repo claims to have *proved*, checked in one run.

The point of collecting it here is that "deterministic" and "monotone" and
"known-answer" are claims, and a claim that lives only in prose is not evidence.
Each section below computes its own result and writes it to a single JSON file
so a reader can diff the whole set at once.

Sections
--------
  A  determinism            same input, byte-identical output, in fresh processes
  B  monotone refinement    more precision separates, never conflates, never contradicts
  C  distance preservation  does the address respect a known ordering of places
  D  known-answer cases     results whose answer is known before the metric is trusted
  E  nulls                  every headline number against a null of equal information
  F  frame identity         the primer fingerprint, and what happens when it differs
  G  disagreements          where a measurement contradicted the pre-registration

Run:  python3 scripts/09_validate.py
Out:  evidence/validation.json
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import generator, locus as L, primer, world  # noqa: E402

EVIDENCE = ROOT / "evidence"


def rank(v):
    return np.argsort(np.argsort(np.asarray(v, dtype=float)))


def spearman(a, b) -> float:
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    places = list(world.WORLDS)
    loci = {p: enc.encode(world.build(p).observations()) for p in places}
    vocab = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]
    out: dict = {"primer_fingerprint": frame.fingerprint()}

    # ---- A. determinism -------------------------------------------------
    print("A  determinism")
    obs = world.build("shared_workshop").observations()
    first = enc.encode(obs, timestamp=1700000000)
    repeats = {enc.encode(obs, timestamp=1700000000).commitment for _ in range(50)}
    unpinned = {enc.encode(obs).commitment for _ in range(50)}

    src = (
        "import sys, hashlib, json\n"
        "sys.path.insert(0, %r)\n"
        "from marco import primer, locus as L, world\n"
        "f = primer.expand(); e = L.Encoder(f)\n"
        "o = world.build('shared_workshop').observations()\n"
        "print(e.encode(o, timestamp=1700000000).commitment)\n" % str(ROOT)
    )
    fresh = set()
    for _ in range(3):
        r = subprocess.run([sys.executable, "-c", src], capture_output=True, text=True)
        fresh.add(r.stdout.strip())

    enc_det = {
        "pinned_50_runs_distinct_outputs": len(repeats),
        "unpinned_50_runs_distinct_outputs": len(unpinned),
        "fresh_processes_distinct_outputs": len(fresh),
        "fresh_processes_match_in_process": fresh == {first.commitment},
        "identical": (len(repeats) == 1 and len(unpinned) == 1
                      and fresh == {first.commitment}),
        "no_wall_clock_leak": len(unpinned) == 1,
    }
    out["determinism"] = enc_det
    for k, v in enc_det.items():
        print(f"     {k:<42} {v}")

    # ---- B. monotone refinement ----------------------------------------
    print("\nB  monotone refinement")
    curve = []
    prev_distinct, prev_groups = 0, None
    violations = 0
    for k in range(1, len(frame.partition.axes) + 1):
        groups: dict[str, list[str]] = {}
        for p in places:
            loc = enc.encode(world.build(p).observations(), precision=k)
            groups.setdefault(loc.prefix, []).append(p)
        distinct = len(groups)
        if distinct < prev_distinct:
            violations += 1
        # refining must SPLIT groups, never merge them
        if prev_groups is not None:
            for members in prev_groups.values():
                homes = {min(g for g in groups.values() if p in g) for p in members} \
                    if False else None
            for p in places:
                prev_home = next(m for m in prev_groups.values() if p in m)
                now_home = next(m for m in groups.values() if p in m)
                # every member of a group must stay together or split away,
                # never join members of a different previous group
                if not set(now_home) <= set(prev_home):
                    violations += 1
                    break
        curve.append({"axes": k, "distinct": distinct})
        prev_distinct, prev_groups = distinct, groups
    out["monotone_refinement"] = {
        "violations": violations, "monotone": violations == 0,
        "curve": curve,
        "axes_for_all_places": next(r["axes"] for r in curve if r["distinct"] == len(places)),
        "first_two_axes_distinct": curve[1]["distinct"],
    }
    print(f"     violations over {len(curve)} precisions       {violations}")
    print(f"     monotone                                  {violations == 0}")
    print(f"     axes needed to name all {len(places)} places    "
          f"{out['monotone_refinement']['axes_for_all_places']}")

    # ---- C. distance preservation --------------------------------------
    print("\nC  distance preservation against a known ordering")
    pairs = []
    for a, b in itertools.combinations(places, 2):
        A, B = set(world.WORLDS[a]), set(world.WORLDS[b])
        pairs.append({"a": a, "b": b,
                      "known_jaccard_distance": round(1 - len(A & B) / len(A | B), 4),
                      "hamming": enc.hamming(loci[a], loci[b]),
                      "lcp": L.Partition.lcp(loci[a].prefix, loci[b].prefix)})
    rho = spearman([p["known_jaccard_distance"] for p in pairs],
                   [p["hamming"] for p in pairs])
    rng = random.Random(20260925)
    null_rho = []
    known = [p["known_jaccard_distance"] for p in pairs]
    ham = [p["hamming"] for p in pairs]
    for _ in range(2000):
        rng.shuffle(ham)
        null_rho.append(spearman(known, ham))
    out["distance_preservation"] = {
        "spearman_known_vs_hamming": round(rho, 4),
        "pairs": len(pairs),
        "null_shuffled_mean": round(float(np.mean(null_rho)), 4),
        "null_shuffled_sd": round(float(np.std(null_rho)), 4),
        "detail": pairs,
    }
    print(f"     spearman(known, hamming) over {len(pairs)} pairs    {rho:.4f}")
    print(f"     null with the pairing shuffled            "
          f"{np.mean(null_rho):+.4f} (sd {np.std(null_rho):.4f})")

    # ---- D. known-answer cases -----------------------------------------
    print("\nD  known-answer cases (answer known before the metric is trusted)")
    # The same four cases the blind match uses, so the two files cannot report
    # different numbers for the same check. An earlier revision built its own
    # sets here and reported 21 where the blind match reported 27.
    A = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors[:12]}
    B = set(A)
    C = set(A) - {sorted(A)[0]}
    D = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors[20:32]}

    def loc_of(keys):
        return enc.encode([L.Obs(*k.split("/", 2)) for k in sorted(keys)])

    la, lb, lc, ld = loc_of(A), loc_of(B), loc_of(C), loc_of(D)
    ka = {
        "identical_sets_same_root": la.commitment == lb.commitment,
        "identical_sets_hamming": enc.hamming(la, lb),
        "one_statement_removed_hamming": enc.hamming(la, lc),
        "disjoint_sets_hamming": enc.hamming(la, ld),
        "ordering_is_monotone": (enc.hamming(la, lb) <= enc.hamming(la, lc)
                                 <= enc.hamming(la, ld)),
        "different_sets_different_root": la.commitment != lc.commitment,
    }
    out["known_answer"] = ka
    for k, v in ka.items():
        print(f"     {k:<42} {v}")

    # ---- E. nulls -------------------------------------------------------
    print("\nE  nulls")
    bp = ROOT / "evidence" / "blind" / "blind-match.json"
    if bp.exists():
        b = json.loads(bp.read_text())
        out["nulls"] = {
            "chance": b["chance"],
            "real_top1": b["top1_accuracy"],
            "real_top1_strict": b["top1_strict_accuracy"],
            "hungarian": b["hungarian_accuracy"],
            "label_shuffle": b["null_label_shuffle"],
            "random_vocabulary": b["null_random_vocabulary"],
            "mean_landmark_jaccard": b["mean_pairwise_landmark_jaccard"]["mean"],
            "source": "evidence/blind/blind-match.json",
        }
        n = out["nulls"]
        print(f"     real top-1 {n['real_top1']:.4f} (strict {n['real_top1_strict']:.4f})"
              f"   chance {n['chance']:.4f}")
        print(f"     label-shuffle null {n['label_shuffle']['accuracy']:.4f} "
              f"(sd {n['label_shuffle']['sd']:.4f})")
        print(f"     random-vocabulary null {n['random_vocabulary']['accuracy']:.4f} "
              f"(sd {n['random_vocabulary']['sd']:.4f})")
        print(f"     statement-level agreement {n['mean_landmark_jaccard']:.4f}")
    else:
        print("     blind-match.json absent; run scripts/03_blind_match.py")
        out["nulls"] = None

    # ---- F. frame identity ---------------------------------------------
    print("\nF  frame identity")
    # A different primer must make the geometry incommensurable rather than
    # silently comparable. This is the check the library performs.
    alt_seed = primer.load_seed()
    alt_seed["similarity"]["minhash_seed"] = 43
    alt = primer.expand(alt_seed)
    other = L.Encoder(alt).encode(obs, timestamp=1700000000)
    cmp = enc.compare(first, other)
    same_fp = L.Encoder(frame).encode(obs, timestamp=1700000000)
    cmp_same = enc.compare(first, same_fp)
    out["frame_identity"] = {
        "fingerprint": frame.fingerprint(),
        "seed_bytes": frame.seed_bytes(),
        "derived_bytes": frame.naive_transport_bytes(),
        "reduction_factor": frame.compression()["reduction_factor"],
        "different_primer_comparable": cmp["comparable"],
        "different_primer_reason": cmp.get("reason"),
        "same_primer_comparable": cmp_same["comparable"],
        "primers_differ": alt.fingerprint() != frame.fingerprint(),
    }
    f = out["frame_identity"]
    print(f"     fingerprint {f['fingerprint'][:32]}...")
    print(f"     seed {f['seed_bytes']:,} B reconstructs {f['derived_bytes']:,} B "
          f"({f['reduction_factor']}x)")
    print(f"     different primer comparable: {f['different_primer_comparable']} "
          f"({f['different_primer_reason']})")

    # ---- G. disagreements ----------------------------------------------
    print("\nG  where a measurement contradicted the pre-registration")
    reg = {}
    for label, (a, b) in world.KNOWN_RELATIONS.items():
        reg[label] = {"pair": [a, b], "hamming": enc.hamming(loci[a], loci[b]),
                      "lcp": L.Partition.lcp(loci[a].prefix, loci[b].prefix)}
    base = "kitchen_with_friend"
    strict_near = enc.hamming(loci[base], loci["kitchen_alone"])
    strict_mid = enc.hamming(loci[base], loci["shared_workshop"])
    out["preregistration"] = {
        "expected": "kitchen_alone strictly nearest to kitchen_with_friend, then shared_workshop",
        "measured": {"kitchen_alone": strict_near, "shared_workshop": strict_mid},
        "strict_ordering_holds": strict_near < strict_mid,
        "weak_ordering_holds": (
            reg["near"]["hamming"] <= reg["mid"]["hamming"]
            < reg["far"]["hamming"] < reg["furthest"]["hamming"]),
        "relations": reg,
        "resolution": ("the two are tied, so the strict expectation fails and the "
                       "weak one holds; kept as a test rather than retuned"),
    }
    p = out["preregistration"]
    print(f"     expected strict near<mid: {p['strict_ordering_holds']}")
    print(f"     measured near {strict_near}, mid {strict_mid} -> tie")
    print(f"     weak ordering near<=mid<far<furthest: {p['weak_ordering_holds']}")

    # ---- bootstrap, for completeness ------------------------------------
    boot = generator.bootstrap_report(frame, n_trials=64)
    out["bootstrap"] = boot
    print(f"\nH  bootstrap  {boot['resolved']}/{boot['trials']} resolved, "
          f"mean {boot['mean_questions']} questions, floor {boot['log2_population']}")

    out["all_checks_pass"] = bool(
        enc_det["identical"] and out["monotone_refinement"]["monotone"]
        and ka["ordering_is_monotone"] and ka["identical_sets_same_root"]
        and ka["different_sets_different_root"]
        and f["same_primer_comparable"] and not f["different_primer_comparable"]
        and boot["resolved"] == boot["trials"]
    )
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "validation.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nall checks pass: {out['all_checks_pass']}")
    print("wrote evidence/validation.json")
    return 0 if out["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())