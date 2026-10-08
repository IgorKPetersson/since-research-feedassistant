"""Unit tests for vg09.date_range (T-021/T-043).

The real-question tests (against docs/eval-questions.md's 15 actual Swedish questions,
and T-043's real English translations of the same 15, not retyped examples) live in
scripts/t021_test_date_extraction_against_eval_questions.py and
scripts/t043_test_english_date_extraction.py, since they read/embed the real questions
rather than exercising pure logic in isolation - this file covers the extraction logic
itself, including edge cases the 15 real questions don't happen to hit (calendar-month
day-clamping, the absolute-date year rollback, digit vs. spelled-out numbers) for both
languages.
"""

from __future__ import annotations

import unittest
from datetime import date

from vg09.date_range import detect_recency_ranking, extract_date_range, resolve_date_range


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


class EnglishRelativeWeeksTests(unittest.TestCase):
    """T-043: same rules as RelativeWeeksTests above, English phrasing."""

    def test_last_week_is_a_7_day_window_ending_today(self):
        self.assertEqual(
            extract_date_range("What happened last week?", date(2026, 9, 16)),
            (date(2026, 9, 10), date(2026, 9, 16)),
        )

    def test_this_week_is_the_same_7_day_window(self):
        self.assertEqual(
            extract_date_range("What's new this week?", date(2026, 9, 16)),
            (date(2026, 9, 10), date(2026, 9, 16)),
        )

    def test_the_last_two_weeks_spelled_out_number(self):
        self.assertEqual(
            extract_date_range("in the last two weeks", date(2026, 9, 16)),
            (date(2026, 9, 3), date(2026, 9, 16)),
        )

    def test_the_last_n_weeks_digit_number(self):
        self.assertEqual(
            extract_date_range("in the last 3 weeks", date(2026, 9, 16)),
            (date(2026, 8, 27), date(2026, 9, 16)),
        )

    def test_bare_plural_weeks_with_no_number_is_deliberately_unparseable(self):
        """"recent weeks" (plural, no number) is genuinely ambiguous - same rule as
        the Swedish "de senaste veckorna" case: no guessed count."""
        self.assertIsNone(extract_date_range("mentioned in recent weeks", date(2026, 9, 16)))


class EnglishRelativeDaysAndMonthsTests(unittest.TestCase):
    """T-043: same rules as RelativeDaysAndMonthsTests above, English phrasing."""

    def test_the_last_n_days(self):
        self.assertEqual(
            extract_date_range("in the last 5 days", date(2026, 9, 16)),
            (date(2026, 9, 12), date(2026, 9, 16)),
        )

    def test_last_month_is_one_calendar_month_not_30_days(self):
        """Same convention as Swedish "senaste manaden": 2026-08-16, a calendar
        month back, not today-30 (2026-08-17)."""
        self.assertEqual(
            extract_date_range("in the last month", date(2026, 9, 16)),
            (date(2026, 8, 16), date(2026, 9, 16)),
        )

    def test_this_past_month_is_the_same_calendar_month_window(self):
        self.assertEqual(
            extract_date_range("this past month", date(2026, 9, 16)),
            (date(2026, 8, 16), date(2026, 9, 16)),
        )

    def test_the_last_n_months_day_clamped_for_a_shorter_target_month(self):
        # Mar 31 minus 1 month has no Feb 31 - clamps to the last real day of Feb.
        self.assertEqual(
            extract_date_range("in the last 1 months", date(2026, 3, 31)),
            (date(2026, 2, 28), date(2026, 3, 31)),
        )

    def test_the_last_n_months_across_a_year_boundary(self):
        self.assertEqual(
            extract_date_range("in the last 2 months", date(2026, 1, 15)),
            (date(2025, 11, 15), date(2026, 1, 15)),
        )


class EnglishAbsoluteDateTests(unittest.TestCase):
    """T-043: same rules as AbsoluteDateTests above, both real English word orders."""

    def test_month_then_day_resolves_to_this_year_when_not_in_the_future(self):
        self.assertEqual(
            extract_date_range("What's new on September 16th?", date(2026, 9, 16)),
            (date(2026, 9, 16), date(2026, 9, 16)),
        )

    def test_day_of_month_word_order_also_resolves(self):
        self.assertEqual(
            extract_date_range("What happened on the 16th of September?", date(2026, 9, 16)),
            (date(2026, 9, 16), date(2026, 9, 16)),
        )

    def test_rolls_back_a_year_when_that_date_is_still_in_the_future(self):
        self.assertEqual(
            extract_date_range("What happened on September 16?", date(2026, 3, 1)),
            (date(2025, 9, 16), date(2025, 9, 16)),
        )

    def test_invalid_calendar_date_is_not_guessed(self):
        self.assertIsNone(extract_date_range("February 31", date(2026, 9, 16)))


