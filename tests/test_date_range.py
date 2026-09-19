"""Unit tests for vg09.date_range (T-021).

The real-question test (against docs/eval-questions.md's 15 actual questions, not
retyped examples) lives in scripts/t021_test_date_extraction_against_eval_questions.py,
since it reads a doc file rather than exercising pure logic - this file covers the
extraction logic itself, including edge cases the 15 real questions don't happen to
hit (calendar-month day-clamping, the absolute-date year rollback, digit vs. spelled-out
numbers).
"""

from __future__ import annotations

import unittest
from datetime import date

from vg09.date_range import extract_date_range, resolve_date_range


class RelativeWeeksTests(unittest.TestCase):
    def test_senaste_veckan_is_a_7_day_window_ending_today(self):
        self.assertEqual(
            extract_date_range("Vad har hänt senaste veckan?", date(2026, 9, 16)),
            (date(2026, 9, 10), date(2026, 9, 16)),
        )

    def test_forra_veckan_is_the_same_7_day_window(self):
        self.assertEqual(
            extract_date_range("Vad hände förra veckan?", date(2026, 9, 16)),
            (date(2026, 9, 10), date(2026, 9, 16)),
        )

    def test_senaste_tva_veckorna_spelled_out_number(self):
        self.assertEqual(
            extract_date_range("de senaste två veckorna", date(2026, 9, 16)),
            (date(2026, 9, 3), date(2026, 9, 16)),
        )

    def test_senaste_n_veckorna_digit_number(self):
        self.assertEqual(
            extract_date_range("de senaste 3 veckorna", date(2026, 9, 16)),
            (date(2026, 8, 27), date(2026, 9, 16)),
        )

    def test_bare_plural_veckorna_with_no_number_is_deliberately_unparseable(self):
        """"de senaste veckorna" (plural, no number) is genuinely ambiguous - this
        module refuses to guess a count rather than silently picking one."""
        self.assertIsNone(extract_date_range("de senaste veckorna", date(2026, 9, 16)))


class RelativeDaysAndMonthsTests(unittest.TestCase):
    def test_senaste_n_dagarna(self):
        self.assertEqual(
            extract_date_range("de senaste 5 dagarna", date(2026, 9, 16)),
            (date(2026, 9, 12), date(2026, 9, 16)),
        )

    def test_senaste_manaden_is_one_calendar_month_not_30_days(self):
        """Matches docs/eval-questions.md's already-written convention exactly:
        2026-08-16, a calendar month back, not today-30 (2026-08-17)."""
        self.assertEqual(
            extract_date_range("den senaste månaden", date(2026, 9, 16)),
            (date(2026, 8, 16), date(2026, 9, 16)),
        )

    def test_senaste_n_manaderna_day_clamped_for_a_shorter_target_month(self):
        # Mar 31 minus 1 month has no Feb 31 - clamps to the last real day of Feb.
        self.assertEqual(
            extract_date_range("de senaste 1 manaderna", date(2026, 3, 31)),
            (date(2026, 2, 28), date(2026, 3, 31)),
        )

    def test_senaste_n_manaderna_across_a_year_boundary(self):
        self.assertEqual(
            extract_date_range("de senaste 2 manaderna", date(2026, 1, 15)),
            (date(2025, 11, 15), date(2026, 1, 15)),
        )


class AbsoluteDateTests(unittest.TestCase):
    def test_den_d_manad_resolves_to_this_year_when_not_in_the_future(self):
        self.assertEqual(
            extract_date_range("Vad är nytt den 16 september?", date(2026, 9, 16)),
            (date(2026, 9, 16), date(2026, 9, 16)),
        )

    def test_den_d_manad_rolls_back_a_year_when_that_date_is_still_in_the_future(self):
        # "today" is 2026-03-01; "den 16 september" this year hasn't happened yet,
        # so it must mean last September, not next.
        self.assertEqual(
            extract_date_range("Vad hände den 16 september?", date(2026, 3, 1)),
            (date(2025, 9, 16), date(2025, 9, 16)),
        )

    def test_den_d_manad_invalid_calendar_date_is_not_guessed(self):
        self.assertIsNone(extract_date_range("den 31 februari", date(2026, 9, 16)))


class NoDiscernibleRangeTests(unittest.TestCase):
    def test_no_time_phrase_at_all_returns_none(self):
        self.assertIsNone(extract_date_range("Nämns LEGO i någon artikel?", date(2026, 9, 16)))

    def test_a_ranking_word_without_a_window_returns_none(self):
        """"det senaste"/"de två senaste" ask for recency ranking, not a bounded
        window - conflating the two would silently invent a range nobody asked for."""
        self.assertIsNone(
            extract_date_range("Vad är det absolut senaste inom X?", date(2026, 9, 16))
        )


class ResolveDateRangeTests(unittest.TestCase):
    """T-021's other acceptance criterion: a manual override (the UI's date picker,
    wired in by T-025) always wins over extraction - never the reverse."""

    def test_manual_override_wins_even_when_the_question_has_its_own_range(self):
        override = (date(2020, 1, 1), date(2020, 1, 31))
        result = resolve_date_range("senaste veckan", date(2026, 9, 16), manual_override=override)
        self.assertEqual(result, override)

    def test_falls_back_to_extraction_when_no_override_is_set(self):
        result = resolve_date_range("senaste veckan", date(2026, 9, 16), manual_override=None)
        self.assertEqual(result, (date(2026, 9, 10), date(2026, 9, 16)))

    def test_none_and_none_means_unfiltered_not_an_error(self):
        result = resolve_date_range("Nämns LEGO?", date(2026, 9, 16), manual_override=None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
