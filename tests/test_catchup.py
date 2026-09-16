"""Unit tests for vg09.catchup (T-013).

No network calls of any kind - `sync_hf` is mocked for the HF tests, and
`catch_up_youtube` is exercised directly: `vg09.catchup` never imports
`vg09.youtube`, so a YouTube call is structurally impossible from this
module, not just avoided by convention.
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

    def test_no_watermark_is_reported_and_skipped_not_an_error(self):
        catch_up_youtube()  # must not raise, must not need a YouTube module at all

    def test_module_never_imports_youtube(self):
        import vg09.catchup as mod

        self.assertNotIn("youtube", mod.__dict__)


if __name__ == "__main__":
    unittest.main()
