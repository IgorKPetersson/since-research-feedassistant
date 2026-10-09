"""Unit tests for vg09.youtube_backfill (T-036, T-090, T-091).

No network calls of any kind. YouTube is faked one level down: `list_video_ids` (the
channel's listing, newest first) and `_fetch_single_video_metadata` (one video's details)
are patched, so `_check_channel()` and the per-channel records run for real. `normalize`
(the transcript fetch) is patched too.

RAW_DIR is patched in both vg09.document and vg09.youtube_backfill - the same
two-place gotcha test_sync.py's setUp already documents (KB-010). The watermark folder
is patched as well, which also redirects `vg09.channel_state`'s file.

time.sleep is always patched too - nothing in this suite waits on a real
wall clock, and vg09.sources.load is patched to one fake channel so a test's
video list is exactly what it declares, not the user's real configuration.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from unittest.mock import patch

from vg09 import channel_state, document
from vg09.document import Document
from vg09.sources import Sources
from vg09.watermark import read_watermark, write_watermark
from vg09.youtube_backfill import SHORT_PAUSE_SECONDS, run

CHANNEL = "testchannel"


def fake_video(video_id: str, feed_date: str, title: str = "A video") -> dict:
    """The subset of a real yt-dlp video dict this module reads (id/upload_date/title),
    matching T-002/KB-001's confirmed real shape. upload_date is yt-dlp's YYYYMMDD."""
    return {"id": video_id, "upload_date": feed_date.replace("-", ""), "title": title}


def fake_document(video_id: str, feed_date: str) -> Document:
    return Document(
        id=video_id, source="youtube", url=f"https://www.youtube.com/watch?v={video_id}",
        title="A video", feed_date=feed_date, text="a real transcript", text_source="captions",
    )


def document_for(video: dict) -> Document:
    d = video["upload_date"]
    return fake_document(video["id"], f"{d[:4]}-{d[4:6]}-{d[6:]}")


class YoutubeBackfillTestCase(unittest.TestCase):
    """Shared isolation: a temp data/ dir (never the real one), one fake channel, and
    no real wall-clock waits. `self.listing()` fakes YouTube for one run."""

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

        # T-053: the channel list comes from vg09.sources.load() at run time.
        channels_patcher = patch(
            "vg09.sources.load",
            return_value=Sources(channels={CHANNEL: "https://example.com/testchannel"}),
        )
        channels_patcher.start()
        self.addCleanup(channels_patcher.stop)

        sleep_patcher = patch("vg09.youtube_backfill.time.sleep")
        self.mock_sleep = sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)
        self.details_asked: list[str] = []

    @contextmanager
    def listing(self, videos, details=None, list_error=None, normalize=document_for):
        """YouTube for one run: `videos` is the channel's listing, newest first, as
        video dicts. `details(video_id)` overrides the details lookup."""
        by_id = {v["id"]: v for v in videos}

        def lookup(video_id):
            self.details_asked.append(video_id)
            return details(video_id) if details else by_id[video_id]

        list_patch = (patch("vg09.youtube_backfill.list_video_ids", side_effect=list_error)
                      if list_error else
                      patch("vg09.youtube_backfill.list_video_ids",
                            return_value=[v["id"] for v in videos]))
        with list_patch, \
             patch("vg09.youtube_backfill._fetch_single_video_metadata", side_effect=lookup), \
             patch("vg09.youtube_backfill.normalize", side_effect=normalize) as mock_normalize:
            yield mock_normalize

    def record(self, handle: str = CHANNEL) -> dict:
        return channel_state.load()["channels"][handle]


class ResumabilityTests(YoutubeBackfillTestCase):
    def test_already_fetched_video_is_skipped_not_refetched(self):
        fake_document("vid1", "2026-09-15").write()  # as if an earlier run already fetched it

        with self.listing([fake_video("vid1", "2026-09-15")]) as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_normalize.assert_not_called()
        self.assertEqual(self.details_asked, [])  # on disk: not even looked up
        self.assertEqual(result.already_done, 1)
        self.assertEqual(result.attempts, 0)

    def test_a_not_yet_fetched_video_is_processed_and_written(self):
        self.assertFalse(document.exists("youtube", "2026-09-15", "vid2"))

        with self.listing([fake_video("vid2", "2026-09-15")]) as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_normalize.assert_called_once()
        self.assertEqual(result.already_done, 0)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.fetched_captions, 1)
        self.assertTrue(document.exists("youtube", "2026-09-15", "vid2"))

    def test_written_document_records_the_channel_it_was_listed_under(self):
        """T-054: without this the store can't count or remove a channel's videos."""
        with self.listing([fake_video("vid3", "2026-09-15")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        written = json.loads(document.raw_path("youtube", "2026-09-15", "vid3").read_text(encoding="utf-8"))
        self.assertEqual(written["channel"], CHANNEL)

    def test_second_run_does_not_refetch_what_the_first_run_wrote(self):
        video = fake_video("vid3", "2026-09-20")  # inside the second run's recheck window
        with self.listing([video]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))  # run 1 - fetches it

        with self.listing([video]) as mock_normalize:
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))  # run 2 - skips it

        mock_normalize.assert_not_called()
        self.assertEqual(result.already_done, 1)
        self.assertEqual(result.attempts, 0)


class PacingTests(YoutubeBackfillTestCase):
    def test_pause_happens_between_each_pair_of_consecutive_video_attempts(self):
        order: list[str] = []
        videos = [fake_video("vidA", "2026-09-10"), fake_video("vidB", "2026-09-11")]

        def normalize(video):
            order.append(f"process:{video['id']}")
            return document_for(video)

        self.mock_sleep.side_effect = lambda secs: order.append("pause")

        with self.listing(videos, normalize=normalize):
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertEqual(order, ["process:vidA", "pause", "process:vidB", "pause"])
        self.assertEqual(self.mock_sleep.call_count, 2)
        self.assertEqual(result.attempts, 2)

    def test_pause_duration_is_drawn_from_the_short_pause_bounds(self):
        """Below LONG_PAUSE_EVERY (20 attempts), every pause uses the short,
        randomized per-video bounds - asserted against the real random source
        the module calls, not a guessed literal duration."""
        with self.listing([fake_video("vidA", "2026-09-10")]), \
             patch("vg09.youtube_backfill.random.uniform", return_value=4.2) as mock_uniform:
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        mock_uniform.assert_called_once_with(*SHORT_PAUSE_SECONDS)
        self.mock_sleep.assert_called_once_with(4.2)

    def test_already_done_videos_are_not_paced_no_normalize_no_sleep(self):
        """Pacing exists to space out real fetch attempts - a video already on disk
        never reaches _process_video(), so it costs no pause either."""
        fake_document("vid1", "2026-09-15").write()

        with self.listing([fake_video("vid1", "2026-09-15")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.mock_sleep.assert_not_called()


class ChannelRecordTests(YoutubeBackfillTestCase):
    """T-091: each channel's progress is its own; the shared watermark is not written."""

    def test_a_complete_check_records_its_date_and_listing(self):
        with self.listing([fake_video("vidA", "2026-09-10")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()
        self.assertEqual(record["checked_through"], "2026-09-20")
        self.assertIsNone(record["pending_from"])
        self.assertEqual(record["last_result"], channel_state.RESULT_COMPLETE)
        self.assertEqual(record["listing"], ["vidA"])
        self.assertEqual(record["newest_content"], "2026-09-10")
        self.assertIsNotNone(record["last_success"])
        self.assertIsNone(read_watermark("youtube"))  # retired for YouTube (D-021)

    def test_an_interrupted_run_leaves_the_channel_unchecked(self):
        videos = [fake_video("vidA", "2026-09-10"), fake_video("vidB", "2026-09-11")]

        def normalize(video):
            if video["id"] == "vidB":
                raise RuntimeError("simulated crash mid-run")
            return document_for(video)

        with self.listing(videos, normalize=normalize), self.assertRaises(RuntimeError):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()  # the record was created before fetching, then never advanced
        self.assertIsNone(record["checked_through"])
        self.assertEqual(record["pending_from"], "2026-09-01")

    def test_one_failing_channel_keeps_its_window_while_the_other_moves_on(self):
        """The loss T-091 fixes: the shared watermark advanced past a failed channel."""
        channels = {"good": "https://example.com/good", "bad": "https://example.com/bad"}

        def list_ids(url, count):
            if url.endswith("/bad"):
                raise RuntimeError("channel unreachable")
            return ["g1"]

        with patch("vg09.youtube_backfill.list_video_ids", side_effect=list_ids), \
             patch("vg09.youtube_backfill._fetch_single_video_metadata",
                   return_value=fake_video("g1", "2026-09-18")), \
             patch("vg09.youtube_backfill.normalize", side_effect=document_for):
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20), channels=channels)

        good, bad = self.record("good"), self.record("bad")
        self.assertEqual((good["checked_through"], good["pending_from"]), ("2026-09-20", None))
        self.assertEqual((bad["checked_through"], bad["pending_from"]), (None, "2026-09-01"))
        self.assertEqual(bad["last_result"], channel_state.RESULT_FAILED)
        self.assertIn("channel unreachable", bad["last_error"])
        self.assertIn("bad", result.channel_problems)
        self.assertNotIn("good", result.channel_problems)

    def test_a_failed_channel_recovers_its_interval_after_a_long_failure(self):
        """Complete on the 1st, failing from the 2nd to the 9th, back on the 10th: the
        retry starts at the 1st's recheck window, far beyond the two-day overlap."""
        with self.listing([fake_video("old", "2026-10-01")]):
            run(start=date(2026, 9, 20), today=date(2026, 10, 1))
        for day in range(2, 10):
            with self.listing([], list_error=RuntimeError("down")):
                run(start=date(2026, 9, 20), today=date(2026, 10, day))
        self.assertEqual(self.record()["pending_from"], "2026-09-30")  # kept, not moved on

        videos = [fake_video(f"v{d}", f"2026-10-0{d}") for d in (9, 5, 2)] + \
            [fake_video("old", "2026-10-01")]
        with self.listing(videos) as mock_normalize:
            run(start=date(2026, 9, 20), today=date(2026, 10, 10))

        self.assertEqual(sorted(c.args[0]["id"] for c in mock_normalize.call_args_list),
                         ["v2", "v5", "v9"])
        self.assertEqual(self.record()["checked_through"], "2026-10-10")
        self.assertIsNone(self.record()["pending_from"])

    def test_a_video_that_fails_to_load_for_another_reason_keeps_the_window(self):
        def details(video_id):
            if video_id == "flaky":
                raise RuntimeError("HTTP Error 503")
            return fake_video(video_id, "2026-09-18")

        with self.listing([fake_video("flaky", "2026-09-19"), fake_video("fine", "2026-09-18")],
                          details=details):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()
        self.assertEqual(record["last_result"], channel_state.RESULT_INCOMPLETE)
        self.assertEqual(record["pending_from"], "2026-09-01")
        self.assertIn("503", record["last_error"])
        self.assertTrue(document.exists("youtube", "2026-09-18", "fine"))  # still fetched

    def test_members_only_and_private_videos_do_not_block_completion(self):
        def details(video_id):
            if video_id == "members":
                raise RuntimeError("ERROR: [youtube] members: Join this channel to get access "
                                   "to members-only content like this video")
            if video_id == "private":
                raise RuntimeError("ERROR: [youtube] private: Private video")
            return fake_video(video_id, "2026-09-18")

        with self.listing([fake_video("members", "2026-09-19"), fake_video("private", "2026-09-19"),
                           fake_video("fine", "2026-09-18")], details=details):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()
        self.assertEqual(record["last_result"], channel_state.RESULT_COMPLETE)
        self.assertEqual(record["unreadable"], {"members": "members-only", "private": "private"})
        self.assertIn("2 listed videos can't be read", channel_state.coverage_text(record))


