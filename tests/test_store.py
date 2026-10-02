"""Unit tests for vg09.store.

T-027 added LatestFeedDateTests/IsEmptyTests for the function it introduced, per
"test what changed", not a backfill of the rest of the module. T-036 closes the
remaining gap the Phase 1 grill-me review found and docs/PLAN.md's risk register
deferred to Phase 3: embed_batch()'s compliance with CLAUDE.md's hard rules
(explicit bge-m3, explicit num_ctx) was previously asserted only by code review,
never by an automated test that would catch a future refactor silently dropping
either.
"""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from vg09.store import EMBED_MODEL, EMBED_NUM_CTX, corpus_stats, embed_batch, is_empty, latest_feed_date


class OllamaAddressTests(unittest.TestCase):
    def test_no_module_addresses_ollama_as_localhost(self):
        """T-049/KB-024: "localhost" cost about 2 seconds per request on Windows (IPv6
        tried first, Ollama on IPv4 only) - 68.6s per retrieval against 1.4s measured
        with the literal address. All three constants, so one can't quietly go back."""
        import vg09.answer
        import vg09.retrieval
        import vg09.store

        for module in (vg09.answer, vg09.retrieval, vg09.store):
            self.assertEqual(module.OLLAMA, "http://127.0.0.1:11434", module.__name__)


class LatestFeedDateTests(unittest.TestCase):
    def test_returns_the_max_feed_date_ordinal_across_both_sources(self):
        collection = MagicMock()
        collection.count.return_value = 3
        collection.get.return_value = {
            "metadatas": [
                {"feed_date_ordinal": date(2026, 9, 14).toordinal()},  # hf
                {"feed_date_ordinal": date(2026, 9, 17).toordinal()},  # youtube - latest
                {"feed_date_ordinal": date(2026, 9, 10).toordinal()},
            ]
        }
        with patch("vg09.store.get_collection", return_value=collection):
            result = latest_feed_date()

        self.assertEqual(result, date(2026, 9, 17))

    def test_empty_store_returns_none(self):
        collection = MagicMock()
        collection.count.return_value = 0
        with patch("vg09.store.get_collection", return_value=collection):
            result = latest_feed_date()

        self.assertIsNone(result)
        collection.get.assert_not_called()


class IsEmptyTests(unittest.TestCase):
    def test_empty_collection_is_empty(self):
        collection = MagicMock()
        collection.count.return_value = 0
        with patch("vg09.store.get_collection", return_value=collection):
            self.assertTrue(is_empty())

    def test_non_empty_collection_is_not_empty(self):
        collection = MagicMock()
        collection.count.return_value = 1971
        with patch("vg09.store.get_collection", return_value=collection):
            self.assertFalse(is_empty())


class CorpusStatsTests(unittest.TestCase):
    """T-042: real corpus counts for the chat UI's status bar."""

    def test_counts_distinct_documents_per_source_and_total_chunks(self):
        collection = MagicMock()
        collection.count.return_value = 5
        collection.get.return_value = {
            "metadatas": [
                {"source": "hf", "doc_id": "paper1"},
                {"source": "hf", "doc_id": "paper1"},  # a second chunk of the same paper
                {"source": "hf", "doc_id": "paper2"},
                {"source": "youtube", "doc_id": "vid1"},
                {"source": "youtube", "doc_id": "vid1"},  # a second chunk of the same video
            ]
        }
        with patch("vg09.store.get_collection", return_value=collection):
            result = corpus_stats()

        self.assertEqual(result, {"hf_documents": 2, "youtube_documents": 1, "chunks": 5})

    def test_empty_store_returns_all_zeros_without_a_metadata_scan(self):
        collection = MagicMock()
        collection.count.return_value = 0
        with patch("vg09.store.get_collection", return_value=collection):
            result = corpus_stats()

        self.assertEqual(result, {"hf_documents": 0, "youtube_documents": 0, "chunks": 0})
        collection.get.assert_not_called()


