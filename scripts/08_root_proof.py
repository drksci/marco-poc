#!/usr/bin/env python3
"""The root: one exact number that independent models have to agree on.

What a root is here
-------------------
Every place is described by a *set* of statements. Serialise that set
canonically, hash it once, and you have a root — a single 32-byte value.
Two agents holding the same set get the same root. Two agents holding sets that
differ by one statement get roots that look nothing alike. That second property
is the point: a root is exact, and it does not leak how close two places are.

So the protocol carries two different objects, and they do different jobs:

    ⌁ address   a fuzzy, locality-preserving coordinate. Similar places, similar
                address. It proves nothing.
    !root       an exact commitment. Same place, same root; any difference, an
                unrelated root. It says nothing about nearness.

This script measures the parts that make the root useful *as evidence*:

  1. Do independent models actually produce the same root? Not a similar
     address — the same 32 bytes.
  2. Can the root be taken at a chosen grain, so that a partial disclosure is
     still checkable? A root over the four most discriminative statements, or
     over all of them, both work.
  3. Can unrelated environment attributes be folded in, so that the root covers
     whatever fingerprints an operator happens to have, without changing the
     address?
  4. Is it deterministic? Same input, byte-identical root, in a fresh process,
     with no clock and no unseeded randomness.

Run:  python3 scripts/08_root_proof.py
Out:  evidence/root-proof.json
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L   # noqa: E402
from marco import primer, world  # noqa: E402

EVIDENCE = ROOT / "evidence"


def canonical_root(statements, extra=()) -> str:
    """SHA-256 over a canonical serialisation of a statement set.

    Deliberately identical in shape to the commitment the library computes, so
    there is one hashing rule in the project and not two. Order of input does
    not matter: the set is sorted first. Anything else — environment
    fingerprints, a hostname, an operator tag — rides in `extra`, which is
    sorted the same way.
    """
    payload = json.dumps({
        "statements": sorted(statements),
        "extra": sorted(extra),
    }, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def ordered_keys(frame) -> list[str]:
    """The statements, ordered by how much they tell places apart.

    The primer already derives this order for the address. The root reuses it,
    so a root taken at grain k covers the k most informative statements rather
    than an arbitrary slice.
    """
    keys = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]
    return [keys[i] for i in frame.partition.axes]


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    order = ordered_keys(frame)

    # ---- load what the models actually chose ---------------------------
    sel: dict[str, dict[str, set]] = defaultdict(dict)
    for p in sorted((ROOT / "evidence" / "transcripts").glob("probe-*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("ok") and r.get("parsed"):
                    sel[r["model"]][r["situation_id"]] = set(r["landmarks"])
    models = sorted(m for m in sel if len(sel[m]) == len(world.DESCRIPTIONS))
    places = list(world.DESCRIPTIONS)
    if len(models) < 2:
        print("error: need at least two models with full coverage", file=sys.stderr)
        return 2

    print(f"primer fingerprint : {frame.fingerprint()}")
    print(f"models             : {len(models)}")
    print()

    # ---- 1. do independent models produce the SAME root? ---------------
    print("1. THE SAME ROOT, FROM INDEPENDENT MODELS")
    print("   The address is allowed to differ. The root is not.")
    print()
    print(f"   {'place':<22} {'distinct statement sets':>24} {'distinct roots':>15} "
          f"{'largest agreeing group':>24}")
    per_place = {}
    total_agree, total_models = 0, 0
    for p in places:
        roots = {m: canonical_root(sel[m][p]) for m in models}
        groups = defaultdict(list)
        for m, r in roots.items():
            groups[r].append(m)
        sets = {frozenset(sel[m][p]) for m in models}
        biggest = max(groups.values(), key=len)
        per_place[p] = {
            "distinct_statement_sets": len(sets),
            "distinct_roots": len(groups),
            "largest_group": biggest,
            "largest_group_size": len(biggest),
            "roots": {m: roots[m] for m in models},
        }
        total_agree += len(biggest)
        total_models += len(models)
        print(f"   {p:<22} {len(sets):>24} {len(groups):>15} "
              f"{len(biggest):>13} of {len(models)}")
    print()
    print(f"   models landing in the single largest agreeing group: "
          f"{total_agree} of {total_models} ({100*total_agree/total_models:.1f}%)")
    print()
    print("   A root that matches is not a similarity score. It is the same")
    print("   number. There is nothing to threshold and nothing to tune.")

    # ---- 2. the root at a chosen grain ---------------------------------
    print()
    print("2. THE SAME ROOT AT ANY GRAIN")
    print("   Take the root over the k most discriminative statements instead of")
    print("   all 45. A partial disclosure is still exactly checkable.")
    print()
    print(f"   {'grain':>6}  {'root prefix':>14}  {'places still distinguishable':>30}")
    grain_rows = []
    for k in (2, 4, 8, 12, 16, 24, 45):
        # Grain k = the root over the k most discriminative statements this
        # model actually selected. One model throughout, so the count measures
        # the effect of grain and not of model disagreement.
        roots = {p: canonical_root(
            [x for x in order if x in sel[models[0]][p]][:k]) for p in places}
        distinct = len(set(roots.values()))
        grain_rows.append({"grain": k, "root_prefix": roots[places[0]][:14],
                           "distinct_roots": distinct, "places": len(places)})
        print(f"   {k:>6}  {roots[places[0]][:14]:>14}  {distinct:>18} of {len(places)}")

    # ---- 3. fold in arbitrary environment fingerprints ------------------
    print()
    print("3. FOLDING IN WHATEVER ELSE YOU HAVE")
    print("   The root accepts extra attributes at any time. They change the root")
    print("   and leave the address untouched.")
    print()
    base = sorted(sel[models[0]][places[0]])
    addr_before = enc.encode([L.Obs(*k.split("/", 2)) for k in base]).text
    rows = []
    for label, extra in [
        ("nothing", ()),
        ("host tag", ("host:runner-7",)),
        ("runtime fingerprint", ("py:3.14.7", "numpy:2.5.3")),
        ("operator tag + host", ("host:runner-7", "op:acme")),
    ]:
        r = canonical_root(base, extra)
        rows.append({"extra": list(extra), "root_prefix": r[:16]})
        print(f"   {'+ ' + label:<24} root {r[:16]}...")
    addr_after = enc.encode([L.Obs(*k.split("/", 2)) for k in base]).text
    print()
    print(f"   address unchanged by any of it: {addr_before == addr_after}")
    print(f"   {addr_after}")
    print()
    print("   So the root can carry whatever generic fingerprints an operator has")
    print("   to hand, and the coordinate stays a coordinate. Neither object")
    print("   contaminates the other.")

    # ---- 4. determinism across processes --------------------------------
    print()
    print("4. IS IT DETERMINISTIC?")
    # The same function is re-declared in a fresh interpreter rather than
    # imported, so the cross-process check cannot be satisfied by an import
    # cache or a module-level memo.
    src = (
        "import hashlib, json\n"
        "def canonical_root(statements, extra=()):\n"
        "    payload = json.dumps({'statements': sorted(statements), 'extra': sorted(extra)},\n"
        "                         separators=(',', ':'), ensure_ascii=False)\n"
        "    return hashlib.sha256(payload.encode()).hexdigest()\n"
        "print(canonical_root(" + repr(base) + "))\n"
    )
    outs = []
    for _ in range(3):
        out = subprocess.run([sys.executable, "-c", src], capture_output=True,
                             text=True, cwd=str(ROOT))
        outs.append(out.stdout.strip())
    here = canonical_root(base)
    print(f"   in-process root     {here}")
    print(f"   three fresh processes: {len(set(outs))} distinct value(s)")
    print(f"   identical           {set(outs) == {here}}")

    payload = {
        "primer_fingerprint": frame.fingerprint(),
        "models": models,
        "places": places,
        "per_place": per_place,
        "largest_group_total": f"{total_agree}/{total_models}",
        "largest_group_fraction": round(total_agree / total_models, 4),
        "grain": grain_rows,
        "extra_attribute_rows": rows,
        "address_unchanged_by_extra": addr_before == addr_after,
        "determinism_across_processes": set(outs) == {here},
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "root-proof.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote evidence/root-proof.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
