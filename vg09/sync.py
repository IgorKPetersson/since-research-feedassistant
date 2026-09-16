"""Day-by-day HF Daily Papers sync (T-013/T-015): the same mechanism serves
both the initial 8-week backfill and ongoing catch-up - the only difference is
the start date. Factored out of T-015's backfill script so both use identical,
already-tested logic rather than two copies that could drift apart.

Reopen window (T-015's follow-up fix): the last REOPEN_DAYS calendar days are
always re-fetched and never marked done, since HF may still add papers to a
recent date, and Sweden runs ahead of UTC so a run shortly after local
midnight could otherwise close out a day still open on HF's server clock.

YouTube is not handled here - it's a different, per-video mechanism (T-010's
Pending/IngestBlocked), not day-based, and T-017 (its backfill) is still
blocked on a transcript-path decision."""

from __future__ import annotations

import time
from datetime import date, timedelta

from vg09 import hf_papers
from vg09.watermark import write_watermark

PAUSE_BETWEEN_DAYS = 0.3  # seconds - no rate limit observed (KB-002, 14 days), a courtesy pause anyway
REOPEN_DAYS = 2  # always re-check the last 2 calendar days - Sweden runs ahead of UTC


def sync_hf(start: date, today: date | None = None) -> dict:
    """Fetch HF papers for every day from `start` through `today` (inclusive),
    write them to data/raw/hf/, and advance the hf watermark through the day
    before the reopen window. Returns a summary dict."""
    today = today or date.today()
    if start > today:
        start = today
    days = [start + timedelta(days=i) for i in range((today - start).days + 1)]

    fetched_days = 0
    skipped_days = 0
    total_papers = 0

    for d in days:
        if (today - d).days < REOPEN_DAYS:
            hf_papers.clear_day_marker(d)
            docs = hf_papers.collect_day(d)
            fetched_days += 1
            total_papers += len(docs)
            print(f"{d.isoformat()}: {len(docs)} papers (reopen window - always re-checked, not marked done)")
            time.sleep(PAUSE_BETWEEN_DAYS)
            continue

        if hf_papers.is_day_done(d):
            skipped_days += 1
            continue

        docs = hf_papers.collect_day(d)
        hf_papers.mark_day_done(d, len(docs))
        fetched_days += 1
        total_papers += len(docs)
        note = "  (empty - weekend, per KB-002)" if not docs else ""
        print(f"{d.isoformat()}: {len(docs)} papers{note}")
        time.sleep(PAUSE_BETWEEN_DAYS)

    watermark_date = today - timedelta(days=REOPEN_DAYS)
    write_watermark("hf", watermark_date.isoformat())

    return {
        "fetched_days": fetched_days,
        "skipped_days": skipped_days,
        "total_papers": total_papers,
        "watermark": watermark_date.isoformat(),
        "window_start": days[0].isoformat(),
        "window_end": days[-1].isoformat(),
    }
