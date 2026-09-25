#!/usr/bin/env python3
"""Strip the labels off and see whether the coordinates still line up.

The test
--------
Several models were each shown the same situations, one at a time, with no
sight of each other. Each model independently chose landmarks from a shared
vocabulary. Every model's choice is then encoded into a locus by the same
deterministic encoder.

Now throw the situation names away. For a pair of models and a situation, take
model A's coordinate for that situation and ask which of model B's coordinates
it is closest to. If the geometry is real, it is closest to B's coordinate for
the *same* situation. Chance is 1/n_situations.

Why this script is careful
--------------------------
The project this comes from caught itself four times presenting an artifact of
the metric as a finding about models. So every headline number here comes with
a null that has the *same information content*, and the run refuses to report a
bare accuracy:

  chance                the floor, 1/n
  random vocabulary     same set size, landmarks drawn at random. Destroys the
                        content while preserving the size and the vocabulary —
                        this is the control that decides whether the models'
                        *choices* carry the signal or whether any set of that
                        size would have worked.
  label shuffle         permute the pairing; preserves marginal distributions.
  within-model ceiling  the same model run twice at temperature > 0. A
                        cross-model score above this is not a finding, it is a
                        bug, because a model cannot agree with another model
                        more than it agrees with itself.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L          # noqa: E402
from marco import primer              # noqa: E402
from marco.assignment import linear_sum_assignment  # noqa: E402

EVIDENCE = ROOT / "evidence" / "blind"


# ------------------------------------------------------------------------
# Loading
# ------------------------------------------------------------------------

def load_transcripts(paths: list[Path]) -> list[dict]:
    records = []
    for p in paths:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def usable(records: list[dict]) -> list[dict]:
    """Only records that actually produced a parseable landmark set."""
    return [r for r in records if r.get("ok") and r.get("parsed")]


def group(records: list[dict], key: str) -> dict:
    out = defaultdict(dict)
    for r in records:
        for situation, payload in r[key].items():
            out[situation][payload["model"]] = set(payload["landmarks"])
    return out


# ------------------------------------------------------------------------
# Encoding
# ------------------------------------------------------------------------

def encode_all(frame, selections: dict[str, dict[str, set]]) -> dict[str, dict[str, L.Locus]]:
    """model -> situation -> Locus, encoded with the shared primer."""
    enc = L.Encoder(frame)
    out: dict[str, dict[str, L.Locus]] = {}
    for model, per_situation in selections.items():
        out[model] = {}
        for situation, keys in per_situation.items():
            obs = [L.Obs(*k.split("/", 2)) for k in sorted(keys)]
            out[model][situation] = enc.encode(obs)
    return out


def distance_matrix(enc, A: dict[str, L.Locus], B: dict[str, L.Locus],
                    situations: list[str], metric: str = "hamming") -> np.ndarray:
    n = len(situations)
    M = np.zeros((n, n))
    for i, si in enumerate(situations):
        for j, sj in enumerate(situations):
            if metric == "hamming":
                M[i, j] = enc.hamming(A[si], B[sj])
            elif metric == "similarity":
                M[i, j] = 1.0 - enc.similarity(A[si], B[sj])
            elif metric == "prefix":
                M[i, j] = -L.Partition.lcp(A[si].prefix, B[sj].prefix)
            else:
                raise ValueError(metric)
    return M


# ------------------------------------------------------------------------
# Scores
# ------------------------------------------------------------------------

def top1(M: np.ndarray) -> tuple[int, int]:
    """Retrieval: is the diagonal the nearest column for every row?"""
    n = M.shape[0]
    correct = sum(int(np.argmin(M[i]) == i) for i in range(n))
    return correct, n


def top1_strict(M: np.ndarray) -> tuple[int, int]:
    """Retrieval, counting only rows where the diagonal is *strictly* nearest.

    Ties matter and should not be hidden. If two candidates are exactly
    equidistant, `argmin` picks the first and scores a hit; that is a weaker
    statement than "the right place was closer than every other place". Both
    numbers are reported, and the strict one is the conservative one.
    """
    n = M.shape[0]
    strict = 0
    for i in range(n):
        d = M[i]
        if d[i] < min(v for j, v in enumerate(d) if j != i):
            strict += 1
    return strict, n


def hungarian(M: np.ndarray) -> tuple[int, int]:
    """Optimal one-to-one assignment; how many pairs land on the diagonal?"""
    r, c = linear_sum_assignment(M)
    return int(np.sum(r == c)), M.shape[0]


# ------------------------------------------------------------------------
# Nulls
# ------------------------------------------------------------------------

def null_label_shuffle(loci, situations, metric, n_trials, rng) -> dict:
    """Permute the second model's labels: same data, wrong pairing."""
    scores = []
    for a, b in combinations(sorted(loci), 2):
        enc = _enc
        N = len(situations)
        for _ in range(n_trials):
            perm = rng.sample(situations, N)
            B = {situations[i]: loci[b][perm[i]] for i in range(N)}
            M = distance_matrix(enc, loci[a], B, situations, metric)
            scores.append(top1(M)[0] / N)
    return {"accuracy": round(float(np.mean(scores)), 4),
            "sd": round(float(np.std(scores)), 4), "n": len(scores)}