class CheckChannelTests(YoutubeBackfillTestCase):
    """T-091: the listing is walked whole; no date order is assumed."""

    def test_an_older_video_listed_first_does_not_hide_the_in_window_videos_below_it(self):
        """Before T-091 the walk stopped at the first new video dated before the window."""
        videos = [fake_video("older", "2026-09-01"), fake_video("in1", "2026-09-18"),
                  fake_video("in2", "2026-09-17")]

        with self.listing(videos) as mock_normalize:
            run(start=date(2026, 9, 10), today=date(2026, 9, 20))

        self.assertEqual([c.args[0]["id"] for c in mock_normalize.call_args_list], ["in1", "in2"])
        self.assertEqual(self.record()["dates"], {"older": "2026-09-01"})

    def test_a_scheduled_upload_at_the_top_with_an_old_date(self):
        """A scheduled video appears newest in the listing but carries the date it was
        uploaded, days before it went public. The in-window videos below it are fetched.
        The scheduled video itself is outside the window and is recorded as a late
        discovery, not fetched: delayed discovery is T-103, not solved here."""
        with self.listing([fake_video("before", "2026-10-07")]):
            run(start=date(2026, 10, 1), today=date(2026, 10, 8))
        listing = [fake_video("scheduled", "2026-10-02"), fake_video("today", "2026-10-09"),
                   fake_video("before", "2026-10-07")]

        with self.listing(listing) as mock_normalize:
            run(start=date(2026, 10, 1), today=date(2026, 10, 9))

        self.assertEqual([c.args[0]["id"] for c in mock_normalize.call_args_list], ["today"])
        record = self.record()
        self.assertEqual(record["late"], [["scheduled", "2026-10-02"]])
        self.assertEqual(record["last_result"], channel_state.RESULT_COMPLETE)

    def test_a_looked_up_video_outside_the_window_is_not_looked_up_again(self):
        videos = [fake_video("in", "2026-09-18"), fake_video("old", "2026-08-01")]
        with self.listing(videos):
            run(start=date(2026, 9, 10), today=date(2026, 9, 20))
        self.details_asked.clear()

        with self.listing(videos):
            run(start=date(2026, 9, 10), today=date(2026, 9, 21))

        self.assertEqual(self.details_asked, [])

    def test_a_broken_listing_page_keeps_the_window(self):
        """With raise_incomplete_data, yt-dlp raises on an incomplete page (KB-041)."""
        with self.listing([], list_error=RuntimeError("Incomplete data received")):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()
        self.assertEqual(record["last_result"], channel_state.RESULT_FAILED)
        self.assertEqual(record["pending_from"], "2026-09-01")

    def test_a_full_listing_that_does_not_reach_the_window_start_records_a_gap(self):
        """Every listed video is in the window, so older ones may have scrolled out of
        the newest N. The listed ones are fetched; the rest is shown as not verified."""
        videos = [fake_video("a", "2026-09-19"), fake_video("b", "2026-09-15"),
                  fake_video("c", "2026-09-12")]
        with patch("vg09.youtube_backfill.LIST_COUNT_PER_CHANNEL", 3), self.listing(videos):
            result = run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        record = self.record()
        self.assertEqual(record["last_result"], channel_state.RESULT_COMPLETE_WITH_GAP)
        self.assertEqual(record["gaps"], [{"from": "2026-09-01", "through": "2026-09-12",
                                           "reason": "older than the newest 3 videos YouTube lists"}])
        self.assertIn("not verified 2026-09-01 to 2026-09-12", channel_state.coverage_text(record))
        self.assertIn(CHANNEL, result.channel_problems)

    def test_a_full_listing_reaching_before_the_window_is_complete(self):
        videos = [fake_video("a", "2026-09-19"), fake_video("b", "2026-09-15"),
                  fake_video("c", "2026-08-30")]
        with patch("vg09.youtube_backfill.LIST_COUNT_PER_CHANNEL", 3), self.listing(videos):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        self.assertEqual(self.record()["last_result"], channel_state.RESULT_COMPLETE)

    def test_a_full_listing_containing_an_earlier_listed_video_is_complete(self):
        """Publication order: anything new is above a video from the last complete listing."""
        with patch("vg09.youtube_backfill.LIST_COUNT_PER_CHANNEL", 3):
            with self.listing([fake_video("x", "2026-09-10"), fake_video("y", "2026-09-09"),
                               fake_video("z", "2026-08-01")]):
                run(start=date(2026, 9, 1), today=date(2026, 9, 10))
            with self.listing([fake_video("n1", "2026-09-12"), fake_video("n2", "2026-09-11"),
                               fake_video("x", "2026-09-10")]):
                run(start=date(2026, 9, 1), today=date(2026, 9, 12))

        record = self.record()
        self.assertEqual(record["last_result"], channel_state.RESULT_COMPLETE)
        self.assertEqual(record["gaps"], [])


