"""T-013: catch-up ingestion since the last successful run, per source.

Per-source watermarks (`vg09.watermark`), not one combined watermark, so HF's
catch-up (backed by T-015's completed backfill) never waits on YouTube's
(T-017, still blocked on a transcript-path decision, KB-008). No YouTube
calls are made from this module - if no YouTube watermark exists yet, that
source is skipped and reported, never silently treated as "caught up"."""

from __future__ import annotations

from datetime import date, timedelta

from vg09.sync import sync_hf
from vg09.watermark import read_watermark


def catch_up_hf(today: date | None = None) -> dict | None:
    watermark = read_watermark("hf")
    if watermark is None:
        print("No hf watermark found - run the backfill (T-015) first. Skipping HF catch-up.")
        return None
    start = date.fromisoformat(watermark) + timedelta(days=1)
    print(f"HF watermark: {watermark} -> catching up from {start.isoformat()}")
    return sync_hf(start=start, today=today)


def catch_up_youtube() -> None:
    """No YouTube calls are ever made here. If a YouTube watermark doesn't
    exist yet (T-017 hasn't run), that's reported and skipped, not treated as
    an error or as "nothing to catch up" (the two mean different things -
    the former is "never started", the latter is "already up to date")."""
    watermark = read_watermark("youtube")
    if watermark is None:
        print("No youtube watermark found - T-017 hasn't run yet. Skipping YouTube catch-up "
              "(no YouTube call made).")
        return
    print(f"YouTube watermark: {watermark} - YouTube catch-up logic isn't implemented yet (T-017).")


def catch_up(today: date | None = None) -> dict:
    hf_result = catch_up_hf(today=today)
    catch_up_youtube()
    return {"hf": hf_result}
