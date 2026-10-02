"""Unit tests for vg09.youtube_backfill (T-036).

Closes the Phase 1 grill-me review's deferred finding (docs/PLAN.md's risk
register): "the riskiest orchestration code in the ingest pipeline, verified
only by real production runs" (T-019's own self-flagged note). No network
calls of any kind - vg09.youtube_backfill._list_channel and .normalize
(imported names, not vg09.youtube's own) are mocked directly.

RAW_DIR is patched in both vg09.document and vg09.youtube_backfill - the same
two-place gotcha test_sync.py's setUp already documents: youtube_backfill.py
does `from vg09.document import RAW_DIR, Document`, which binds its own
module-level copy of the name (used by _pending_videos()) at import time.
Patching vg09.document.RAW_DIR alone would redirect document.exists()/
Document.write() but not youtube_backfill's own pending-marker glob.

time.sleep is always patched too - nothing in this suite waits on a real
wall clock, and vg09.sources.load is patched to one fake channel so a test's
video list is exactly what it declares, not the user's real configuration.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from vg09 import document
from vg09.document import Document
from vg09.sources import Sources
from vg09.watermark import read_watermark
from vg09.youtube_backfill import SHORT_PAUSE_SECONDS, run


def fake_video(video_id: str, feed_date: str, title: str = "A video") -> dict:
    """The subset of a real yt-dlp video-listing dict this module actually
    reads (id/upload_date/title) - matches T-002/KB-001's confirmed real
    shape. upload_date is yt-dlp's own YYYYMMDD form."""
    return {"id": video_id, "upload_date": feed_date.replace("-", ""), "title": title}


def fake_document(video_id: str, feed_date: str) -> Document:
    return Document(
        id=video_id, source="youtube", url=f"https://www.youtube.com/watch?v={video_id}",
        title="A video", feed_date=feed_date, text="a real transcript", text_source="captions",
    )