class MigrationTests(YoutubeBackfillTestCase):
    """T-091: the shared watermark is not trusted as per-channel coverage."""

    def test_a_channel_under_the_old_watermark_gets_a_full_unverified_check(self):
        write_watermark("youtube", "2026-09-19")
        fake_document("seen", "2026-09-18").write()
        missed = fake_video("missed", "2026-09-05")  # a gap the shared watermark hid

        with self.listing([fake_video("seen", "2026-09-18"), missed]) as mock_normalize:
            run(start=date(2026, 8, 24), today=date(2026, 9, 20))

        self.assertEqual([c.args[0]["id"] for c in mock_normalize.call_args_list], ["missed"])
        state = channel_state.load()
        self.assertEqual(state["migrated_from"]["shared_watermark"], "2026-09-19")
        self.assertFalse(state["migrated_from"]["trusted"])
        self.assertEqual(self.record()["unverified_before"], "2026-08-24")

    def test_migration_is_idempotent_and_keeps_existing_records(self):
        with self.listing([fake_video("a", "2026-09-18")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))
        first = self.record()

        state = channel_state.load()
        self.assertEqual(channel_state.ensure_channels(state, [CHANNEL], date(2026, 9, 15)), [])
        self.assertEqual(state["channels"][CHANNEL], first)

    def test_an_interrupted_state_write_leaves_the_previous_file(self):
        with self.listing([fake_video("a", "2026-09-18")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))
        before = channel_state.state_path().read_text(encoding="utf-8")

        with patch("vg09.channel_state.os.replace", side_effect=OSError("power cut")), \
             self.assertRaises(OSError):
            channel_state.save({"version": channel_state.VERSION, "channels": {}})

        self.assertEqual(channel_state.state_path().read_text(encoding="utf-8"), before)

    def test_a_removed_channel_loses_its_record(self):
        with self.listing([fake_video("a", "2026-09-18")]):
            run(start=date(2026, 9, 1), today=date(2026, 9, 20))

        channel_state.remove(CHANNEL)

        self.assertNotIn(CHANNEL, channel_state.load()["channels"])


