"""Unit tests for vg09.ui_helpers (T-025)."""

from __future__ import annotations

import unittest
from datetime import date

from vg09.ui_helpers import describe_retrieval_mode


class DescribeRetrievalModeTests(unittest.TestCase):
    def test_manual_override_wins_even_with_an_interpreted_window_present(self):
        override = (date(2020, 1, 1), date(2020, 1, 31))
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=override)
        self.assertIn("manuellt", result)
        self.assertIn("2020-01-01", result)

    def test_interpreted_window_shown_when_no_override(self):
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=None)
        self.assertIn("tolkat", result)
        self.assertIn("2026-09-10", result)
        self.assertIn("2026-09-16", result)

    def test_ranking_mode_shown_when_no_window_and_no_override(self):
        result = describe_retrieval_mode(None, ranking=True, manual_override=None)
        self.assertIn("rankning", result)

    def test_unfiltered_when_nothing_fired(self):
        result = describe_retrieval_mode(None, ranking=False, manual_override=None)
        self.assertIn("Inget datumfilter", result)


if __name__ == "__main__":
    unittest.main()
