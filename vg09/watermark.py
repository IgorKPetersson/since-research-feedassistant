"""Per-source watermarks (T-013/T-015/T-017): the most recent `feed_date` a
backfill or catch-up run has fully settled for that source. Catch-up fetches
everything with `feed_date` after the watermark, going forward - not the
8-weeks-ago start of a backfill window.

Kept one file per source (not one combined watermark) so HF's backfill (T-015)
and YouTube's (T-017, currently blocked) can each progress independently."""

from __future__ import annotations

import json
from pathlib import Path

WATERMARK_DIR = Path(__file__).resolve().parent.parent / "data"


def watermark_path(source: str) -> Path:
    return WATERMARK_DIR / f"watermark_{source}.json"


def read_watermark(source: str) -> str | None:
    """The most recent settled `feed_date` for this source, or None if no
    backfill/catch-up has completed for it yet."""
    path = watermark_path(source)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["feed_date"]


def write_watermark(source: str, feed_date: str) -> None:
    path = watermark_path(source)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"feed_date": feed_date}, indent=2), encoding="utf-8")
