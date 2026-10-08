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

    def test_real_shape_three_sources_in_one_bracket_all_resolve(self):
        """T-028's real find: a real answer cited three sources in one bracket
        ("[17, 18, 19]") and only produced one citation before this fix - all three
        must resolve now."""
        source_map = {
            17: make_chunk("doc17", "Agent as Policy"),
            18: make_chunk("doc18", "RSIAgent"),
            19: make_chunk("doc19", "Atria Dawn Preview"),
        }
        result = build_citations("Several advances happened [17, 18, 19] this week.", source_map)
        self.assertEqual({c.doc_id for c in result.citations}, {"doc17", "doc18", "doc19"})
        self.assertEqual(len(result.citations), 3)
        self.assertEqual(result.unlinked_references, [])

    def test_multiple_numbers_no_space_between_them(self):
        source_map = {17: make_chunk("doc17", "A"), 18: make_chunk("doc18", "B")}
        result = build_citations("[17,18]", source_map)
        self.assertEqual({c.doc_id for c in result.citations}, {"doc17", "doc18"})

    def test_multiple_numbers_one_resolves_one_out_of_range(self):
        source_map = {17: make_chunk("doc17", "A")}
        result = build_citations("Claim [17, 99].", source_map)
        self.assertEqual(len(result.citations), 1)
        self.assertEqual(result.citations[0].doc_id, "doc17")
        self.assertEqual(result.unlinked_references, ["[99]"])

    def test_multiple_numbers_same_doc_deduplicated_within_one_bracket(self):
        chunk_a = make_chunk("doc1", "Title")
        chunk_b = make_chunk("doc1", "Title")  # a second chunk of the same document
        source_map = {1: chunk_a, 2: chunk_b}
        result = build_citations("[1, 2]", source_map)
        self.assertEqual(len(result.citations), 1)

    def test_non_numeric_comma_bracket_is_still_one_whole_unlinked_reference(self):
        """A bracket that isn't a list of bare numbers (T-024's original case) is not
        torn apart just because it contains a comma - unchanged from before this fix."""
        source_map = {1: make_chunk("doc1", "Title 1")}
        result = build_citations("As shown in [Title 1, 2026-09-09].", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, ["[Title 1, 2026-09-09]"])