class LateUploadRecheckTests(YoutubeBackfillTestCase):
    """T-090: a video that appears after an update, dated on or just before the day of
    the channel's last complete check, is found by the next update. Each `update()` is
    one whole catch-up run; `self.published` is the channel's listing, newest first."""

    def setUp(self):
        super().setUp()
        self.published: list[dict] = []
        self.normalized: list[str] = []

    def publish(self, video_id: str, feed_date: str) -> None:
        self.published.insert(0, fake_video(video_id, feed_date))

    def update(self, today: date):
        with self.listing(list(self.published)) as mock_normalize:
            result = run(start=date(2026, 9, 20), today=today)
        self.normalized += [c.args[0]["id"] for c in mock_normalize.call_args_list]
        return result

    def fetched(self, video_id: str, feed_date: str) -> bool:
        return document.exists("youtube", feed_date, video_id)

    def test_a_video_uploaded_after_the_days_update_is_found_the_next_day(self):
        self.publish("morning", "2026-10-08")
        self.update(date(2026, 10, 8))
        self.publish("evening", "2026-10-08")  # uploaded after that update had run

        self.update(date(2026, 10, 9))

        self.assertTrue(self.fetched("evening", "2026-10-08"))

    def test_a_second_update_on_the_same_day_finds_a_later_upload(self):
        self.update(date(2026, 10, 8))
        self.publish("later", "2026-10-08")

        self.update(date(2026, 10, 8))

        self.assertTrue(self.fetched("later", "2026-10-08"))

    def test_across_midnight_a_video_dated_the_day_before_the_check_is_found(self):
        """yt-dlp's upload_date is a UTC date, and the update's "today" is the local
        date. Sweden runs ahead of UTC, so an update just after local midnight on the 9th
        records 2026-10-09 while a video uploaded minutes later, before UTC midnight,
        is dated the 8th."""
        self.update(date(2026, 10, 9))  # 00:30 local, 22:30 UTC on the 8th
        self.publish("late_utc", "2026-10-08")  # uploaded at 23:00 UTC on the 8th

        self.update(date(2026, 10, 10))

        self.assertTrue(self.fetched("late_utc", "2026-10-08"))

    def test_a_video_dated_after_the_local_date_is_found_the_next_day(self):
        """West of UTC the UTC date runs ahead: a video dated tomorrow is left alone
        today and picked up by the next update."""
        self.publish("ahead", "2026-10-09")
        self.update(date(2026, 10, 8))
        self.assertFalse(self.fetched("ahead", "2026-10-09"))

        self.update(date(2026, 10, 9))

        self.assertTrue(self.fetched("ahead", "2026-10-09"))

    def test_the_recheck_reaches_back_two_days_and_no_further(self):
        """The documented bound: the day of the last complete check and the day before.
        A video that shows up later still, dated earlier, is not fetched. Since T-091 it
        no longer hides the videos listed below it, and it is recorded as a late
        discovery (T-103)."""
        self.publish("seen", "2026-10-09")
        self.update(date(2026, 10, 9))
        self.publish("one_day_back", "2026-10-08")
        self.publish("two_days_back", "2026-10-07")  # listed above, dated older

        self.update(date(2026, 10, 10))

        self.assertTrue(self.fetched("one_day_back", "2026-10-08"))
        self.assertFalse(self.fetched("two_days_back", "2026-10-07"))
        self.assertEqual(self.record()["late"], [["two_days_back", "2026-10-07"]])

    def test_catch_up_after_several_days_off_includes_the_weekend(self):
        """Last update Friday 2026-10-02, next one Thursday 2026-10-08. Videos from the
        weekend and the weekdays in between are fetched, and so is one uploaded late on
        the Friday itself."""
        self.publish("friday_morning", "2026-10-02")
        self.update(date(2026, 10, 2))
        for video_id, day in (("friday_late", "2026-10-02"), ("saturday", "2026-10-03"),
                              ("sunday", "2026-10-04"), ("monday", "2026-10-05"),
                              ("wednesday", "2026-10-07")):
            self.publish(video_id, day)

        self.update(date(2026, 10, 8))

        for video in self.published:
            d = video["upload_date"]
            self.assertTrue(self.fetched(video["id"], f"{d[:4]}-{d[4:6]}-{d[6:]}"), video["id"])
        self.assertEqual(self.record()["checked_through"], "2026-10-08")

    def test_repeated_and_overlapping_updates_fetch_each_video_once(self):
        self.publish("a", "2026-10-07")
        self.publish("b", "2026-10-08")
        for today in (date(2026, 10, 8), date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 9)):
            result = self.update(today)

        self.assertEqual(sorted(self.normalized), ["a", "b"])  # one transcript fetch each
        self.assertEqual(sorted(self.details_asked), ["a", "b"])  # details asked for once
        self.assertEqual(result.already_done, 1)  # the last run's window holds only "b"
        stored = sorted(p.stem for p in document.RAW_DIR.glob("youtube/*/*.json"))
        self.assertEqual(stored, ["a", "b"])  # one file per video id, nothing duplicated


