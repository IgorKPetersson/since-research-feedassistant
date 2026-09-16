"""T-015: initial 8-week HF Daily Papers backfill.

HF only - YouTube's backfill is T-017, blocked on a transcript-path decision
(KB-008: the caption-fetch path is still IpBlocked). No YouTube calls here.

Resumable: each day gets a `_done.json` completion marker in data/raw/hf/<date>/
once it's been fetched - even a weekend day with 0 papers (KB-002) counts as
done. A re-run skips any day that already has one, rather than re-hitting the
API to re-confirm an empty result.

The last REOPEN_DAYS calendar days (today and yesterday) are deliberately never
marked done and never become the watermark: HF may still add papers to a
recent date later on, and Sweden's local clock runs ahead of UTC, so a run
shortly after local midnight could otherwise close out a day that's still open
on HF's server clock. Document.write() overwrites safely (same arXiv id, same
file, no duplicates), so re-checking costs nothing extra. The watermark
advances only through the day before the reopen window, and T-013's catch-up
will always re-check the reopen window too, since those feed_dates are never
<= the watermark.

Makes real network calls to the HF Daily Papers API; run it manually.
"""

import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09 import hf_papers  # noqa: E402
from vg09.watermark import read_watermark, write_watermark  # noqa: E402

WEEKS_BACK = 8
PAUSE_BETWEEN_DAYS = 0.3  # seconds - no rate limit observed (KB-002, 14 days), a courtesy pause anyway
REOPEN_DAYS = 2  # always re-check today and yesterday - Sweden runs ahead of UTC


def main() -> None:
    today = date.today()
    days = sorted(today - timedelta(days=i) for i in range(WEEKS_BACK * 7))

    prior_watermark = read_watermark("hf")
    print(f"Prior hf watermark: {prior_watermark or '(none - first run)'}")
    print(f"Backfill window: {days[0].isoformat()} .. {days[-1].isoformat()} ({len(days)} days)\n")

    fetched_days = 0
    skipped_days = 0
    total_papers = 0

    for d in days:
        if (today - d).days < REOPEN_DAYS:
            # In the reopen window - always re-check, never trust a marker
            # (even one left by an older run under different rules).
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

    watermark_date = today - timedelta(days=REOPEN_DAYS)  # last day before the reopen window
    write_watermark("hf", watermark_date.isoformat())

    print(f"\nDone. {fetched_days} days fetched this run, {skipped_days} already done (skipped), "
          f"{total_papers} papers written this run.")
    print(f"New hf watermark: {watermark_date.isoformat()} (reopen window excluded on purpose - see docstring)")


if __name__ == "__main__":
    main()
