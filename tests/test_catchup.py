"""Unit tests for vg09.catchup (T-013/T-019).

No network calls of any kind - both `sync_hf` (HF) and `run_youtube_backfill`
(YouTube, D-009/T-019's paced three-tier-fallback logic) are mocked, same
pattern for both sources now that YouTube catch-up is real rather than a
stub. The old "vg09.catchup never imports vg09.youtube" structural guarantee
(back when YouTube's transcript path was still blocked, KB-008) no longer
applies - D-009/T-019 gave YouTube catch-up a real implementation to call.
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from vg09.catchup import catch_up_hf, catch_up_youtube
from vg09.watermark import write_watermark


class CatchUpHfTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = patch("vg09.watermark.WATERMARK_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_no_watermark_skips_without_calling_sync(self):
        with patch("vg09.catchup.sync_hf") as mock_sync:
            result = catch_up_hf(today=date(2026, 9, 16))

        mock_sync.assert_not_called()
        self.assertIsNone(result)

    def test_watermark_present_calls_sync_from_the_day_after(self):
        write_watermark("hf", "2026-09-10")
        with patch("vg09.catchup.sync_hf") as mock_sync:
            mock_sync.return_value = {
                "fetched_days": 1, "skipped_days": 0, "total_papers": 5,
                "watermark": "2026-09-14", "window_start": "x", "window_end": "y",
            }
            result = catch_up_hf(today=date(2026, 9, 16))

        mock_sync.assert_called_once_with(start=date(2026, 9, 11), today=date(2026, 9, 16))
        self.assertEqual(result["total_papers"], 5)


class CatchUpYoutubeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = patch("vg09.watermark.WATERMARK_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_no_watermark_skips_without_calling_the_backfill(self):
        with patch("vg09.catchup.run_youtube_backfill") as mock_run:
            result = catch_up_youtube(today=date(2026, 9, 16))

        mock_run.assert_not_called()
        self.assertIsNone(result)

    def test_watermark_present_calls_backfill_from_the_day_after(self):
        write_watermark("youtube", "2026-09-10")
        with patch("vg09.catchup.run_youtube_backfill") as mock_run:
            mock_run.return_value = "fake result"
            result = catch_up_youtube(today=date(2026, 9, 16))

        mock_run.assert_called_once_with(start=date(2026, 9, 11), today=date(2026, 9, 16))
        self.assertEqual(result, "fake result")


if __name__ == "__main__":
    unittest.main()