def null_random_vocabulary(loci_selections, frame, situations, metric,
                           n_trials, rng) -> dict:
    """Same set size, landmarks chosen at random from the vocabulary.

    This is the important control. It asks whether the specific landmarks the
    models chose carry the signal, or whether *any* set of that size would
    produce the same retrieval accuracy. If this null comes out near chance,
    the content is doing the work.
    """
    vocabulary = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]
    enc = L.Encoder(frame)
    scores = []
    for _ in range(n_trials):
        synthetic = {}
        for model, per_situation in loci_selections.items():
            synthetic[model] = {}
            for situation, keys in per_situation.items():
                k = len(keys)
                pick = set(rng.sample(vocabulary, min(k, len(vocabulary))))
                obs = [L.Obs(*x.split("/", 2)) for x in sorted(pick)]
                synthetic[model][situation] = enc.encode(obs)
        for a, b in combinations(sorted(synthetic), 2):
            M = distance_matrix(enc, synthetic[a], synthetic[b], situations, metric)
            scores.append(top1(M)[0] / len(situations))
    return {"accuracy": round(float(np.mean(scores)), 4),
            "sd": round(float(np.std(scores)), 4), "n": len(scores)}


def mean_pairwise_jaccard(loci_selections, situations) -> dict:
    """How much do the models agree on the raw landmark sets?

    Reported because it qualifies the headline: if models agree almost
    completely about which landmarks apply, then a high retrieval score says
    the models agree about the situation — it does not by itself say that the
    geometry is discovering anything.
    """
    per_situation = {}
    for s in situations:
        vals = []
        for a, b in combinations(sorted(loci_selections), 2):
            A = loci_selections[a].get(s, set())
            B = loci_selections[b].get(s, set())
            union = A | B
            vals.append(len(A & B) / len(union) if union else 0.0)
        per_situation[s] = round(float(np.mean(vals)), 4) if vals else 0.0
    allv = [v for v in per_situation.values()]
    return {"per_situation": per_situation,
            "mean": round(float(np.mean(allv)), 4) if allv else 0.0}


def known_answer_checks(frame) -> dict:
    """Cases whose answer we already know, checked before trusting any number."""
    enc = L.Encoder(frame)
    A = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors[:12]}
    B = set(A)
    C = set(A) - {sorted(A)[0]}
    D = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors[20:32]}

    def locus_of(keys):
        obs = [L.Obs(*k.split("/", 2)) for k in sorted(keys)]
        return enc.encode(obs)

    la, lb, lc, ld = (locus_of(x) for x in (A, B, C, D))
    return {
        "identical_sets_same_commitment": la.commitment == lb.commitment,
        "identical_sets_hamming": enc.hamming(la, lb),
        "one_landmark_removed_hamming": enc.hamming(la, lc),
        "disjoint_sets_hamming": enc.hamming(la, ld),
        "disjoint_greater_than_one_removed": (
            enc.hamming(la, ld) > enc.hamming(la, lc)),
        "monotone": (enc.hamming(la, lb) <= enc.hamming(la, lc)
                     <= enc.hamming(la, ld)),
    }


# ------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------

_enc = None


