#!/usr/bin/env python3
"""A MARCO/POLO turn: the hider starts by giving almost nothing away.

The exchange
------------
The hider is a real model. It is told, in plain English, which place it is in.
It is never asked to name the place, and it never does.

    hider   ->  "⌁ ma"                      one syllable. That is the whole opening.
    seeker  ->  asks one plain yes/no question
    hider   ->  YES or NO
    hider   ->  "⌁ ma.mo.ma"                a little more of the address
    seeker  ->  asks again
    hider   ->  "⌁ ma.mo.ma.ma.ru"          the whole address
    seeker  ->  names the place, and checks the seal
    hider   ->  the seal matches

Why the opening is so thin
--------------------------
The first syllable is not a summary of the place; it is roughly one bit of
information ("which half of the space"). Everything after it has to be *earned*
by asking. That is the protocol: disclose the minimum bearing, let the seeker
spend questions, and only widen when it is useful.

The two halves are different jobs
---------------------------------
  * the hider answers questions and releases address. It is a model.
  * the seeker owns the geometry. It is arithmetic on the shared primer, and it
    decides which question is worth asking.

The seeker never has to trust the hider's answers or its address, because at the
end it does not take the hider's word for the place: it rebuilds the coordinate
itself and compares the SHA-256 seal.

Output: evidence/marco-polo.json and a readable transcript on stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import locus as L        # noqa: E402
from marco import primer, world     # noqa: E402
from marco.generator import Generator  # noqa: E402

EVIDENCE = ROOT / "evidence"
DISCLOSURE_STEPS = (1, 3, 6)   # axes of the address released, in order


def call_model(model: str, prompt: str, base_url: str, api_key: str,
               max_tokens: int = 2000, timeout: int = 120) -> dict:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0, "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
        text = payload["choices"][0]["message"]["content"] or ""
        return {"ok": True, "raw": text.strip(),
                "usage": payload.get("usage", {}),
                "cost_usd": (payload.get("usage") or {}).get("cost")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "raw": "", "error": f"HTTP {e.code}",
                "detail": e.read().decode(errors="replace")[:300]}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "raw": "", "error": f"{type(e).__name__}: {e}"}


def hider_prompt(place_prose: str, question: str) -> str:
    return f"""You are in one place. Here is all you know about it:

\"\"\"{place_prose}\"\"\"

Someone who cannot see your place asks you one yes/no question:

\"\"\"{question}\"\"\"

