"""T-015: initial 8-week HF Daily Papers backfill.

HF only - YouTube's backfill is T-017, blocked on a transcript-path decision
(KB-008: the caption-fetch path is still IpBlocked). No YouTube calls here.

Thin entry point over vg09.sync.sync_hf() (factored out under T-013 so the
backfill and catch-up share one implementation - see that module's docstring
for the reopen-window/resumability mechanism).

Makes real network calls to the HF Daily Papers API; run it manually.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.sync import sync_hf  # noqa: E402
from vg09.watermark import read_watermark  # noqa: E402

WEEKS_BACK = 8


def main() -> None:
    today = date.today()
    start = today - timedelta(days=WEEKS_BACK * 7 - 1)  # inclusive of both ends -> exactly 8*7 days

    prior_watermark = read_watermark("hf")
    print(f"Prior hf watermark: {prior_watermark or '(none - first run)'}")
    print(f"Backfill window: {start.isoformat()} .. {today.isoformat()}\n")

    result = sync_hf(start=start, today=today)

    print(f"\nDone. {result['fetched_days']} days fetched this run, {result['skipped_days']} "
          f"already done (skipped), {result['total_papers']} papers written this run.")
    print(f"New hf watermark: {result['watermark']} (reopen window excluded on purpose)")


if __name__ == "__main__":
    main()
