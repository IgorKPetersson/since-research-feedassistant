"""T-019: verify the recalibrated TARGET_CHUNK_CHARS keeps real chunks under
T-008's 400-qwen3-token cap, using the largest real caption document on disk.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from vg09.chunking import chunk_youtube_document  # noqa: E402

OLLAMA = "http://localhost:11434"


def count_qwen_tokens(text: str) -> int:
    resp = requests.post(
        f"{OLLAMA}/api/generate",
        json={"model": "qwen3:30b-a3b", "prompt": text, "stream": False,
              "options": {"num_ctx": 16000, "num_predict": 1}},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["prompt_eval_count"]


def main() -> None:
    doc = json.loads(Path("data/raw/youtube/2026-08-30/4wjHNgMLeyY.json").read_text(encoding="utf-8"))
    chunks = chunk_youtube_document(doc)
    print(f"{len(chunks)} chunks for the largest real document ({len(doc['text'])} chars)")
    max_tok = 0
    for c in chunks:
        tok = count_qwen_tokens(c.text)
        max_tok = max(max_tok, tok)
        print(f"  chunk {c.id}: {len(c.text)} chars, {tok} qwen3 tokens")
    print(f"\nmax tokens in any chunk: {max_tok} (cap: 400)")


if __name__ == "__main__":
    main()
