"""T-012: calibrate a chars-per-qwen3-token ratio for auto-caption-style text.

No real YouTube transcript exists yet (still IpBlocked, KB-008) and no YouTube
calls are allowed this ticket, so real caption text isn't available to chunk
against directly. This measures qwen3's real tokenizer (same technique as
T-008: /api/generate, num_predict=1, prompt_eval_count) against a SYNTHETIC
but text-realistic stand-in for auto-captions: real English sentences
(borrowed from data/raw/hf/ abstracts - genuine text, not lorem ipsum),
lowercased and stripped of punctuation, since KB-001 notes auto-captions have
no punctuation and no capitalization.

The resulting ratio calibrates chunk_youtube_document()'s character-based
window size so it targets T-008's 400-qwen3-token chunk cap without needing a
live tokenizer call per chunk boundary during real chunking (which would be
too slow - hundreds of transcript segments per video).

This is an ESTIMATE from synthetic text, not a measurement of real captions -
flagged for re-confirmation once T-017 produces real transcript data.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

OLLAMA = "http://localhost:11434"
CHAT_MODEL = "qwen3:30b-a3b"
NUM_CTX = 16000
RAW_HF_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "hf" / "2026-09-16"


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
    return resp.json()["prompt_eval_count"]


def to_caption_style(text: str) -> str:
    """Lowercase, strip punctuation - a rough stand-in for auto-caption text
    shape (KB-001: no punctuation, no capitalization in auto-generated
    captions)."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main() -> None:
    paths = sorted(RAW_HF_DIR.glob("*.json"))[:5]
    samples = []
    for p in paths:
        doc = json.loads(p.read_text(encoding="utf-8"))
        caption_style = to_caption_style(doc["text"])
        tokens = count_qwen_tokens(caption_style)
        chars = len(caption_style)
        samples.append({"id": doc["id"], "chars": chars, "tokens": tokens, "chars_per_token": chars / tokens})
        print(f"{doc['id']}: {chars} chars, {tokens} qwen3 tokens, {chars/tokens:.2f} chars/token")

    ratios = [s["chars_per_token"] for s in samples]
    mean_ratio = sum(ratios) / len(ratios)
    min_ratio = min(ratios)
    print(f"\nchars/token: min={min_ratio:.2f} mean={mean_ratio:.2f}")
    print(f"Conservative (fewest chars per token, i.e. most tokens per char): {min_ratio:.2f}")


if __name__ == "__main__":
    main()
