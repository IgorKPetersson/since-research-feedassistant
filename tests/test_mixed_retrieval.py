"""T-095: exact names, both-source questions, balanced packing and the search scope.

A real in-memory Chroma collection with hand-made 3-number embeddings, so `$regex`
name matching and `where` filters run in Chroma itself. Nothing reaches Ollama: the
question's embedding and token counts are patched.
"""

from __future__ import annotations

import tempfile
import unittest
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import patch

import chromadb

from vg09 import channel_state
from vg09.exact_names import exact_names
from vg09.retrieval import Candidate, name_candidates, pack_balanced, retrieve
from vg09.scope import channel_coverage_notes, scope_lines, scope_prompt, search_scope
from vg09.source_filter import asks_for_both_sources

D1, D2 = date(2026, 9, 10), date(2026, 9, 16)
QUERY = [1.0, 0.0, 0.0]

# id, doc_id, source, feed date, text, embedding (closer to QUERY = more similar)
ROWS = [
    ("v1:0", "v1", "youtube", D2, "New agents for coding, a long video", [1.0, 0.0, 0.0]),
    ("v2:0", "v2", "youtube", D2, "More agent news this week", [0.99, 0.1, 0.0]),
    ("v3:0", "v3", "youtube", D1, "Agents everywhere", [0.98, 0.15, 0.0]),
    ("v4:0", "v4", "youtube", D1, "Agent tooling roundup", [0.97, 0.2, 0.0]),
    ("v5:0", "v5", "youtube", D1, "Title only video", [0.96, 0.25, 0.0]),
    ("p1:0", "p1", "hf", D1, "NeoHorse-1: recursive self-improvement for agents", [0.2, 1.0, 0.0]),
    ("p2:0", "p2", "hf", D2, "A paper on agent benchmarks", [0.3, 0.9, 0.0]),
    ("p3:0", "p3", "hf", date(2026, 8, 1), "An old paper mentioning neohorse in passing", [0.0, 0.0, 1.0]),
]


def make_collection():
    client = chromadb.EphemeralClient()
    col = client.create_collection(f"t095_{uuid.uuid4().hex}", embedding_function=None)
    col.add(ids=[r[0] for r in ROWS], documents=[r[4] for r in ROWS], embeddings=[r[5] for r in ROWS],
            metadatas=[{"doc_id": r[1], "source": r[2], "feed_date": r[3].isoformat(),
                        "feed_date_ordinal": r[3].toordinal(), "title": r[4], "url": f"https://x/{r[1]}",
                        **({"text_source": "title_description" if r[1] == "v5" else "captions"}
                           if r[2] == "youtube" else {})} for r in ROWS])
    return col


class ExactNameTests(unittest.TestCase):
    def test_names_are_found_by_shape_not_by_a_list(self):
        self.assertEqual(exact_names("Har NeoHorse nämnts?"), ["NeoHorse"])
        self.assertEqual(exact_names("Nämns LEGO i någon artikel?"), ["LEGO"])
        self.assertEqual(exact_names("Has OpenAI released GPT-6 or Qwen3?"), ["OpenAI", "GPT-6", "Qwen3"])
        self.assertEqual(exact_names('What did "Kimi K3" do?'), ["Kimi K3"])
        self.assertEqual(exact_names("Har Palantir nämnts i någon video?"), ["Palantir"])

    def test_compounds_sentence_starts_and_plain_words_are_not_names(self):
        self.assertEqual(exact_names("Vad har hänt med AI-agenter den senaste veckan?"), [])
        self.assertEqual(exact_names("Har det sagts något om stora AI-verktyg?"), [])
        self.assertEqual(exact_names("What is a transformer?"), [])
        self.assertEqual(exact_names("How is text-to-video going?"), [])


class NameCandidateTests(unittest.TestCase):
    def setUp(self):
        self.col = make_collection()
        patcher = patch("vg09.retrieval.get_collection", return_value=self.col)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_name_is_matched_whatever_its_case(self):
        found, counts = name_candidates("Har NeoHorse nämnts?", None, None, QUERY)
        self.assertEqual(counts, {"NeoHorse": 2})  # "NeoHorse-1" and "neohorse"
        self.assertEqual({c.metadata["doc_id"] for c in found}, {"p1", "p3"})

    def test_the_date_filter_applies_to_name_matches(self):
        found, counts = name_candidates("Har NeoHorse nämnts?", (D1, D2), None, QUERY)
        self.assertEqual(counts, {"NeoHorse": 1})
        self.assertEqual([c.metadata["doc_id"] for c in found], ["p1"])

    def test_an_absent_name_counts_zero_and_adds_nothing(self):
        found, counts = name_candidates("Har AutoDev nämnts?", None, None, QUERY)
        self.assertEqual((found, counts), ([], {"AutoDev": 0}))

    def test_a_name_in_too_many_documents_is_counted_but_adds_nothing(self):
        with patch("vg09.exact_names.DISTINCTIVE_MAX_DOCS", 1):
            found, counts = name_candidates("Har NeoHorse nämnts?", None, None, QUERY)
        self.assertEqual((found, counts), ([], {"NeoHorse": 2}))

    def test_a_name_is_matched_as_a_word_not_inside_another(self):
        found, counts = name_candidates("Is there anything on Agen?", None, None, QUERY)
        self.assertEqual(counts, {"Agen": 0})


