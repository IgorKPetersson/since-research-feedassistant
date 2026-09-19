"""Unit tests for vg09.citations (T-024)."""

from __future__ import annotations

import unittest

from vg09.citations import build_citations
from vg09.retrieval import Candidate


def make_chunk(
    doc_id: str, title: str, feed_date: str = "2026-09-16", source: str = "hf",
    url: str | None = None, text_source: str | None = None,
    arxiv_published_at: str | None = None,
) -> Candidate:
    return Candidate(
        id=f"{source}:{doc_id}:0",
        text="chunk text",
        metadata={
            "doc_id": doc_id,
            "title": title,
            "feed_date": feed_date,
            "url": url or f"https://example.com/{doc_id}",
            "source": source,
            **({"text_source": text_source} if text_source is not None else {}),
            **({"arxiv_published_at": arxiv_published_at} if arxiv_published_at is not None else {}),
        },
    )


class BuildCitationsTests(unittest.TestCase):
    def test_resolves_a_numeric_citation_to_a_real_chunk(self):
        chunk = make_chunk("2609.08183", "NeoHorse-1", feed_date="2026-09-09")
        source_map = {1: chunk}
        result = build_citations("NeoHorse is mentioned in [1].", source_map)

        self.assertEqual(len(result.citations), 1)
        c = result.citations[0]
        self.assertEqual(c.doc_id, "2609.08183")
        self.assertEqual(c.title, "NeoHorse-1")
        self.assertEqual(c.feed_date, "2026-09-09")
        self.assertEqual(result.unlinked_references, [])

    def test_out_of_range_number_is_unlinked_not_dropped(self):
        source_map = {1: make_chunk("doc1", "Title 1")}
        result = build_citations("See [99] for details.", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, ["[99]"])

    def test_non_numeric_bracket_is_unlinked(self):
        """The originally-requested [Title, YYYY-MM-DD] format, if the model still
        produces it, is not parsed/guessed at - it's reported as unlinked."""
        source_map = {1: make_chunk("doc1", "Title 1")}
        result = build_citations("As shown in [Title 1, 2026-09-09].", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, ["[Title 1, 2026-09-09]"])

    def test_dedup_by_doc_id_across_two_different_citation_numbers(self):
        """Two chunks of the same document, cited via two different numbers, produce
        one citation - not two."""
        chunk_a = make_chunk("doc1", "Title 1")
        chunk_b = make_chunk("doc1", "Title 1")  # same doc_id, a different chunk
        source_map = {1: chunk_a, 2: chunk_b}
        result = build_citations("First [1], then again [2].", source_map)
        self.assertEqual(len(result.citations), 1)

    def test_the_same_number_cited_twice_produces_one_citation(self):
        source_map = {1: make_chunk("doc1", "Title 1")}
        result = build_citations("[1] says X, and [1] also says Y.", source_map)
        self.assertEqual(len(result.citations), 1)

    def test_unlinked_references_are_deduplicated_too(self):
        source_map: dict[int, Candidate] = {}
        result = build_citations("See [99] and also [99] again.", source_map)
        self.assertEqual(result.unlinked_references, ["[99]"])

    def test_youtube_url_with_timestamp_is_passed_through_unmodified(self):
        """T-012 already bakes &t=SECONDS into a windowed YouTube chunk's own url -
        this module doesn't need to (and must not) construct it itself."""
        chunk = make_chunk(
            "abc123", "Some Video", source="youtube",
            url="https://www.youtube.com/watch?v=abc123&t=90",
        )
        result = build_citations("[1]", {1: chunk})
        self.assertEqual(result.citations[0].url, "https://www.youtube.com/watch?v=abc123&t=90")

    def test_hf_citation_carries_arxiv_published_at(self):
        chunk = make_chunk("2609.08183", "NeoHorse-1", arxiv_published_at="2026-09-01T00:00:00.000Z")
        result = build_citations("[1]", {1: chunk})
        self.assertEqual(result.citations[0].arxiv_published_at, "2026-09-01T00:00:00.000Z")

    def test_youtube_citation_has_no_arxiv_published_at(self):
        chunk = make_chunk("abc123", "Some Video", source="youtube")
        result = build_citations("[1]", {1: chunk})
        self.assertIsNone(result.citations[0].arxiv_published_at)

    def test_fallback_document_is_marked_as_such(self):
        chunk = make_chunk("abc123", "Some Video", source="youtube", text_source="title_description")
        result = build_citations("[1]", {1: chunk})
        self.assertTrue(result.citations[0].is_fallback)

    def test_real_transcript_chunk_is_not_marked_fallback(self):
        chunk = make_chunk("abc123", "Some Video", source="youtube", text_source="captions")
        result = build_citations("[1]", {1: chunk})
        self.assertFalse(result.citations[0].is_fallback)

    def test_no_citations_at_all_in_the_answer(self):
        result = build_citations("This answer has no brackets at all.", {1: make_chunk("d", "t")})
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])

    def test_empty_source_map_makes_every_bracket_unlinked(self):
        result = build_citations("See [1] and [2].", {})
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, ["[1]", "[2]"])


if __name__ == "__main__":
    unittest.main()
