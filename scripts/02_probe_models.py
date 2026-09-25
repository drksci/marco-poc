#!/usr/bin/env python3
"""Probe several models with the same situations and record what they said.

Bring your own key
------------------
This script talks to any OpenAI-compatible chat-completions endpoint and needs
no SDK, only the standard library. Set:

    export OPENAI_BASE_URL="https://<your-endpoint>/v1"
    export OPENAI_API_KEY="<your-key>"

Provider name is never written into the evidence. Each record carries the
*model id* and a neutral provider label, because the scientific claim is about
models, not about who sold access to them.

What is recorded
----------------
Every call is written verbatim to `evidence/transcripts/`: the exact prompt
sent, the exact text returned, the parsed landmark set, latency, and token
counts. Nothing is post-processed away, and a failed call is recorded as a
failure rather than retried into looking clean.

Blindness
---------
One situation per call. A model never sees the other situations, never sees
another model's answer, and is never told that other models exist. This is the
whole point: if the coordinates converge it must be because the primer, not
because of coordination.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from marco import primer, world  # noqa: E402

TRANSCRIPT_DIR = ROOT / "evidence" / "transcripts"

# ─────────────────────────────────────────────────────────────────────────
# The situations. Deliberately spread across the space: some near each other
# (two coding situations) and some far (an idle sandbox with no network).
# ─────────────────────────────────────────────────────────────────────────

# Situations come straight from the world harness, so the prose a model reads and
# the landmarks it is choosing between cannot drift apart.
SITUATIONS: dict[str, str] = world.DESCRIPTIONS


def build_prompt(frame, situation: str) -> str:
    """The exact prompt. Kept stable and hashable.

    Each statement is shown with its plain reading next to its key, so a reader
    can check both what the model was asked and what it answered, without a
    glossary.
    """
    vocab = "\n".join(
        f'  {i+1:>2}. {key:<34} "{frame.plain[key]}"'
        for i, key in enumerate(f"{k}/{r}/{v}" for (k, r, v) in frame.anchors)
    )
    return f"""You are asked about one place. Below is a fixed list of statements.

STATEMENTS ({len(frame.anchors)}):
{vocab}

Here is the place:

\"\"\"{situation}\"\"\"

Which statements are true of that place? Choose only statements the description
actually supports. Do not choose a statement because it sounds plausible.

Reply with JSON only, no prose, no markdown fence. Use the keys exactly as
written, on the left of each line:
{{"true_statements": ["group/subject/detail", ...]}}"""


# ─────────────────────────────────────────────────────────────────────────
# Transport
# ─────────────────────────────────────────────────────────────────────────

def call_model(model: str, prompt: str, base_url: str, api_key: str,
               temperature: float = 0.0, timeout: int = 120,
               max_tokens: int = 16000) -> dict:
    """One chat completion. Returns a record; never raises on API failure."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
        latency = round(time.time() - started, 3)
        text = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {}) or {}
        return {"ok": True, "raw_response": text, "latency_s": latency,
                "usage": usage, "cost_usd": usage.get("cost"),
                "finish_reason": payload["choices"][0].get("finish_reason"),
                "response_id": payload.get("id")}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        return {"ok": False, "error": f"HTTP {e.code}", "detail": detail,
                "latency_s": round(time.time() - started, 3)}
    except Exception as e:  # noqa: BLE001 - recorded, not swallowed
        return {"ok": False, "error": f"{type(e).__name__}: {e}",
                "latency_s": round(time.time() - started, 3)}