class BothSourcesTests(unittest.TestCase):
    def test_a_question_naming_papers_and_videos_asks_for_both(self):
        self.assertTrue(asks_for_both_sources("Har det sagts något, både i videor och i artiklar?"))
        self.assertTrue(asks_for_both_sources("What happened with agents, in both papers and videos?"))
        self.assertFalse(asks_for_both_sources("Which papers came out?"))
        self.assertFalse(asks_for_both_sources("What is new in video generation?"))

    def test_the_quota_brings_the_other_source_in_and_keeps_relevance_order(self):
        def cand(i, src):
            return Candidate(id=i, text=i, metadata={"doc_id": i, "source": src, "title": i,
                                                     "url": f"https://x/{i}", "feed_date": "2026-09-16"})

        ranked = [cand(f"v{i}", "youtube") for i in range(6)] + [cand("p1", "hf"), cand("p2", "hf")]
        with patch("vg09.retrieval.count_qwen_tokens", return_value=100):
            plain, _, _ = pack_balanced(ranked, 0, budget_tokens=400)
            balanced, _, _ = pack_balanced(ranked, 2, budget_tokens=400)
        self.assertEqual([c.id for c in plain], ["v0", "v1", "v2", "v3"])
        self.assertEqual([c.id for c in balanced], ["v0", "v1", "p1", "p2"])  # original order kept

    def test_retrieve_applies_the_quota_only_when_both_are_asked_for(self):
        col = make_collection()
        with patch("vg09.retrieval.get_collection", return_value=col), \
             patch("vg09.retrieval.embed_question", return_value=QUERY), \
             patch("vg09.retrieval.count_qwen_tokens", return_value=3000):  # room for 3 chunks
            plain = retrieve("What is new on agents?", date_range=None, ranking=False)
            both = retrieve("What is new on agents, in both papers and videos?", date_range=None,
                            ranking=False)
        self.assertEqual({c.metadata["source"] for c in plain.chunks}, {"youtube"})
        self.assertEqual({c.metadata["source"] for c in both.chunks}, {"youtube", "hf"})


class SearchScopeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        for target, value in (("vg09.store.get_collection", lambda: make_collection()),
                              ("vg09.watermark.WATERMARK_DIR", Path(tmp.name))):
            patcher = patch(target, value) if not callable(value) or target.endswith("DIR") \
                else patch(target, side_effect=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_counts_documents_and_video_transcripts_in_the_filter(self):
        scope = search_scope((D1, D2), None, {"AutoDev": 0})
        self.assertEqual((scope.papers, scope.videos), (2, 5))
        self.assertEqual(scope.video_text, {"captions": 4, "title_description": 1})
        lines = scope_lines(scope)
        self.assertIn("Searched 2 papers and 5 videos dated 2026-09-10 to 2026-09-16.", lines[0])
        self.assertIn("Of the videos, 1 has only a title and description.", lines[0])
        self.assertIn("Exact text: “AutoDev” in no source.", lines[1])

    def test_the_prompt_says_how_to_phrase_not_found(self):
        prompt = scope_prompt(search_scope(None, "hf", {"NeoHorse": 1}))
        self.assertIn("covered 3 papers and 0 videos of all dates", prompt)
        self.assertNotIn("NeoHorse", prompt)  # names are shown to the user, not the model
        self.assertIn("say it was not found in these sources for this period", prompt)

    def test_channel_gaps_failures_and_unreadable_videos_are_named(self):
        state = {"version": channel_state.VERSION, "channels": {
            "ok": {**channel_state.new_record(date(2026, 9, 12)), "last_attempt": "x",
                   "last_result": "complete", "checked_through": "2026-09-20", "pending_from": None,
                   "unreadable": {"m1": "members-only"}},
            "bad": {**channel_state.new_record(date(2026, 9, 12)), "last_attempt": "x",
                    "last_result": "failed", "pending_from": "2026-09-14",
                    "gaps": [{"from": "2026-09-12", "through": "2026-09-13", "reason": "r"}]},
        }}
        channel_state.save(state)
        notes = channel_coverage_notes((D1, D2), ["ok", "bad", "new"])
        self.assertIn("@ok: 1 listed videos can't be read (members-only or private)", notes)
        self.assertIn("@bad: the last check failed, so videos from 2026-09-14 on may be missing", notes)
        self.assertIn("@bad: 2026-09-12 to 2026-09-13 not verified", notes)
        self.assertIn("@new has not been checked yet", notes)
        self.assertIn("Videos before 2026-09-12 were never checked", notes)
        self.assertEqual(channel_coverage_notes((date(2026, 9, 21), date(2026, 9, 22)), ["ok"]),
                         ["@ok: 1 listed videos can't be read (members-only or private)"])


if __name__ == "__main__":
    unittest.main()
