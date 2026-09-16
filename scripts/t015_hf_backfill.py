"""T-015: initial 8-week HF Daily Papers backfill.

HF only - YouTube's backfill is T-017, blocked on a transcript-path decision
(KB-008: the caption-fetch path is still IpBlocked). No YouTube calls here.

Resumable: each day gets a `_done.json` completion marker in data/raw/hf/<date>/
once it's been fetched - even a weekend day with 0 papers (KB-002) counts as
done. A re-run skips any day that already has one, rather than re-hitting the
API to re-confirm an empty result.

`today` is deliberately never marked done and never becomes the watermark: HF
may still add papers to today's date later in the day, so every run re-checks
today fresh (Document.write() overwrites safely - same arXiv id, same file, no
duplicates), and the watermark only advances through the last fully-elapsed
day. T-013's catch-up then always re-checks "today" too, since today's
feed_date is never <= the watermark.

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
        if d == today:
            docs = hf_papers.collect_day(d)
            fetched_days += 1
            total_papers += len(docs)
            print(f"{d.isoformat()}: {len(docs)} papers (today - always re-checked, not marked done)")
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

    watermark_date = today - timedelta(days=1)  # last fully-elapsed day, not today
    write_watermark("hf", watermark_date.isoformat())

    print(f"\nDone. {fetched_days} days fetched this run, {skipped_days} already done (skipped), "
          f"{total_papers} papers written this run.")
    print(f"New hf watermark: {watermark_date.isoformat()} (today excluded on purpose - see docstring)")


if __name__ == "__main__":
    main()
