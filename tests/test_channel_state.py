"""Unit tests for vg09.channel_state (T-091): the coverage line shown on Sources."""

from __future__ import annotations

import unittest
from datetime import date

from vg09 import channel_state


def record(**fields) -> dict:
    base = channel_state.new_record(date(2026, 9, 12))
    base.update(fields)
    return base


class CoverageTextTests(unittest.TestCase):
    def test_a_channel_never_checked_says_so(self):
        self.assertEqual(channel_state.coverage_text(None), "Not checked yet")
        self.assertEqual(channel_state.coverage_text(record()), "Not checked yet")

    def test_a_complete_channel_says_how_far_and_what_was_never_checked(self):
        text = channel_state.coverage_text(record(
            last_attempt="2026-10-09T20:00:00", last_result="complete",
            checked_through="2026-10-09", pending_from=None))
        self.assertEqual(text, "Checked through 2026-10-09; nothing before 2026-09-12 checked")

    def test_a_failed_check_is_never_shown_as_complete(self):
        text = channel_state.coverage_text(record(
            last_attempt="2026-10-10T08:00:00", last_result="failed",
            last_error="listing failed: down", checked_through="2026-10-09",
            pending_from="2026-10-08"))
        self.assertIn("last check failed (listing failed: down); retrying from 2026-10-08", text)

    def test_a_first_check_that_failed_has_no_checked_date(self):
        text = channel_state.coverage_text(record(
            last_attempt="2026-10-10T08:00:00", last_result="failed", last_error="down"))
        self.assertTrue(text.startswith("Not yet checked completely"))

    def test_a_gap_is_listed_as_not_verified(self):
        text = channel_state.coverage_text(record(
            last_attempt="2026-10-09T20:00:00", last_result="complete_with_gap",
            checked_through="2026-10-09", pending_from=None,
            gaps=[{"from": "2026-09-12", "through": "2026-09-20",
                   "reason": "older than the newest 50 videos YouTube lists"}]))
        self.assertIn("not verified 2026-09-12 to 2026-09-20", text)


class WindowStartTests(unittest.TestCase):
    def test_a_kept_interval_wins_over_the_recheck_window(self):
        self.assertEqual(channel_state.window_start(record(
            checked_through="2026-10-09", pending_from="2026-10-01")), date(2026, 10, 1))

    def test_without_a_kept_interval_the_recheck_window_applies(self):
        self.assertEqual(channel_state.window_start(record(
            checked_through="2026-10-09", pending_from=None)), date(2026, 10, 8))

    def test_a_failure_never_moves_a_kept_interval_later(self):
        r = record(checked_through="2026-10-09", pending_from="2026-10-01")
        channel_state.record_failure(r, date(2026, 10, 5), channel_state.RESULT_FAILED, "down")
        self.assertEqual(r["pending_from"], "2026-10-01")


if __name__ == "__main__":
    unittest.main()
