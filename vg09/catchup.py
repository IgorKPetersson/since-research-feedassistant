"""T-013: catch-up ingestion since the last successful run, per source.

Per-source watermarks (`vg09.watermark`), not one combined watermark, so
each source's catch-up is independent - HF's never waited on YouTube's
having a real transcript path (D-009/T-019 now gives it one). If a source's
watermark doesn't exist yet, that source is skipped and reported, never
silently treated as "caught up" (the two mean different things - "never
started" vs. "already up to date")."""

from __future__ import annotations

from datetime import date, timedelta

from vg09 import sources
from vg09.sync import sync_hf
from vg09.watermark import read_watermark
from vg09.youtube_backfill import run as run_youtube_backfill


def catch_up_hf(today: date | None = None) -> dict | None:
    if not sources.load().hf_enabled:
        print("Hugging Face Daily Papers is switched off in data/sources.json. Skipping HF catch-up.")
        return None
    watermark = read_watermark("hf")
    if watermark is None:
        print("No hf watermark found - run the backfill (T-015) first. Skipping HF catch-up.")
        return None
    start = date.fromisoformat(watermark) + timedelta(days=1)
    print(f"HF watermark: {watermark} -> catching up from {start.isoformat()}")
    return sync_hf(start=start, today=today)


def catch_up_youtube(today: date | None = None):
    """T-091 (D-021): the same per-channel catch-up the app's update runs. Each channel
    starts where its own record says; a channel without one gets the configured backfill
    window. Catch-up and backfill are therefore one operation."""
    return run_youtube_backfill(weeks_back=sources.load().youtube_weeks, today=today)


def catch_up(today: date | None = None) -> dict:
    hf_result = catch_up_hf(today=today)
    youtube_result = catch_up_youtube(today=today)
    return {"hf": hf_result, "youtube": youtube_result}