class CatchUpStartTests(unittest.TestCase):
    """T-090: the documented recheck window, in one place for every caller."""

    def test_the_check_day_and_the_day_before_are_rechecked(self):
        from vg09.youtube_backfill import RECHECK_DAYS, catch_up_start

        self.assertEqual(RECHECK_DAYS, 2)
        self.assertEqual(catch_up_start("2026-10-09"), date(2026, 10, 8))

    def test_month_and_year_boundaries(self):
        from vg09.youtube_backfill import catch_up_start

        self.assertEqual(catch_up_start("2026-11-01"), date(2026, 10, 31))
        self.assertEqual(catch_up_start("2027-01-01"), date(2026, 12, 31))


class ListVideoIdsTests(unittest.TestCase):
    """T-091 (KB-041): a broken listing page raises instead of shortening the list."""

    def test_the_listing_asks_yt_dlp_to_raise_on_incomplete_data(self):
        from vg09 import youtube

        with patch("vg09.youtube.yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {
                "entries": [{"id": "a"}, {"id": "b"}]}
            ids = youtube.list_video_ids("https://example.com/c", 50)

        opts = mock_ydl.call_args.args[0]
        self.assertEqual(opts["extractor_args"], {"youtube": {"raise_incomplete_data": ["true"]}})
        self.assertEqual(ids, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
