"""Unit tests for vg09.ui_helpers (T-025, T-029, T-042)."""

from __future__ import annotations

import unittest
from datetime import date

from vg09.citations import Citation
from vg09.retrieval import Candidate
from vg09.ui_helpers import (
    build_retrieval_ranks,
    citation_source_type,
    describe_retrieval_mode,
    escape_markdown_link_text,
    format_date_range_short,
    render_citation_chips,
    text_source_label,
)

# T-029: a real title, not synthetic - copied verbatim from
# data/raw/youtube/2026-09-16/S2VJU5DQqlU.json's "title" field (data/raw/ is
# gitignored per D-004, so the test embeds the real string rather than reading it
# live - same pattern test_llm.py/test_chunking.py use for other real-shaped data).
REAL_PARENTHETICAL_TITLE = "He Built The Ultimate Spy Tool (Free and Open-Source)"


def make_chunk(doc_id: str, url: str, feed_date_ordinal: int = 0) -> Candidate:
    return Candidate(
        id=f"{doc_id}:0", text="chunk text",
        metadata={"doc_id": doc_id, "url": url, "feed_date_ordinal": feed_date_ordinal},
    )


def make_citation(doc_id: str, url: str, text_source: str | None = None) -> Citation:
    return Citation(
        doc_id=doc_id, title=f"Title {doc_id}", feed_date="2026-09-16", url=url,
        is_fallback=(text_source == "title_description"), text_source=text_source,
    )


class EscapeMarkdownLinkTextTests(unittest.TestCase):
    def test_real_parenthetical_title_round_trips_intact(self):
        """T-029: parens inside a markdown [text] portion don't need escaping under
        CommonMark, but this confirms a real title survives escaping unmangled - no
        accidental corruption of ordinary punctuation, only the genuinely dangerous
        characters get a backslash."""
        escaped = escape_markdown_link_text(REAL_PARENTHETICAL_TITLE)
        self.assertIn("(Free and Open-Source)", escaped)
        self.assertIn("He Built The Ultimate Spy Tool", escaped)

    def test_closing_bracket_is_escaped_so_the_link_cannot_be_cut_short(self):
        title = "New Model [SOTA]"
        escaped = escape_markdown_link_text(title)
        # the raw, unescaped "]" that would close a [text](url) link early is gone -
        # every bracket in the output is backslash-escaped
        self.assertNotIn(title, escaped)  # escaping actually changed something
        self.assertIn("\\[SOTA\\]", escaped)

    def test_backslash_is_escaped_first_so_output_is_not_double_escaped(self):
        title = "C:\\path and a * and a _"
        escaped = escape_markdown_link_text(title)
        self.assertEqual(escaped, "C:\\\\path and a \\* and a \\_")


class DescribeRetrievalModeTests(unittest.TestCase):
    """T-042/D-016: English text - was Swedish before this ticket."""

    def test_manual_override_wins_even_with_an_interpreted_window_present(self):
        override = (date(2020, 1, 1), date(2020, 1, 31))
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=override)
        self.assertIn("manually", result)
        self.assertIn("2020-01-01", result)

    def test_interpreted_window_shown_when_no_override(self):
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=None)
        self.assertIn("interpreted", result)
        self.assertIn("2026-09-10", result)
        self.assertIn("2026-09-16", result)

    def test_ranking_mode_shown_when_no_window_and_no_override(self):
        result = describe_retrieval_mode(None, ranking=True, manual_override=None)
        self.assertIn("most recent", result)

    def test_unfiltered_when_nothing_fired(self):
        result = describe_retrieval_mode(None, ranking=False, manual_override=None)
        self.assertIn("No date filter", result)


class FormatDateRangeShortTests(unittest.TestCase):
    """T-044: the pipeline strip's "Date range" tile."""

    def test_none_renders_as_none(self):
        self.assertEqual(format_date_range_short(None), "None")

    def test_same_month_range_is_month_day_dash_day(self):
        result = format_date_range_short((date(2026, 9, 11), date(2026, 9, 17)))
        self.assertEqual(result, "Sep 11-17")

    def test_single_day_range_is_just_month_day(self):
        result = format_date_range_short((date(2026, 9, 16), date(2026, 9, 16)))
        self.assertEqual(result, "Sep 16")

    def test_range_crossing_a_month_boundary_names_both_months(self):
        result = format_date_range_short((date(2026, 8, 28), date(2026, 9, 3)))
        self.assertEqual(result, "Aug 28 - Sep 3")

    def test_range_crossing_a_year_boundary_still_reads_correctly(self):
        result = format_date_range_short((date(2025, 12, 20), date(2026, 1, 2)))
        self.assertEqual(result, "Dec 20 - Jan 2")

    def test_no_platform_specific_strftime_flags_double_digit_days_unaffected(self):
        """Built by hand, not date.strftime() - %-d (no leading zero) is a POSIX
        extension this project's real Windows environment doesn't support (KB-005-
        adjacent portability concern, not a formatting nicety)."""
        result = format_date_range_short((date(2026, 9, 1), date(2026, 9, 9)))
        self.assertEqual(result, "Sep 1-9")  # single-digit days, no leading zero either way


