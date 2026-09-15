"""T-007: re-verify KB-007's think:false claim via /api/chat.

KB-007 tested think:true/false against /api/generate. This script
repeats the same comparison against /api/chat (messages-based, the
endpoint Ollama's docs generally illustrate `think` with) to check
whether the endpoint - not a genuine Qwen3 behavior - explains why
think:false didn't suppress reasoning in KB-007.

Makes real local calls; run it manually, it is not a test.
"""

import json
import time
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:30b-a3b"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

QUESTION = "What causes rain?"


def ask(think: bool) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": QUESTION}],
        "stream": False,
        "think": think,
        "options": {"num_ctx": 16000},
    }
    start = time.monotonic()
    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    elapsed = time.monotonic() - start
    resp.raise_for_status()
    body = resp.json()
    message = body.get("message", {})
    return {
        "request_body": payload,
        "elapsed_s": elapsed,
        "content": message.get("content", ""),
        "thinking": message.get("thinking", None),
        "eval_count": body.get("eval_count"),
    }


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    results = {}
    for label, think in [("think_true", True), ("think_false", False)]:
        print(f"== {label} ==")
        r = ask(think)
        results[label] = r
        print(f"  request body: {json.dumps(r['request_body'])}")
        print(f"  time: {r['elapsed_s']:.1f}s  eval_count: {r['eval_count']}")
        print(f"  thinking field len: {len(r['thinking'] or '')}")
        print(f"  content field len: {len(r['content'])}")
        print(f"  content starts with: {r['content'][:150]!r}")

    out_path = DATA_DIR / "t007_verify_think_chat.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
