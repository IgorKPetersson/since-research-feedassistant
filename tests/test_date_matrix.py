"""T-094: the documented date-phrase matrix, English and Swedish, at fixed reference dates.

Each case is (question, reference date, expected). Expected is a (start, end) interval,
both ends included; ASK when the app must ask for a period instead of searching
(`unresolved_time_phrase()`); RANK for a "latest" ranking; NONE for an ordinary question
that searches every date, as before. `docs/date-phrases.md` lists the same cases; a test
below keeps the two in step.
"""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

from vg09.date_range import detect_recency_ranking, extract_date_range, unresolved_time_phrase

FRI = date(2026, 10, 9)   # the main reference date, a Friday
MON = date(2026, 10, 12)  # a Monday
JAN = date(2026, 1, 5)    # just after a year boundary
MAR31 = date(2026, 3, 31) # a month end
LEAP = date(2028, 3, 1)   # the day after a leap day
ASK, RANK, NONE = "ASK", "RANK", "NONE"


def d(y, m, day):
    return date(y, m, day)


def span(a, b):
    return (a, b)


MATRIX = [
    # Single days
    ("What came out today?", FRI, span(FRI, FRI)),
    ("Vad kom idag?", FRI, span(FRI, FRI)),
    ("What was published yesterday?", FRI, span(d(2026, 10, 8), d(2026, 10, 8))),
    ("Vad publicerades igår?", FRI, span(d(2026, 10, 8), d(2026, 10, 8))),
    ("What came out the day before yesterday?", FRI, span(d(2026, 10, 7), d(2026, 10, 7))),
    ("Vad kom i förrgår?", FRI, span(d(2026, 10, 7), d(2026, 10, 7))),
    ("What was posted two days ago?", FRI, span(d(2026, 10, 7), d(2026, 10, 7))),
    ("Vad kom för tre dagar sedan?", FRI, span(d(2026, 10, 6), d(2026, 10, 6))),
    ("What came out on Friday?", FRI, span(FRI, FRI)),
    ("What came out last Friday?", FRI, span(d(2026, 10, 2), d(2026, 10, 2))),
    ("Vad kom i fredags?", FRI, span(d(2026, 10, 2), d(2026, 10, 2))),
    ("Papers from October 5", FRI, span(d(2026, 10, 5), d(2026, 10, 5))),
    ("Vad kom den 5 oktober?", FRI, span(d(2026, 10, 5), d(2026, 10, 5))),
    ("What was published on 2026-10-05?", FRI, span(d(2026, 10, 5), d(2026, 10, 5))),
    ("What was published on October 5, 2025?", FRI, span(d(2025, 10, 5), d(2025, 10, 5))),
    ("What came out on December 24?", FRI, span(d(2025, 12, 24), d(2025, 12, 24))),
    ("What came out on February 29?", FRI, ASK),
    ("What came out on February 29?", LEAP, span(d(2028, 2, 29), d(2028, 2, 29))),
    ("What came out on 2026-02-30?", FRI, ASK),
    # Rolling periods, ending on the reference date
    ("What happened in the last 7 days?", FRI, span(d(2026, 10, 3), FRI)),
    ("Vad hände de senaste 5 dagarna?", FRI, span(d(2026, 10, 5), FRI)),
    ("How did agents develop over the past three weeks?", FRI, span(d(2026, 9, 19), FRI)),
    ("Vad hände de senaste två veckorna?", FRI, span(d(2026, 9, 26), FRI)),
    ("What happened in the last week?", FRI, span(d(2026, 10, 3), FRI)),
    ("What happened over the past week?", FRI, span(d(2026, 10, 3), FRI)),
    ("Vad hände senaste veckan?", FRI, span(d(2026, 10, 3), FRI)),
    ("What happened in the last month?", FRI, span(d(2026, 9, 9), FRI)),
    ("What happened over the past month?", FRI, span(d(2026, 9, 9), FRI)),
    ("Vad hände senaste månaden?", MAR31, span(d(2026, 2, 28), MAR31)),
    ("What happened over the past year?", FRI, span(d(2025, 10, 9), FRI)),
    ("What happened in the last 7 days?", d(2026, 1, 3), span(d(2025, 12, 28), d(2026, 1, 3))),
    # Since-periods, from a start date through the reference date
    ("What is new since yesterday?", FRI, span(d(2026, 10, 8), FRI)),
    ("Vad är nytt sedan igår?", FRI, span(d(2026, 10, 8), FRI)),
    ("What is new since Monday?", FRI, span(d(2026, 10, 5), FRI)),
    ("What is new since Monday?", MON, span(MON, MON)),
    ("What is new since last Monday?", MON, span(d(2026, 10, 5), MON)),
    ("Vad är nytt sedan i måndags?", MON, span(d(2026, 10, 5), MON)),
    ("What is new since October 1?", FRI, span(d(2026, 10, 1), FRI)),
    ("What is new since 2026-10-01?", FRI, span(d(2026, 10, 1), FRI)),
    ("Vad är nytt sedan 1 oktober?", FRI, span(d(2026, 10, 1), FRI)),
    ("What is new since December 20?", JAN, span(d(2025, 12, 20), JAN)),
    ("What is new since September?", FRI, span(d(2026, 9, 1), FRI)),
    # Calendar periods
    ("What happened last week?", FRI, span(d(2026, 9, 28), d(2026, 10, 4))),
    ("Vad hände förra veckan?", FRI, span(d(2026, 9, 28), d(2026, 10, 4))),
    ("What happened last week?", MON, span(d(2026, 10, 5), d(2026, 10, 11))),
    ("Vad hände förra veckan?", JAN, span(d(2025, 12, 29), d(2026, 1, 4))),
    ("What's new this week?", FRI, span(d(2026, 10, 5), FRI)),
    ("Vad är nytt denna vecka?", FRI, span(d(2026, 10, 5), FRI)),
    ("What's new this week?", MON, span(MON, MON)),
    ("What happened last month?", FRI, span(d(2026, 9, 1), d(2026, 9, 30))),
    ("Vad hände förra månaden?", FRI, span(d(2026, 9, 1), d(2026, 9, 30))),
    ("Vad hände förra månaden?", JAN, span(d(2025, 12, 1), d(2025, 12, 31))),
    ("What happened this month?", FRI, span(d(2026, 10, 1), FRI)),
    ("Vad hände denna månad?", FRI, span(d(2026, 10, 1), FRI)),
    ("Vad hände den här månaden?", FRI, span(d(2026, 10, 1), FRI)),
    ("What happened in September?", FRI, span(d(2026, 9, 1), d(2026, 9, 30))),
    ("Vad hände i december?", JAN, span(d(2025, 12, 1), d(2025, 12, 31))),
    ("What happened in September 2025?", FRI, span(d(2025, 9, 1), d(2025, 9, 30))),
    ("What happened in week 41?", FRI, span(d(2026, 10, 5), d(2026, 10, 11))),
    ("Vad hände vecka 1?", FRI, span(d(2025, 12, 29), d(2026, 1, 4))),
    ("What happened this year?", FRI, span(d(2026, 1, 1), FRI)),
    ("Vad har hänt i år?", FRI, span(d(2026, 1, 1), FRI)),
    # Explicit ranges
    ("What happened between October 1 and October 5?", FRI, span(d(2026, 10, 1), d(2026, 10, 5))),
    ("Vad hände mellan den 1 och den 5 oktober?", FRI, span(d(2026, 10, 1), d(2026, 10, 5))),
    ("What happened from 2026-10-01 to 2026-10-05?", FRI, span(d(2026, 10, 1), d(2026, 10, 5))),
    ("What happened from September 28 to October 2?", FRI, span(d(2026, 9, 28), d(2026, 10, 2))),
    ("What happened between December 28 and January 3?", JAN, span(d(2025, 12, 28), d(2026, 1, 3))),
    # Ambiguous or impossible: ask for a period
    ("What are recent advances in agents?", FRI, ASK),
    ("Vad har hänt nyligen?", FRI, ASK),
    ("What came out two weeks ago?", FRI, ASK),
    ("Vad kom för en månad sedan?", FRI, ASK),
    ("What came out a month ago?", FRI, ASK),
    ("What happened last year?", FRI, ASK),
    ("Vad har hänt de senaste veckorna?", FRI, ASK),
    ("What happened between October 5 and October 1?", FRI, ASK),
    ("What happened in week 54?", FRI, ASK),
    ("What happened this weekend?", FRI, ASK),
    ("Vad hände i helgen?", FRI, ASK),
    ("What happened the week after October 1?", FRI, ASK),
    ("Vad hände veckan efter den 1 oktober?", FRI, ASK),
    ("What came out in Q3?", FRI, ASK),
    ("Vad hände i höstas?", FRI, ASK),
    # Rankings, not periods
    ("What are the latest papers on agents?", FRI, RANK),
    ("Vad är det senaste om agenter?", FRI, RANK),
    # Ordinary questions: no date filter, nothing asked
    ("What is a transformer?", FRI, NONE),
    ("What may come next for agents?", FRI, NONE),
    ("Vad är RAG?", FRI, NONE),
]


