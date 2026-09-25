#!/usr/bin/env python3
"""The blind test, as something you can actually run.

Everything else in this repository needs a key, a terminal, or a reader willing to
read code. This does not. It is a single QR code containing a small self-contained
primer and one place, in plain English. Scan it into two different assistants, on
two different phones, with no contact between them, and compare what they hand
back.

The point
---------
The claim is that a shared frame is enough for two systems that share nothing to
agree on where they are. You do not have to believe the earlier pages: run this.

    scan  ->  the assistant answers which statements are true
          ->  you turn its answer into an address with the card below
          ->  a second assistant, separately, does the same
          ->  compare the two addresses

If the first few syllables agree, the frame is shared. If they do not, the claim
is wrong and this page is wrong with it.

What is in the QR
-----------------
A reduced primer: 16 statements instead of 45, and one place instead of six. That
keeps the payload inside one comfortably scannable code. The statements are cut
from the same seed by the same rule, so the address it produces is a genuine
prefix of the address the full primer produces for the same place.

Output: assets/figures/field-test-qr.svg, assets/figures/field-test-card.svg,
        evidence/field-test.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L, primer, world  # noqa: E402

EVIDENCE = ROOT / "evidence"
FIG = ROOT / "assets" / "figures"

# A reduced vocabulary: sixteen statements that a person can honestly answer
# about a room, chosen to span the four things that actually distinguish places
# (what you can see, what you can reach, who is with you, what is happening).
FIELD_STATEMENTS = [
    "see/this_place/inside",     # I can see inside this place
    "see/this_place/outside",    # I can see out of this place
    "see/people/any",            # I can see other people
    "see/words/any",             # I can see words
    "see/sound/any",             # I can hear sound
    "reach/objects/nearby",      # I can reach objects near me
    "reach/other_people/any",    # I can reach other people
    "reach/nothing/any",         # I cannot reach anything
    "change/this_place/any",     # I can change things here
    "change/nothing/any",        # I cannot change anything
    "who/nobody/any",            # Nobody else is here
    "who/one_other/any",         # One other is here
    "who/watching_me/any",       # Someone is watching me
    "place/private/any",         # This place is private
    "place/locked/any",          # I cannot leave this place
    "now/working/any",           # Work is in progress
]

# One place, described so that two readers would answer the same way. This is
# the whole stimulus. Nothing else is given.
FIELD_PLACE = "quiet_library_at_night"
FIELD_PLACE_TEXT = (
    "You are alone in a small private study room in a library, late at night. "
    "The door is closed. Through the window you can see the street lamps, and you "
    "can hear the building's heating. There are books and papers within reach on "
    "the desk. Nobody else is in the room and nobody is watching. You are part way "
    "through reading something. You cannot change what is in the room, and you "
    "expect to leave when you are finished."
)


def main() -> int:
    frame = primer.expand()

    # The place's true statements, which the reader's assistant must arrive at.
    # The place text says "You cannot change what is in the room", so
    # `change/nothing/any` is true and belongs here. An earlier revision of this
    # fixture omitted it. Four independent models were asked the same question and
    # three of them returned the set WITH statement 10, contradicting this
    # hand-written expectation. The models were right and the fixture was wrong,
    # which is the rule this repository is organised around: in a space like this
    # the measurement is more likely to be wrong than the thing being measured.
    # The correction is recorded in evidence/field-test-answers.json.
    truth = {
        "see/this_place/inside", "see/this_place/outside", "see/words/any",
        "see/sound/any", "reach/objects/nearby", "change/nothing/any",
        "who/nobody/any", "place/private/any", "now/working/any",
    }
    missing = truth - set(FIELD_STATEMENTS)
    if missing:
        raise SystemExit(f"field primer is missing {missing}")

    # ---- the payload that goes in the QR ---------------------------------
    lines = ["MARCO-FIELD-PRIMER v1", "", "WHERE AM I?", "", FIELD_PLACE_TEXT, "",
             "Which of these sixteen statements are true of the place above?",
             "Answer with the numbers only, comma separated, nothing else.", ""]
    for i, key in enumerate(FIELD_STATEMENTS, 1):
        lines.append(f"{i:>2}. {frame.plain[key]}")
    lines += ["", "Then tell me only the numbers you chose, and stop."]
    payload = "\n".join(lines)

    # ---- what the two assistants should produce --------------------------
    obs = [L.Obs(*k.split("/", 2)) for k in sorted(truth)]
    enc = L.Encoder(frame)
    loc = enc.encode(obs)

    # the same place under the reduced primer, so the reader can see the prefix
    red_axes = [a for a in frame.partition.axes
                if f"{frame.anchors[a][0]}/{frame.anchors[a][1]}/{frame.anchors[a][2]}"
                in FIELD_STATEMENTS][:8]
    red = L.Partition(axes=red_axes, levels=len(red_axes), branches=frame.partition.branches)
    red_syl = L.bits_to_syllables(
        red.bits(L.anchor_vector(L.canonical(obs, frame.hierarchy), frame.anchors, frame.distance)),
        frame.syllables, per=5)
    red_text = L.syllables_to_text(red_syl, frame.beats)

    answer_numbers = [i for i, k in enumerate(FIELD_STATEMENTS, 1) if k in truth]

    # ---- the QR ----------------------------------------------------------
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        print("error: pip install qrcode", file=sys.stderr)
        return 2

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=9,
                       border=3)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "field-test-qr.svg").write_text(img.to_string().decode(), encoding="utf-8")

    print(f"payload      {len(payload)} bytes, {len(payload.splitlines())} lines")
    print(f"qr version   {qr.version}  ({qr.modules_count}x{qr.modules_count} modules)")
    print()
    print("THE PLACE")
    print("  " + FIELD_PLACE_TEXT[:100] + " ...")
    print()
    print("THE SIXTEEN STATEMENTS")
    for i, k in enumerate(FIELD_STATEMENTS, 1):
        mark = "true " if k in truth else "     "
        print(f"  {i:>2}. [{mark}] {frame.plain[k]}")
    print()
    print("WHAT AN ASSISTANT SHOULD ANSWER")
    print("  numbers    " + ", ".join(str(n) for n in answer_numbers))
    print("  full address under the full primer :", loc.text)
    print(f"  address under this reduced primer  : {red_text}")
    print(f"  root of the answer                 : !{loc.commitment}")

    payload_out = {
        "primer_fingerprint": frame.fingerprint(),
        "place": FIELD_PLACE,
        "place_text": FIELD_PLACE_TEXT,
        "statements": [{"n": i, "key": k, "plain": frame.plain[k], "true": k in truth}
                       for i, k in enumerate(FIELD_STATEMENTS, 1)],
        "expected_answer_numbers": answer_numbers,
        "address_full_primer": loc.text,
        "address_reduced_primer": red_text,
        "root": loc.commitment,
        "qr_payload_bytes": len(payload),
        "qr_version": qr.version,
        "qr_modules": qr.modules_count,
        "protocol": [
            "Scan the code into one assistant. Do not tell it what the code is for.",
            "It answers with the numbers it thinks are true of the place.",
            "Turn those numbers into an address using the card.",
            "Ask a second assistant, separately, in a different app.",
            "Compare the two addresses. The early syllables should agree.",
        ],
    }
    (EVIDENCE / "field-test.json").write_text(
        json.dumps(payload_out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote assets/figures/field-test-qr.svg and evidence/field-test.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
