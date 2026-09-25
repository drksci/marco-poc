"""The properties this repo claims, checked rather than assumed.

Each check corresponds to a claim made in the README or in one of the articles,
so a wrong claim fails a test instead of quietly becoming part of the story.
Two of them exist because a measurement disagreed with what was written down
beforehand, and the disagreement is now a check rather than a footnote.

    python3 -m pytest tests/ -q
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import generator, locus as L, primer, world  # noqa: E402


@pytest.fixture(scope="session")
def frame():
    """The primer, expanded once. It is a pure function of the seed."""
    return primer.expand()


@pytest.fixture(scope="session")
def encoder(frame):
    return L.Encoder(frame)


@pytest.fixture(scope="session")
def loci(encoder):
    return {name: encoder.encode(world.build(name).observations())
            for name in world.WORLDS}


# -- the primer ----------------------------------------------------------

def test_seed_expands_to_45_landmarks(frame):
    assert len(frame.anchors) == 45
    assert len(frame.plain) == 45
    assert all(isinstance(s, str) and s.strip() for s in frame.plain.values())


def test_every_statement_key_is_group_subject_detail(frame):
    for key in frame.plain:
        assert len(key.split("/")) == 3, key


def test_codebook_adjacent_entries_differ_by_one_phoneme(frame):
    assert len(frame.syllables) == 32
    for a, b in zip(frame.syllables, frame.syllables[1:]):
        assert len(a) == len(b) == 2
        assert sum(1 for x, y in zip(a, b) if x != y) == 1, (a, b)


def test_fingerprint_is_stable_across_expansions(frame):
    assert primer.expand().fingerprint() == frame.fingerprint()


def test_seed_is_much_smaller_than_what_it_reconstructs(frame):
    c = frame.compression()
    assert c["seed_bytes"] < 4000
    assert c["naive_transport_bytes"] > 50000
    assert c["reduction_factor"] > 10


def test_axis_order_is_derived_not_stored(frame):
    """The seed must not contain the axis order; it must be recoverable from it."""
    seed = primer.load_seed()
    assert "axes" not in json.dumps(seed)
    assert frame.partition.axes != list(range(len(frame.partition.axes)))


# -- the places ----------------------------------------------------------

@pytest.mark.parametrize("name", sorted(world.WORLDS))
def test_every_place_passes_its_own_consistency_check(frame, name):
    check = world.build(name).self_check(frame)
    assert check["ok"], check["problems"]
    assert not check["contradictions"]
    assert not check["off_vocabulary"]


def test_preregistered_weak_ordering_holds(encoder, loci):
    """kitchen_with_friend gets further from each of four places, in order.

    Written down before the geometry was consulted. The *strict* version of the
    expectation fails, and is checked separately below.
    """
    base = "kitchen_with_friend"
    near = encoder.hamming(loci[base], loci["kitchen_alone"])
    mid = encoder.hamming(loci[base], loci["shared_workshop"])
    far = encoder.hamming(loci[base], loci["warehouse_alone"])
    furthest = encoder.hamming(loci[base], loci["dark_empty_room"])
    assert near <= mid < far < furthest, (near, mid, far, furthest)


def test_preregistration_disagreement_is_a_tie_not_an_ordering(encoder, loci):
    """The expectation that the alone/with-friend pair is *strictly* nearest fails.

    Kept as a check rather than a footnote. shared_workshop is as close to
    kitchen_with_friend as kitchen_alone is, because both are "a room with
    people in it, working". The geometry is right and the pre-registration was
    too fine-grained; the honest reading is a tie.
    """
    base = "kitchen_with_friend"
    near = encoder.hamming(loci[base], loci["kitchen_alone"])
    mid = encoder.hamming(loci[base], loci["shared_workshop"])
    assert near == mid, "the recorded tie no longer holds; update the write-up"


def test_addresses_are_not_identities(loci):
    """Two nearby places must not share a root."""
    assert loci["kitchen_with_friend"].commitment != loci["kitchen_alone"].commitment
    assert loci["kitchen_with_friend"].text != loci["kitchen_alone"].text


# -- determinism ---------------------------------------------------------

def test_encoding_is_deterministic(encoder):
    obs = world.build("shared_workshop").observations()
    first = encoder.encode(obs, timestamp=1234)
    second = encoder.encode(world.build("shared_workshop").observations(), timestamp=1234)
    assert first.text == second.text
    assert first.commitment == second.commitment
    assert first.short() == second.short()


def test_no_wall_clock_leaks_in(encoder):
    obs = world.build("locked_storeroom").observations()
    assert encoder.encode(obs).commitment == encoder.encode(obs).commitment


def test_root_is_stable_in_a_fresh_interpreter():
    statements = sorted(world.WORLDS["dark_empty_room"])
    src = (
        "import hashlib, json\n"
        "def canonical_root(statements, extra=()):\n"
        "    payload = json.dumps({'statements': sorted(statements), 'extra': sorted(extra)},\n"
        "                         separators=(',', ':'), ensure_ascii=False)\n"
        "    return hashlib.sha256(payload.encode()).hexdigest()\n"
        "print(canonical_root(%r))\n" % (statements,)
    )
    out = subprocess.run([sys.executable, "-c", src], capture_output=True,
                         text=True, cwd=str(ROOT))
    payload = json.dumps({"statements": statements, "extra": []},
                         separators=(",", ":"), ensure_ascii=False)
    assert out.stdout.strip() == hashlib.sha256(payload.encode()).hexdigest()


# -- progressive precision -----------------------------------------------

def test_more_precision_never_merges_two_places(encoder):
    """Reading further may separate places; it may never conflate them."""
    distinct_so_far = 0
    for k in (2, 4, 6, 8, 12, 16, 24, 45):
        groups = {}
        for p in world.WORLDS:
            loc = encoder.encode(world.build(p).observations(), precision=k)
            groups.setdefault(loc.prefix, []).append(p)
        assert len(groups) >= distinct_so_far, "precision %d lost a distinction" % k
        distinct_so_far = len(groups)


def test_six_axes_names_every_place(encoder):
    """The headline precision claim: six characters is enough for six places."""
    got = {encoder.encode(world.build(p).observations(), precision=6).prefix
           for p in world.WORLDS}
    assert len(got) == len(world.WORLDS)


def test_one_axis_is_coarse(encoder):
    got = {encoder.encode(world.build(p).observations(), precision=1).prefix
           for p in world.WORLDS}
    assert 1 < len(got) < len(world.WORLDS)


# -- the generator -------------------------------------------------------

def test_generator_resolves_the_population(frame):
    gen = generator.Generator(frame)
    trials = min(16, len(frame.population))
    resolved = sum(1 for i in range(trials) if gen.run(frame.population[i]).resolved)
    assert resolved == trials


def test_generator_asks_questions(frame):
    """Regression guard for the information-gain stall.

    Choosing by information gain alone left the generator with two candidates
    and no question worth asking, because a 1-vs-1 split has zero gain. This
    run returned zero steps before the fix.
    """
    trace = generator.Generator(frame).run(frame.population[0])
    assert len(trace.steps) > 0
    assert trace.resolved


def test_generator_is_deterministic(frame):
    a = generator.Generator(frame).run(frame.population[3])
    b = generator.Generator(frame).run(frame.population[3])
    assert [s.description for s in a.steps] == [s.description for s in b.steps]


# -- evidence integrity --------------------------------------------------

def test_recorded_results_match_the_frozen_primer():
    results = json.loads((ROOT / "evidence" / "RESULTS.json").read_text())
    assert results["primer"]["fingerprint"] == primer.expand().fingerprint()


def test_transcripts_are_from_the_frozen_primer():
    recorded = {
        json.loads(line)["primer_fingerprint"]
        for p in (ROOT / "evidence" / "transcripts").glob("probe-*.jsonl")
        for line in p.read_text().splitlines() if line.strip()
    }
    assert recorded == {primer.expand().fingerprint()}, "transcripts used a different primer"


def test_failed_probe_calls_are_recorded_not_dropped():
    """The probe must keep its failures. A tidy transcript is a warning sign."""
    records = [json.loads(line)
               for p in (ROOT / "evidence" / "transcripts").glob("probe-*.jsonl")
               for line in p.read_text().splitlines() if line.strip()]
    assert records, "no transcripts found"
    for r in records:
        assert "ok" in r
        if not r["ok"]:
            assert r.get("error"), "a failed call must say how it failed"


def test_known_answer_checks_pass():
    """Cases whose answer is known before the metric is trusted."""
    ka = json.loads((ROOT / "evidence" / "blind" / "blind-match.json").read_text())["known_answer"]
    assert ka["identical_sets_same_commitment"] is True
    assert ka["identical_sets_hamming"] == 0
    assert ka["disjoint_greater_than_one_removed"] is True
    assert ka["monotone"] is True