class RangeCitationTests(unittest.TestCase):
    """T-040/D-015: numeric ranges in a bracket ("[1-20]", "[21-22]"). D-015's real
    data: T-032's F10-A wrote a real short-range citation ([21-22], 2 sources) that
    T-028's comma-only splitting couldn't resolve, alongside a long range ([1-20])
    describing "all 20 sources today" rather than citing evidence; F12-A wrote a
    similar long range ([1-31]) on a "not mentioned" answer - the exact false-positive
    shape T-024's own ticket predicted. The three tests below are built directly from
    those real bracket/source-count shapes."""

    def _source_map(self, n: int) -> dict[int, object]:
        return {i: make_chunk(f"doc{i}", f"Title {i}") for i in range(1, n + 1)}

    def test_real_shape_short_range_resolves_like_a_comma_list(self):
        """F10-A's real [21-22] - 2 numbers, a genuine two-source citation - must
        resolve exactly as a comma-separated bracket would, not fall into
        unlinked_references the way it did before this fix."""
        source_map = self._source_map(22)
        result = build_citations("A YouTube video covered this [21-22].", source_map)
        self.assertEqual({c.doc_id for c in result.citations}, {"doc21", "doc22"})
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, [])

    def test_real_shape_range_covering_the_days_papers_is_descriptive(self):
        """F10-A's real [1-20] - "all 20 papers and videos listed... [1-20]" - is a
        descriptive enumeration of everything offered that day, not a citation for a
        specific claim; must not expand into 20 citations."""
        source_map = self._source_map(20)
        result = build_citations(
            "All 20 papers and videos listed in the sources were published today [1-20].",
            source_map,
        )
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, ["[1-20]"])

    def test_real_shape_reviewed_all_sources_range_is_descriptive_not_31_citations(self):
        """F12-A's real [1-31] - "I've carefully reviewed all 38 sources (from [1] to
        [38])"-shaped answer, here at the real F12 scale (31 offered sources) - must
        not silently become 31 false-positive citations on a correct "not mentioned"
        answer (T-024's own predicted risk, now real)."""
        source_map = self._source_map(31)
        result = build_citations(
            "No, Palantir has not been mentioned in any of the provided sources [1-31].",
            source_map,
        )
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, ["[1-31]"])

    def test_same_claim_spelled_out_as_31_comma_separated_bare_numbers_is_also_descriptive(self):
        """T-041, real gap the first version of D-015 left open: the identical F12-A
        "reviewed all sources" claim, but with the model spelling out every number
        individually instead of writing a range - "[1,2,3,...,31]" rather than
        "[1-31]". Must classify the same way: descriptive, not 31 citations. Before
        T-041 this resolved as 31 real citations, since each bare number's own span
        is 1 and the original check only looked at one piece at a time."""
        source_map = self._source_map(31)
        bracket = "[" + ",".join(str(n) for n in range(1, 32)) + "]"
        result = build_citations(f"No, Palantir has not been mentioned {bracket}.", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, [bracket])

    def test_threshold_boundary_exactly_five_resolves_six_is_descriptive(self):
        source_map = self._source_map(6)
        at_threshold = build_citations("[1-5]", source_map)
        self.assertEqual(len(at_threshold.citations), 5)
        self.assertEqual(at_threshold.descriptive_ranges, [])

        over_threshold = build_citations("[1-6]", source_map)
        self.assertEqual(over_threshold.citations, [])
        self.assertEqual(over_threshold.descriptive_ranges, ["[1-6]"])

    def test_out_of_range_number_within_a_short_range_is_unlinked_individually(self):
        """Mirrors T-028's existing out-of-range-within-comma-list behavior: the
        numbers that do resolve still become citations, only the missing one is
        reported, and the range itself is not treated as descriptive just because one
        number in it doesn't exist."""
        source_map = {1: make_chunk("doc1", "A"), 2: make_chunk("doc2", "B")}
        result = build_citations("Claim [1-3].", source_map)
        self.assertEqual({c.doc_id for c in result.citations}, {"doc1", "doc2"})
        self.assertEqual(result.unlinked_references, ["[3]"])
        self.assertEqual(result.descriptive_ranges, [])

    def test_reversed_range_is_unlinked_not_treated_as_a_citation_shape(self):
        source_map = self._source_map(5)
        result = build_citations("See [5-1].", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, ["[5-1]"])
        self.assertEqual(result.descriptive_ranges, [])

    def test_range_mixed_with_a_comma_number_all_short_resolves_normally(self):
        source_map = self._source_map(3)
        result = build_citations("[1, 2-3]", source_map)
        self.assertEqual({c.doc_id for c in result.citations}, {"doc1", "doc2", "doc3"})
        self.assertEqual(result.descriptive_ranges, [])

    def test_range_mixed_with_a_comma_number_long_range_makes_whole_bracket_descriptive(self):
        """A long range dominates the bracket even when paired with an otherwise-valid
        short piece - the bracket as a whole isn't a real per-source citation."""
        source_map = self._source_map(10)
        result = build_citations("[1, 2-10]", source_map)
        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, ["[1, 2-10]"])

    def test_pathological_huge_range_is_descriptive_immediately_not_materialized(self):
        """independent review finding (2026-09-22): a hallucinated or malformed huge range in
        real model output must be classified as descriptive from its bounds alone -
        never by actually building a list of its numbers first. Asserts both the
        classification and that it happens with no measurable delay (previously ~7s
        for this exact bracket, materializing 500 million ints)."""
        import time

        source_map = self._source_map(2)
        start = time.monotonic()
        result = build_citations("See [1-500000000].", source_map)
        elapsed = time.monotonic() - start

        self.assertEqual(result.citations, [])
        self.assertEqual(result.unlinked_references, [])
        self.assertEqual(result.descriptive_ranges, ["[1-500000000]"])
        self.assertLess(elapsed, 0.5, f"took {elapsed:.2f}s - range size was materialized")

    def test_descriptive_ranges_are_deduplicated(self):
        source_map = self._source_map(20)
        result = build_citations("[1-20] ... later, [1-20] again.", source_map)
        self.assertEqual(result.descriptive_ranges, ["[1-20]"])

    def test_existing_behavior_unaffected_comma_list_and_non_numeric_bracket(self):
        """T-028's comma-list resolution and T-024's non-numeric-bracket handling are
        unaffected by range support - full regression check in one place."""
        source_map = {
            17: make_chunk("doc17", "A"), 18: make_chunk("doc18", "B"), 99: make_chunk("doc99", "C"),
        }
        comma = build_citations("Several advances happened [17, 18] this week.", source_map)
        self.assertEqual({c.doc_id for c in comma.citations}, {"doc17", "doc18"})

        non_numeric = build_citations("As shown in [Title 1, 2026-09-09].", {1: make_chunk("doc1", "T")})
        self.assertEqual(non_numeric.citations, [])
        self.assertEqual(non_numeric.unlinked_references, ["[Title 1, 2026-09-09]"])


if __name__ == "__main__":
    unittest.main()
