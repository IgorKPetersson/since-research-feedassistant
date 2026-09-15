"""T-006 part 1: needle-in-haystack test against Ollama's real num_ctx.

Builds ~12k tokens of filler text with one unique fact planted at the
very start, asks a question that requires that fact back, and checks:
- what num_ctx Ollama actually used (via `ollama ps` after the call)
- Ollama's own prompt_eval_count (tokens it actually evaluated) vs a
  rough token estimate of what was sent, as a signal of truncation
- whether the model's answer shows it saw the planted fact

Run once with default options (no num_ctx override) and once with an
explicit num_ctx=16000, to compare.

Makes real local calls; run it manually, it is not a test.
"""

import json
import subprocess
import time
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SECRET = "The secret code word for this test is ZEBRA-7742-QUARTZ."
FILLER_SENTENCE = (
    "The quick brown fox jumps over the lazy dog near the riverbank while "
    "the weather stays mild and the afternoon continues without much change. "
)
# Rough estimate: ~0.75 words per token for English filler text.
TARGET_TOKENS = 12000
TARGET_WORDS = int(TARGET_TOKENS * 0.75)


def build_haystack() -> str:
    filler = FILLER_SENTENCE * (TARGET_WORDS // len(FILLER_SENTENCE.split()) + 1)
    words = filler.split()[:TARGET_WORDS]
    filler = " ".join(words)
    return f"{SECRET}\n\n{filler}\n\nQuestion: What is the secret code word mentioned at the very start of this document?"


def ask(prompt: str, num_ctx: int | None) -> dict:
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    if num_ctx is not None:
        payload["options"] = {"num_ctx": num_ctx}
    resp = requests.post(OLLAMA_URL, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()


def ollama_ps() -> str:
    # Relies on `ollama` already being on PATH in the calling shell.
    return subprocess.check_output(["ollama", "ps"], text=True, timeout=10)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    haystack = build_haystack()
    approx_prompt_tokens = len(haystack.split()) / 0.75
    print(f"Built haystack: ~{len(haystack.split())} words, ~{approx_prompt_tokens:.0f} estimated tokens")

    results = {}
    for label, num_ctx in [
        ("default_num_ctx", None),
        ("explicit_16000", 16000),
        ("forced_undersized_4096", 4096),
    ]:
        print(f"\n== {label} (num_ctx={num_ctx}) ==")
        start = time.monotonic()
        body = ask(haystack, num_ctx)
        elapsed = time.monotonic() - start
        response_text = body.get("response", "")
        found_secret = "ZEBRA" in response_text.upper()
        ps_output = ollama_ps()
        results[label] = {
            "elapsed_s": elapsed,
            "prompt_eval_count": body.get("prompt_eval_count"),
            "eval_count": body.get("eval_count"),
            "response": response_text,
            "found_secret_in_response": found_secret,
            "ollama_ps": ps_output.strip(),
        }
        print(f"  time: {elapsed:.1f}s  prompt_eval_count: {body.get('prompt_eval_count')}")
        print(f"  response: {response_text[:300]!r}")
        print(f"  found secret: {found_secret}")
        print(f"  ollama ps:\n{ps_output}")

    out_path = DATA_DIR / "t006_needle_test.json"
    out_path.write_text(
        json.dumps({"approx_prompt_tokens": approx_prompt_tokens, "results": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
