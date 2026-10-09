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
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from vg09.answer import AnswerResult
from vg09.retrieval import RetrievalResult
from vg09.sources import Sources

APP = Path(__file__).resolve().parent.parent / "app.py"
TODAY = date(2026, 10, 12)  # a Monday
NEWEST = date(2026, 9, 18)  # the index stopped 24 days earlier


class AppQuestionDatesTests(unittest.TestCase):
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
        self.assertTrue(any("the question's own period (2026-10-06 – 2026-10-12) is not used" in c
                            for c in self.texts(at.caption)))

    def test_an_empty_index_asks_nothing_and_still_runs(self):
        self.empty = True
        at = AppTest.from_file(str(APP), default_timeout=30)
        at.run()

        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("No data yet" in i for i in self.texts(at.info)))
        self.assertNotIn("retrieve_range", self.calls)


if __name__ == "__main__":
    unittest.main()