def outcome(question: str, today: date):
    found = extract_date_range(question, today)
    if found is not None:
        return found
    if detect_recency_ranking(question):
        return RANK
    return ASK if unresolved_time_phrase(question, today) else NONE


class DateMatrixTests(unittest.TestCase):
    def test_the_matrix_has_at_least_30_cases_in_both_languages(self):
        swedish = [q for q, _, _ in MATRIX if re.search(r"[åäö]|\b(vad|kom|hände)\b", q.lower())]
        self.assertGreaterEqual(len(MATRIX), 30)
        self.assertGreaterEqual(len(swedish), 15)
        self.assertGreaterEqual(len(MATRIX) - len(swedish), 15)

    def test_every_case(self):
        for question, today, expected in MATRIX:
            with self.subTest(question=question, today=today):
                self.assertEqual(outcome(question, today), expected)

    def test_the_documented_matrix_lists_the_same_questions(self):
        doc = (Path(__file__).resolve().parent.parent / "docs" / "date-phrases.md").read_text(
            encoding="utf-8")
        matrix_section = doc[doc.index("## Test matrix"):]
        documented = re.findall(r"^\| [^|]*\| (.+?) \| \d{4}-\d{2}-\d{2}", matrix_section, flags=re.M)
        self.assertEqual(sorted(set(documented)), sorted({q for q, _, _ in MATRIX}))


