"""Unit tests for vg09.retrieval (T-022).

No live network calls: Chroma's collection and the Ollama token-count/embed calls are
all mocked at the boundary, same pattern T-010/T-012's tests use. A real end-to-end
verification against the production Chroma store and real Ollama lives in
scripts/t022_verify_retrieval.py, not here.
"""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from vg09.retrieval import (
    Candidate,
    order_candidates,
    pack_to_budget,
    query_candidates,
    retrieve,
)


def make_candidate(id_: str, text: str, feed_date_ordinal: int) -> Candidate:
    return Candidate(id=id_, text=text, metadata={"feed_date_ordinal": feed_date_ordinal})


class OrderCandidatesTests(unittest.TestCase):
    def test_ranking_false_keeps_similarity_order_untouched(self):
        candidates = [make_candidate("a", "x", 100), make_candidate("b", "y", 50)]
        self.assertEqual(order_candidates(candidates, ranking=False), candidates)

    def test_ranking_true_sorts_by_feed_date_ordinal_descending(self):
        older = make_candidate("older", "x", 100)
        newer = make_candidate("newer", "y", 200)
        result = order_candidates([older, newer], ranking=True)
        self.assertEqual([c.id for c in result], ["newer", "older"])

    def test_ranking_true_is_a_stable_sort_for_equal_dates(self):
        a = make_candidate("a", "x", 100)
        b = make_candidate("b", "y", 100)  # same date as a, was more relevant (came first)
        c = make_candidate("c", "z", 200)
        result = order_candidates([a, b, c], ranking=True)
        self.assertEqual([x.id for x in result], ["c", "a", "b"])  # a before b preserved


class PackToBudgetTests(unittest.TestCase):
    def test_packs_until_budget_would_be_exceeded_then_stops(self):
        candidates = [make_candidate(str(i), f"text{i}", 0) for i in range(5)]
        with patch("vg09.retrieval.count_qwen_tokens", side_effect=[40, 40, 40, 40, 40]):
            packed, total, dropped = pack_to_budget(candidates, budget_tokens=100)
        # 40+40+40=120 > 100 after the 3rd - so only the first 2 fit (40+40=80),
        # and packing STOPS there rather than skipping the 3rd to try a smaller 4th/5th.
        self.assertEqual([c.id for c in packed], ["0", "1"])
        self.assertEqual(total, 80)
        self.assertEqual(dropped, [])

    def test_a_single_oversized_candidate_is_dropped_not_sent_and_packing_continues(self):
        candidates = [
            make_candidate("small1", "s1", 0),
            make_candidate("huge", "h", 0),
            make_candidate("small2", "s2", 0),
        ]
        with patch("vg09.retrieval.count_qwen_tokens", side_effect=[30, 500, 30]):
            packed, total, dropped = pack_to_budget(candidates, budget_tokens=100)
        self.assertEqual([c.id for c in packed], ["small1", "small2"])
        self.assertEqual(total, 60)
        self.assertEqual(dropped, ["huge"])

    def test_empty_candidate_list_packs_to_nothing(self):
        packed, total, dropped = pack_to_budget([], budget_tokens=100)
        self.assertEqual((packed, total, dropped), ([], 0, []))


class QueryCandidatesTests(unittest.TestCase):
    def _mock_collection(self):
        collection = MagicMock()
        collection.query.return_value = {
            "ids": [["a", "b"]],
            "documents": [["text a", "text b"]],
            "metadatas": [[{"feed_date_ordinal": 1}, {"feed_date_ordinal": 2}]],
        }
        return collection

    def test_no_date_range_queries_with_embeddings_and_no_where_clause(self):
        collection = self._mock_collection()
        with (
            patch("vg09.retrieval.get_collection", return_value=collection),
            patch("vg09.retrieval.embed_batch", return_value=[[0.1, 0.2]]),
        ):
            result = query_candidates("vad är nytt?", date_range=None, n_results=10)

        self.assertEqual([c.id for c in result], ["a", "b"])
        collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2]], n_results=10, where=None
        )

    def test_date_range_filters_by_feed_date_ordinal_never_the_string(self):
        collection = self._mock_collection()
        start, end = date(2026, 9, 10), date(2026, 9, 16)
        with (
            patch("vg09.retrieval.get_collection", return_value=collection),
            patch("vg09.retrieval.embed_batch", return_value=[[0.1, 0.2]]),
        ):
            query_candidates("senaste veckan", date_range=(start, end), n_results=10)

        call_kwargs = collection.query.call_args.kwargs
        self.assertEqual(
            call_kwargs["where"],
            {"$and": [
                {"feed_date_ordinal": {"$gte": start.toordinal()}},
                {"feed_date_ordinal": {"$lte": end.toordinal()}},
            ]},
        )

    def test_never_calls_query_texts(self):
        """CLAUDE.md hard rule: query_texts= would silently invoke Chroma's default
        embedder (KB-006). This asserts the actual call signature, not just intent."""
        collection = self._mock_collection()
        with (
            patch("vg09.retrieval.get_collection", return_value=collection),
            patch("vg09.retrieval.embed_batch", return_value=[[0.1, 0.2]]),
        ):
            query_candidates("vad är nytt?", date_range=None)

        self.assertNotIn("query_texts", collection.query.call_args.kwargs)


class RetrieveIntegrationTests(unittest.TestCase):
    def test_full_pipeline_wires_query_order_and_pack_together(self):
        collection = MagicMock()
        collection.query.return_value = {
            "ids": [["newer", "older"]],
            "documents": [["new text", "old text"]],
            "metadatas": [
                [{"feed_date_ordinal": 200}, {"feed_date_ordinal": 100}],
            ],
        }
        with (
            patch("vg09.retrieval.get_collection", return_value=collection),
            patch("vg09.retrieval.embed_batch", return_value=[[0.1, 0.2]]),
            patch("vg09.retrieval.count_qwen_tokens", side_effect=[10, 10]),
        ):
            result = retrieve("vad är det senaste?", date_range=None, ranking=True)

        self.assertEqual([c.id for c in result.chunks], ["newer", "older"])
        self.assertEqual(result.total_tokens, 20)
        self.assertTrue(result.ranking_used)
        self.assertIsNone(result.date_range_used)
        self.assertEqual(result.candidates_considered, 2)


if __name__ == "__main__":
    unittest.main()
