"""T-012: chunk, embed and store all documents currently in data/raw/.

Reads data/raw/ (populated by T-015's HF backfill; YouTube's T-017 is still
blocked, KB-008 - no YouTube calls here, this only reads what's already on
disk). Real Ollama calls for embedding (bge-m3); no YouTube calls.

Run twice in a row to confirm idempotency (same chunk/document counts, same
collection.count()).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import build_store  # noqa: E402


def main() -> None:
    start = time.time()
    result = build_store()
    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s. documents={result['documents']} chunks={result['chunks']} "
          f"collection.count()={result['collection_count']}")


if __name__ == "__main__":
    main()