class CitationSourceTypeTests(unittest.TestCase):
    def test_huggingface_url_is_a_paper(self):
        self.assertEqual(citation_source_type("https://huggingface.co/papers/2609.12345"), "paper")

    def test_youtube_url_is_a_video(self):
        self.assertEqual(
            citation_source_type("https://www.youtube.com/watch?v=abc123&t=90"), "video"
        )

    def test_unrecognized_url_is_unknown_not_guessed(self):
        self.assertEqual(citation_source_type("https://example.com/whatever"), "unknown")


class TextSourceLabelTests(unittest.TestCase):
    def test_none_stays_none_hf_papers_have_no_text_source(self):
        self.assertIsNone(text_source_label(None))

    def test_captions_whisper_and_title_description_are_distinct(self):
        self.assertEqual(text_source_label("captions"), "captions")
        self.assertEqual(text_source_label("whisper"), "whisper")
        self.assertEqual(text_source_label("title_description"), "title + description")


class BuildRetrievalRanksTests(unittest.TestCase):
    def test_first_occurrence_of_each_doc_id_is_its_rank(self):
        chunks = [make_chunk("docA", "u"), make_chunk("docB", "u"), make_chunk("docA", "u")]
        ranks = build_retrieval_ranks(chunks)
        self.assertEqual(ranks, {"docA": 1, "docB": 2})

    def test_empty_chunks_gives_an_empty_map(self):
        self.assertEqual(build_retrieval_ranks([]), {})


class RenderCitationChipsTests(unittest.TestCase):
    def test_a_resolved_single_number_becomes_one_chip_linking_to_its_card(self):
        chunk = make_chunk("doc1", "https://huggingface.co/papers/1")
        citation = make_citation("doc1", "https://huggingface.co/papers/1")
        result = render_citation_chips(
            "NeoHorse is mentioned in [1].", {1: chunk}, [citation],
            unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="#cite-1"', result)
        self.assertIn("chip-paper", result)
        self.assertIn(">1<", result)
        self.assertNotIn("[1]", result)

    def test_video_citation_gets_the_video_chip_class(self):
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc")
        citation = make_citation("vid1", "https://www.youtube.com/watch?v=abc")
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn("chip-video", result)

    def test_comma_bracket_becomes_one_chip_per_number(self):
        c1, c2 = make_chunk("doc1", "https://huggingface.co/papers/1"), \
            make_chunk("doc2", "https://huggingface.co/papers/2")
        citations = [make_citation("doc1", c1.metadata["url"]), make_citation("doc2", c2.metadata["url"])]
        result = render_citation_chips(
            "[17, 18]", {17: c1, 18: c2}, citations, unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="#cite-1"', result)
        self.assertIn('href="#cite-2"', result)

    def test_unlinked_bracket_is_left_as_plain_text_not_a_chip(self):
        result = render_citation_chips(
            "See [99] for details.", {}, [], unlinked_references=["[99]"], descriptive_ranges=[],
        )
        self.assertEqual(result, "See [99] for details.")
        self.assertNotIn("citation-chip", result)

    def test_descriptive_range_is_left_as_plain_text_not_a_chip(self):
        result = render_citation_chips(
            "All 20 sources [1-20].", {}, [], unlinked_references=[], descriptive_ranges=["[1-20]"],
        )
        self.assertEqual(result, "All 20 sources [1-20].")
        self.assertNotIn("citation-chip", result)

    def test_two_numbers_citing_the_same_document_link_to_the_same_card(self):
        chunk_a = make_chunk("doc1", "https://huggingface.co/papers/1")
        chunk_b = make_chunk("doc1", "https://huggingface.co/papers/1")  # a second chunk, same doc
        citation = make_citation("doc1", "https://huggingface.co/papers/1")
        result = render_citation_chips(
            "First [1], then again [2].", {1: chunk_a, 2: chunk_b}, [citation],
            unlinked_references=[], descriptive_ranges=[],
        )
        self.assertEqual(result.count('href="#cite-1"'), 2)

    def test_no_brackets_at_all_is_unchanged(self):
        result = render_citation_chips(
            "No citations here.", {}, [], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertEqual(result, "No citations here.")


if __name__ == "__main__":
    unittest.main()