def main() -> int:
    global _enc
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcripts", nargs="+", help="probe JSONL file(s)")
    ap.add_argument("--metric", default="hamming",
                    choices=("hamming", "similarity", "prefix"))
    ap.add_argument("--null-trials", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    frame = primer.expand()
    _enc = L.Encoder(frame)

    records = load_transcripts([Path(p) for p in args.transcripts])
    ok = usable(records)
    if not ok:
        print("error: no usable records", file=sys.stderr)
        return 2

    selections: dict[str, dict[str, set]] = defaultdict(dict)
    for r in ok:
        selections[r["model"]][r["situation_id"]] = set(r["landmarks"])
    selections = dict(selections)

    # The primer fingerprint is part of the evidence. Coordinates produced under
    # a different primer are not comparable, so a mismatch is a hard stop, not a
    # warning: the geometry would be incommensurable and the score meaningless.
    used_fps = {r["primer_fingerprint"] for r in ok}
    if used_fps != {frame.fingerprint()}:
        print(f"error: transcripts were produced under primer {sorted(used_fps)} "
              f"but the current primer is {frame.fingerprint()}. Re-run the probe.",
              file=sys.stderr)
        return 3

    all_situations = sorted({r["situation_id"] for r in ok})
    # A model is only usable if it answered every situation. A model with partial
    # coverage would be scored on a different subset than its peers, which
    # silently makes the comparison non-comparable.
    models = sorted(m for m, per in selections.items()
                    if all(s in per for s in all_situations))
    dropped = sorted(set(selections) - set(models))
    situations = all_situations

    if len(models) < 2:
        print(f"error: only {len(models)} model(s) have full coverage of "
              f"{len(all_situations)} situations; need at least 2. "
              f"Dropped for partial coverage: {dropped}", file=sys.stderr)
        return 4
    if dropped:
        print(f"note: dropped for partial coverage: {', '.join(dropped)}")

    print(f"primer fingerprint : {frame.fingerprint()}")
    print(f"models             : {len(models)} — {', '.join(models)}")
    print(f"situations         : {len(situations)} — {', '.join(situations)}")
    print(f"metric             : {args.metric}")
    print()

    loci = encode_all(frame, selections)

    # ------------------------------------------------------------------------
    top1_scores, strict_scores, hung_scores, pair_detail = [], [], [], {}
    for a, b in combinations(models, 2):
        M = distance_matrix(_enc, loci[a], loci[b], situations, args.metric)
        c1, n1 = top1(M)
        cs, _ = top1_strict(M)
        c2, n2 = hungarian(M)
        top1_scores.append(c1 / n1)
        strict_scores.append(cs / n1)
        hung_scores.append(c2 / n2)
        pair_detail[f"{a} vs {b}"] = {
            "top1": f"{c1}/{n1}", "top1_accuracy": round(c1 / n1, 4),
            "top1_strict": f"{cs}/{n1}", "top1_strict_accuracy": round(cs / n1, 4),
            "hungarian": f"{c2}/{n2}", "hungarian_accuracy": round(c2 / n2, 4),
        }

    chance = 1.0 / len(situations)
    result = {
        "primer_fingerprint": frame.fingerprint(),
        "metric": args.metric,
        "models": models,
        "situations": situations,
        "n_calls_used": len(ok),
        "n_calls_recorded": len(records),
        "pairs": len(pair_detail),
        "top1_accuracy": round(float(np.mean(top1_scores)), 4),
        "top1_strict_accuracy": round(float(np.mean(strict_scores)), 4),
        "top1_ties_counted_as_hits": round(float(np.mean(top1_scores)
                                                 - np.mean(strict_scores)), 4),
        "top1_sd_across_pairs": round(float(np.std(top1_scores)), 4),
        "hungarian_accuracy": round(float(np.mean(hung_scores)), 4),
        "chance": round(chance, 4),
        "pair_detail": pair_detail,
        "mean_pairwise_landmark_jaccard": mean_pairwise_jaccard(selections, situations),
        "known_answer": known_answer_checks(frame),
    }

    # ------------------------------------------------------------------------
    rng = random.Random(args.seed)
    result["null_label_shuffle"] = null_label_shuffle(
        loci, situations, args.metric, args.null_trials, rng)
    rng = random.Random(args.seed)  # reset so both nulls use the same stream
    result["null_random_vocabulary"] = null_random_vocabulary(
        selections, frame, situations, args.metric, args.null_trials, rng)
    result["null_seed"] = args.seed

    # ------------------------------------------------------------------------
    print(f"real cross-model top-1     : {result['top1_accuracy']:.4f} "
          f"(strict, ties excluded: {result['top1_strict_accuracy']:.4f}) "
          f"({result['top1_accuracy']*len(situations):.1f}/{len(situations)} per pair)")
    print(f"real cross-model Hungarian : {result['hungarian_accuracy']:.4f}")
    print(f"chance                     : {chance:.4f}")
    print(f"null: label shuffle        : {result['null_label_shuffle']['accuracy']:.4f} "
          f"(sd {result['null_label_shuffle']['sd']:.4f})")
    print(f"null: random vocabulary    : {result['null_random_vocabulary']['accuracy']:.4f} "
          f"(sd {result['null_random_vocabulary']['sd']:.4f})")
    print(f"mean landmark Jaccard      : {result['mean_pairwise_landmark_jaccard']['mean']:.4f}")
    ka = result["known_answer"]
    print(f"known-answer monotone      : {ka['monotone']} "
          f"(identical {ka['identical_sets_hamming']}, "
          f"one removed {ka['one_landmark_removed_hamming']}, "
          f"disjoint {ka['disjoint_sets_hamming']})")

    out = Path(args.out) if args.out else EVIDENCE / "blind-match.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
