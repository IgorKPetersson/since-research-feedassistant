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

import requests

from vg09.retrieval import (
    Candidate,
    count_qwen_tokens,
    dedup_by_doc,
    order_candidates,
    pack_to_budget,
    query_candidates,
    retrieve,
)


def make_candidate(id_: str, text: str, feed_date_ordinal: int) -> Candidate:
    return Candidate(id=id_, text=text, metadata={"feed_date_ordinal": feed_date_ordinal})


def make_doc_candidate(chunk_id: str, doc_id: str) -> Candidate:
    return Candidate(id=chunk_id, text=chunk_id, metadata={"doc_id": doc_id, "feed_date_ordinal": 0})


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


class DedupByDocTests(unittest.TestCase):
    def test_caps_chunks_per_doc_keeping_the_highest_ranked_ones(self):
        candidates = [
            make_doc_candidate("v:0", "video"),
            make_doc_candidate("v:1", "video"),
            make_doc_candidate("v:2", "video"),  # 3rd chunk of the same doc - dropped
            make_doc_candidate("paper:0", "paper"),
        ]
        result = dedup_by_doc(candidates, max_per_doc=2)
        self.assertEqual([c.id for c in result], ["v:0", "v:1", "paper:0"])

    def test_real_shape_one_video_would_otherwise_fill_the_whole_top(self):
        """The real pattern this fixes: one video with many chunks ranked 1st, 3rd,
        5th, 10th for a real question, crowding out on-topic papers ranked 7th-36th."""
        candidates = (
            [make_doc_candidate(f"video:{i}", "video") for i in range(4)]
            + [make_doc_candidate("paper_a:0", "paper_a")]
            + [make_doc_candidate("paper_b:0", "paper_b")]
        )
        result = dedup_by_doc(candidates, max_per_doc=2)
        self.assertEqual(
            [c.id for c in result], ["video:0", "video:1", "paper_a:0", "paper_b:0"]
        )

    def test_default_cap_is_two(self):
        candidates = [make_doc_candidate(f"v:{i}", "video") for i in range(5)]
        result = dedup_by_doc(candidates)
        self.assertEqual(len(result), 2)

    def test_no_duplicates_leaves_everything_untouched(self):
        candidates = [make_doc_candidate("a:0", "a"), make_doc_candidate("b:0", "b")]
        self.assertEqual(dedup_by_doc(candidates), candidates)

    def test_empty_input(self):
        self.assertEqual(dedup_by_doc([]), [])


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


class CountQwenTokensTests(unittest.TestCase):
    """T-029: a non-2xx Ollama response must fail loudly here, not later as an opaque
    KeyError from reading a partial/error body - matches vg09.store.embed_batch()'s
    existing raise_for_status() pattern."""

    def test_real_response_shape_returns_prompt_eval_count(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"prompt_eval_count": 123}
        with patch("vg09.retrieval.requests.post", return_value=mock_resp):
            self.assertEqual(count_qwen_tokens("some text"), 123)
        mock_resp.raise_for_status.assert_called_once()

    def test_non_2xx_response_raises_before_reading_the_body(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        with patch("vg09.retrieval.requests.post", return_value=mock_resp):
            with self.assertRaises(requests.exceptions.HTTPError):
                count_qwen_tokens("some text")
        mock_resp.json.assert_not_called()


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
    def test_full_pipeline_wires_query_order_dedup_and_pack_together(self):
        collection = MagicMock()
        collection.query.return_value = {
            "ids": [["newer", "older"]],
            "documents": [["new text", "old text"]],
            "metadatas": [
                [
                    {"feed_date_ordinal": 200, "doc_id": "doc_newer"},
                    {"feed_date_ordinal": 100, "doc_id": "doc_older"},
                ],
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

    def test_full_pipeline_dedup_prevents_one_doc_from_filling_the_pack(self):
        """T-027's real scenario: one video (many chunks) plus one paper (one chunk).
        Without dedup, all 3 "video" chunks would out-rank and could crowd out the
        paper; with it, the paper survives into the packed result."""
        collection = MagicMock()
        collection.query.return_value = {
            "ids": [["video:0", "video:1", "video:2", "paper:0"]],
            "documents": [["v0", "v1", "v2", "p0"]],
            "metadatas": [[
                {"feed_date_ordinal": 100, "doc_id": "video"},
                {"feed_date_ordinal": 100, "doc_id": "video"},
                {"feed_date_ordinal": 100, "doc_id": "video"},
                {"feed_date_ordinal": 100, "doc_id": "paper"},
            ]],
        }
        with (
            patch("vg09.retrieval.get_collection", return_value=collection),
            patch("vg09.retrieval.embed_batch", return_value=[[0.1, 0.2]]),
            patch("vg09.retrieval.count_qwen_tokens", side_effect=[10, 10, 10]),
        ):
            result = retrieve("fråga", date_range=None, ranking=False)

        self.assertEqual([c.id for c in result.chunks], ["video:0", "video:1", "paper:0"])


if __name__ == "__main__":
    unittest.main()
