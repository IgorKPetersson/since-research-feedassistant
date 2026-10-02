"""T-049: time each step of retrieval separately, and record which models Ollama has
loaded before and after each, to find where KB-023's 40-100s goes. Real calls against
the production store and Ollama; nothing is written.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.retrieval import (
    PACKING_PLACEHOLDER_SOURCE_NUMBER,
    count_qwen_tokens,
    dedup_by_doc,
    format_source,
    query_candidates,
    retrieve,
)
from vg09.store import embed_batch

QUESTION = "Har NeoHorse nämnts de senaste två veckorna?"


def loaded() -> list[str]:
    models = requests.get("http://127.0.0.1:11434/api/ps", timeout=10).json()["models"]
    return [m["name"] for m in models]


def timed(label: str, fn):
    start = time.monotonic()
    result = fn()
    print(f"{label}: {time.monotonic() - start:.2f}s  loaded={loaded()}")
    return result


def main() -> None:
    # Optional base URL: pass http://localhost:11434 to reproduce the slow case.
    if len(sys.argv) > 1:
        import vg09.answer
        import vg09.retrieval
        import vg09.store

        for module in (vg09.answer, vg09.retrieval, vg09.store):
            module.OLLAMA = sys.argv[1]
        print(f"OLLAMA overridden to {sys.argv[1]}")
    print(f"loaded at start: {loaded()}")
    timed("embed 1st", lambda: embed_batch([QUESTION]))
    timed("embed 2nd", lambda: embed_batch([QUESTION]))
    candidates = timed("query_candidates", lambda: query_candidates(QUESTION, None))
    deduped = dedup_by_doc(candidates)
    print(f"candidates={len(candidates)} deduped={len(deduped)}")
    for c in deduped[:6]:
        text = format_source(c, PACKING_PLACEHOLDER_SOURCE_NUMBER)
        timed("count_qwen_tokens", lambda: count_qwen_tokens(text))
    timed("embed after counts", lambda: embed_batch([QUESTION]))
    result = timed("retrieve() whole", lambda: retrieve(QUESTION, None, False))
    print(f"packed={len(result.chunks)} tokens={result.total_tokens}")


if __name__ == "__main__":
    main()
