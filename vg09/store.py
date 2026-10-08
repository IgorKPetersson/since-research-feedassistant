"""ChromaDB storage (T-012): embed chunks with bge-m3 (explicit call, the project rules
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

# The literal IPv4 address, never "localhost" (T-049, KB-024): on Windows "localhost"
# is tried over IPv6 first, Ollama listens on IPv4 only, and every single request then
# waits about 2 seconds for that attempt to give up. Retrieval makes ~30 requests per
# question, which was the whole of KB-023's 40-100s.
OLLAMA = "http://127.0.0.1:11434"
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


def reset_client() -> None:
    """Make the next `get_collection()` read the store from disk again. Chroma keeps one
    client per path for the life of the process, with the vector index held in memory.
    When another process (the ingest job, T-055) has added to the store, that in-memory
    index no longer matches the files, and every similarity query fails with "Error
    finding id" until the process restarts - found for real in T-056, where counts kept
    working and questions did not. Dropping the cached client is what a restart did."""
    from chromadb.api.shared_system_client import SharedSystemClient

    SharedSystemClient.clear_system_cache()


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
    if c.channel is not None:
        meta["channel"] = c.channel
    return meta


def build_store(
    sources: tuple[str, ...] = ("hf", "youtube"), on_progress=None, only_new: bool = False
) -> dict:
    """`on_progress(done_chunks, total_chunks)` is called after every batch, for the
    background ingest job's status file (T-055). `only_new` embeds and stores just the
    chunks whose id the store doesn't have yet: the job's case, where the app can't be
    queried while the store is written, so the write should take seconds, not the 40-50
    it takes to re-embed everything. The default still rewrites every chunk, which is
    what a change to existing chunks' metadata needs."""
    collection = get_collection()
    documents = load_documents(sources)

    all_chunks: list[Chunk] = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    document_chunks = len(all_chunks)
    if only_new:
        stored = set(collection.get(include=[])["ids"])
        all_chunks = [c for c in all_chunks if c.id not in stored]

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
        if on_progress is not None:
            on_progress(min(start + len(batch), total), total)

    return {"documents": len(documents), "chunks": document_chunks, "written": total,
            "collection_count": collection.count()}


def is_empty() -> bool:
    """T-025: the chat UI's empty-state check ("ingen data ännu, kör ingest") - a
    thin, testable wrapper rather than the UI reaching into `get_collection().count()`
    directly."""
    return get_collection().count() == 0


def latest_feed_date() -> date | None:
    """The most recent `feed_date` actually present across the whole store, both
    sources combined - not a per-source watermark (T-013's watermarks are
    deliberately a few days conservative, T-015's `REOPEN_DAYS`) and not any single
    source's own cutoff (T-027: anchoring a shared relative window, e.g. "senaste
    veckan", to the slowest-moving source silently excludes genuinely newer content
    from a faster one - found for real via `YTG0rdHPTDE`, a video one day newer than
    HF's cutoff that a HF-anchored window excluded outright). `None` if the store is
    empty - callers decide what "no data yet" means for a relative window themselves.

    A full metadata scan (`collection.get()`), not an indexed aggregate - Chroma has
    no native max() - fine at this project's real scale (~2000 chunks); would need
    revisiting only if the corpus grew by orders of magnitude."""
    collection = get_collection()
    if collection.count() == 0:
        return None
    result = collection.get(include=["metadatas"])
    max_ordinal = max(m["feed_date_ordinal"] for m in result["metadatas"])
    return date.fromordinal(max_ordinal)


def corpus_stats() -> dict:
    """T-042: real counts for the chat UI's status bar - distinct documents per source
    (papers, videos) and total chunk count, never hardcoded. Same full-metadata-scan
    approach as `latest_feed_date()`, same real-scale caveat - one `collection.get()`
    call, not per-source queries, so this stays one real Chroma call regardless of how
    many sources exist."""
    collection = get_collection()
    total_chunks = collection.count()
    if total_chunks == 0:
        return {"hf_documents": 0, "youtube_documents": 0, "chunks": 0}
    result = collection.get(include=["metadatas"])
    hf_docs: set[str] = set()
    youtube_docs: set[str] = set()
    for m in result["metadatas"]:
        source = m.get("source")
        doc_id = m.get("doc_id")
        if source == "hf":
            hf_docs.add(doc_id)
        elif source == "youtube":
            youtube_docs.add(doc_id)
    return {
        "hf_documents": len(hf_docs),
        "youtube_documents": len(youtube_docs),
        "chunks": total_chunks,
    }


def channel_stats() -> dict[str, dict]:
    """T-054: per YouTube channel, how many distinct videos the store holds and the
    latest feed date among them - `{handle: {"documents": int, "latest": date}}`. Videos
    stored before T-054's migration have no channel and are counted under `None`, so a
    missing assignment is visible rather than silently left out of every count."""
    collection = get_collection()
    if collection.count() == 0:
        return {}
    result = collection.get(where={"source": "youtube"}, include=["metadatas"])
    docs: dict[str | None, set[str]] = {}
    latest: dict[str | None, int] = {}
    for m in result["metadatas"]:
        handle = m.get("channel")
        docs.setdefault(handle, set()).add(m["doc_id"])
        latest[handle] = max(latest.get(handle, 0), m["feed_date_ordinal"])
    return {
        handle: {"documents": len(ids), "latest": date.fromordinal(latest[handle])}
        for handle, ids in docs.items()
    }


def remove_channel_data(handle: str) -> dict:
    """T-054 (D-017): removing a channel removes what was fetched from it - its chunks
    from the store, so no answer can cite it, and its raw files, so the next
    `build_store()` doesn't put it back (that function only ever upserts)."""
    collection = get_collection()
    before = collection.count()
    collection.delete(where={"channel": handle})
    removed_files = 0
    for path in sorted((RAW_DIR / "youtube").rglob("*.json")):
        if path.name.endswith(".pending.json"):
            continue
        if json.loads(path.read_text(encoding="utf-8")).get("channel") == handle:
            path.unlink()
            removed_files += 1
    return {"chunks": before - collection.count(), "documents": removed_files}