def parse_landmarks(text: str, vocabulary: list[str]) -> dict:
    """Parse the model's reply. Reports exactly how it failed when it does.

    A model that returns unparseable text, or invents landmarks that are not in
    the vocabulary, is recorded as such. Invented landmarks are dropped but
    counted, because a model quietly extending the vocabulary would invalidate
    the cross-model comparison.
    """
    if text is None:
        return {"parsed": False, "reason": "empty response", "landmarks": []}
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.lstrip().startswith("json"):
            cleaned = cleaned.lstrip()[4:]
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                return {"parsed": False, "reason": f"json: {e}", "landmarks": []}
        else:
            return {"parsed": False, "reason": f"json: {e}", "landmarks": []}

    raw = data.get("true_statements", data.get("landmarks",
                  data if isinstance(data, list) else []))
    if not isinstance(raw, list):
        return {"parsed": False, "reason": "landmarks is not a list", "landmarks": []}

    valid = set(vocabulary)
    kept = sorted({str(x).strip() for x in raw if str(x).strip() in valid})
    unknown = sorted({str(x).strip() for x in raw if str(x).strip() not in valid})
    return {"parsed": True, "landmarks": kept, "unknown_landmarks": unknown,
            "n_selected": len(kept)}


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True,
                    help="model ids to probe, in order")
    ap.add_argument("--situations", nargs="*", default=list(SITUATIONS),
                    help=f"which situations (default: all {len(SITUATIONS)})")
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL"),
                    help="OpenAI-compatible base URL (default $OPENAI_BASE_URL)")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"),
                    help="credential (default $OPENAI_API_KEY)")
    ap.add_argument("--provider-label", default="openai-compatible",
                    help="neutral provider label recorded in the evidence")
    ap.add_argument("--out", default=None, help="transcript path")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--jobs", type=int, default=4,
                    help="concurrent calls (keep modest to stay under rate limits)")
    ap.add_argument("--max-tokens", type=int, default=16000,
                    help="completion budget; reasoning tokens count against it, "
                         "so a low value yields an empty reply with "
                         "finish_reason=length")
    ap.add_argument("--seed-label", default="", help="note for the run, e.g. git sha")
    args = ap.parse_args()

    if not args.base_url or not args.api_key:
        print("error: set OPENAI_BASE_URL and OPENAI_API_KEY, or pass "
              "--base-url/--api-key", file=sys.stderr)
        return 2

    frame = primer.expand()
    vocabulary = [f"{k}/{r}/{v}" for (k, r, v) in frame.anchors]

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = Path(args.out) if args.out else TRANSCRIPT_DIR / f"probe-{stamp}.jsonl"

    print(f"primer fingerprint : {frame.fingerprint()}")
    print(f"vocabulary         : {len(vocabulary)} landmarks")
    print(f"models             : {', '.join(args.models)}")
    print(f"situations         : {', '.join(args.situations)}")
    print(f"transcript         : {out_path}")
    print()

    jobs = [(m, s) for m in args.models for s in args.situations]
    prompts = {k: build_prompt(frame, SITUATIONS[k[1]]) for k in jobs}

    def run_one(job):
        model, situation_id = job
        prompt = prompts[job]
        result = call_model(model, prompt, args.base_url, args.api_key,
                            temperature=args.temperature,
                            max_tokens=args.max_tokens)
        record = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "provider": args.provider_label,
            "situation_id": situation_id,
            "primer_fingerprint": frame.fingerprint(),
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt": prompt,
            "temperature": args.temperature,
            **result,
        }
        if result.get("ok"):
            record.update(parse_landmarks(result["raw_response"], vocabulary))
        else:
            record["parsed"] = False
        return job, record

    records, n_ok, n_fail = [], 0, 0
    with out_path.open("w", encoding="utf-8") as fh:
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futures = [pool.submit(run_one, j) for j in jobs]
            for fut in as_completed(futures):
                (model, situation_id), record = fut.result()
                if record.get("ok"):
                    n_ok += 1
                    n = record.get("n_selected", 0)
                    unk = len(record.get("unknown_landmarks", []))
                    status = f"{n:2d} chosen" + (f", {unk} not in vocabulary" if unk else "")
                    if record.get("finish_reason") == "length":
                        status += "  [TRUNCATED: reasoning ate the budget]"
                else:
                    n_fail += 1
                    status = f"FAILED {record.get('error')}"
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                fh.flush()
                records.append(record)
                print(f"  {model:24s} {situation_id:18s} {status}", flush=True)

    summary = {
        "transcript": str(out_path.relative_to(ROOT)) if out_path.is_relative_to(ROOT) else str(out_path),
        "primer_fingerprint": frame.fingerprint(),
        "provider_label": args.provider_label,
        "models": args.models,
        "situations": args.situations,
        "calls": len(records), "ok": n_ok, "failed": n_fail,
        "seed_label": args.seed_label,
    }
    (out_path.with_suffix(".summary.json")).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{n_ok}/{len(records)} calls succeeded")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
