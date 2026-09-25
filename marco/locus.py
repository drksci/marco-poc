"""The locus kernel: observations in, one deterministic coordinate out.

This is a cleaned port of `src/locus.py` from the research tree. The arithmetic
is unchanged; what changed is that every constant now arrives from the primer
frame instead of being a module global, so the geometry is a parameter of the
protocol rather than a property of the source file.

Pipeline
--------
    observations (each with an epistemic marker)
        -> canonical landmark set        (order-independent, deduplicated)
        -> distance-to-landmark vector   (the chart)
        -> MinHash signature             (similarity)
        -> calibrated partition prefix   (progressive precision)
        -> Gray-coded syllables          (pronounceable rendering)
        -> "⌁ world·place+reach~now  marker!commitment"

Determinism contract
--------------------
Given the same observations, the same primer frame and the same pinned
timestamp, `Encoder.encode` returns byte-identical output. There is no
wall-clock read, no unseeded randomness and no hidden state. `evidence/`
records a check of exactly this.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

import numpy as np

# ─────────────────────────────────────────────────────────────────────────
# Epistemic markers — the certainty ladder
# ─────────────────────────────────────────────────────────────────────────
#
# A locus may only be *anchored* (usable as a proof) at rank 4 or above.
# The point of the ladder is that a model's confidence cannot promote a claim;
# only evidence can. `~` and `?` are still useful — they are honest about being
# beliefs — but they never anchor.

MARKER_LADDER: dict[str, tuple[int, bool, str]] = {
    "=": (5, True,  "exact equality established by commitment"),
    "\u22a2": (4, True,  "derived reproducibly from admitted evidence"),
    "\u2248": (3, False, "statistical or sensor estimate"),
    "~": (2, False, "model belief, not evidence"),
    "?": (1, False, "unsupported guess"),
}


def marker_rank(m: str) -> int:
    return MARKER_LADDER.get(m, (0, False, ""))[0]


def can_anchor(m: str) -> bool:
    return MARKER_LADDER.get(m, (0, False, ""))[1]


def weakest(markers: Iterable[str]) -> str:
    """A claim is only as honest as its weakest input."""
    best = "="
    for m in markers:
        if marker_rank(m) < marker_rank(best):
            best = m
    return best


def promote(current: str, evidence: str) -> str:
    """Evidence may raise a marker; confidence may not."""
    return evidence if marker_rank(evidence) >= marker_rank(current) else current


# ─────────────────────────────────────────────────────────────────────────
# Observations
# ─────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Obs:
    """One canonical observation, carrying its own epistemic status."""
    kind: str       # namespace: self, fs, cap, perm, rel, env, sense, time
    relation: str   # predicate: is, ancestor, reachable, present, ...
    value: str      # canonical value
    marker: str = "\u22a2"
    weight: float = 1.0

    def key(self) -> str:
        return f"{self.kind}/{self.relation}/{self.value}"

    def __post_init__(self):
        if self.marker not in MARKER_LADDER:
            raise ValueError(f"unknown marker {self.marker!r}; "
                             f"use one of {list(MARKER_LADDER)}")


def expand(obs: Sequence[Obs], hierarchy=("ancestor", "inside", "path")) -> list[Obs]:
    """Expand hierarchical landmarks into weighted ancestors.

    `/src/marco/locus.py` also asserts the presence of `/src/marco` and `/src`,
    each at a reduced weight. This is what makes two agents working in the same
    subtree count as *near* rather than merely *different*.
    """
    out: list[Obs] = []
    for o in obs:
        out.append(o)
        if "/" in o.value and o.relation in hierarchy:
            parts = o.value.strip("/").split("/")
            for i in range(1, len(parts)):
                anc = "/" + "/".join(parts[:i])
                out.append(Obs(o.kind, o.relation, anc,
                               marker=o.marker, weight=o.weight * i / len(parts)))
    return out


def canonical(obs: Sequence[Obs], hierarchy=("ancestor", "inside", "path")) -> list[str]:
    """Order-independent, deduplicated landmark set (max weight wins)."""
    seen: dict[str, Obs] = {}
    for o in expand(obs, hierarchy):
        k = o.key()
        if k not in seen or o.weight > seen[k].weight:
            seen[k] = o
    return sorted(seen)


def commit(canon: Sequence[str], extra: Sequence[str] = ()) -> str:
    """The root. Exact, order-independent, seed-independent identity of a state.

    One hashing rule for the whole project, and this is it:

        sha256 of the canonical JSON of {"statements": sorted(canon),
                                         "extra":      sorted(extra)}

    This is the part that *destroys* adjacency on purpose: two nearby states get
    unrelated roots. Identity and nearness are separate objects, and this
    function is the boundary between them.

    `extra` is where anything that is not a statement goes: a pinned timestamp,
    a host tag, library versions, an operator label. Folding something into
    `extra` changes the root and leaves the address untouched, which is what
    lets an operator attest to a situation plus whatever environment
    fingerprints they happen to have, without disturbing the coordinate.

    Getting two hashing rules into a project by accident is easy, and it makes
    every quoted root suspect. An earlier revision of this repo had exactly that
    problem: `scripts/08_root_proof.py` hashed a `{"statements", "extra"}`
    document while this function hashed a bare sorted list, so two different
    32-byte values were both being called "the root". `tests/test_smoke.py`
    now checks that they agree.
    """
    payload = json.dumps({"statements": sorted(canon), "extra": sorted(extra)},
                         separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────
# The chart: distance to public landmarks
# ─────────────────────────────────────────────────────────────────────────

def distance_to_anchor(key: str, anchor: tuple[str, str, str], dist: dict) -> float:
    kind, rel, val = anchor
    if key == f"{kind}/{rel}/{val}":
        return 0.0
    if key.startswith(f"{kind}/{rel}/"):
        return dist["same_group_same_subject"]
    if key.startswith(f"{kind}/"):
        return dist["same_group_other_subject"]
    return dist["different_group"]


def anchor_vector(canon: Sequence[str], anchors, dist: dict) -> np.ndarray:
    """Distance-to-landmark vector. One coordinate per public landmark."""
    v = np.empty(len(anchors), dtype=float)
    for i, a in enumerate(anchors):
        v[i] = min((distance_to_anchor(k, a, dist) for k in canon), default=1.0)
    return v


# ─────────────────────────────────────────────────────────────────────────
# Pronounceable, locality-preserving rendering
# ─────────────────────────────────────────────────────────────────────────

def build_syllables(phonology: dict) -> list[str]:
    """A 32-entry codebook where adjacent entries differ by exactly one phoneme.

    Walk the consonant ring boustrophedon-style (left to right, then right to
    left), holding the vowel across the turn. A naive row-major walk costs two
    phonemes at every row boundary (`mu -> na`); the snake costs one. Combined
    with Gray decoding of the input chunk, one bit of state change becomes one
    phoneme of change.
    """
    cons = phonology["consonants"]
    vow = phonology["vowels"]
    out: list[str] = []
    for row, c in enumerate(cons):
        row_vowels = vow if row % 2 == 0 else list(reversed(vow))
        out.extend(c + v for v in row_vowels)
    out.extend(phonology.get("pad", []))
    if len(out) != 32:
        raise ValueError(f"codebook must have 32 entries, built {len(out)}")
    return out


def gray_decode(n: int) -> int:
    """Binary-reflected Gray decode: g -> b."""
    b, shift = n, 1
    while (n >> shift) > 0:
        b ^= n >> shift
        shift += 1
    return b


def bits_to_syllables(bits: Sequence[int], syllables: Sequence[str],
                      per: int = 5) -> list[str]:
    out = []
    for i in range(0, len(bits), per):
        chunk = list(bits[i:i + per])
        if len(chunk) < per:
            chunk += [0] * (per - len(chunk))
        val = 0
        for b in chunk:
            val = (val << 1) | int(b)
        out.append(syllables[gray_decode(val) % len(syllables)])
    return out


def syllables_to_text(syl: Sequence[str], beats=("world", "place", "reach", "now")) -> str:
    """Render an address. Flat when short, four-beat when there is enough to divide.

    The four beats are `world · place + reach ~ now`. Filling them requires
    enough syllables to give each beat at least two; below that the beat markers
    would be decorative, so a short address is written as one flat run instead.
    An address that claims a structure it has not got is worse than a plain one.
    """
    n = len(syl)
    if n == 0:
        return "\u2301 ??"
    if n < 8:
        return "\u2301 " + ".".join(syl)
    q = max(1, math.ceil(n / 4))
    groups = [list(syl[0:q]), list(syl[q:2 * q]), list(syl[2 * q:3 * q]), list(syl[3 * q:])]
    parts = [".".join(g) for g in groups]
    while len(parts) < 4:
        parts.append("")
    return f"\u2301 {parts[0]}\u00b7{parts[1]}+{parts[2]}~{parts[3]}"


# ─────────────────────────────────────────────────────────────────────────
# Similarity primitive
# ─────────────────────────────────────────────────────────────────────────

class MinHash:
    """Estimates Jaccard similarity over the *full* signature.

    Deliberately not used for prefixes. Individual positions of a MinHash
    signature carry no ordering information, so a shared prefix of a MinHash is
    not a neighbourhood — a fact this project learned the hard way and which is
    why prefixes come from `Partition` instead.
    """

    def __init__(self, n: int = 96, seed: int = 0):
        self.n = n
        rng = np.random.RandomState(seed & 0xFFFFFFFF)
        self._a = [int(x) for x in rng.randint(1, 2**31 - 1, size=n)]
        self._b = [int(x) for x in rng.randint(0, 2**31 - 1, size=n)]
        self._p = 2**31 - 1

    def _h(self, s: str, i: int) -> int:
        h = int(hashlib.blake2b(s.encode(), digest_size=8).hexdigest(), 16)
        return (self._a[i] * h + self._b[i]) % self._p

    def signature(self, canon: Sequence[str]) -> np.ndarray:
        sig = np.full(self.n, self._p, dtype=np.int64)
        for key in canon:
            for i in range(self.n):
                hv = self._h(key, i)
                if hv < sig[i]:
                    sig[i] = hv
        return sig

    def distance(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.sum(a != b)) / self.n


# ─────────────────────────────────────────────────────────────────────────
# Prefix primitive: the calibrated hierarchical partition
# ─────────────────────────────────────────────────────────────────────────

class Partition:
    """Fixed-axis, fixed-boundary hierarchical partition.

    Axes are calibrated on a reference population and ordered by descending
    discriminative power, so the positions that cost the most when they change
    carry the strongest landmarks.
    """

    def __init__(self, axes: Optional[Sequence[int]] = None, levels: int = 45,
                 branches: int = 2):
        self.levels = levels
        self.branches = branches
        self.axes: list[int] = list(axes) if axes is not None else list(range(levels))
        self.boundaries: list[list[float]] = [
            [j / branches for j in range(1, branches)] for _ in self.axes
        ]

    @classmethod
    def calibrate(cls, population: np.ndarray, levels: int = 45,
                  branches: int = 2) -> "Partition":
        pop = np.asarray(population, dtype=float)
        if pop.ndim != 2 or pop.shape[0] < 2:
            return cls(levels=levels, branches=branches)
        order = np.argsort(-np.var(pop, axis=0))[:levels]
        return cls(axes=[int(a) for a in order], levels=levels, branches=branches)

    def prefix(self, vec: np.ndarray) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        out = []
        for axis, cuts in zip(self.axes, self.boundaries):
            b = 0
            for j, cut in enumerate(cuts):
                if vec[axis] >= cut:
                    b = j + 1
            out.append(chars[b % len(chars)])
        return "".join(out)

    def bits(self, vec: np.ndarray) -> list[int]:
        out: list[int] = []
        width = int(math.log2(self.branches))
        for axis in self.axes:
            b = int(np.clip(vec[axis] * self.branches, 0, self.branches - 1))
            out.extend([(b >> s) & 1 for s in range(width - 1, -1, -1)])
        return out

    @staticmethod
    def lcp(a: str, b: str) -> int:
        n = 0
        for x, y in zip(a, b):
            if x != y:
                break
            n += 1
        return n

    def to_dict(self) -> dict:
        return {"axes": self.axes, "levels": self.levels, "branches": self.branches}

    @classmethod
    def from_dict(cls, d: dict) -> "Partition":
        return cls(axes=d["axes"], levels=d.get("levels", len(d["axes"])),
                   branches=d.get("branches", 2))


# ─────────────────────────────────────────────────────────────────────────
# Locus and encoder
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class Locus:
    """A complete, self-describing reading. Never an identity — a description."""
    text: str
    commitment: str
    marker: str
    prefix: str
    signature: list[int]
    anchor_vector: list[float]
    canon: list[str]
    primer_fp: str
    timestamp: Optional[int] = None

    def short(self) -> str:
        a = self.commitment[:6]
        if can_anchor(self.marker):
            return f"{self.text} !{a}"
        return f"{self.text} {self.marker}!{a}"

    def is_anchored(self) -> bool:
        return can_anchor(self.marker)


class Encoder:
    """Observations -> Locus. Deterministic given (observations, frame, ts)."""

    def __init__(self, frame):
        self.frame = frame
        self._mh = MinHash(n=frame.minhash_n, seed=frame.minhash_seed)

    def encode(self, obs: Sequence[Obs], timestamp: Optional[int] = None,
               precision: Optional[int] = None) -> Locus:
        canon = canonical(obs, self.frame.hierarchy)
        vec = anchor_vector(canon, self.frame.anchors, self.frame.distance)
        sig = self._mh.signature(canon)

        axes = self.frame.partition.axes
        if precision is not None:
            k = max(1, min(int(precision), len(axes)))
            sub = Partition(axes=axes[:k], levels=k,
                            branches=self.frame.partition.branches)
        else:
            sub = self.frame.partition

        syl = bits_to_syllables(sub.bits(vec), self.frame.syllables, per=5)
        text = syllables_to_text(syl, self.frame.beats)
        marker = weakest(o.marker for o in obs)

        # A pinned timestamp rides in `extra`, so a state root (no timestamp) and
        # a session root (timestamp pinned) are two different, well-defined things.
        extra = [f"t={timestamp}"] if timestamp is not None else []
        return Locus(
            text=text, commitment=commit(canon, extra), marker=marker, prefix=sub.prefix(vec),
            signature=[int(x) for x in sig],
            anchor_vector=[float(x) for x in vec],
            canon=canon, primer_fp=self.frame.fingerprint(), timestamp=timestamp,
        )

    # ── comparison ────────────────────────────────────────────────────────

    def similarity(self, a: Locus, b: Locus) -> float:
        """1 - MinHash distance; estimates Jaccard of the two landmark sets."""
        return 1.0 - self._mh.distance(np.array(a.signature), np.array(b.signature))

    def hamming(self, a: Locus, b: Locus) -> int:
        """Phoneme-level distance between two rendered loci."""
        sa = a.text.replace("\u2301 ", "").replace("\u00b7", "").replace("+", "") \
                   .replace("~", "").replace(".", "")
        sb = b.text.replace("\u2301 ", "").replace("\u00b7", "").replace("+", "") \
                   .replace("~", "").replace(".", "")
        return sum(1 for x, y in zip(sa, sb) if x != y) + abs(len(sa) - len(sb))

    def compare(self, a: Locus, b: Locus) -> dict:
        if a.primer_fp != b.primer_fp:
            return {
                "comparable": False,
                "reason": "different primer: the two geometries are incommensurable; "
                          "only exact identity can be compared",
                "same_identity": a.commitment == b.commitment,
            }
        return {
            "comparable": True,
            "same_identity": a.commitment == b.commitment,
            "similarity": round(self.similarity(a, b), 4),
            "prefix_lcp": Partition.lcp(a.prefix, b.prefix),
            "prefix_len": len(a.prefix),
            "hamming": self.hamming(a, b),
            "shared_landmarks": len(set(a.canon) & set(b.canon)),
            "marker": weakest([a.marker, b.marker]),
        }