class VideoDateAtMidnightTests(unittest.TestCase):
    """T-094 (D-022, KB-040): a video's date is yt-dlp's UTC upload day, stored as is.
    One uploaded at 00:30 on 9 October in Stockholm (22:30 UTC on the 8th) is dated the
    8th, so "today" asked that night doesn't include it and "yesterday" does."""

    def test_the_stored_date_is_the_utc_day_and_is_not_converted(self):
        from datetime import datetime, timezone

        from vg09 import reference_date
        from vg09.youtube import _feed_date

        uploaded = datetime(2026, 10, 8, 22, 30, tzinfo=timezone.utc)
        stored = date.fromisoformat(_feed_date(uploaded.strftime("%Y%m%d")))
        today = reference_date.today("Europe/Stockholm", now=uploaded)

        self.assertEqual((stored, today), (date(2026, 10, 8), date(2026, 10, 9)))
        start, end = extract_date_range("What came out today?", today)
        self.assertFalse(start.toordinal() <= stored.toordinal() <= end.toordinal())
        start, end = extract_date_range("What came out yesterday?", today)
        self.assertTrue(start.toordinal() <= stored.toordinal() <= end.toordinal())

    def test_the_note_appears_next_to_a_date_filter_that_includes_videos(self):
        from vg09.ui_helpers import video_date_note

        period = (date(2026, 10, 9), date(2026, 10, 9))
        self.assertIn("upload day in UTC", video_date_note(period, None))
        self.assertIn("upload day in UTC", video_date_note(period, "youtube"))
        self.assertIsNone(video_date_note(period, "hf"))
        self.assertIsNone(video_date_note(None, None))


if __name__ == "__main__":
    unittest.main()
