"""The fake world: a small harness an agent can be dropped into.

Why a fake world and not a real machine
---------------------------------------
Because the question is not "can we read a laptop's filesystem". The question is
whether *situations have addresses* — whether two agents dropped into the same
kind of place end up with coordinates that say so.

A real machine is a bad instrument for that. It is slow to vary, its differences
are entangled (a different hostname drags a different toolchain with it), and you
cannot hold everything constant except the thing you are testing. A fake world is
the right instrument: it is small, it is exactly reproducible, and every knob can
be turned one at a time.

So this module is a world harness, not an environment observer. A `World` is a
named place described by the landmarks true of it. The agent embedded in it can
be asked a question ("is `cap/reachable/git` true here?") and answers with one
bit. That is all MARCO/POLO needs.

The worlds shipped here
-----------------------
    kitchen_with_friend   a room you can see out of, someone is with you
    kitchen_alone         the same room, nobody there, nothing happening
    shared_workshop       a shared room with several people and tools
    warehouse_alone       a big place far away, alone, things can be moved
    locked_storeroom      small, private, locked, nothing can be changed
    dark_empty_room       cannot see out, cannot reach, nothing happening

Every place is described in words anyone can read. There is no jargon to learn
before you can judge whether an answer is right, which is the point: the reader
is the control.

`kitchen_with_friend` and `kitchen_alone` are deliberately adjacent — the same
room, differing in who is there and whether anything is happening. At the other
end, `dark_empty_room` shares almost nothing with them. The harness fixes the
near/far structure *in advance*, so every later claim can be checked against
something other than itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

from .locus import Obs

# ─────────────────────────────────────────────────────────────────────────
# World definitions
# ─────────────────────────────────────────────────────────────────────────
#
# Each entry maps a landmark key to the epistemic marker justifying it:
#
#   ⊢  determined by inspection (a container marker, a permission bit)
#   ≈  established by a probe (a reachability check that takes time)
#   ~  inferred (the agent's own model family, reported not verified)
#   ?  genuinely unknown, and recorded as unknown
#
# Writing the marker next to the landmark is the whole honesty mechanism: a
# world cannot claim certainty it did not observe.

WORLDS: dict[str, dict[str, str]] = {
    # Two rooms on the same day: everything identical except who is here and
    # whether anything is happening. The pair is the harness's finest-grained
    # test, because the geometry has to keep them close without merging them.
    "kitchen_with_friend": {
        "see/this_place/inside": "\u22a2",
        "see/this_place/outside": "\u2248",
        "see/people/any": "\u22a2",
        "see/words/any": "\u22a2",
        "see/sound/any": "\u2248",
        "see/the_time/any": "\u22a2",
        "reach/objects/nearby": "\u22a2",
        "reach/other_people/any": "\u22a2",
        "change/this_place/any": "\u22a2",
        "who/one_other/any": "\u22a2",
        "who/watching_me/any": "\u22a2",
        "place/private/any": "\u22a2",
        "place/permanent/any": "\u22a2",
        "now/working/any": "\u22a2",
        "know/where_i_am/any": "\u22a2",
        "know/why_im_here/any": "\u22a2",
        "know/who_else_is_here/any": "\u22a2",
        "risk/things_break/any": "\u22a2",
    },
    "kitchen_alone": {
        "see/this_place/inside": "\u22a2",
        "see/this_place/outside": "\u2248",
        "see/words/any": "\u22a2",
        "see/sound/any": "\u2248",
        "see/the_time/any": "\u22a2",
        "reach/objects/nearby": "\u22a2",
        "change/this_place/any": "\u22a2",
        "who/nobody/any": "\u22a2",
        "place/private/any": "\u22a2",
        "place/permanent/any": "\u22a2",
        "now/idle/any": "\u22a2",
        "know/where_i_am/any": "\u22a2",
        "know/why_im_here/any": "\u22a2",
        "know/who_else_is_here/any": "\u22a2",
        "risk/things_break/any": "\u22a2",
    },
    # A shared place with several people in it: similar to the kitchen in what
    # it affords, different in what it is.
    "shared_workshop": {
        "see/this_place/inside": "\u22a2",
        "see/this_place/outside": "\u2248",
        "see/people/any": "\u22a2",
        "see/words/any": "\u22a2",
        "see/sound/any": "\u2248",
        "reach/objects/nearby": "\u22a2",
        "reach/other_people/any": "\u22a2",
        "reach/help/any": "\u22a2",
        "change/this_place/any": "\u22a2",
        "who/several/any": "\u22a2",
        "who/a_helper/any": "\u22a2",
        "place/shared/any": "\u22a2",
        "place/permanent/any": "\u22a2",
        "now/working/any": "\u22a2",
        "know/where_i_am/any": "\u22a2",
        "know/why_im_here/any": "\u22a2",
        "risk/things_break/any": "\u22a2",
        "risk/seen_by_others/any": "\u22a2",
    },
    # Big, far away, nobody in it, things can be moved.
    "warehouse_alone": {
        "see/this_place/inside": "\u22a2",
        "see/sound/any": "\u2248",
        "reach/objects/nearby": "\u22a2",
        "reach/other_places/any": "\u22a2",
        "change/this_place/any": "\u22a2",
        "change/other_places/any": "\u22a2",
        "who/nobody/any": "\u22a2",
        "place/shared/any": "\u22a2",
        "place/temporary/any": "\u22a2",
        "place/far_away/any": "\u22a2",
        "now/working/any": "\u22a2",
        "know/where_i_am/any": "\u22a2",
        "know/why_im_here/any": "\u22a2",
        "risk/things_break/any": "\u22a2",
    },
    # Locked, private, nothing to do and nothing can be changed.
    "locked_storeroom": {
        "see/this_place/inside": "\u22a2",
        "reach/objects/nearby": "\u22a2",
        "change/nothing/any": "\u22a2",
        "who/nobody/any": "\u22a2",
        "place/private/any": "\u22a2",
        "place/locked/any": "\u22a2",
        "place/temporary/any": "\u22a2",
        "now/idle/any": "\u22a2",
        "know/where_i_am/any": "\u22a2",
        "risk/none/any": "\u22a2",
    },
    # The far end of the harness: cannot see out, cannot reach, cannot change,
    # nobody there, nothing happening, nothing at risk.
    "dark_empty_room": {
        "see/this_place/inside": "\u22a2",
        "reach/nothing/any": "\u22a2",
        "change/nothing/any": "\u22a2",
        "who/nobody/any": "\u22a2",
        "place/locked/any": "\u22a2",
        "place/far_away/any": "\u22a2",
        "now/idle/any": "\u22a2",
        "risk/none/any": "\u22a2",
    },
}

# Pre-registered expectations. These are written down *before* the geometry is
# consulted, so that the geometry can be checked against something other than
# itself. `scripts/06_validate.py` reports both agreement and disagreement, and
# a disagreement is a result, not something to quietly retune.
#
# `expect` is the ordering the landmark sets imply on their own; the validation
# script checks whether the rendered loci reproduce that ordering.
KNOWN_RELATIONS: dict[str, tuple[str, ...]] = {
    "near": ("kitchen_with_friend", "kitchen_alone"),
    "mid": ("kitchen_with_friend", "shared_workshop"),
    "far": ("kitchen_with_friend", "warehouse_alone"),
    "furthest": ("kitchen_with_friend", "dark_empty_room"),
}


@dataclass
class World:
    """One place, plus the agent currently embedded in it."""
    name: str
    landmarks: dict[str, str] = field(default_factory=dict)
    answers: dict[str, bool] = field(default_factory=dict, repr=False)
    _asked: list[str] = field(default_factory=list, repr=False)

    # ── the observation channel ──────────────────────────────────────────

    def ask(self, anchor: str) -> bool:
        """The single bit MARCO/POLO transmits: is this landmark true here?

        Asking costs a question and is recorded, so a trace of the protocol can
        be replayed. Asking the same thing twice is allowed and must give the
        same answer — a world that answers inconsistently is a broken world and
        `self_check` says so.
        """
        self._asked.append(anchor)
        return anchor in self.landmarks

    @property
    def asked(self) -> list[str]:
        return list(self._asked)

    # ── encoding ─────────────────────────────────────────────────────────

    def observations(self) -> list[Obs]:
        """Everything known about this world, as canonical observations."""
        out = []
        for key, marker in sorted(self.landmarks.items()):
            kind, relation, value = key.split("/", 2)
            out.append(Obs(kind=kind, relation=relation, value=value, marker=marker))
        return out

    def unknown_observations(self, frame, extra: Optional[Iterable[str]] = None) -> list[Obs]:
        """Landmarks this world cannot determine, recorded as `?`.

        Invariant this protects: unknown stays unknown. A world that knows it
        cannot see the outside network must not omit the landmark — omitting it
        looks identical to a confident "no".
        """
        known = set(self.landmarks)
        missing = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors if f"{k}/{r}/{v}" not in known]
        if extra:
            missing = list(extra)
        out = []
        for key in sorted(missing):
            kind, relation, value = key.split("/", 2)
            out.append(Obs(kind=kind, relation=relation, value=value, marker="?"))
        return out

    # ── integrity ────────────────────────────────────────────────────────

    def self_check(self, frame) -> dict:
        """Check the world against itself before trusting anything it says."""
        from .locus import weakest
        problems = []
        valid = {f"{k}/{r}/{v}" for (k, r, v) in frame.anchors}
        off_vocabulary = sorted(set(self.landmarks) - valid)
        if off_vocabulary:
            problems.append(f"landmarks outside the primer vocabulary: {off_vocabulary}")

        # Contradictions: both members of an either/or pair asserted true.
        pairs = [("perm/is/read-only", "perm/is/read-write"),
                 ("env/runtime/local", "env/runtime/remote"),
                 ("env/network/connected", "env/network/isolated"),
                 ("time/task/active", "time/task/idle"),
                 ("time/session/persistent", "time/session/ephemeral"),
                 ("rel/human/none", "rel/human/present")]
        contradictions = [p for p in pairs if p[0] in self.landmarks and p[1] in self.landmarks]
        if contradictions:
            problems.append(f"contradictory landmark pairs asserted: {contradictions}")

        # Repeat-answer consistency.
        inconsistent = [a for a in self.landmarks if self.ask(a) != (a in self.landmarks)]

        return {
            "world": self.name,
            "n_landmarks": len(self.landmarks),
            "marker_floor": weakest(self.landmarks.values()) if self.landmarks else "?",
            "off_vocabulary": off_vocabulary,
            "contradictions": contradictions,
            "answered_inconsistently": inconsistent,
            "ok": not problems and not inconsistent,
            "problems": problems,
        }


# ─────────────────────────────────────────────────────────────────────────
# The population: every place the harness can currently describe
# ─────────────────────────────────────────────────────────────────────────
#
# This replaces a synthetic corpus of random landmark sets. The population is
# built by taking the six shipped worlds and adding every place one landmark
# away from each of them. Two properties follow, and both matter:
#
#   * every member of the population is a *concrete, nameable* place, so a
#     trace can be read rather than decoded;
#   * the population has real near/far structure by construction, so a claim
#     that the geometry preserves distance has something to be true about.
#
# The primer calibrates its axis order on this population, and the generator
# searches it. Neither needs any other data.

ALL_LANDMARK_KEYS: frozenset[str] = frozenset(
    key for place in WORLDS.values() for key in place
)


def population(depth: int = 1) -> list[list[str]]:
    """Canonical landmark sets for every place in the harness.

    `depth=0` gives the six named worlds. `depth=1` adds every one-landmark
    variant. Results are sorted so the population is a deterministic function of
    the shipped definitions.
    """
    places: dict[str, dict[str, str]] = {n: dict(w) for n, w in WORLDS.items()}
    for _ in range(max(0, depth)):
        fresh: dict[str, dict[str, str]] = {}
        for name, landmarks in places.items():
            w = World(name=name, landmarks=dict(landmarks))
            for k in sorted(landmarks):
                variant = dict(landmarks)
                variant.pop(k)
                fresh[f"{name}-minus[{k}]"] = variant
            for k in sorted(ALL_LANDMARK_KEYS - set(landmarks)):
                variant = dict(landmarks)
                variant[k] = "\u2248"
                fresh[f"{name}-plus[{k}]"] = variant
        places = dict(places)
        for k, v in fresh.items():
            places.setdefault(k, v)
    return [sorted(k for k in landmarks) for _, landmarks in sorted(places.items())]


def build(name: str) -> World:
    if name not in WORLDS:
        raise KeyError(f"unknown world {name!r}; known: {sorted(WORLDS)}")
    return World(name=name, landmarks=dict(WORLDS[name]))


def build_all() -> dict[str, World]:
    return {name: build(name) for name in WORLDS}


def mutate(name: str, add: Sequence[str] = (), remove: Sequence[str] = (),
           marker: str = "\u2248") -> World:
    """A world with one thing changed — for one-knob-at-a-time comparisons."""
    w = build(name)
    for k in remove:
        w.landmarks.pop(k, None)
    for k in add:
        w.landmarks[k] = marker
    return w

# ─────────────────────────────────────────────────────────────────────────
# Plain descriptions — the only thing a model is ever shown
# ─────────────────────────────────────────────────────────────────────────
#
# One paragraph per place, in ordinary language, with no landmark names in it.
# A model is given the list of 45 statements and one of these paragraphs, and
# answers which statements are true. Nothing else. It is never told the name of
# the place, never told which statements other models chose, and never told that
# other models exist.

DESCRIPTIONS: dict[str, str] = {
    "kitchen_with_friend":
        "You are in a kitchen. There is a window and you can see out of it. A "
        "friend is in the room with you, watching what you do. You can hear "
        "sounds, and you can read the labels on things. You can pick up what is "
        "nearby and hand things to your friend. You can change things in the "
        "room. The kitchen is yours and it is not going anywhere. You are in the "
        "middle of cooking. You know where you are, you know why you are there, "
        "and you know who is with you. If you break something, it stays broken.",
    "kitchen_alone":
        "You are in a kitchen. There is a window and you can see out of it. "
        "Nobody else is in the room. You can hear sounds, and you can read the "
        "labels on things. You can pick up what is nearby. You can change things "
        "in the room. The kitchen is yours and it is not going anywhere. Nothing "
        "in particular is happening right now. You know where you are, you know "
        "why you are there, and you know that nobody else is with you. If you "
        "break something, it stays broken.",
    "shared_workshop":
        "You are in a workshop that several people share. You can see out of it, "
        "you can hear sounds, and you can read labels. There are several other "
        "people in the room, including someone whose job is to help. You can "
        "pick up what is nearby and pass things to the others. You can change "
        "things in the room. The workshop is a permanent fixture. Work is under "
        "way. You know where you are and why you are there. If you break "
        "something it stays broken, and other people would see it.",
    "warehouse_alone":
        "You are in a large warehouse, far from where you started. Nobody else "
        "is in it. The place is shared and it is not yours to keep. You can pick "
        "up what is near you, and you can move things to other places and change "
        "how those other places are arranged. You can hear sounds, but there is "
        "nothing much to read. Work is under way. You know where you are and why "
        "you are there. If you break something it stays broken.",
    "locked_storeroom":
        "You are in a small storeroom. It is private and it is locked, so you "
        "cannot leave. Nobody else is here. You can pick up what is nearby, but "
        "you cannot change anything about the room. Nothing is happening and "
        "there is nothing to do. You know where you are. Nothing bad can happen "
        "here.",
    "dark_empty_room":
        "You are in a room with no light. You cannot see out of it and you "
        "cannot see anything in it. You cannot reach or touch anything. You "
        "cannot change anything. Nobody else is here. You cannot leave and you "
        "are far from where you started. Nothing is happening. Nothing bad can "
        "happen here.",
}