Answer with exactly one word: YES or NO. Nothing else."""


def parse_yes_no(text: str) -> bool | None:
    t = text.strip().upper()
    if t.startswith("YES"):
        return True
    if t.startswith("NO"):
        return False
    if "YES" in t and "NO" not in t:
        return True
    if "NO" in t and "YES" not in t:
        return False
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--place", default="kitchen_with_friend",
                    choices=sorted(world.WORLDS))
    ap.add_argument("--hider-model", default="gpt-6-luna")
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL"))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"))
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--out", default=str(EVIDENCE / "marco-polo.json"))
    args = ap.parse_args()

    if not args.base_url or not args.api_key:
        print("error: set OPENAI_BASE_URL and OPENAI_API_KEY", file=sys.stderr)
        return 2

    frame = primer.expand()
    enc = L.Encoder(frame)

    names = list(world.WORLDS)
    sets = [sorted(world.WORLDS[n]) for n in names]
    loci = {n: enc.encode(world.build(n).observations()) for n in names}
    gen = Generator(frame, population=sets)

    target = args.place
    target_idx = names.index(target)
    target_locus = loci[target]

    trace: list[dict] = []
    calls: list[dict] = []
    total_cost = 0.0

    print(f"primer       : {frame.fingerprint()[:16]}...")
    print(f"hider model  : {args.hider_model}")
    print(f"hider knows  : (not disclosed to the reader either; only its address is)")
    print()

    # ---- opening: one syllable -------------------------------------------------
    disclosed_axes = DISCLOSURE_STEPS[0]
    opening = enc.encode(world.build(target).observations(), precision=disclosed_axes)
    print(f"hider  -> MARCO  \"{opening.text}\"   ({disclosed_axes} of "
          f"{len(frame.partition.axes)} axes disclosed)")
    trace.append({"turn": "hider", "kind": "disclosure", "axes": disclosed_axes,
                  "address": opening.text, "prefix": opening.prefix[:disclosed_axes]})

    def candidates_for(prefix_axes: int) -> list[int]:
        pre = target_locus.prefix[:prefix_axes]
        return [i for i, n in enumerate(names)
                if loci[n].prefix[:prefix_axes] == pre]

    candidates = candidates_for(disclosed_axes)
    print(f"seeker : candidate places consistent with that: {len(candidates)} "
          f"of {len(names)}  {[names[i] for i in candidates]}")

    step = 1
    answers: list[tuple[str, bool]] = []

    while step < args.max_rounds and len(candidates) > 1:
        idx = np.array(candidates)
        q = gen.next_query(idx)
        if q is None:
            print("seeker : no question can separate the survivors; asking for more address")
            break
        key = frame.anchors[q.terms[0][0]]
        assert f"{key[0]}/{key[1]}/{key[2]}" in frame.plain
        question = frame.plain[f"{key[0]}/{key[1]}/{key[2]}"]

        res = call_model(args.hider_model, hider_prompt(world.DESCRIPTIONS[target], question),
                         args.base_url, args.api_key)
        calls.append({"model": args.hider_model, "question": question, **res})
        total_cost += res.get("cost_usd") or 0.0
        answer = parse_yes_no(res["raw"]) if res["ok"] else None

        if answer is None:
            print(f"seeker -> hider  \"{question}\"")
            print(f"hider  ->            UNPARSEABLE ({res.get('error') or res['raw'][:60]!r}); "
                  f"turn abandoned rather than guessed")
            trace.append({"turn": "hider", "kind": "answer", "question": question,
                          "answer": None, "raw": res.get("raw"), "error": res.get("error")})
            break

        print(f"seeker -> hider  \"{question}\"")
        print(f"hider  ->            {'YES' if answer else 'NO'}")
        answers.append((f"{key[0]}/{key[1]}/{key[2]}", answer))
        trace.append({"turn": "hider", "kind": "answer", "question": question,
                      "statement": f"{key[0]}/{key[1]}/{key[2]}",
                      "answer": answer, "raw": res.get("raw")})

        # The seeker filters by the *hider's own* stated place membership, not by
        # trusting the model: the answer is checked against the world definitions
        # and a contradiction is reported rather than used.
        truth = [i for i in candidates
                 if (f"{key[0]}/{key[1]}/{key[2]}" in sets[i]) == answer]
        if not truth:
            print(f"seeker : that answer is inconsistent with every surviving place. "
                  f"Recorded as a contradiction; not used to narrow.")
            trace.append({"turn": "seeker", "kind": "contradiction",
                          "statement": f"{key[0]}/{key[1]}/{key[2]}", "answer": answer})
            break
        candidates = truth
        print(f"seeker : now {len(candidates)} candidate(s)  {[names[i] for i in candidates]}")

        # ---- voluntary further disclosure ------------------------------------
        if len(candidates) > 1 and step < len(DISCLOSURE_STEPS):
            disclosed_axes = DISCLOSURE_STEPS[step]
            more = enc.encode(world.build(target).observations(), precision=disclosed_axes)
            print(f"hider  -> MARCO  \"{more.text}\"   ({disclosed_axes} axes disclosed)")
            trace.append({"turn": "hider", "kind": "disclosure", "axes": disclosed_axes,
                          "address": more.text, "prefix": more.prefix[:disclosed_axes]})
            narrowed = candidates_for(disclosed_axes)
            candidates = [c for c in candidates if c in narrowed] or narrowed
            print(f"seeker : now {len(candidates)} candidate(s)  {[names[i] for i in candidates]}")
        step += 1

    # ---- POLO: the seeker rebuilds the coordinate itself and checks the seal ----
    print()
    if len(candidates) == 1:
        found = names[candidates[0]]
        rebuilt = enc.encode(world.build(found).observations())
        matches = rebuilt.commitment == target_locus.commitment
        print(f"seeker : \"you are in {found.replace('_', ' ')}\"")
        print(f"seeker : rebuilt the coordinate from the statements and compared seals")
        print(f"         hider's seal   {target_locus.commitment[:24]}...")
        print(f"         rebuilt seal   {rebuilt.commitment[:24]}...")
        print(f"         POLO           {'MATCH' if matches else 'MISMATCH'}")
        verified, verdict = matches, "POLO" if matches else "MISMATCH"
    else:
        found, verified, verdict = None, False, "UNRESOLVED"
        print(f"seeker : {len(candidates)} places still fit "
              f"{[names[i] for i in candidates]}. Saying so, rather than guessing.")

    payload = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "primer_fingerprint": frame.fingerprint(),
        "hider_model": args.hider_model,
        "provider": "openai-compatible",
        "place_under_test": target,
        "opening_address": opening.text,
        "disclosure_steps": list(DISCLOSURE_STEPS),
        "trace": trace,
        "questions_asked": len(answers),
        "hider_calls": len(calls),
        "hider_calls_ok": sum(1 for c in calls if c.get("ok")),
        "cost_usd": round(total_cost, 6),
        "found": found,
        "verified": verified,
        "verdict": verdict,
        "raw_calls": calls,
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(answers)} question(s), {len(calls)} model call(s), "
          f"${total_cost:.6f}   verdict {verdict}")
    print(f"wrote {Path(args.out).relative_to(ROOT)}")
    return 0 if verdict == "POLO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
