"""T-093 (D-022): one reference date reaches parsing, the date filter and the answer.

Runs the real `app.py` with Streamlit's own test runner. The clock is fixed, the index
is stale (its newest source is weeks old), and retrieval and the model are replaced by
stubs that record what they were given. Nothing reaches Ollama, Chroma or the network.
"""

from __future__ import annotations

import unittest
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

from vg09.answer import AnswerResult
from vg09.retrieval import RetrievalResult
from vg09.retrieval import retrieve as _REAL_RETRIEVE
from vg09.sources import Sources
from vg09.ui_helpers import format_interval

APP = Path(__file__).resolve().parent.parent / "app.py"
TODAY = date(2026, 10, 12)  # a Monday
NEWEST = date(2026, 9, 18)  # the index stopped 24 days earlier


class _AppTestCase(unittest.TestCase):
    """The stubs and helpers; no tests of its own."""

    def setUp(self):
        self.calls: dict = {}
        stack = ExitStack()
        self.addCleanup(stack.close)

        def retrieve(question, date_range=None, ranking=False, source=None):
            self.calls["retrieve_range"] = date_range
            return RetrievalResult(chunks=[], candidates_considered=0)

        def generate_answer(question, chunks, date_range=None, today=None, **_):
            self.calls["answer_today"] = today
            self.calls["answer_range"] = date_range
            return AnswerResult(reasoning="r", answer="Nothing in the sources.", done_reason="stop",
                                incomplete=False, retries=0, prompt_eval_count=100, source_map={})

        self.empty = False
        for target, kwargs in (
            ("vg09.reference_date.today", {"return_value": TODAY}),
            ("vg09.store.latest_feed_date", {"return_value": NEWEST}),
            ("vg09.store.corpus_stats", {"return_value": {"hf_documents": 5, "youtube_documents": 2,
                                                          "chunks": 40}}),
            ("vg09.store.is_empty", {"side_effect": lambda: self.empty}),
            ("vg09.ingest_job.start_on_open", {}),
            ("vg09.ingest_job.refresh_store_if_updated", {}),
            ("vg09.ingest_job.status", {"return_value": {"state": "done",
                                                         "finished": "2026-09-18T08:00:00"}}),
            ("vg09.ingest_job.is_writing_store", {"return_value": False}),
            ("vg09.retrieval.retrieve", {"side_effect": retrieve}),
            ("vg09.answer.generate_answer", {"side_effect": generate_answer}),
            ("vg09.coverage.papers_checked_through", {"return_value": date(2026, 9, 18)}),
            ("vg09.coverage.videos_checked_through", {"return_value": None}),
            ("vg09.sources.load", {"return_value": Sources(channels={"c": "u"}, saved=True)}),
        ):
            stack.enter_context(patch(target, **kwargs))

    def ask(self, question: str, manual: tuple[date, date] | None = None) -> AppTest:
        at = AppTest.from_file(str(APP), default_timeout=30)
        at.run()
        if manual:
            at.sidebar.checkbox[0].check().run()
            at.sidebar.date_input[0].set_value(manual[0])
            at.sidebar.date_input[1].set_value(manual[1]).run()
        at.text_input(key="question_input").input(question)
        next(b for b in at.button if b.label == "Ask").click().run()
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        return at

    @staticmethod
    def texts(elements) -> list[str]:
        return [e.value for e in elements]

class AppQuestionDatesTests(_AppTestCase):
    def test_one_reference_date_reaches_parsing_filter_and_answer_on_a_stale_index(self):
        at = self.ask("What happened in the last 7 days?")

        window = (date(2026, 10, 6), date(2026, 10, 12))  # from today, not from NEWEST
        self.assertEqual(self.calls["retrieve_range"], window)
        self.assertEqual(self.calls["answer_range"], window)
        self.assertEqual(self.calls["answer_today"], TODAY)
        captions = self.texts(at.caption)
        self.assertIn("Today: Mon 2026-10-12 (Europe/Stockholm) · Newest source: 2026-09-18 · "
                      "Checked: papers through 2026-09-18, videos not complete", captions)
        self.assertTrue(any("is after the newest source in the index (2026-09-18)" in w
                            for w in self.texts(at.warning)))

    def test_a_reversed_manual_range_is_refused_before_searching(self):
        at = self.ask("What happened?", manual=(date(2026, 10, 12), date(2026, 10, 1)))

        self.assertNotIn("retrieve_range", self.calls)
        self.assertTrue(any("after the end date" in e for e in self.texts(at.error)))

    def test_a_manual_range_wins_and_the_questions_own_period_is_named(self):
        manual = (date(2026, 9, 1), date(2026, 9, 10))
        at = self.ask("What happened in the last 7 days?", manual=manual)

        self.assertEqual(self.calls["retrieve_range"], manual)
        self.assertEqual(self.calls["answer_today"], TODAY)
        self.assertTrue(any("the question's own period (Tue 2026-10-06 – Mon 2026-10-12 (7 days)) "
                            "is not used" in c
                            for c in self.texts(at.caption)))

    def test_an_empty_index_asks_nothing_and_still_runs(self):
        self.empty = True
        at = AppTest.from_file(str(APP), default_timeout=30)
        at.run()

        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("No data yet" in i for i in self.texts(at.info)))
        self.assertNotIn("retrieve_range", self.calls)