class EnglishTodayTests(unittest.TestCase):
    """T-043: "today" - not exercised by any of the 15 real questions (Swedish or
    English), but named explicitly in my own instruction for this ticket."""

    def test_today_resolves_to_a_single_day_window(self):
        self.assertEqual(
            extract_date_range("What's new today?", date(2026, 9, 16)),
            (date(2026, 9, 16), date(2026, 9, 16)),
        )


class EnglishNoDiscernibleRangeTests(unittest.TestCase):
    def test_no_time_phrase_at_all_returns_none(self):
        self.assertIsNone(extract_date_range("Is LEGO mentioned in any article?", date(2026, 9, 16)))

    def test_a_ranking_word_without_a_window_returns_none(self):
        """"the latest"/"the two latest" ask for recency ranking, not a bounded
        window - same rule as the Swedish case."""
        self.assertIsNone(
            extract_date_range("What is the absolute latest in X?", date(2026, 9, 16))
        )


MONDAY = date(2026, 10, 5)  # T-066: the probe run's real date, a Monday


class T066PhrasesFromTheProbeRunTests(unittest.TestCase):
    """T-066: every phrase here was ignored, or misread, by the 2026-10-05 probe run."""

    def check(self, question: str, start: date, end: date, today: date = MONDAY):
        self.assertEqual(extract_date_range(question, today), (start, end), question)

    def test_between_two_dates_is_the_whole_span_not_the_first_day(self):
        sep = lambda d: date(2026, 9, d)  # noqa: E731
        for q in ("What happened in AI between September 20 and September 25?",
                  "What happened between September 20 and 25?",
                  "What happened from September 20 to September 25?",
                  "What happened September 20-25?",
                  "What happened Sept 20 - 25?",
                  "Vad hände mellan den 20 och den 25 september?",
                  "Vad hände mellan den 20 september och den 25 september?"):
            self.check(q, sep(20), sep(25))

    def test_yesterday(self):
        for q in ("What were the most important papers yesterday?", "Vad hände igår?",
                  "Vad hände i går?"):
            self.check(q, date(2026, 10, 4), date(2026, 10, 4))

    def test_a_weekday_is_the_most_recent_one(self):
        for q in ("What was new on Friday?", "What was new last Friday?",
                  "What was new Friday?", "Vad var nytt i fredags?"):
            self.check(q, date(2026, 10, 2), date(2026, 10, 2))

    def test_the_weekday_of_today_is_today_unless_it_says_last(self):
        self.check("What came out on Monday?", MONDAY, MONDAY)
        self.check("What came out last Monday?", date(2026, 9, 28), date(2026, 9, 28))

    def test_since_a_weekday(self):
        self.check("Did anyone mention Gemini 4 since Friday?", date(2026, 10, 2), MONDAY)
        self.check("Har någon nämnt Gemini 4 sedan i fredags?", date(2026, 10, 2), MONDAY)
        self.check("Any news since Monday?", MONDAY, MONDAY)

    def test_since_a_month_or_a_date(self):
        self.check("How has reasoning in small models progressed since September?",
                   date(2026, 9, 1), MONDAY)
        self.check("Vad har hänt sedan september?", date(2026, 9, 1), MONDAY)
        self.check("What changed since September 20?", date(2026, 9, 20), MONDAY)
        self.check("What changed since yesterday?", date(2026, 10, 4), MONDAY)

    def test_since_a_month_still_ahead_this_year_means_last_year(self):
        self.check("What happened since November?", date(2025, 11, 1), MONDAY)

    def test_in_a_month_is_that_whole_month(self):
        self.check("What came out in August?", date(2026, 8, 1), date(2026, 8, 31))
        self.check("Vad kom ut i augusti?", date(2026, 8, 1), date(2026, 8, 31))
        self.check("What happened during September?", date(2026, 9, 1), date(2026, 9, 30))

    def test_this_month_runs_from_its_first_day(self):
        self.check("What came out this month?", date(2026, 10, 1), MONDAY)

    def test_a_single_date_still_works(self):
        self.check("What happened on September 16?", date(2026, 9, 16), date(2026, 9, 16))


class T079PhrasesFromTheHumansTestTests(unittest.TestCase):
    """T-079: my 2026-10-05 test asked "over the 5 days" and got no date filter."""

    TODAY = date(2026, 10, 5)

    def check(self, question: str, start: date) -> None:
        self.assertEqual(extract_date_range(question, self.TODAY), (start, self.TODAY), question)

    def test_the_n_days_after_over_during_in_within(self):
        for q in ("How has research on coding agents developed over the 5 days?",
                  "What happened during the 5 days?",
                  "Anything new within the five days?",
                  "What came up in the previous 5 days?"):
            self.check(q, date(2026, 10, 1))
        self.check("What happened over the 2 weeks?", date(2026, 9, 22))

    def test_swedish_number_before_senaste(self):
        self.check("Vad har hänt de 5 senaste dagarna?", date(2026, 10, 1))
        self.check("Vad hände de två senaste veckorna?", date(2026, 9, 22))

    def test_the_n_days_before_or_after_something_is_not_a_recent_window(self):
        self.assertIsNone(extract_date_range("What happened in the 5 days before the launch?", self.TODAY))


