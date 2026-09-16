"""Shared normalized document shape for all collectors (T-009).

Every source (HF Daily Papers, YouTube) is normalized to this one shape before
anything downstream (T-012's chunk/embed/store) touches it, so storage never needs
to know which source a document came from.

`feed_date` is the date used for all filtering and catch-up ingestion - the date
something appeared in the source we watch, not its original publish date. See
docs/DECISIONS.md D-002. For papers, the arXiv `publishedAt` date is kept as extra
metadata for citations only, never for filtering.

Documents are persisted under data/raw/<source>/<feed_date>/<id>.json so the
database (T-012) can be rebuilt from disk without re-fetching from YouTube or HF,
and so a backfill (T-015) can tell what it has already fetched by checking for the
file rather than keeping a separate resume log.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

_UNSAFE_ID_CHARS = re.compile(r"[^A-Za-z0-9_.-]")


def raw_path(source: str, feed_date: str, doc_id: str) -> Path:
    """Where a document with this id would live, whether or not it exists yet.

    Callers that need to check "have I already fetched this?" before doing
    expensive work (a transcript fetch, an API call) should call this - or
    `exists()` - first.
    """
    safe_id = _UNSAFE_ID_CHARS.sub("_", doc_id)
    return RAW_DIR / source / feed_date / f"{safe_id}.json"


def pending_path(source: str, feed_date: str, doc_id: str) -> Path:
    """Where a *pending* marker for this id would live - a video whose fetch was
    blocked (D-006/KB-008) rather than a source that genuinely lacks the data.
    Kept alongside, not inside, the final document so a reader that only wants
    finished documents can glob `*.json` and skip `*.pending.json`."""
    safe_id = _UNSAFE_ID_CHARS.sub("_", doc_id)
    return RAW_DIR / source / feed_date / f"{safe_id}.pending.json"


def exists(source: str, feed_date: str, doc_id: str) -> bool:
    return raw_path(source, feed_date, doc_id).exists()


def clear_pending(source: str, feed_date: str, doc_id: str) -> None:
    """Remove a stale pending marker once a final document has been written for
    the same id - otherwise a resolved video would still look pending to a
    reader that only checks for `*.pending.json` (T-015's retry logic)."""
    pending_path(source, feed_date, doc_id).unlink(missing_ok=True)


@dataclass
class Document:
    id: str  # stable unique id within `source` - arXiv id, or YouTube video id
    source: str  # "hf" | "youtube"
    url: str
    title: str
    feed_date: str  # ISO date (YYYY-MM-DD) - D-002
    text: str
    arxiv_published_at: str | None = None  # papers only; never used for filtering
    text_source: str | None = None  # "captions" | "title_description" (YouTube only)
    fallback_reason: str | None = None  # exception class name; set iff text_source is
    # "title_description" (D-006) - lets a fallback document be told apart from a real
    # transcript and reconsidered later without re-deriving that from `text` itself

    def write(self) -> Path:
        path = raw_path(self.source, self.feed_date, self.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


@dataclass
class Pending:
    """A video whose caption fetch was blocked (D-006) rather than genuinely
    missing captions - deliberately has no `text`, since nothing was fetched.
    Retried later (T-015), not treated as a finished document."""

    id: str
    source: str
    url: str
    title: str
    feed_date: str
    reason: str  # the exception class name that caused the block

    def write(self) -> Path:
        path = pending_path(self.source, self.feed_date, self.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
        return path
