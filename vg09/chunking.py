"""Chunking (T-012): normalized Document -> one or more Chunks ready to embed.

- **HF**: one chunk per paper, the whole abstract. Already well under T-008's
  400-qwen3-token chunk cap (max observed 363 tokens across all 20 real
  abstracts on disk).
- **YouTube**: chunked by transcript *timestamp*, not sentence, for both
  caption- and Whisper-sourced documents (T-019 adds Whisper as a second
  transcript source, D-009) - real segments always have a meaningful start
  time to cite (`&t=SECONDS`, D-002), which sentence splitting would have to
  reconstruct anyway. Whole segments are merged into a window until
  `TARGET_CHUNK_CHARS` is reached; a window only ever closes *after* a whole
  segment is added, so a chunk boundary is always a segment boundary, never
  mid-segment - true for both sources since both are normalized to the same
  `{text, start, duration}` shape before reaching this module.
  **Correction (KB-014):** an earlier version of this docstring claimed
  auto-generated captions have no punctuation, attributed to KB-001 - KB-001
  never actually says that, and real fetched captions (T-017) turned out to
  have normal punctuation and capitalization throughout. That claim was an
  unverified assumption, not a measured fact; removed rather than repeated.

The YouTube chunk-size target (`TARGET_CHUNK_CHARS`) is calibrated from a real
qwen3 tokenizer measurement against **real** caption text (T-019,
`scripts/t019_caption_token_recalibration.py`, 17 real transcripts fetched by
T-017), replacing T-012's original estimate from synthetic
lowercased/depunctuated stand-in text (no real captions existed yet at the
time, KB-008). The real measurement came out *worse* (fewer chars per token:
4.16 real worst-case vs. 5.55 assumed) - the synthetic estimate under-budgeted
real token count for a given character window, the dangerous direction per
KB-005's silent-truncation risk. Fixed by using the real ratio.
"""

from __future__ import annotations

from dataclasses import dataclass

# Real chars/token measured via qwen3's tokenizer against 17 real caption
# transcripts fetched by T-017 (scripts/t019_caption_token_recalibration.py):
# 4.1566 (worst case, i.e. most tokens per char - shown rounded as 4.16 in
# that script's own output) to 4.61 chars/token, mean 4.38. Supersedes
# T-012's synthetic-text estimate of 5.55-6.71 (see module docstring) - real
# captions tokenize less efficiently than the synthetic stand-in assumed.
# Using the worst case with a safety margin: target 350 of T-008's 400-token
# cap, 350 * 4.1566 ~= 1454, rounded down.
CHARS_PER_TOKEN_CAPTION_WORST_CASE = 4.1566
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
    channel: str | None = None  # YouTube only: the channel handle (T-054, D-017)


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
                channel=doc.get("channel"),
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
                fallback_reason=doc.get("fallback_reason"),
                start_seconds=start,
                channel=doc.get("channel"),
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
