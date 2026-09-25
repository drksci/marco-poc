#!/usr/bin/env python3
"""Two organisations, incompatible capability paths, no mapping table.

The problem this script solves
------------------------------
`arXiv:2601.14567v2` gives agents a name that survives migration: the `agent://`
URI, with a trust root, a capability path, and a sortable id. Discovery is by
capability path, and the identifier is a hash — deliberately, so that identity
does not leak location.

The paper is candid about one weakness in its own design. Two organisations can
describe the *same* capability with paths that share no prefix:

    agent://acme.com/workflow/approval/01h...
    agent://globex.io/process/authorize/01h...

Those are the same job. Exact-path discovery cannot see it, and the paper's own
remedy is an external capability-mapping service: a second system to run, and a
second source of truth that can drift away from the first.

What is demonstrated here
-------------------------
Each agent also publishes a `⌁` address derived from the *situation it works in*,
not from its name. Equivalent jobs across the two organisations happen in the
same kind of place, so they land near each other. Discovery by nearness finds
all four equivalents with no mapping table, no curator, and no shared path
vocabulary.

Both halves are kept separate on purpose: `agent://` is untouched and still does
identity. The address is descriptive only and is never used to authorise
anything.

Run:  python3 scripts/07_capability_nearness.py
Out:  evidence/capability-nearness.json
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L   # noqa: E402
from marco import primer       # noqa: E402

EVIDENCE = ROOT / "evidence"

# ---------------------------------------------------------------------------
# The two organisations. Same four jobs, different words for them.
# ---------------------------------------------------------------------------

CAPABILITIES = {
    "acme.com": {
        "workflow/approval":   "approval",
        "workflow/build":      "build",
        "workflow/rollback":   "rollback",
        "process/audit":       "audit",
    },
    "globex.io": {
        "process/authorize":   "approval",
        "process/compile":     "build",
        "process/revert":      "rollback",
        "process/review":      "audit",
    },
}

# The situation each job happens in, in the 45 plain statements. The two
# organisations describe the same jobs, so the *situations* are what line up —
# not the names. This is the whole mechanism.
SITUATIONS: dict[str, list[str]] = {
    "approval": [
        "see/this_place/inside", "see/words/any", "reach/other_people/any",
        "who/one_other/any", "who/telling_me_what_to_do/any",
        "place/private/any", "now/waiting/any",
        "know/why_im_here/any", "know/what_comes_next/any",
        "risk/mistakes_last/any",
    ],
    "build": [
        "see/this_place/inside", "reach/objects/nearby", "reach/other_places/any",
        "change/this_place/any", "who/nobody/any", "place/temporary/any",
        "now/working/any", "know/why_im_here/any",
    ],
    "rollback": [
        "see/this_place/inside", "reach/other_places/any",
        "change/this_place/any", "change/other_places/any",
        "who/nobody/any", "now/urgent/any",
        "risk/things_break/any", "risk/mistakes_last/any",
        "know/why_im_here/any",
    ],
    "audit": [
        "see/this_place/inside", "see/words/any", "reach/nothing/any",
        "change/nothing/any", "who/watching_me/any", "who/one_other/any",
        "place/private/any", "now/working/any",
        "know/where_i_am/any", "risk/seen_by_others/any",
    ],
    # A capability that exists only on the globex side and has no equivalent.
    # Discovery must NOT return it as a neighbour of anything at acme.
    "migrate": [
        "see/this_place/inside", "reach/other_places/any",
        "change/other_places/any", "who/nobody/any",
        "place/shared/any", "place/far_away/any",
        "now/working/any", "risk/things_break/any",
    ],
}

# Real organisations do not observe identical things, even when the job is the
# same. Each side records a slightly different set of statements — a different
# tool visible, a different thing happening — so the equivalent pairs come out
# *near* rather than identical. If the demonstration only worked because the two
# sides were byte-identical, it would be proving a tautology.
ORG_VARIATION: dict[tuple[str, str], list[str]] = {
    ("globex.io", "approval"): ["see/the_time/any"],
    ("globex.io", "build"):    ["see/sound/any", "reach/help/any"],
    ("globex.io", "rollback"): ["see/the_time/any"],
    ("globex.io", "audit"):    ["reach/objects/nearby", "see/the_time/any"],
}


def situation_for(org: str, job: str) -> list[str]:
    keys = list(SITUATIONS[job]) + ORG_VARIATION.get((org, job), [])
    return sorted(set(keys))


def show(keys: list[str], width: int = 38) -> str:
    return f"{len(keys):>2} statements"


def main() -> int:
    frame = primer.expand()
    enc = L.Encoder(frame)
    vocab = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors}

    allkeys = set(SITUATIONS) | set()
    bad = {j: sorted(set(situation_for(o, j)) - vocab)
           for o, caps in CAPABILITIES.items() for j in caps.values()
           if set(situation_for(o, j)) - vocab}
    if bad:
        print(f"error: statements outside the primer vocabulary: {bad}", file=sys.stderr)
        return 2

    # ---- build the two populations --------------------------------------
    agents = []   # (org, path, uri, job, address)
    for org, caps in CAPABILITIES.items():
        for path, job in caps.items():
            obs = [L.Obs(*k.split("/", 2)) for k in situation_for(org, job)]
            addr = enc.encode(obs)
            agents.append({"org": org, "path": path, "job": job,
                           "uri": f"agent://{org}/{path}/01h{'0' * 22}",
                           "address": addr.text, "locus": addr})
    # the decoy lives on globex only
    obs = [L.Obs(*k.split("/", 2)) for k in sorted(SITUATIONS["migrate"])]
    decoy_addr = enc.encode(obs)
    agents.append({"org": "globex.io", "path": "process/migrate", "job": "migrate",
                   "uri": "agent://globex.io/process/migrate/01h" + "0" * 22,
                   "address": decoy_addr.text, "locus": decoy_addr})

    acme = [a for a in agents if a["org"] == "acme.com"]
    globex = [a for a in agents if a["org"] == "globex.io"]

    print(f"primer fingerprint : {frame.fingerprint()}")
    print()
    print("TWO ORGANISATIONS, SAME FOUR JOBS, NO SHARED WORDS")
    print(f"  {'agent:// URI':<52} {'job':<10} {'⌁ address':<34}")
    for a in acme + globex:
        print(f"  {a['uri']:<52} {a['job']:<10} {a['address']:<34}")

    # ---- 1. exact-path discovery ----------------------------------------
    print()
    print("1. DISCOVERY BY CAPABILITY PATH (the paper's mechanism, unmodified)")
    path_hits = 0
    for a in acme:
        # exact path match across organisations: is there another org with the
        # identical path? There never is, which is the paper's stated problem.
        matches = [b for b in globex if b["path"] == a["path"]]
        # prefix match, the mechanism actually available
        prefix = [b for b in globex
                  if b["path"].split("/")[0] == a["path"].split("/")[0]]
        got = matches or prefix
        hit = any(b["job"] == a["job"] for b in got)
        path_hits += int(hit)
        print(f"  {a['path']:<22} -> {len(got)} result(s)"
              f"{'  ' + str([b['path'] for b in got]) if got else '  none'}"
              f"   {'HIT' if hit else 'MISS'}")
    print(f"  recall = {path_hits}/{len(acme)}")

    # ---- 2. discovery by nearness, no mapping table ---------------------
    print()
    print("2. DISCOVERY BY NEARNESS (addresses only, no mapping table)")
    near_hits, decoy_hits = 0, 0
    detail = []
    for a in acme:
        d = sorted(globex, key=lambda b: enc.hamming(a["locus"], b["locus"]))
        best = d[0]
        hit = best["job"] == a["job"]
        near_hits += int(hit)
        decoy_hits += int(best["job"] == "migrate")
        detail.append({"query": a["path"], "nearest": best["path"],
                       "nearest_job": best["job"], "hit": hit,
                       "hamming": enc.hamming(a["locus"], best["locus"]),
                       "runners_up": [{"path": b["path"], "job": b["job"],
                                       "hamming": enc.hamming(a["locus"], b["locus"])}
                                      for b in d[1:3]]})
        print(f"  {a['path']:<22} -> {best['path']:<22} (hamming "
              f"{enc.hamming(a['locus'], best['locus']):>2})   "
              f"{'HIT' if hit else 'MISS'}")
    print(f"  recall = {near_hits}/{len(acme)}")
    print(f"  decoy 'process/migrate' returned as nearest: {decoy_hits} times "
          f"(the query set has no migrate equivalent)")

    # ---- 3. separation: are equivalent pairs actually the near ones? -----
    print()
    print("3. IS THE EQUIVALENCE VISIBLE IN THE GEOMETRY AT ALL?")
    same, diff = [], []
    for a, b in itertools.product(acme, globex):
        h = enc.hamming(a["locus"], b["locus"])
        (same if a["job"] == b["job"] else diff).append(h)
    print(f"  equivalent pairs    n={len(same):>2}  mean hamming {np.mean(same):.1f}  "
          f"range {min(same)}-{max(same)}")
    print(f"  non-equivalent      n={len(diff):>2}  mean hamming {np.mean(diff):.1f}  "
          f"range {min(diff)}-{max(diff)}")
    sep = np.mean(diff) - np.mean(same)
    print(f"  separation          {sep:+.1f} hamming "
          f"({'equivalents are nearer' if sep > 0 else 'NOT separated'})")

    # ---- 4. null: shuffle which agent does which job ---------------------
    print()
    print("4. NULL — shuffle the job labels and repeat the nearness query")
    rng = random.Random(20260925)
    jobs = [b["job"] for b in globex]
    null = []
    for _ in range(2000):
        perm = jobs[:]
        rng.shuffle(perm)
        hits = 0
        for a in acme:
            d = sorted(zip(perm, globex), key=lambda t: enc.hamming(a["locus"], t[1]["locus"]))
            hits += int(d[0][0] == a["job"])
        null.append(hits / len(acme))
    print(f"  shuffled-label recall: mean {np.mean(null):.3f}  sd {np.std(null):.3f}  "
          f"chance 1/{len(globex)} = {1/len(globex):.3f}")
    print(f"  real recall          : {near_hits/len(acme):.3f}")

    # ---- 5. the pair that matches the paper's own example ----------------
    print()
    print("5. THE PAPER'S OWN EXAMPLE, WORKED")
    a = next(x for x in acme if x["job"] == "approval")
    b = next(x for x in globex if x["job"] == "approval")
    print(f"  {a['uri']}")
    print(f"  {b['uri']}")
    print(f"  identical path?           {a['path'] == b['path']}")
    print(f"  shared path prefix?       "
          f"{a['path'].split('/')[0] == b['path'].split('/')[0]}")
    print(f"  distance between names?   not defined — strings have no distance")
    print(f"  distance between addresses: {enc.hamming(a['locus'], b['locus'])}")
    print(f"  {a['address']}")
    print(f"  {b['address']}")

    payload = {
        "primer_fingerprint": frame.fingerprint(),
        "organisations": {org: list(caps) for org, caps in CAPABILITIES.items()},
        "agents": [{k: v for k, v in a.items() if k != "locus"} for a in agents],
        "path_discovery_recall": f"{path_hits}/{len(acme)}",
        "nearness_discovery_recall": f"{near_hits}/{len(acme)}",
        "decoy_returned_as_nearest": decoy_hits,
        "equivalent_mean_hamming": round(float(np.mean(same)), 3),
        "non_equivalent_mean_hamming": round(float(np.mean(diff)), 3),
        "separation_hamming": round(float(sep), 3),
        "null_shuffled_recall_mean": round(float(np.mean(null)), 4),
        "null_shuffled_recall_sd": round(float(np.std(null)), 4),
        "chance": round(1 / len(globex), 4),
        "detail": detail,
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "capability-nearness.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote evidence/capability-nearness.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())