class EmbedBatchTests(unittest.TestCase):
    """T-036: mocked at the requests.post boundary, matching this project's
    existing test pattern - no real Ollama call."""

    def _mock_response(self, embeddings, prompt_eval_count=10):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {"embeddings": embeddings, "prompt_eval_count": prompt_eval_count}
        return resp

    def test_request_body_always_includes_explicit_bge_m3_model(self):
        with patch("vg09.store.requests.post", return_value=self._mock_response([[0.1, 0.2]])) as mock_post:
            embed_batch(["hello world"])

        body = mock_post.call_args.kwargs["json"]
        self.assertEqual(body["model"], "bge-m3")
        self.assertEqual(body["model"], EMBED_MODEL)  # never silently drifts from the named constant

    def test_request_body_always_includes_an_explicit_num_ctx(self):
        with patch("vg09.store.requests.post", return_value=self._mock_response([[0.1, 0.2]])) as mock_post:
            embed_batch(["hello world"])

        body = mock_post.call_args.kwargs["json"]
        self.assertIn("num_ctx", body["options"])  # CLAUDE.md's hard rule: never left implicit
        self.assertEqual(body["options"]["num_ctx"], EMBED_NUM_CTX)
        self.assertEqual(body["options"]["num_ctx"], 8192)  # bge-m3's own context window (KB-007)

    def test_all_input_texts_are_sent_and_embeddings_are_returned_unmodified(self):
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        with patch("vg09.store.requests.post", return_value=self._mock_response(embeddings)) as mock_post:
            result = embed_batch(["first chunk", "second chunk"])

        body = mock_post.call_args.kwargs["json"]
        self.assertEqual(body["input"], ["first chunk", "second chunk"])
        self.assertEqual(result, embeddings)

    def test_non_2xx_response_raises_before_reading_the_body(self):
        """Matches T-029's pattern for the other two real Ollama call sites
        (generate_answer, count_qwen_tokens) - a non-2xx response (model not
        pulled, OOM, ...) must fail loudly here, not surface later as an
        opaque KeyError from reading a partial/error body."""
        resp = MagicMock()
        resp.raise_for_status.side_effect = RuntimeError("simulated non-2xx response")
        with patch("vg09.store.requests.post", return_value=resp):
            with self.assertRaises(RuntimeError):
                embed_batch(["hello world"])
        resp.json.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class ChannelTests(unittest.TestCase):
    """T-054 (D-017): the store knows which channel a video came from."""

    def _collection(self):
        collection = MagicMock()
        collection.count.return_value = 5
        collection.get.return_value = {
            "metadatas": [
                {"doc_id": "v1", "channel": "alpha", "feed_date_ordinal": date(2026, 9, 10).toordinal()},
                {"doc_id": "v1", "channel": "alpha", "feed_date_ordinal": date(2026, 9, 10).toordinal()},
                {"doc_id": "v2", "channel": "alpha", "feed_date_ordinal": date(2026, 9, 20).toordinal()},
                {"doc_id": "v3", "channel": "beta", "feed_date_ordinal": date(2026, 9, 15).toordinal()},
                {"doc_id": "v4", "feed_date_ordinal": date(2026, 9, 1).toordinal()},  # pre-T-054
            ]
        }
        return collection

    def test_chunk_metadata_carries_the_channel_only_when_there_is_one(self):
        from vg09.chunking import Chunk
        from vg09.store import chunk_metadata

        base = dict(id="youtube:v1:0", doc_id="v1", source="youtube", url="u", title="t",
                    feed_date="2026-09-10", text="x")
        self.assertEqual(chunk_metadata(Chunk(**base, channel="alpha"))["channel"], "alpha")
        self.assertNotIn("channel", chunk_metadata(Chunk(**base)))

    def test_channel_stats_counts_distinct_videos_and_latest_date_per_channel(self):
        from vg09.store import channel_stats

        collection = self._collection()
        with patch("vg09.store.get_collection", return_value=collection):
            stats = channel_stats()

        collection.get.assert_called_once_with(where={"source": "youtube"}, include=["metadatas"])
        self.assertEqual(stats["alpha"], {"documents": 2, "latest": date(2026, 9, 20)})
        self.assertEqual(stats["beta"], {"documents": 1, "latest": date(2026, 9, 15)})
        # a video with no channel is visible under None, not dropped from every count
        self.assertEqual(stats[None]["documents"], 1)

    def test_channel_stats_of_an_empty_store_is_empty(self):
        from vg09.store import channel_stats

        collection = MagicMock()
        collection.count.return_value = 0
        with patch("vg09.store.get_collection", return_value=collection):
            self.assertEqual(channel_stats(), {})

    def test_remove_channel_data_deletes_its_chunks_and_only_its_raw_files(self):
        import json
        import tempfile
        from pathlib import Path

        from vg09.store import remove_channel_data

        collection = MagicMock()
        collection.count.side_effect = [10, 7]
        with tempfile.TemporaryDirectory() as tmp:
            day = Path(tmp) / "youtube" / "2026-09-10"
            day.mkdir(parents=True)
            (day / "v1.json").write_text(json.dumps({"id": "v1", "channel": "alpha"}), encoding="utf-8")
            (day / "v3.json").write_text(json.dumps({"id": "v3", "channel": "beta"}), encoding="utf-8")
            (day / "v9.pending.json").write_text(json.dumps({"id": "v9"}), encoding="utf-8")
            # vg09.store.RAW_DIR, its own imported copy of the name (KB-010)
            with patch("vg09.store.get_collection", return_value=collection), \
                 patch("vg09.store.RAW_DIR", Path(tmp)):
                result = remove_channel_data("alpha")

            self.assertEqual(sorted(p.name for p in day.iterdir()), ["v3.json", "v9.pending.json"])
        collection.delete.assert_called_once_with(where={"channel": "alpha"})
        self.assertEqual(result, {"chunks": 3, "documents": 1})
