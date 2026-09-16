"""ChromaDB storage (T-012): embed chunks with bge-m3 (explicit call, CLAUDE.md
hard rule - never Chroma's default embedder) and store with feed date as a
numeric field for range filtering (KB-004: ISO date strings aren't guaranteed
to compare correctly under Chroma's `$gte`/`$lte`; `date.toordinal()` is).

Reads normalized documents from data/raw/ (T-009/T-015/T-017's durable store)
rather than calling collectors directly, so the database can be rebuilt from
disk without re-fetching from YouTube or HF. Only reads final `*.json`
documents - `*.pending.json` markers (T-010/D-006) have no `text` to chunk
yet, and `_done.json` day-completion markers (T-015) aren't documents at all.

`collection.upsert()` (not `add()`) makes rebuilding idempotent: re-running
against the same data/raw/ contents produces the same store state rather than
growing duplicates, since chunk ids are deterministic (doc id + index).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import chromadb
import requests

from vg09.chunking import Chunk, chunk_document
from vg09.document import RAW_DIR

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
EMBED_NUM_CTX = 8192  # bge-m3's own context window, per KB-007 - never left implicit
STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "chroma_store"
COLLECTION_NAME = "vg09_chunks"
EMBED_BATCH_SIZE = 20


def load_documents(sources: tuple[str, ...] = ("hf", "youtube")) -> list[dict]:
    docs = []
    for source in sources:
        source_dir = RAW_DIR / source
        if not source_dir.exists():
            continue
        for path in sorted(source_dir.rglob("*.json")):
            if path.name.endswith(".pending.json") or path.name == "_done.json":
                continue
            docs.append(json.loads(path.read_text(encoding="utf-8")))
    return docs


def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = requests.post(
        f"{OLLAMA}/api/embed",
        json={"model": EMBED_MODEL, "input": texts, "options": {"num_ctx": EMBED_NUM_CTX}},
        timeout=300,
    )
    resp.raise_for_status()
    body = resp.json()
    avg_tokens = body.get("prompt_eval_count", 0) / max(len(texts), 1)
    if avg_tokens >= 0.9 * EMBED_NUM_CTX:
        print(f"  !! close to bge-m3 num_ctx: avg {avg_tokens:.0f} tokens/item in this batch "
              f"(num_ctx={EMBED_NUM_CTX}) - a batch average near the limit can hide one "
              f"oversized item; per-chunk size is bounded by construction (T-012), not just "
              f"hoped, but this is a coarse check, not a per-item guarantee")
    return body["embeddings"]


def get_collection():
    client = chromadb.PersistentClient(path=str(STORE_PATH))
    return client.get_or_create_collection(COLLECTION_NAME)


def chunk_metadata(c: Chunk) -> dict:
    meta = {
        "doc_id": c.doc_id,
        "source": c.source,
        "url": c.url,
        "title": c.title,
        "feed_date": c.feed_date,
        "feed_date_ordinal": date.fromisoformat(c.feed_date).toordinal(),
    }
    # Chroma metadata values must be primitives - omit rather than pass None.
    if c.text_source is not None:
        meta["text_source"] = c.text_source
    if c.fallback_reason is not None:
        meta["fallback_reason"] = c.fallback_reason
    if c.arxiv_published_at is not None:
        meta["arxiv_published_at"] = c.arxiv_published_at
    if c.start_seconds is not None:
        meta["start_seconds"] = c.start_seconds
    return meta


def build_store(sources: tuple[str, ...] = ("hf", "youtube")) -> dict:
    collection = get_collection()
    documents = load_documents(sources)

    all_chunks: list[Chunk] = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))

    total = len(all_chunks)
    for start in range(0, total, EMBED_BATCH_SIZE):
        batch = all_chunks[start:start + EMBED_BATCH_SIZE]
        embeddings = embed_batch([c.text for c in batch])
        collection.upsert(
            ids=[c.id for c in batch],
            embeddings=embeddings,
            documents=[c.text for c in batch],
            metadatas=[chunk_metadata(c) for c in batch],
        )
        print(f"  embedded+stored {min(start + len(batch), total)}/{total} chunks")

    return {"documents": len(documents), "chunks": total, "collection_count": collection.count()}