class YoutubeBackfillTestCase(unittest.TestCase):
    """Shared isolation for every test below: a temp data/ dir (never the real
    one), a single fake channel (never the real 4), and no real wall-clock
    waits. `self.mock_sleep` is available for tests that want to assert on
    pacing specifically."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raw_dir = Path(tmp.name) / "raw"
        for target in ("vg09.document.RAW_DIR", "vg09.youtube_backfill.RAW_DIR"):
            patcher = patch(target, raw_dir)
            patcher.start()
            self.addCleanup(patcher.stop)

        watermark_patcher = patch("vg09.watermark.WATERMARK_DIR", Path(tmp.name))
        watermark_patcher.start()
        self.addCleanup(watermark_patcher.stop)

        # T-053: the channel list now comes from vg09.sources.load() at run time.
        channels_patcher = patch(
            "vg09.sources.load",
            return_value=Sources(channels={"testchannel": "https://example.com/testchannel"}),
        )
        channels_patcher.start()
        self.addCleanup(channels_patcher.stop)

        sleep_patcher = patch("vg09.youtube_backfill.time.sleep")
        self.mock_sleep = sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)


class ResumabilityTests(YoutubeBackfillTestCase):
    def test_already_fetched_video_is_skipped_not_refetched(self):
        fake_document("vid1", "2026-09-15").write()  # as if an earlier run already fetched it

        with patch("vg09.youtube_backfill._list_channel",
                    return_value=[fake_video("vid1", "2026-09-15")]) as mock_list, \
             patch("vg09.youtube_backfill.normalize") as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_list.assert_called_once()  # listing still happens - only the fetch is skipped
        mock_normalize.assert_not_called()
        self.assertEqual(result.already_done, 1)
        self.assertEqual(result.attempts, 0)

    def test_a_not_yet_fetched_video_is_processed_and_written(self):
        self.assertFalse(document.exists("youtube", "2026-09-15", "vid2"))

        with patch("vg09.youtube_backfill._list_channel", return_value=[fake_video("vid2", "2026-09-15")]), \
             patch("vg09.youtube_backfill.normalize",
                   return_value=fake_document("vid2", "2026-09-15")) as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_normalize.assert_called_once()
        self.assertEqual(result.already_done, 0)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.fetched_captions, 1)
        self.assertTrue(document.exists("youtube", "2026-09-15", "vid2"))

    def test_written_document_records_the_channel_it_was_listed_under(self):
        """T-054: without this the store can't count or remove a channel's videos."""
        with patch("vg09.youtube_backfill._list_channel", return_value=[fake_video("vid3", "2026-09-15")]), \
             patch("vg09.youtube_backfill.normalize", return_value=fake_document("vid3", "2026-09-15")):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        written = json.loads(document.raw_path("youtube", "2026-09-15", "vid3").read_text(encoding="utf-8"))
        self.assertEqual(written["channel"], "testchannel")

    def test_second_run_does_not_refetch_what_the_first_run_wrote(self):
        video = fake_video("vid3", "2026-09-15")
        with patch("vg09.youtube_backfill._list_channel", return_value=[video]), \
             patch("vg09.youtube_backfill.normalize", return_value=fake_document("vid3", "2026-09-15")):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))  # run 1 - fetches it

        with patch("vg09.youtube_backfill._list_channel", return_value=[video]), \
             patch("vg09.youtube_backfill.normalize") as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))  # run 2 - should skip it

        mock_normalize.assert_not_called()
        self.assertEqual(result.already_done, 1)
        self.assertEqual(result.attempts, 0)


class PacingTests(YoutubeBackfillTestCase):
    def test_pause_happens_between_each_pair_of_consecutive_video_attempts(self):
        order: list[str] = []
        videos = [fake_video("vidA", "2026-09-10"), fake_video("vidB", "2026-09-11")]
        docs_by_id = {"vidA": fake_document("vidA", "2026-09-10"), "vidB": fake_document("vidB", "2026-09-11")}

        def fake_normalize(video):
            order.append(f"process:{video['id']}")
            return docs_by_id[video["id"]]

        self.mock_sleep.side_effect = lambda secs: order.append("pause")

        with patch("vg09.youtube_backfill._list_channel", return_value=videos), \
             patch("vg09.youtube_backfill.normalize", side_effect=fake_normalize):
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertEqual(order, ["process:vidA", "pause", "process:vidB", "pause"])
        self.assertEqual(self.mock_sleep.call_count, 2)
        self.assertEqual(result.attempts, 2)

    def test_pause_duration_is_drawn_from_the_short_pause_bounds(self):
        """Below LONG_PAUSE_EVERY (20 attempts), every pause uses the short,
        randomized per-video bounds - asserted against the real random source
        the module calls, not a guessed literal duration."""
        with patch("vg09.youtube_backfill._list_channel",
                    return_value=[fake_video("vidA", "2026-09-10")]), \
             patch("vg09.youtube_backfill.normalize", return_value=fake_document("vidA", "2026-09-10")), \
             patch("vg09.youtube_backfill.random.uniform", return_value=4.2) as mock_uniform:
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_uniform.assert_called_once_with(*SHORT_PAUSE_SECONDS)
        self.mock_sleep.assert_called_once_with(4.2)

    def test_already_done_videos_are_not_paced_no_normalize_no_sleep(self):
        """Pacing exists to space out real fetch attempts - a video skipped
        via document.exists() never reaches _process_video(), so it costs no
        pause either."""
        fake_document("vid1", "2026-09-15").write()

        with patch("vg09.youtube_backfill._list_channel", return_value=[fake_video("vid1", "2026-09-15")]), \
             patch("vg09.youtube_backfill.normalize"):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.mock_sleep.assert_not_called()


class WatermarkWriteTests(YoutubeBackfillTestCase):
    def test_watermark_written_only_after_the_full_window_completes(self):
        self.assertIsNone(read_watermark("youtube"))

        with patch("vg09.youtube_backfill._list_channel",
                    return_value=[fake_video("vidA", "2026-09-10")]), \
             patch("vg09.youtube_backfill.normalize", return_value=fake_document("vidA", "2026-09-10")):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertEqual(read_watermark("youtube"), "2026-09-20")

    def test_watermark_stays_unwritten_if_the_run_is_interrupted_partway(self):
        videos = [fake_video("vidA", "2026-09-10"), fake_video("vidB", "2026-09-11")]

        def fake_normalize(video):
            if video["id"] == "vidB":
                raise RuntimeError("simulated crash mid-run")
            return fake_document("vidA", "2026-09-10")

        with patch("vg09.youtube_backfill._list_channel", return_value=videos), \
             patch("vg09.youtube_backfill.normalize", side_effect=fake_normalize):
            with self.assertRaises(RuntimeError):
                run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertIsNone(read_watermark("youtube"))

    def test_a_channel_listing_failure_does_not_prevent_the_watermark_from_being_written(self):
        """A single channel's listing failing (a real, handled case -
        run()'s own try/except around list_videos()) is not the same as a
        run being interrupted - the window still completes for the other
        channels, so the watermark still advances."""
        with patch("vg09.youtube_backfill._list_channel", side_effect=RuntimeError("channel unreachable")):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertEqual(read_watermark("youtube"), "2026-09-20")


if __name__ == "__main__":
    unittest.main()


class ListChannelTests(YoutubeBackfillTestCase):
    """T-055: YouTube is asked for a video's details only when the video is new."""

    def list_channel(self, ids, details):
        from vg09.youtube_backfill import _list_channel

        with patch("vg09.youtube_backfill.list_video_ids", return_value=ids), \
             patch("vg09.youtube_backfill._fetch_single_video_metadata",
                   side_effect=details) as mock_fetch:
            videos = _list_channel("https://example.com/testchannel", start=date(2026, 9, 10))
        return videos, mock_fetch

    def test_a_video_already_on_disk_is_not_asked_about_and_keeps_its_stored_date(self):
        fake_document("known", "2026-09-15").write()

        videos, mock_fetch = self.list_channel(["known"], [])

        mock_fetch.assert_not_called()
        self.assertEqual(videos, [{"id": "known", "upload_date": "20260915", "title": None}])

    def test_the_walk_stops_at_the_first_new_video_older_than_the_window(self):
        details = {"new": fake_video("new", "2026-09-18"), "old": fake_video("old", "2026-09-01")}

        videos, mock_fetch = self.list_channel(["new", "old", "older"], lambda vid: details[vid])

        self.assertEqual([c.args[0] for c in mock_fetch.call_args_list], ["new", "old"])
        self.assertEqual([v["id"] for v in videos], ["new", "old"])

    def test_one_unreadable_video_is_skipped_and_the_rest_are_still_listed(self):
        def details(video_id):
            if video_id == "broken":
                raise RuntimeError("members only")
            return fake_video(video_id, "2026-09-18")

        videos, _ = self.list_channel(["broken", "fine"], details)

        self.assertEqual([v["id"] for v in videos], ["fine"])
