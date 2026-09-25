"""The self-generating bootstrap: the seed that asks its own questions.

What is being demonstrated
--------------------------
A static schema registry has to *enumerate* what it can express. Ask it about a
situation it has never seen and it has nothing to say; add a new capability and
every consumer must update.

A primer behaves differently. It contains no situations and no questions. It
contains a small amount of geometry plus a rule for choosing the next question,
and that rule generates the protocol as it runs:

    q_t   = G(S_t)                     choose the most informative next query
    b_t   = q_t(x)                     ask the world, get one bit
    S_t+1 = Refine(S_t, b_t)           keep only states consistent with the bit

Two agents running the identical G on their own observations therefore walk the
same decision tree without ever transmitting a question list, a state
vocabulary, or a state count. Both sides are doing arithmetic on a shared frame.

Why the query is chosen this way
--------------------------------
A query is worth asking in proportion to how much it *halves* the remaining
candidate set. That is the classical information-gain criterion, and it is what
makes coarse-to-fine emerge instead of being imposed: the first question is the
one that splits the whole population most evenly, so the first rendered beat
carries the coarsest information and later beats refine.

This module is deliberately transparent: `run()` returns the whole trace, so
every claim about how many questions it takes is checkable rather than asserted.
"""

from __future__ import annotations

import math

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True)
class Query:
    """A yes/no question over an anchor set.

    `terms` is a tuple of `(anchor_index, polarity)`; the query is satisfied
    when every term matches. Most queries are a single positive term, which is
    exactly "is this landmark present?".
    """
    terms: tuple

    def satisfied_by(self, state: Sequence[str], anchors: Sequence[str]) -> bool:
        for idx, polarity in self.terms:
            present = anchors[idx] in state
            if present != polarity:
                return False
        return True

    def describe(self, anchors: Sequence[str]) -> str:
        parts = []
        for idx, polarity in self.terms:
            parts.append(("" if polarity else "not ") + anchors[idx])
        return " and ".join(parts)

    @property
    def is_conjunctive(self) -> bool:
        return len(self.terms) > 1


@dataclass
class Step:
    index: int
    query: Query
    description: str
    answer: bool
    candidates_before: int
    candidates_after: int
    bits_so_far: int


@dataclass
class Trace:
    target: str
    steps: list[Step] = field(default_factory=list)
    resolved: bool = False
    survivors: int = 0

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "resolved": self.resolved,
            "survivors": self.survivors,
            "questions_asked": len(self.steps),
            "used_conjunction": self.used_conjunction,
            "steps": [
                {"i": s.index, "query": s.description, "answer": s.answer,
                 "candidates_before": s.candidates_before,
                 "candidates_after": s.candidates_after,
                 "bits": s.bits_so_far}
                for s in self.steps
            ],
        }

    @property
    def used_conjunction(self) -> bool:
        """Did the generator have to build a question that was not in the primer?"""
        return any(s.query.is_conjunctive for s in self.steps)


def _entropy(counts) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c:
            p = c / total
            h -= p * math.log2(p)
    return h


def _discrimination(n: int, pos: np.ndarray) -> np.ndarray:
    """How well each candidate query halves the surviving set.

    Score is `pos * neg`, the larger the more balanced the split. This is the
    quantity that matters, and it is *not* the same as information gain: at
    n = 2 a perfectly discriminating split (1 vs 1) has zero information gain,
    because both outcomes were already equally likely. Choosing by gain alone
    therefore stalls with two candidates left forever — a real bug this repo
    hit and kept in the record (`evidence/validation.json`, section B).

    Maximising `pos * neg` is equivalent to minimising the expected number of
    survivors, `(pos² + neg²) / n`, and behaves correctly at every n.
    """
    n = int(n)
    pos = pos.astype(float)
    neg = n - pos
    valid = (pos > 0) & (neg > 0)
    return np.where(valid, pos * neg, 0.0)


