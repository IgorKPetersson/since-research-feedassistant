"""Unit tests for T-093 (D-022): the reference date, manual ranges and the date notes.

Every clock here is fixed: `now` is passed as an aware datetime. Stockholm is UTC+2 in
summer (CEST) and UTC+1 in winter (CET); in 2026 summer time starts 29 March at 01:00 UTC
and ends 25 October at 01:00 UTC.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

from vg09 import reference_date, sources
from vg09.date_range import manual_range_error, resolve_date_range
from vg09.ui_helpers import dates_note, describe_retrieval_mode, past_newest_note, staleness_note


def utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


class ReferenceDateTests(unittest.TestCase):
    def day(self, *instant, tz="Europe/Stockholm") -> date:
        return reference_date.today(tz, now=utc(*instant))

    def test_just_after_local_midnight_it_is_already_the_next_day(self):
        # 22:30 UTC on the 8th is 00:30 on the 9th in Stockholm (summer time).
        self.assertEqual(self.day(2026, 10, 8, 22, 30), date(2026, 10, 9))
        self.assertEqual(self.day(2026, 10, 8, 21, 59), date(2026, 10, 8))

    def test_midnight_moves_by_an_hour_when_summer_time_ends(self):
        # Before 25 Oct the local day starts at 22:00 UTC, after it at 23:00 UTC.
        self.assertEqual(self.day(2026, 10, 24, 21, 59), date(2026, 10, 24))
        self.assertEqual(self.day(2026, 10, 24, 22, 0), date(2026, 10, 25))
        self.assertEqual(self.day(2026, 10, 25, 22, 59), date(2026, 10, 25))
        self.assertEqual(self.day(2026, 10, 25, 23, 0), date(2026, 10, 26))

    def test_midnight_moves_by_an_hour_when_summer_time_starts(self):
        self.assertEqual(self.day(2026, 3, 28, 22, 59), date(2026, 3, 28))
        self.assertEqual(self.day(2026, 3, 28, 23, 0), date(2026, 3, 29))
        self.assertEqual(self.day(2026, 3, 29, 21, 59), date(2026, 3, 29))
        self.assertEqual(self.day(2026, 3, 29, 22, 0), date(2026, 3, 30))

    def test_another_time_zone_can_be_on_a_different_day(self):
        instant = (2026, 10, 9, 2, 0)  # 04:00 in Stockholm, 22:00 the day before in New York
        self.assertEqual(self.day(*instant), date(2026, 10, 9))
        self.assertEqual(self.day(*instant, tz="America/New_York"), date(2026, 10, 8))

    def test_a_clock_without_a_time_zone_is_refused(self):
        with self.assertRaises(ValueError):
            reference_date.today("Europe/Stockholm", now=datetime(2026, 10, 9, 12, 0))

    def test_an_unknown_time_zone_says_how_to_fix_it(self):
        with self.assertRaises(reference_date.TimezoneError) as caught:
            reference_date.today("Europe/Stockhom", now=utc(2026, 10, 9, 12, 0))
        self.assertIn("data/sources.json", str(caught.exception))

    def test_the_reference_date_does_not_depend_on_the_index(self):
        """Empty or stale: the store is never asked."""
        with patch("vg09.store.latest_feed_date", side_effect=AssertionError("store read")):
            self.assertEqual(self.day(2026, 10, 9, 12, 0), date(2026, 10, 9))


class TimezoneSettingTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "sources.json"
        patcher = patch("vg09.sources.SOURCES_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_default_is_europe_stockholm(self):
        self.assertEqual(sources.load().timezone, "Europe/Stockholm")
        self.assertEqual(reference_date.DEFAULT_TIMEZONE, "Europe/Stockholm")

    def test_a_file_written_before_t093_reads_as_the_default(self):
        self.path.write_text(json.dumps({"hf": {"enabled": True, "backfill_weeks": 8},
                                         "youtube": {"backfill_weeks": 4, "channels": []}}),
                             encoding="utf-8")
        self.assertEqual(sources.load().timezone, "Europe/Stockholm")

    def test_a_saved_time_zone_is_read_back_and_used(self):
        sources.save(sources.Sources(timezone="America/New_York", channels={}))
        self.assertEqual(sources.load().timezone, "America/New_York")
        self.assertEqual(reference_date.today(now=utc(2026, 10, 9, 2, 0)), date(2026, 10, 8))


class ManualRangeTests(unittest.TestCase):
    def test_a_reversed_range_is_rejected(self):
        self.assertIn("after the end date",
                      manual_range_error(date(2026, 10, 9), date(2026, 10, 1)))
        with self.assertRaises(ValueError):
            resolve_date_range("anything", date(2026, 10, 9),
                               manual_override=(date(2026, 10, 9), date(2026, 10, 1)))

    def test_a_missing_end_is_rejected(self):
        self.assertIsNotNone(manual_range_error(date(2026, 10, 9), None))

    def test_a_single_day_and_a_future_end_are_allowed(self):
        self.assertIsNone(manual_range_error(date(2026, 10, 9), date(2026, 10, 9)))
        self.assertIsNone(manual_range_error(date(2026, 10, 9), date(2026, 12, 31)))

    def test_the_manual_range_wins_over_a_period_named_in_the_question(self):
        manual = (date(2026, 9, 1), date(2026, 9, 10))
        self.assertEqual(resolve_date_range("What happened in the last 7 days?",
                                            date(2026, 10, 9), manual_override=manual), manual)

    def test_the_overridden_period_is_shown_as_not_used(self):
        manual = (date(2026, 9, 1), date(2026, 9, 10))
        interpreted = (date(2026, 10, 3), date(2026, 10, 9))
        text = describe_retrieval_mode(interpreted, False, manual)
        self.assertIn("manually set): Tue 2026-09-01 – Thu 2026-09-10 (10 days)", text)
        self.assertIn("the question's own period (Sat 2026-10-03 – Fri 2026-10-09 (7 days)) is not used",
                      text)
        self.assertNotIn("not used", describe_retrieval_mode(None, False, manual))


class RelativeDatesFromTheReferenceTests(unittest.TestCase):
    """Existing phrases only (new phrases are T-094): they count from the reference
    date, not from the newest source."""

    def test_last_7_days_on_a_stale_index_is_the_last_7_calendar_days(self):
        self.assertEqual(resolve_date_range("What happened in the last 7 days?", date(2026, 10, 12)),
                         (date(2026, 10, 6), date(2026, 10, 12)))

    def test_yesterday_on_a_monday_is_sunday(self):
        self.assertEqual(resolve_date_range("What came out yesterday?", date(2026, 10, 12)),
                         (date(2026, 10, 11), date(2026, 10, 11)))


class DateNotesTests(unittest.TestCase):
    def test_the_three_dates_are_shown_apart(self):
        text = dates_note(date(2026, 10, 12), "Europe/Stockholm", date(2026, 9, 18),
                          date(2026, 9, 20), None)
        self.assertEqual(text, "Today: Mon 2026-10-12 (Europe/Stockholm) · Newest source: "
                               "2026-09-18 · Checked: papers through 2026-09-20, videos not complete")

    def test_an_empty_index_has_no_newest_source(self):
        self.assertIn("Newest source: none", dates_note(date(2026, 10, 12), "Europe/Stockholm",
                                                        None, None, None))

    def test_a_period_partly_past_the_newest_source_says_so(self):
        note = past_newest_note((date(2026, 10, 3), date(2026, 10, 9)), date(2026, 10, 7))
        self.assertIn("runs to 2026-10-09", note)
        self.assertIn("newest source in the index is from 2026-10-07", note)

    def test_a_period_entirely_after_the_newest_source_says_so(self):
        note = past_newest_note((date(2026, 10, 6), date(2026, 10, 12)), date(2026, 9, 18))
        self.assertIn("whole period asked about (2026-10-06 – 2026-10-12) is after", note)

    def test_no_note_when_the_index_covers_the_period_or_there_is_no_period(self):
        self.assertIsNone(past_newest_note((date(2026, 10, 1), date(2026, 10, 7)), date(2026, 10, 7)))
        self.assertIsNone(past_newest_note(None, date(2026, 10, 7)))
        self.assertIsNone(past_newest_note((date(2026, 10, 1), date(2026, 10, 7)), None))

    def test_staleness_is_measured_from_the_reference_date(self):
        self.assertEqual(staleness_note(date(2026, 9, 18), date(2026, 10, 12)), "24 days old")


class CoverageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = patch("vg09.watermark.WATERMARK_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_papers_are_checked_through_the_day_the_last_sync_ran(self):
        from vg09 import coverage
        from vg09.watermark import write_watermark

        self.assertIsNone(coverage.papers_checked_through())
        write_watermark("hf", "2026-10-07")  # written by a sync on the 9th (REOPEN_DAYS = 2)
        self.assertEqual(coverage.papers_checked_through(), date(2026, 10, 9))

    def test_videos_are_checked_through_the_least_checked_channel(self):
        from vg09 import channel_state, coverage

        channel_state.save({"version": channel_state.VERSION, "channels": {
            "a": {"checked_through": "2026-10-09"}, "b": {"checked_through": "2026-10-07"},
            "c": {"checked_through": None}}})
        self.assertEqual(coverage.videos_checked_through(["a", "b"]), date(2026, 10, 7))
        self.assertIsNone(coverage.videos_checked_through(["a", "c"]))
        self.assertIsNone(coverage.videos_checked_through(["a", "missing"]))
        self.assertIsNone(coverage.videos_checked_through([]))


if __name__ == "__main__":
    unittest.main()
