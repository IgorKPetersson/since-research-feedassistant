"""Chunking (T-012): normalized Document -> one or more Chunks ready to embed.

- **HF**: one chunk per paper, the whole abstract. Already well under T-008's
  400-qwen3-token chunk cap (max observed 363 tokens across all 20 real
  abstracts on disk).
- **YouTube**: chunked by transcript *timestamp*, not sentence - KB-001 notes
  auto-generated captions have no punctuation, so sentence splitting would be
  unreliable. Each chunk keeps its start time so a citation can link straight
  to `watch?v=ID&t=SECONDS` (D-002: the point in a video "did X come up"
  actually means).

The YouTube chunk-size target (`TARGET_CHUNK_CHARS`) is calibrated from a real
qwen3 tokenizer measurement (`scripts/t012_caption_token_calibration.py`)
against synthetic caption-style text (real English text, lowercased and
stripped of punctuation - no real caption data exists yet, KB-008), not
guessed from word counts. This addresses the risk T-008 flagged: its 400-token
cap was measured on HF abstracts only. **Re-confirm against real transcript
text once T-017 unblocks** - this is still an estimate.
"""

from __future__ import annotations

from dataclasses import dataclass

# Real chars/token measured for caption-style text (lowercase, no punctuation)
# via qwen3's tokenizer on 5 real HF abstracts converted to that style: 5.55
# (worst case, i.e. most tokens per char) to 6.71 chars/token. Using the
# worst case with a safety margin: target 350 of T-008's 400-token cap,
# 350 * 5.55 ~= 1942, rounded down.
CHARS_PER_TOKEN_CAPTION_WORST_CASE = 5.55
TARGET_CHUNK_TOKENS = 350
TARGET_CHUNK_CHARS = int(TARGET_CHUNK_TOKENS * CHARS_PER_TOKEN_CAPTION_WORST_CASE)


@dataclass
class Chunk:
    id: str  # unique within the store
    doc_id: str  # the source Document's id
    source: str  # "hf" | "youtube"
    url: str  # citation link - a YouTube chunk with a start time includes &t=SECONDS
    title: str
    feed_date: str
    text: str
    text_source: str | None = None  # propagated from the Document (D-006)
    fallback_reason: str | None = None
    arxiv_published_at: str | None = None  # papers only; never used for filtering
    start_seconds: float | None = None  # YouTube chunks with real timing only


def chunk_hf_document(doc: dict) -> list[Chunk]:
    return [
        Chunk(
            id=f"hf:{doc['id']}:0",
            doc_id=doc["id"],
            source="hf",
            url=doc["url"],
            title=doc["title"],
            feed_date=doc["feed_date"],
            text=doc["text"],
            text_source=doc.get("text_source"),
            fallback_reason=doc.get("fallback_reason"),
            arxiv_published_at=doc.get("arxiv_published_at"),
        )
    ]


def chunk_youtube_document(doc: dict) -> list[Chunk]:
    """Groups real transcript segments into ~TARGET_CHUNK_CHARS windows, each
    chunk starting at its first segment's real timestamp. Falls back to one
    whole-document chunk with no timestamp for a `title_description` document
    (D-006's fallback path never has `segments` - nothing was ever fetched to
    time)."""
    segments = doc.get("segments")
    if not segments:
        return [
            Chunk(
                id=f"youtube:{doc['id']}:0",
                doc_id=doc["id"],
                source="youtube",
                url=doc["url"],
                title=doc["title"],
                feed_date=doc["feed_date"],
                text=doc["text"],
                text_source=doc.get("text_source"),
                fallback_reason=doc.get("fallback_reason"),
            )
        ]

    chunks: list[Chunk] = []
    window_start: float | None = None
    window_parts: list[str] = []
    window_chars = 0
    index = 0

    def flush() -> None:
        nonlocal index
        if not window_parts:
            return
        start = window_start if window_start is not None else 0.0
        chunks.append(
            Chunk(
                id=f"youtube:{doc['id']}:{index}",
                doc_id=doc["id"],
                source="youtube",
                url=f"{doc['url']}&t={int(start)}",
                title=doc["title"],
                feed_date=doc["feed_date"],
                text=" ".join(window_parts),
                text_source=doc.get("text_source"),
                start_seconds=start,
            )
        )
        index += 1

    for seg in segments:
        if window_start is None:
            window_start = seg["start"]
        window_parts.append(seg["text"])
        window_chars += len(seg["text"]) + 1
        if window_chars >= TARGET_CHUNK_CHARS:
            flush()
            window_parts = []
            window_chars = 0
            window_start = None

    flush()
    return chunks


def chunk_document(doc: dict) -> list[Chunk]:
    if doc["source"] == "hf":
        return chunk_hf_document(doc)
    if doc["source"] == "youtube":
        return chunk_youtube_document(doc)
    raise ValueError(f"unknown document source: {doc['source']!r}")