class Generator:
    """Chooses its own questions against a population of situations.

    The population is the only thing with content. It stands in for "the
    situations an agent might find itself in" — in the shipped demo it is the
    corpus the primer derives from its own seed; in a real deployment it would
    be the agent's own recent history, or a peer's advertised samples.

    The presence matrix is precomputed once and every gain is computed with a
    single matmul, so a 45-landmark question set over hundreds of candidates is
    a microsecond-scale operation rather than a nested loop.
    """

    def __init__(self, frame, population: Optional[Sequence[Sequence[str]]] = None):
        self.frame = frame
        self.anchors: list[str] = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]
        self.population = [list(s) for s in (population if population is not None
                                             else frame.population)]
        self.n_anchors = len(self.anchors)
        self.n_pop = len(self.population)
        # presence[a, p] == True iff landmark a is present in situation p
        self.presence = np.zeros((self.n_anchors, self.n_pop), dtype=bool)
        for a, anchor in enumerate(self.anchors):
            for p, state in enumerate(self.population):
                if anchor in state:
                    self.presence[a, p] = True

    # ── the generator function G ─────────────────────────────────────────

    def _single_scores(self, idx: np.ndarray) -> np.ndarray:
        sub = self.presence[:, idx]
        return _discrimination(len(idx), sub.sum(axis=1))

    def _conjunction_scores(self, idx: np.ndarray):
        """Gain for every two-term query, via one matmul per polarity pattern."""
        sub = self.presence[:, idx]
        sub_i = sub.astype(np.int32)
        not_sub_i = (~sub).astype(np.int32)
        n = len(idx)
        both = sub_i @ sub_i.T          # i present AND j present
        i_notj = sub_i @ not_sub_i.T    # i present AND j absent
        return {
            (True, True): _discrimination(n, both),
            (True, False): _discrimination(n, i_notj),
            (False, True): _discrimination(n, i_notj.T),
        }

    def next_query(self, idx: np.ndarray) -> Optional[Query]:
        """The query that removes the most uncertainty, or None if none exists.

        Single landmarks are tried first because "is this landmark present?" is
        the cheap, honest question the primer's vocabulary supports. Only when
        no single landmark separates the survivors does the generator *build* a
        question — a conjunction that appears nowhere in the primer. That
        fallback is the part that earns the word generating.
        """
        scores = self._single_scores(idx)
        best = int(np.argmax(scores))
        if scores[best] > 0:
            return Query(((best, True),))

        conj = self._conjunction_scores(idx)
        best_terms, best_gain = None, 0.0
        for (pi, pj), mat in conj.items():
            # Only the upper triangle is a distinct unordered pair.
            m = np.triu(mat, k=1)
            j, i = np.unravel_index(int(np.argmax(m)), m.shape)
            if m[i, j] > best_gain:
                best_gain = m[i, j]
                best_terms = ((i, pi), (j, pj))
                best_index = (i, j)
        if best_terms is None:
            return None
        # Normalise order so the description is stable.
        terms = tuple(sorted(best_terms))
        return Query(terms)

    # ── the loop ─────────────────────────────────────────────────────────

    def run(self, target: Sequence[str], max_steps: int = 64,
            use_conjunctions: bool = True) -> Trace:
        """Run MARCO/POLO against one situation and return the full trace."""
        target_key = "|".join(sorted(target))
        idx = np.arange(self.n_pop)
        trace = Trace(target=target_key)
        bits = 0

        for step_i in range(max_steps):
            if len(idx) <= 1:
                break
            q = self.next_query(idx)
            if q is None:
                break
            if q.is_conjunctive and not use_conjunctions:
                break
            answer = q.satisfied_by(target, self.anchors)
            before = len(idx)
            matched = np.array([q.satisfied_by(self.population[p], self.anchors)
                                for p in idx])
            idx = idx[matched if answer else ~matched]
            bits += math.log2(before / len(idx)) if idx.size else 0.0
            trace.steps.append(Step(
                index=step_i, query=q, description=q.describe(self.anchors),
                answer=answer, candidates_before=before,
                candidates_after=len(idx), bits_so_far=round(bits, 3),
            ))

        trace.survivors = int(len(idx))
        trace.resolved = len(idx) == 1
        return trace

    def reset(self) -> None:
        return None


# ─────────────────────────────────────────────────────────────────────────
# What "self-generating" buys, measured
# ─────────────────────────────────────────────────────────────────────────

def bootstrap_report(frame, n_trials: int = 64, max_steps: int = 64) -> dict:
    """Run the bootstrap over the population and summarise what it generated.

    Reports the two numbers that separate a generator from a registry:
    how many questions it took, and how often it had to *invent* one that was
    not in the primer's vocabulary.
    """
    gen = Generator(frame)
    questions, conjunctions, resolved = [], 0, 0
    for i in range(min(n_trials, len(frame.population))):
        gen.reset()
        tr = gen.run(frame.population[i], max_steps=max_steps)
        questions.append(len(tr.steps))
        conjunctions += int(tr.used_conjunction)
        resolved += int(tr.resolved)

    n = len(questions)
    return {
        "trials": n,
        "population": len(frame.population),
        "mean_questions": round(sum(questions) / n, 3) if n else 0.0,
        "max_questions": max(questions) if questions else 0,
        "min_questions": min(questions) if questions else 0,
        "resolved": resolved,
        "conjunctive_queries_used": conjunctions,
        "log2_population": round(math.log2(max(1, len(frame.population))), 3),
    }
