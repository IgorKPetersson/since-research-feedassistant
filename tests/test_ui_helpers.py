"""Unit tests for vg09.ui_helpers (T-025, T-029, T-042, T-045)."""

from __future__ import annotations

import re
import string
import unittest
from datetime import date
from html import unescape as html_unescape
from pathlib import Path

from markdown_it import MarkdownIt

from vg09.citations import Citation, build_citations
from vg09.retrieval import Candidate
from vg09.ui_helpers import (
    ACCENT_COLOR,
    APP_NAME,
    CUSTOM_CSS,
    LOGO_MARK_PATH,
    WORD_JOINER,
    build_retrieval_ranks,
    citation_source_type,
    describe_retrieval_mode,
    escape_markdown_link_text,
    escape_markdown_text,
    format_corpus_summary,
    format_date_range_short,
    logo_mark_html,
    misattribution_note,
    reference_note,
    render_citation_chips,
    text_source_label,
)

# CommonMark, as a stand-in for Streamlit's markdown in the T-089 tests. It doesn't turn
# bare URLs into links as Streamlit does; that part was checked in the running app.
_MARKDOWN = MarkdownIt("commonmark")


def rendered_text(markdown: str) -> str:
    """What a reader sees once the markdown is rendered: tags dropped, entities decoded,
    and the invisible word joiners (T-089) left out."""
    shown = html_unescape(re.sub(r"<[^>]+>", "", _MARKDOWN.render(markdown)))
    return shown.replace(WORD_JOINER, "")

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
        self.assertNotIn("only", result)

    def test_a_source_filter_is_named_with_its_reason(self):
        """T-068: narrowing to one source is never silent."""
        self.assertIn("Papers only (the question mentions papers)",
                      describe_retrieval_mode(None, False, None, source="hf"))
        self.assertIn("Videos only (the question mentions videos)",
                      describe_retrieval_mode(None, False, None, source="youtube"))


class VisualIdentityTests(unittest.TestCase):
    """T-045: the app's real name, accent colour, and the CSS that actually applies
    them - not exhaustive CSS testing, just the concrete regressions worth catching
    (a typo in the hex breaking the config.toml/CSS cross-reference, the Google Font
    link disappearing, an icon-breaking blanket font-family selector creeping in)."""

    def test_app_name_is_since(self):
        self.assertEqual(APP_NAME, "Since")

    def test_accent_color_is_a_real_hex_and_matches_streamlit_config(self):
        self.assertRegex(ACCENT_COLOR, r"^#[0-9A-Fa-f]{6}$")
        config = Path(__file__).resolve().parent.parent / ".streamlit" / "config.toml"
        self.assertIn(ACCENT_COLOR, config.read_text(encoding="utf-8"),
                      "the CSS accent and .streamlit/config.toml's primaryColor must match")

    def test_accent_color_drives_the_citation_chip_css(self):
        self.assertIn(f"background-color: {ACCENT_COLOR}", CUSTOM_CSS)

    def test_citation_chip_text_overrides_streamlit_link_color(self):
        # Found live: without the scoped selector + !important, chips rendered as
        # blue underlined link text on the accent.
        self.assertIn('[data-testid="stMarkdownContainer"] a.citation-chip', CUSTOM_CSS)
        self.assertIn("color: #ffffff !important", CUSTOM_CSS)
        self.assertIn("text-decoration: none !important", CUSTOM_CSS)

    def test_streamlits_press_enter_hint_is_hidden(self):
        """T-080: the hint stayed while focus stayed in the field, long after the answer."""
        self.assertIn('[data-testid="InputInstructions"]', CUSTOM_CSS)
        self.assertIn("display: none", CUSTOM_CSS)

    def test_white_text_on_the_accent_reaches_wcag_aa(self):
        """T-050: the Ask button's label and the citation chips are white on the accent.
        Computed from the constant, so a lighter accent can't be chosen again unnoticed
        (T-045's #C17F1A was 3.32:1)."""
        def channel(value: int) -> float:
            s = value / 255
            return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

        r, g, b = (channel(int(ACCENT_COLOR[i:i + 2], 16)) for i in (1, 3, 5))
        accent_luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        self.assertGreaterEqual(1.05 / (accent_luminance + 0.05), 4.5)

    def test_logo_mark_svg_uses_the_accent_and_no_placeholder(self):
        svg = LOGO_MARK_PATH.read_text(encoding="utf-8")
        self.assertNotIn("CURRENT_ACCENT", svg)
        self.assertEqual(svg.count(ACCENT_COLOR), 3)

    def test_logo_mark_html_is_a_decorative_svg_data_uri_image(self):
        html = logo_mark_html()
        self.assertTrue(html.startswith('<img class="app-mark" src="data:image/svg+xml;base64,'))
        self.assertIn('alt=""', html)

    def test_source_badges_are_one_neutral_grey_not_per_type_colours(self):
        self.assertNotIn(".badge-video", CUSTOM_CSS)
        self.assertNotIn(".badge-paper", CUSTOM_CSS)
        self.assertIn("background-color: #6b6b6b", CUSTOM_CSS)

    def test_source_card_links_use_text_colour_with_accent_underline(self):
        self.assertIn(".st-key-source_cards", CUSTOM_CSS)
        self.assertIn(f"text-decoration-color: {ACCENT_COLOR} !important", CUSTOM_CSS)

    def test_google_font_is_loaded(self):
        self.assertIn("fonts.googleapis.com", CUSTOM_CSS)
        self.assertIn("Instrument+Sans", CUSTOM_CSS)

    def test_font_family_override_does_not_use_a_blanket_universal_selector(self):
        """A bare "*" selector would also override Streamlit's own higher-specificity
        icon-font rules (e.g. the reasoning expander's arrow glyph), turning icons
        into literal text - found and avoided while building this ticket, not just a
        style nitpick. Scoped to [data-testid] (Streamlit's own content wrappers,
        never its icon elements) instead - also found live: html/body/.stApp alone
        lost a real cascade tie against Streamlit's own font rule on
        [data-testid="stMarkdownContainer"]."""
        self.assertIn("html, body, .stApp, [data-testid], [data-testid] *", CUSTOM_CSS)
        self.assertNotRegex(CUSTOM_CSS, r"\n\*\s*\{[^}]*font-family")

    def test_font_is_loaded_via_a_style_import_not_a_link_tag(self):
        """Found live: st.html() silently strips <link> tags entirely - an @import
        inside <style> survives instead."""
        self.assertIn("@import url(", CUSTOM_CSS)
        self.assertNotIn("<link", CUSTOM_CSS)


