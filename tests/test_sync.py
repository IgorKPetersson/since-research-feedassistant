"""Unit tests for vg09.sync (T-013/T-015).

No live network calls: vg09.hf_papers.fetch_day is mocked directly, returning
controlled fake HF API responses in the real shape KB-002 confirmed (top-level
title/summary/publishedAt, paper.id, paper.submittedOnDailyAt).
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from vg09 import hf_papers
from vg09.sync import sync_hf


def fake_entry(arxiv_id: str, feed_date: str, title: str = "A paper") -> dict:
    return {
        "title": title,
        "summary": f"Abstract for {title}.",
        "publishedAt": f"{feed_date}T00:00:00.000Z",
        "paper": {"id": arxiv_id, "submittedOnDailyAt": f"{feed_date}T00:00:00.000Z"},
    }


class SyncHfTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_dir = Path(tmp.name)
        raw_dir = tmp_dir / "raw"
        # vg09.hf_papers did `from vg09.document import RAW_DIR`, which binds
        # its own module-level name at import time - patching
        # vg09.document.RAW_DIR alone does NOT redirect vg09.hf_papers's
        # day-marker functions (day_marker_path/is_day_done/mark_day_done/
        # clear_day_marker), which read their own copy of the name. Both must
        # be patched together, or day-marker calls silently hit the real
        # data/raw/hf/ directory. (Caught the hard way: an earlier version of
        # this test deleted 4 real _done.json markers before this fix.)
        for target in ("vg09.document.RAW_DIR", "vg09.hf_papers.RAW_DIR"):
            patcher = patch(target, raw_dir)
            patcher.start()
            self.addCleanup(patcher.stop)
        watermark_patcher = patch("vg09.watermark.WATERMARK_DIR", tmp_dir)
        watermark_patcher.start()
        self.addCleanup(watermark_patcher.stop)

    def test_fetches_every_day_and_advances_watermark_before_the_reopen_window(self):
        by_date = {
            "2026-09-10": [fake_entry("1000.1", "2026-09-10")],
            "2026-09-11": [fake_entry("1000.2", "2026-09-11")],
            "2026-09-12": [],  # weekend, per KB-002
        }
        with patch("vg09.hf_papers.fetch_day", side_effect=lambda d: by_date.get(d.isoformat(), [])):
            result = sync_hf(start=date(2026, 9, 10), today=date(2026, 9, 12))

        # today=9-12 and yesterday=9-11 fall inside the 2-day reopen window;
        # only 9-10 is old enough to be marked settled.
        self.assertEqual(result["total_papers"], 2)
        self.assertEqual(result["watermark"], "2026-09-10")
        self.assertTrue(hf_papers.is_day_done(date(2026, 9, 10)))
        self.assertFalse(hf_papers.is_day_done(date(2026, 9, 11)))
        self.assertFalse(hf_papers.is_day_done(date(2026, 9, 12)))

        path = hf_papers.RAW_DIR / "hf" / "2026-09-10" / "1000.1.json"
        self.assertTrue(path.exists())

    def test_second_run_skips_settled_days_with_no_duplicate_fetch(self):
        # 2026-09-01 .. 2026-09-10: 10 days. today/yesterday (9-10, 9-09) are
        # always in the reopen window; the other 8 (9-01..9-08) settle.
        by_date = {"2026-09-01": [fake_entry("3000.1", "2026-09-01")]}
        calls: list[str] = []

        def fake_fetch_day(d):
            calls.append(d.isoformat())
            return by_date.get(d.isoformat(), [])

        with patch("vg09.hf_papers.fetch_day", side_effect=fake_fetch_day):
            sync_hf(start=date(2026, 9, 1), today=date(2026, 9, 10))
            calls.clear()
            result2 = sync_hf(start=date(2026, 9, 1), today=date(2026, 9, 10))

        self.assertNotIn("2026-09-01", calls)  # settled on run 1 - not re-fetched on run 2
        self.assertEqual(sorted(calls), ["2026-09-09", "2026-09-10"])  # only the reopen window
        self.assertEqual(result2["fetched_days"], 2)
        self.assertEqual(result2["skipped_days"], 8)


if __name__ == "__main__":
    unittest.main()