class T084SinceNDaysTests(unittest.TestCase):
    """T-084: "since 3 days" got no date filter on 2026-10-08. Like "since yesterday",
    the start day is included: N days back, up to today."""

    TODAY = date(2026, 10, 8)

    def check(self, question: str, start: date) -> None:
        self.assertEqual(extract_date_range(question, self.TODAY), (start, self.TODAY), question)

    def test_since_n_days(self):
        for q in ("What is new in AI since 3 days?", "What is new in AI since 3 days ago?",
                  "What is new since three days?", "Vad har hänt sedan 3 dagar?"):
            self.check(q, date(2026, 10, 5))

    def test_any_number(self):
        self.check("What is new since 9 days?", date(2026, 9, 29))
        self.check("What is new since 1 day ago?", date(2026, 10, 7))

    def test_since_n_weeks(self):
        self.check("What is new since 2 weeks ago?", date(2026, 9, 24))
        self.check("Vad har hänt sedan två veckor?", date(2026, 9, 24))


class DetectRecencyRankingTests(unittest.TestCase):
    """T-022: real ranking questions from docs/eval-questions.md (F01/F03/F06) vs.
    real window questions that also contain the word "senaste" (F02/F04/F05/F07/F11/
    F13/F15) - the two must not be confused, since they trigger different retrieval
    mechanisms (sort vs. filter, docs/DESIGN.md)."""

    def test_f01_two_latest_news_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking(
            "I området Recursive self-improvement, vad är de två senaste nyheterna "
            "och vad handlar de om?"
        ))

    def test_f03_absolute_latest_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking(
            "Vad är det absolut  senaste inom Video genereation och är det "
            "hårdvaru- eller mjukvarurelaterat?"
        ))

    def test_f06_the_latest_within_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking(
            "Vad är det senaste inom benchmarking av coding agents?"
        ))

    def test_f04_last_week_is_a_window_question_not_ranking(self):
        self.assertFalse(detect_recency_ranking(
            "Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta."
        ))

    def test_f05_last_two_weeks_is_a_window_question_not_ranking(self):
        self.assertFalse(detect_recency_ranking("Har NeoHorse nämnts de senaste två veckorna?"))

    def test_f09_bare_plural_weeks_is_neither_ranking_nor_a_window(self):
        """"de senaste veckorna" (F09) is a plain existence-check with an ambiguous
        window phrase, not a ranking question - detect_recency_ranking and
        extract_date_range both correctly return the "no signal" result for it."""
        self.assertFalse(detect_recency_ranking("Har AutoDev nämnts de senaste veckorna?"))

    def test_no_senaste_at_all_is_not_a_ranking_question(self):
        self.assertFalse(detect_recency_ranking("Nämns LEGO i någon artikel?"))

    # T-043: English - the real F01/F03/F06/F02/F05/F09 translations, mirroring the
    # Swedish cases above one-for-one.
    def test_english_f01_two_latest_news_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking(
            "In the area of recursive self-improvement, what are the two latest "
            "news items and what are they about?"
        ))

    def test_english_f03_absolute_latest_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking(
            "What is the absolute latest in video generation, and is it hardware- "
            "or software-related?"
        ))

    def test_english_f06_the_latest_within_is_a_ranking_question(self):
        self.assertTrue(detect_recency_ranking("What is the latest in benchmarking of coding agents?"))

    def test_english_f04_last_week_is_a_window_question_not_ranking(self):
        self.assertFalse(detect_recency_ranking(
            "In the last week, what has been said about coding agents? Please summarize."
        ))

    def test_english_f05_last_two_weeks_is_a_window_question_not_ranking(self):
        self.assertFalse(detect_recency_ranking("Has NeoHorse been mentioned in the last two weeks?"))

    def test_english_f09_bare_plural_weeks_is_neither_ranking_nor_a_window(self):
        self.assertFalse(detect_recency_ranking("Has AutoDev been mentioned in recent weeks?"))

    def test_no_latest_or_most_recent_at_all_is_not_a_ranking_question(self):
        self.assertFalse(detect_recency_ranking("Is LEGO mentioned in any article?"))

    def test_most_recent_is_also_a_ranking_phrase(self):
        self.assertTrue(detect_recency_ranking("What is the most recent paper on X?"))


if __name__ == "__main__":
    unittest.main()