class AppDateFilterTests(_AppTestCase):
    """T-094: the interval the app shows is the filter the vector store receives.

    Unlike the class above, retrieval runs for real here; only the vector store and the
    question's embedding are stubs, so the `where` clause is the one the app builds."""

    def setUp(self):
        super().setUp()
        self.collection = MagicMock()
        self.collection.query.return_value = {"ids": [[]], "documents": [[]], "metadatas": [[]]}
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch("vg09.retrieval.retrieve", _REAL_RETRIEVE))
        stack.enter_context(patch("vg09.retrieval.get_collection", return_value=self.collection))
        stack.enter_context(patch("vg09.retrieval.embed_question", return_value=[0.0] * 4))

    def where(self) -> dict | None:
        return self.collection.query.call_args.kwargs["where"]

    def shown_interval(self, at) -> str:
        return next(c for c in self.texts(at.caption) if c.startswith(("Date filter", "No date")))

    def assert_filter(self, at, start: date, end: date):
        self.assertEqual(self.where(), {"$and": [{"feed_date_ordinal": {"$gte": start.toordinal()}},
                                                  {"feed_date_ordinal": {"$lte": end.toordinal()}}]})
        self.assertIn(format_interval((start, end)), self.shown_interval(at))

    def test_parsed_intervals_reach_the_vector_store_filter_as_shown(self):
        for question, start, end in (
            ("What happened in week 41?", date(2026, 10, 5), date(2026, 10, 11)),
            ("Vad kom för två dagar sedan?", date(2026, 10, 10), date(2026, 10, 10)),
            ("What is new since 2026-10-01?", date(2026, 10, 1), TODAY),
            ("Vad hände mellan den 1 och den 5 oktober?", date(2026, 10, 1), date(2026, 10, 5)),
            # T-105: calendar weeks and months (TODAY is Monday 2026-10-12)
            ("What happened last week?", date(2026, 10, 5), date(2026, 10, 11)),
            ("Vad hände denna vecka?", TODAY, TODAY),
            ("Vad hände förra månaden?", date(2026, 9, 1), date(2026, 9, 30)),
            ("What happened this month?", date(2026, 10, 1), TODAY),
            ("What happened in the last month?", date(2026, 9, 12), TODAY),
        ):
            with self.subTest(question=question):
                at = self.ask(question)
                self.assert_filter(at, start, end)
                self.assertIn("upload day in UTC", " ".join(self.texts(at.caption)))

    def test_a_vague_question_is_asked_about_and_searched_only_after_a_choice(self):
        at = self.ask("What are recent advances in agents?")

        self.collection.query.assert_not_called()
        self.assertTrue(any("“recent” doesn't say which dates to search" in w
                            for w in self.texts(at.warning)))
        next(b for b in at.button if b.label == "The last 30 days").click().run()

        self.assert_filter(at, date(2026, 9, 13), TODAY)
        self.assertIn("chosen when asked", self.shown_interval(at))
        self.assertEqual(self.calls["answer_range"], (date(2026, 9, 13), TODAY))

    def test_choosing_all_dates_searches_without_a_filter_and_says_so(self):
        at = self.ask("Vad har hänt nyligen?")
        next(b for b in at.button if b.label == "All dates").click().run()

        self.assertIsNone(self.where())
        self.assertEqual(self.shown_interval(at), "No date filter — all dates, as chosen")

    def test_an_impossible_date_is_asked_about(self):
        self.ask("What came out on February 30?")
        self.collection.query.assert_not_called()

    def test_an_ordinary_question_searches_every_date_without_asking(self):
        at = self.ask("What is a transformer?")

        self.assertIsNone(self.where())
        self.assertEqual(self.texts(at.warning), [])
        self.assertNotIn("upload day in UTC", " ".join(self.texts(at.caption)))

    def test_a_papers_only_filter_has_no_video_date_note(self):
        at = self.ask("Which papers came out in week 41?")

        self.assertIn({"source": "hf"}, self.where()["$and"])
        self.assertNotIn("upload day in UTC", " ".join(self.texts(at.caption)))


if __name__ == "__main__":
    unittest.main()