class FormatCorpusSummaryTests(unittest.TestCase):
    """T-045: the compact header's right-hand side."""

    def test_includes_all_three_counts_and_the_freshness_date(self):
        stats = {"hf_documents": 1184, "youtube_documents": 41, "chunks": 1971}
        result = format_corpus_summary(stats, date(2026, 9, 17))
        self.assertIn("1184 papers", result)
        self.assertIn("41 videos", result)
        self.assertIn("1971 chunks", result)
        self.assertIn("2026-09-17", result)

    def test_no_freshness_date_when_the_store_has_never_been_populated(self):
        stats = {"hf_documents": 0, "youtube_documents": 0, "chunks": 0}
        result = format_corpus_summary(stats, None)
        self.assertIn("0 papers", result)
        self.assertNotIn("Caught up", result)


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
    def test_a_resolved_single_number_becomes_one_chip_opening_its_source(self):
        """T-062: a chip opens the source itself in a new tab, not the card below."""
        chunk = make_chunk("doc1", "https://huggingface.co/papers/1")
        citation = make_citation("doc1", "https://huggingface.co/papers/1")
        result = render_citation_chips(
            "NeoHorse is mentioned in [1].", {1: chunk}, [citation],
            unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="https://huggingface.co/papers/1"', result)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('class="citation-chip"', result)
        self.assertIn(">1<", result)
        self.assertNotIn("[1]", result)

    def test_a_video_chip_opens_the_cited_excerpts_own_moment(self):
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc&t=95")
        citation = make_citation("vid1", "https://www.youtube.com/watch?v=abc&t=12")
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="https://www.youtube.com/watch?v=abc&amp;t=95"', result)

    def test_a_chip_names_its_source_type_and_title_escaped(self):
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc")
        citation = make_citation("vid1", "https://www.youtube.com/watch?v=abc")
        citation.title = 'The "Best" <Model>'
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
        )
        expected = 'Video: The &quot;Best&quot; &lt;Model&gt;'
        self.assertIn(f'title="{expected}"', result)
        self.assertIn(f'aria-label="{expected}"', result)

    def test_video_citation_also_gets_the_one_shared_chip_class(self):
        """T-045: chips dropped T-042's per-source-type colouring by my explicit
        decision - a paper and a video citation render identically now (source type
        stays visible via the unchanged PAPER/VIDEO source-card badge instead)."""
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc")
        citation = make_citation("vid1", "https://www.youtube.com/watch?v=abc")
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('class="citation-chip"', result)
        self.assertNotIn("chip-video", result)
        self.assertNotIn("chip-paper", result)

    def test_a_quoted_video_chip_links_to_the_quote_and_says_so(self):
        """T-063: the quote is spoken at 9:50; the link starts two seconds early."""
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc&t=572")
        chunk.metadata["start_seconds"] = 572.04
        citation = make_citation("vid1", chunk.metadata["url"])
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
            quote_seconds={1: 590.48},
        )
        self.assertIn('href="https://www.youtube.com/watch?v=abc&amp;t=588"', result)
        self.assertIn("(the quote, at 9:48)", result)

    def test_an_unquoted_video_chip_says_where_the_excerpt_starts(self):
        chunk = make_chunk("vid1", "https://www.youtube.com/watch?v=abc&t=572")
        chunk.metadata["start_seconds"] = 572.04
        citation = make_citation("vid1", chunk.metadata["url"])
        result = render_citation_chips(
            "[1]", {1: chunk}, [citation], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="https://www.youtube.com/watch?v=abc&amp;t=572"', result)
        self.assertIn("(excerpt from 9:32, about 1.5 minutes long)", result)

    def test_comma_bracket_becomes_one_chip_per_number(self):
        c1, c2 = make_chunk("doc1", "https://huggingface.co/papers/1"), \
            make_chunk("doc2", "https://huggingface.co/papers/2")
        citations = [make_citation("doc1", c1.metadata["url"]), make_citation("doc2", c2.metadata["url"])]
        result = render_citation_chips(
            "[17, 18]", {17: c1, 18: c2}, citations, unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn('href="https://huggingface.co/papers/1"', result)
        self.assertIn('href="https://huggingface.co/papers/2"', result)

    def test_unlinked_bracket_is_left_as_plain_text_not_a_chip(self):
        result = render_citation_chips(
            "See [99] for details.", {}, [], unlinked_references=["[99]"], descriptive_ranges=[],
        )
        self.assertIn("<p>See [99] for details.</p>", result)  # T-072: rendered as HTML
        self.assertNotIn("citation-chip", result)

    def test_descriptive_range_is_left_as_plain_text_not_a_chip(self):
        result = render_citation_chips(
            "All 20 sources [1-20].", {}, [], unlinked_references=[], descriptive_ranges=["[1-20]"],
        )
        self.assertIn("<p>All 20 sources [1-20].</p>", result)
        self.assertNotIn("citation-chip", result)

    def test_two_numbers_citing_the_same_document_both_become_chips(self):
        chunk_a = make_chunk("doc1", "https://huggingface.co/papers/1")
        chunk_b = make_chunk("doc1", "https://huggingface.co/papers/1")  # a second chunk, same doc
        citation = make_citation("doc1", "https://huggingface.co/papers/1")
        result = render_citation_chips(
            "First [1], then again [2].", {1: chunk_a, 2: chunk_b}, [citation],
            unlinked_references=[], descriptive_ranges=[],
        )
        self.assertEqual(result.count('href="https://huggingface.co/papers/1"'), 2)

    def test_no_brackets_at_all_is_unchanged(self):
        result = render_citation_chips(
            "No citations here.", {}, [], unlinked_references=[], descriptive_ranges=[],
        )
        self.assertIn("<p>No citations here.</p>", result)


class AnswerRenderingSafetyTests(unittest.TestCase):
    """T-072 (D-020): nothing the model writes becomes live HTML, and the app's own chips
    survive however the model formats its answer."""

    def render(self, answer, urls=None):
        urls = urls or {1: "https://huggingface.co/papers/1", 2: "https://www.youtube.com/watch?v=v2&t=5"}
        source_map = {n: make_chunk(f"doc{n}", u) for n, u in urls.items()}
        citations = [make_citation(f"doc{n}", u) for n, u in urls.items()]
        return render_citation_chips(answer, source_map, citations,
                                     unlinked_references=[], descriptive_ranges=[])

    def test_html_written_by_the_model_is_shown_as_text(self):
        for injected, tag in (('<img src=x onerror="alert(1)">', "<img"),
                              ("<script>alert(1)</script>", "<script"),
                              ('<a href="javascript:alert(1)">click</a>', '<a href="javascript'),
                              ('<iframe src="https://evil.example"></iframe>', "<iframe")):
            result = self.render(f"Answer {injected} [1].")
            self.assertNotIn(tag, result, injected)
            self.assertIn("&lt;", result, injected)
            self.assertIn('class="citation-chip"', result, injected)

    def test_markdown_links_and_images_written_by_the_model_are_not_links(self):
        for injected in ("[click](javascript:alert(1))", "[site](https://evil.example)",
                         "![x](https://evil.example/p.png)", "<https://evil.example>"):
            result = self.render(f"See {injected} and [1].")
            self.assertNotIn("evil.example\"", result, injected)
            self.assertNotIn('href="javascript', result, injected)
            self.assertNotIn("<img", result, injected)
            self.assertEqual(result.count("<a "), 1, injected)  # only the chip

    def test_backticks_around_citations_cannot_turn_chips_into_visible_html(self):
        """My 2026-10-05 report: a code span the model opened swallowed chips
        29-31, shown as raw `<a class="citation-chip" ...>` text. Reproduced in Streamlit."""
        result = self.render("Sources [1] text `Claude\n[2] Gemini` and [2] again.")
        self.assertNotIn("&lt;a class", result)
        self.assertIn("<code>Claude [2] Gemini</code>", result)  # the model's own code, as text
        self.assertEqual(result.count('class="citation-chip"'), 2)  # [1] and the last [2]

    def test_a_chip_is_only_built_for_an_https_url_on_a_source_host(self):
        for url in ("https://evil.example/papers/1", "http://huggingface.co/papers/1",
                    "javascript:alert(1)", "https://huggingface.co.evil.example/x"):
            result = self.render("Claim [1].", urls={1: url})
            self.assertNotIn("citation-chip", result, url)
            self.assertIn("Claim [1].", result, url)
        for url in ("https://huggingface.co/papers/1", "https://arxiv.org/abs/2609.1",
                    "https://www.youtube.com/watch?v=x&t=3", "https://youtube.com/watch?v=x"):
            self.assertIn("citation-chip", self.render("Claim [1].", urls={1: url}), url)

    def test_ordinary_markdown_still_renders(self):
        result = self.render("**Bold** intro.\n\n1. first [1]\n2. second [2]\n\n- dash item")
        self.assertIn("<strong>Bold</strong>", result)
        self.assertIn("<ol>", result)
        self.assertIn("<ul>", result)
        self.assertEqual(result.count('class="citation-chip"'), 2)

    def test_output_is_one_line_so_streamlit_keeps_it_one_html_block(self):
        """A blank line would end the HTML block and hand the rest back to Streamlit's
        markdown, which is how chips became text in the first place."""
        result = self.render("Para one [1].\n\nPara two [2].\n\n```\ncode\n\nmore\n```")
        self.assertNotIn("\n", result)
        self.assertTrue(result.startswith("<div"))
        self.assertIn("code&#10;&#10;more", result)  # line breaks inside code survive


# Tags the app itself puts around an answer; anything else in the output came from the model.
_APP_TAGS = {"div", "p"}
_CHIP_RE = re.compile(r'<a class="citation-chip" [^>]*>\d+</a>')
# An address nothing listens on, so a rendered fixture can never send anything anywhere.
_INERT_URL = "http://127.0.0.1:9/leak.png?q=question"


class BracketedAnswerTextSafetyTests(unittest.TestCase):
    """T-089 (D-020): text in square brackets is escaped like the rest of the answer.

    These go through `build_citations()` first, as `app.py` does. The tests above pass
    empty unlinked lists, which is how a bracket that `build_citations()` reports as
    unlinked reached the page unescaped (reproduced 2026-10-09)."""

    def render(self, answer, urls=None):
        urls = {1: "https://huggingface.co/papers/1"} if urls is None else urls
        source_map = {
            n: Candidate(id=f"doc{n}:0", text="chunk text", metadata={
                "doc_id": f"doc{n}", "url": u, "title": f"Title {n}", "feed_date": "2026-10-01",
            })
            for n, u in urls.items()
        }
        found = build_citations(answer, source_map)
        return render_citation_chips(answer, source_map, found.citations,
                                     found.unlinked_references, found.descriptive_ranges)

    def model_tags(self, html):
        """Every tag left once the app's own chips are removed."""
        return set(re.findall(r"<\s*/?\s*([a-zA-Z][\w-]*)", _CHIP_RE.sub("", html))) - _APP_TAGS

    def test_html_inside_brackets_is_escaped_and_valid_chips_still_link(self):
        for injected in (f'<img src="{_INERT_URL}">',
                         '<img src=x onerror="alert(1)">',
                         '<svg onload="alert(1)"></svg>',
                         "<script>alert(1)</script>",
                         f'<a href="{_INERT_URL}">log in</a>',
                         f'<iframe src="{_INERT_URL}"></iframe>',
                         '<div style="position:fixed;inset:0">x</div>',
                         "<b>bold</b>"):
            result = self.render(f"Claim [1]. See [{injected}].")
            self.assertEqual(self.model_tags(result), set(), injected)
            self.assertIn("&lt;", result, injected)  # the attempt stays visible, as text
            self.assertEqual(result.count('class="citation-chip"'), 1, injected)
            self.assertIn('href="https://huggingface.co/papers/1"', result, injected)

    def test_bracketed_prose_stays_visible_as_text(self):
        result = self.render("As shown [Title, 2026-09-09] and [<b>this</b>].")
        self.assertIn("[Title, 2026-09-09]", result)
        self.assertIn("[&lt;b&gt;this&lt;/b&gt;]", result)
        self.assertNotIn("citation-chip", result)

    def test_unlinked_number_and_descriptive_range_stay_visible(self):
        result = self.render("Claim [1]. Also [99], and all of them [1-20].")
        self.assertIn("[99]", result)
        self.assertIn("[1-20]", result)
        self.assertEqual(result.count('class="citation-chip"'), 1)

    def test_malformed_brackets_with_html_are_escaped(self):
        for answer in ("Odd [1,, <i>2</i>] here.", "Odd [1-<b>3</b>] here.",
                       "Odd [<img src=x onerror=alert(1)> here.",
                       "Odd ]<img src=x onerror=alert(1)>[ here.",
                       "Nested [[<img src=x onerror=alert(1)>]] here."):
            self.assertEqual(self.model_tags(self.render(answer)), set(), answer)

    def test_entity_encoded_html_in_brackets_stays_text(self):
        """The markdown parser decodes `&lt;` to `<` before the chip step sees the text."""
        for answer in ("See [&lt;img src=x onerror=alert(1)&gt;].",
                       "See [&#60;img src=x onerror=alert(1)&#62;].",
                       "See [\\<img src=x onerror=alert(1)\\>]."):
            self.assertEqual(self.model_tags(self.render(answer)), set(), answer)

    def test_html_outside_brackets_is_still_escaped(self):
        result = self.render('Before <img src=x onerror="alert(1)"> after [1].')
        self.assertEqual(self.model_tags(result), set())
        self.assertIn("&lt;img", result)


class EscapeMarkdownTextTests(unittest.TestCase):
    """T-089: model text shown through Streamlit's markdown outside the answer."""

    ATTEMPTS = ("<https://evil.example>", "[x](https://evil.example)",
                "![i](https://evil.example/p.png)", "*em* **strong** `code`",
                "# heading", "- item", "> quote", "$x^2$", "a \\[b\\] c", "1. first")

    def test_every_ascii_punctuation_mark_is_escaped(self):
        self.assertEqual(escape_markdown_text(string.punctuation).replace(WORD_JOINER, ""),
                         "".join(f"\\{ch}" for ch in string.punctuation))

    def test_bare_urls_www_and_emails_are_broken_up(self):
        """Streamlit's GFM autolinks ignore backslashes; the word joiner stops them."""
        escaped = escape_markdown_text("https://a.example www.b.example me@c.example mailto:x")
        for pattern in ("https\\:", "www\\.", "me\\@", "mailto\\:"):
            self.assertNotIn(pattern, escaped)
        self.assertEqual(escaped.count(WORD_JOINER), 7)  # 2 + 2 + 2 + 1

    def test_no_markdown_forms_and_the_text_reads_unchanged(self):
        for attempt in self.ATTEMPTS:
            html = _MARKDOWN.render(escape_markdown_text(attempt))
            self.assertEqual(re.findall(r"<(\w+)", html), ["p"], attempt)
            self.assertEqual(rendered_text(escape_markdown_text(attempt)).strip(), attempt, attempt)

    def test_line_breaks_become_spaces(self):
        self.assertEqual(escape_markdown_text("one\n\n- two"), "one \\- two")


class ReferenceNoteTests(unittest.TestCase):
    """T-089: the captions listing unlinked brackets and descriptive ranges."""

    def test_nothing_to_list_gives_no_note(self):
        self.assertIsNone(reference_note("Unlinked: ", []))

    def test_brackets_are_listed_as_they_were_written(self):
        note = reference_note("Unlinked: ", ["[99]", "[Title, 2026-09-09]"])
        self.assertEqual(rendered_text(note).strip(), "Unlinked: [99], [Title, 2026-09-09]")

    def test_a_bracket_cannot_become_a_link_or_image(self):
        note = reference_note("Unlinked: ", ["[<https://evil.example>]", "[![i]",
                                             "[<img src=x onerror=alert(1)>]"])
        html = _MARKDOWN.render(note)
        self.assertEqual(re.findall(r"<(\w+)", html), ["p"])
        self.assertIn("&lt;img", html)



if __name__ == "__main__":
    unittest.main()


class StalenessNoteTests(unittest.TestCase):
    """T-056: the header says so when the data has fallen behind."""

    def test_recent_data_and_an_empty_store_give_no_note(self):
        from vg09.ui_helpers import staleness_note

        today = date(2026, 10, 2)
        self.assertIsNone(staleness_note(None, today))
        self.assertIsNone(staleness_note(date(2026, 10, 2), today))
        self.assertIsNone(staleness_note(date(2026, 9, 30), today))  # a weekend's gap

    def test_data_more_than_two_days_behind_is_reported_in_days(self):
        from vg09.ui_helpers import staleness_note

        self.assertEqual(staleness_note(date(2026, 9, 17), date(2026, 10, 2)), "15 days old")
        self.assertEqual(staleness_note(date(2026, 9, 29), date(2026, 10, 2)), "3 days old")


class MisattributionNoteTests(unittest.TestCase):
    """T-064: the warning under an answer that credits a quote to the wrong source."""

    def test_nothing_misattributed_gives_no_note(self):
        from vg09.ui_helpers import misattribution_note

        self.assertIsNone(misattribution_note([]))

    def test_each_quote_is_listed_with_its_source_number(self):
        from vg09.ui_helpers import misattribution_note

        note = misattribution_note([("I've been working in Claude Code and Codex", [23], 25),
                                    ("the model is cheaper and faster", [3, 4], None)])
        shown = rendered_text(note)  # T-089: the quote is escaped, so compare what is shown
        self.assertIn("not in the source the answer credits them to", shown)
        self.assertIn("\"I've been working in Claude Code and Codex\" "
                      "(credited to source 23; it is in source 25)", shown)
        self.assertIn('"the model is cheaper and faster" '
                      "(credited to sources 3, 4; not found in any source of this answer)", shown)

    def test_a_quote_cannot_become_a_link_image_or_list(self):
        """T-089: the quote is the model's own text; markdown in it stays text."""
        quote = "see <https://evil.example> and [x](https://evil.example) ![i](https://evil.example/p.png)\n- item"
        html = _MARKDOWN.render(misattribution_note([(quote, [1], None)]))
        self.assertNotIn("<a ", html)
        self.assertNotIn("<img", html)
        self.assertEqual(html.count("<li>"), 1)  # the note's own bullet only
        self.assertIn("[x](https://evil.example)", rendered_text(misattribution_note([(quote, [1], None)])))

    def test_a_long_quote_is_shortened(self):
        from vg09.ui_helpers import misattribution_note

        note = misattribution_note([("word " * 40, [1], None)])
        self.assertIn("…", note)
        self.assertLess(len(note), 300)


class UpdateNoteTests(unittest.TestCase):
    """D-018: the header follows the background update and says why one failed."""

    def test_nothing_to_say_when_idle_or_done(self):
        from vg09.ui_helpers import update_note

        self.assertIsNone(update_note({"state": "idle"}))
        self.assertIsNone(update_note({"state": "done", "finished": "2026-10-05T09:00:00"}))

    def test_a_running_update_shows_its_current_step(self):
        from vg09.ui_helpers import update_note

        self.assertEqual(update_note({"state": "running", "detail": "Hugging Face Daily Papers"}),
                         "Updating… Hugging Face Daily Papers")

    def test_ollama_refusing_the_connection_is_named_in_plain_words(self):
        from vg09.ui_helpers import update_note

        # The shape requests gives a refused connection, as recorded by ingest_job.
        error = ("index: HTTPConnectionPool(host='127.0.0.1', port=11434): Max retries "
                 "exceeded with url: /api/embed (Caused by NewConnectionError(...))")
        note = update_note({"state": "done_with_errors", "errors": [error]})
        self.assertTrue(note.startswith("Ollama isn't running"))

    def test_any_other_failure_points_to_the_sources_page(self):
        from vg09.ui_helpers import update_note

        note = update_note({"state": "done_with_errors", "errors": ["youtube: blocked"]})
        self.assertEqual(note, "The last update had problems. See Sources")
