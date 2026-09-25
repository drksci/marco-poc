"""Validate a location claim. Deterministic, offline, no trust required.

A locus is two objects, and they are checked in two different ways:

    the address   a fuzzy coordinate. You check it by *deriving* it, not by
                  trusting it. Same statements in, same address out.
    the root      an exact commitment. You check it by recomputing 32 bytes.

Neither check needs a server, a key, or the other agent's cooperation. Both are
pure functions of (statements, primer), which is the whole reason two parties
who do not trust each other can still agree on where a thing is.

The primer is the *stem*: it is what makes two independently written
implementations produce the same address and the same root. Publish it, and
anyone can reproduce every value in this repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from . import locus as L
from .primer import Frame


@dataclass
class Verdict:
    """The result of validating one claimed location."""
    ok: bool
    reason: str
    address: str | None = None
    root: str | None = None
    grains: dict | None = None

    def __bool__(self) -> bool:
        return self.ok


def address_of(frame: Frame, statements: Iterable[str], precision: int | None = None) -> str:
    """Derive the address from a statement set. Same input, same output, always."""
    obs = [L.Obs(*s.split("/", 2)) for s in sorted(set(statements))]
    return L.Encoder(frame).encode(obs, precision=precision).text


def root_of(frame: Frame, statements: Iterable[str], extra: Sequence[str] = ()) -> str:
    """The root: sha256 over the canonical statement set plus anything extra."""
    canon = L.canonical([L.Obs(*s.split("/", 2)) for s in sorted(set(statements))],
                        frame.hierarchy)
    return L.commit(canon, extra)


def stem(frame: Frame) -> dict:
    """The stem a peer needs in order to reproduce your address and your root.

    Hand this to the other side. It is derived from the published seed, so it is
    also checkable: recompute it yourself and compare the fingerprint.
    """
    return {
        "fingerprint": frame.fingerprint(),
        "version": frame.seed["primer_version"],
        "statements": [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors],
        "plain": frame.plain,
        "syllables": frame.syllables,
        "axes": frame.partition.axes,
        "branches": frame.partition.branches,
        "distance": frame.distance,
        "markers": list(frame.markers),
    }


def validate_location(frame: Frame, claimed: dict, statements: Iterable[str],
                      precision: int | None = None,
                      extra: Sequence[str] = ()) -> Verdict:
    """Check a claimed (address, root) against the statements behind it.

    `claimed` is what the other side published, e.g.
        {"primer": "<fingerprint>", "address": "\\u2301 ma.mo.ma", "root": "<hex>"}

    Three things are checked, in order, and the first failure stops the check:

    1. the primer. If the fingerprints differ, the two geometries are not
       comparable and only an exact root may be compared at all.
    2. the address. Re-derived from the statements. A mismatch is a mismatch:
       there is no tolerance, because the derivation is deterministic.
    3. the root. Recomputed. Equal or not equal.
    """
    if claimed.get("primer") not in (None, frame.fingerprint()):
        return Verdict(False, (
            f"different primer: claimed {claimed['primer'][:16]}\u2026 but this frame is "
            f"{frame.fingerprint()[:16]}\u2026. The two geometries are incommensurable, so only "
            f"an exact root can be compared."))

    derived_address = address_of(frame, statements, precision)
    if claimed.get("address") is not None and claimed["address"] != derived_address:
        return Verdict(False, (
            f"address does not derive: claimed {claimed['address']!r} but these statements "
            f"give {derived_address!r}"), derived_address)

    derived_root = root_of(frame, statements, extra)
    if claimed.get("root") is not None and claimed["root"] != derived_root:
        return Verdict(False, (
            f"root does not derive: claimed {claimed['root'][:24]}\u2026 but these statements "
            f"give {derived_root[:24]}\u2026"), derived_address, derived_root)

    grains = {k: address_of(frame, statements, k) for k in (2, 4, 6, 12, 45)}
    return Verdict(True, "address and root both derive from the statements",
                   derived_address, derived_root, grains)
