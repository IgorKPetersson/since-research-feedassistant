"""T-019: re-calibrate chars-per-qwen3-token against REAL caption text.

T-012's original calibration (scripts/t012_caption_token_calibration.py) used
synthetic, lowercased/depunctuated stand-in text because no real transcript
existed yet (KB-008). 17 real caption documents now exist on disk (T-017),
and KB-014 found real auto-captions actually have punctuation and normal
capitalization - a materially different text shape than the synthetic
estimate assumed. This re-measures the real ratio and reports whether
TARGET_CHUNK_CHARS in vg09/chunking.py needs to change.

Same method as T-008/T-012: qwen3's real tokenizer via /api/generate,
num_predict=1 (KB-009 - not 0), reading prompt_eval_count.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from vg09.document import RAW_DIR  # noqa: E402

OLLAMA = "http://localhost:11434"
CHAT_MODEL = "qwen3:30b-a3b"
NUM_CTX = 16000


def count_qwen_tokens(text: str) -> int:
    resp = requests.post(
        f"{OLLAMA}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": text,
            "stream": False,
            "options": {"num_ctx": NUM_CTX, "num_predict": 1},
        },
        timeout=120,
    )
    resp.raise_for_status()
    body = resp.json()
    if body["prompt_eval_count"] >= 0.9 * NUM_CTX:
        print("  !! close to num_ctx - truncation risk (KB-005)")
    return body["prompt_eval_count"]


def real_caption_documents() -> list[dict]:
    docs = []
    for path in sorted(RAW_DIR.glob("youtube/**/*.json")):
        if path.name.endswith(".pending.json"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("text_source") == "captions":
            docs.append(doc)
    return docs


def main() -> None:
    docs = real_caption_documents()
    print(f"{len(docs)} real caption documents found on disk\n")

    samples = []
    for doc in docs:
        text = doc["text"]
        tokens = count_qwen_tokens(text)
        chars = len(text)
        ratio = chars / tokens
        samples.append(ratio)
        print(f"{doc['id']}: {chars} chars, {tokens} qwen3 tokens, {ratio:.2f} chars/token")

    min_ratio = min(samples)
    mean_ratio = sum(samples) / len(samples)
    print(f"\nchars/token across {len(samples)} real caption documents: "
          f"min={min_ratio:.2f} mean={mean_ratio:.2f}")
    print(f"Conservative (fewest chars per token, i.e. most tokens per char): {min_ratio:.2f}")

    from vg09.chunking import CHARS_PER_TOKEN_CAPTION_WORST_CASE, TARGET_CHUNK_CHARS, TARGET_CHUNK_TOKENS
    print(f"\nCurrent vg09/chunking.py constant: {CHARS_PER_TOKEN_CAPTION_WORST_CASE} chars/token "
          f"-> TARGET_CHUNK_CHARS={TARGET_CHUNK_CHARS} (targeting {TARGET_CHUNK_TOKENS} tokens)")
    new_target_chars = int(TARGET_CHUNK_TOKENS * min_ratio)
    print(f"Real worst-case ratio {min_ratio:.2f} -> would give TARGET_CHUNK_CHARS={new_target_chars}")
    if min_ratio < CHARS_PER_TOKEN_CAPTION_WORST_CASE:
        print("Real text is WORSE (fewer chars/token) than the synthetic estimate assumed - "
              "the old constant under-budgets token count for a given char window. Should update.")
    else:
        print("Real text is BETTER (more chars/token) than the synthetic estimate assumed - "
              "the old constant was already conservative (safe, just not tight). "
              "Updating is optional; the cap still holds either way.")


if __name__ == "__main__":
    main()
