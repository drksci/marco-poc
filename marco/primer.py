"""The primer: one small seed in, the whole shared geometry out.

The idea
--------
Two agents that have never met cannot compare coordinates unless they share a
frame. The obvious way to share a frame is to transmit it — ship the landmark
list, the codebook, the axis order, the quantisation table. That is what a
schema registry does, and it is why registries have to be versioned, hosted and
kept in sync.

The alternative this repo demonstrates: transmit a *generator*, not the
generated thing. The seed is a few hundred bytes. Both sides expand it with the
same deterministic procedure and arrive at a byte-identical frame — verified by
fingerprint, not by trust.

What the seed determines
------------------------
    landmarks    -> the public chart (45 named places)
    phonology    -> the 32-entry pronounceable codebook
    markers      -> the certainty ladder
    distance     -> the metric on the chart
    partition    -> the axis order (NOT stored; *derived* from a population
                    that is itself derived from the seed)
    similarity   -> MinHash parameters
    beats        -> how the rendering is grouped for human reading

Two properties matter and both are measured in `scripts/01_unroll_primer.py`:

1. **Self-decompressing.** Seed bytes are constant. Frame bytes are ~6x larger
   and fully reconstructed. Nothing about the frame is transmitted.
2. **Self-generating.** The seed does not contain the query set, the state
   vocabulary, or the situations. The generator produces those at run time, so
   the transmitted size stays constant while the emitted protocol is unbounded.

The second property is the real argument against static registries: a registry
must enumerate what it can express, so its size grows with the state space. A
seed does not.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import world as _world
from .locus import Partition, build_syllables

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "primer.seed.json"


def load_seed(path: Path | str = DEFAULT_SEED_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────
# Expansion step 1: landmarks
# ─────────────────────────────────────────────────────────────────────────

def expand_landmarks(seed: dict) -> list[tuple[str, str, str]]:
    """Flatten the landmark spec into explicit (group, subject, detail).

    The seed nests `group -> subject -> {detail: the plain sentence}`. The
    expansion is a plain ordered walk, so the resulting list is a pure function
    of the seed.
    """
    out: list[tuple[str, str, str]] = []
    for group, subjects in seed["landmarks"].items():
        for subject, details in subjects.items():
            for detail in details:
                out.append((group, subject, detail))
    return out


def expand_plain(seed: dict) -> dict[str, str]:
    """The plain-English reading of every statement, keyed by landmark key.

    This travels inside the primer rather than being a docstring, because both
    sides must read a statement the same way for an answer to mean anything.
    """
    return {f"{g}/{s}/{d}": sentence
            for g, subjects in seed["landmarks"].items()
            for s, details in subjects.items()
            for d, sentence in details.items()}


# ─────────────────────────────────────────────────────────────────────────
# The frame
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class Frame:
    """Everything both sides must agree on. Reconstructed, never transmitted."""
    seed: dict
    anchors: list[tuple[str, str, str]]
    plain: dict[str, str]
    syllables: list[str]
    markers: dict
    distance: dict
    hierarchy: tuple
    partition: Partition
    minhash_n: int
    minhash_seed: int
    beats: tuple
    population_params: dict
    population: list[list[str]]
    _fp: str = field(default="", repr=False)

    # ── identity ─────────────────────────────────────────────────────────

    def canonical_form(self) -> dict:
        """The frame, serialised the way the fingerprint hashes it."""
        return {
            "primer_version": self.seed["primer_version"],
            "anchors": [list(a) for a in self.anchors],
            "plain": self.plain,
            "syllables": list(self.syllables),
            "markers": [list(v) for v in self.markers.values()],
            "distance": self.distance,
            "hierarchy": list(self.hierarchy),
            "partition": self.partition.to_dict(),
            "minhash": {"n": self.minhash_n, "seed": self.minhash_seed},
            "beats": list(self.beats),
            "commitment": self.seed["commitment"],
        }

    def fingerprint(self) -> str:
        if not self._fp:
            payload = json.dumps(self.canonical_form(), sort_keys=True,
                                 separators=(",", ":"), ensure_ascii=False)
            self._fp = hashlib.sha256(payload.encode()).hexdigest()
        return self._fp

    # ── sizes, for the self-decompression measurement ────────────────────

    def expanded_bytes(self) -> int:
        """Bytes of the *derived* frame — what the receiver reconstructs."""
        return len(json.dumps(self.canonical_form(), ensure_ascii=False).encode())

    def naive_transport_bytes(self) -> int:
        """Bytes you would have to send if the frame were shipped, not derived.

        This is what a registry-style exchange costs: the landmarks, the
        codebook, the *calibrated axis order*, and the reference population the
        calibration was computed from. Everything here is absent from the seed.
        """
        payload = {
            "anchors": [list(a) for a in self.anchors],
            "plain": self.plain,
            "syllables": list(self.syllables),
            "markers": [list(v) for v in self.markers.values()],
            "distance": self.distance,
            "hierarchy": list(self.hierarchy),
            "beats": list(self.beats),
            "partition": self.partition.to_dict(),
            "minhash": {"n": self.minhash_n, "seed": self.minhash_seed},
            "population": self.population,
        }
        return len(json.dumps(payload, ensure_ascii=False).encode())

    def seed_bytes(self) -> int:
        return len(json.dumps(self.seed, ensure_ascii=False).encode())

    def compression(self) -> dict:
        seed_b = self.seed_bytes()
        naive_b = self.naive_transport_bytes()
        frame_b = self.expanded_bytes()
        return {
            "seed_bytes": seed_b,
            "naive_transport_bytes": naive_b,
            "reconstructed_frame_bytes": frame_b,
            "reduction_factor": round(naive_b / seed_b, 2) if seed_b else 0.0,
            "transmitted_fraction": round(seed_b / naive_b, 4) if naive_b else 0.0,
        }

    def to_dict(self) -> dict:
        d = self.canonical_form()
        d["fingerprint"] = self.fingerprint()
        return d


def anchor_keys(frame: Frame) -> list[str]:
    """The 45 landmark keys in their canonical `kind/relation/value` form."""
    return [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]


def expand(seed: dict | None = None) -> Frame:
    """Seed -> Frame. Pure, deterministic, no I/O beyond the seed itself."""
    seed = seed if seed is not None else load_seed()

    anchors = expand_landmarks(seed)
    plain = expand_plain(seed)
    syllables = build_syllables(seed["phonology"])
    markers = {m[0]: {"rank": m[1], "anchors": m[2], "desc": m[3]}
               for m in seed["markers"]}
    distance = seed["distance"]
    hierarchy = tuple(seed["hierarchy"]["relations"])
    beats = tuple(seed["beats"])

    pp = seed["population"]
    states = _world.population(depth=pp["depth"])
    from .locus import anchor_vector
    pop = np.asarray([anchor_vector(s, anchors, distance) for s in states])

    part_cfg = seed["partition"]
    partition = Partition.calibrate(pop, levels=min(part_cfg["levels"], len(anchors)),
                                    branches=part_cfg["branches"])

    sim = seed["similarity"]
    return Frame(
        seed=seed, anchors=anchors, plain=plain, syllables=syllables, markers=markers,
        distance=distance, hierarchy=hierarchy, partition=partition,
        minhash_n=sim["minhash_n"], minhash_seed=sim["minhash_seed"],
        beats=beats, population_params=pp, population=states,
    )


# `corpus.generate` needs the landmark keys before a Frame exists, so expose a
# seed-only path that does not require a full expansion.
def anchor_keys_from_seed(seed: dict | None = None) -> list[str]:
    seed = seed if seed is not None else load_seed()
    return [f"{k}/{r}/{v}" for (k, r, v) in expand_landmarks(seed)]
