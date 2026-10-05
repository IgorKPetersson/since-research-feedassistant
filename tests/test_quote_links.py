"""Unit tests for vg09.quote_links (T-063). The segments are real: copied from
data/raw/youtube/2026-10-02/avN5R3OhxYs.json (gitignored), the video behind my
report that a "Claude Code" quote was 18 seconds after the link's start."""

from __future__ import annotations

import unittest

from vg09.retrieval import Candidate

from vg09.quote_links import (
    credited_sources,
    find_quote_start,
    misattributed_quotes,
    quote_in_text,
    quotes_in,
    with_timestamp,
)

SEGMENTS = [
    {"text": "or your account may not have permissions", "start": 572.04, "duration": 2.0},
    {"text": "who have never opened a terminal.", "start": 588.40, "duration": 2.0},
    {"text": "So, Cursor, Claude Code, Codex have made", "start": 590.48, "duration": 2.0},
    {"text": "delegating work super familiar to those", "start": 592.56, "duration": 2.0},
    {"text": "of us who have a development background.", "start": 594.64, "duration": 2.0},
    {"text": "I've been working in Claude Code and", "start": 596.72, "duration": 2.0},
]
CHUNK_TEXT = " ".join(s["text"] for s in SEGMENTS)


class QuotesInTests(unittest.TestCase):
    def test_a_quoted_sentence_is_found_with_straight_or_curly_quotes(self):
        for answer in ('Source 26 states: "Cursor, Claude Code, Codex have made '
                       'delegating work super familiar" [26].',
                       'Source 26 states: “Cursor, Claude Code, Codex have made '
                       'delegating work super familiar” [26].'):
            self.assertEqual(quotes_in(answer),
                             ["Cursor, Claude Code, Codex have made delegating work super familiar"])

    def test_short_quotes_are_ignored_they_match_too_much(self):
        self.assertEqual(quotes_in('the term "Claude Code" came up'), [])

    def test_an_ellipsis_splits_a_quote_into_its_pieces(self):
        self.assertEqual(
            quotes_in('"So, Cursor, Claude Code, Codex have made ... to those of us who have"'),
            ["So, Cursor, Claude Code, Codex have made", "to those of us who have"])


class FindQuoteStartTests(unittest.TestCase):
    def test_the_quote_resolves_to_the_line_it_starts_on(self):
        quotes = ["Cursor, Claude Code, Codex have made delegating work super familiar"]
        self.assertEqual(find_quote_start(quotes, SEGMENTS, 572.04, CHUNK_TEXT), 590.48)

    def test_case_and_punctuation_differences_still_match(self):
        quotes = ["cursor claude code codex have made delegating work"]
        self.assertEqual(find_quote_start(quotes, SEGMENTS, 572.04, CHUNK_TEXT), 590.48)

    def test_a_quote_that_is_not_in_this_excerpt_gives_none(self):
        quotes = ["something the speaker never said at all"]
        self.assertIsNone(find_quote_start(quotes, SEGMENTS, 572.04, CHUNK_TEXT))

    def test_a_quote_under_the_wrong_excerpt_number_is_found_elsewhere_in_the_video(self):
        """Found for real: the model cited the 14:56 excerpt for words spoken at 9:50.
        The words are exact, the number is not."""
        quotes = ["Cursor, Claude Code, Codex have made delegating work super familiar"]
        self.assertEqual(find_quote_start(quotes, SEGMENTS, 896.0, "text of the 14:56 excerpt"),
                         590.48)

    def test_a_quote_in_this_excerpt_wins_over_an_earlier_one_elsewhere(self):
        segments = [{"text": "we said the same thing twice here", "start": 10.0},
                    {"text": "and later we said the same thing twice here", "start": 600.0}]
        quotes = ["said the same thing twice here"]
        self.assertEqual(find_quote_start(quotes, segments, 600.0, segments[1]["text"]), 600.0)

    def test_no_segments_gives_none(self):
        self.assertIsNone(find_quote_start(["a b c d e"], [], 0.0, "a b c d e"))


class CreditedSourcesTests(unittest.TestCase):
    """T-064: which source number an answer credits each quote to."""

    # The real false answer from T-063's browser run (2026-10-05), as the model wrote it.
    FALSE_ANSWER = ('Yes, "Claude Code" has been mentioned in the last week. It appears in '
                    'source [23] with the statement "I\'ve been working in Claude Code and Codex '
                    'for months and months and months now" and in source [25] with the '
                    'identical statement.')

    def test_the_source_named_before_the_quote_in_its_sentence_is_credited(self):
        self.assertEqual(credited_sources(self.FALSE_ANSWER), [
            ("I've been working in Claude Code and Codex for months and months and months now", [23])])

    def test_a_citation_right_after_the_quote_wins(self):
        answer = 'Source 4 covers agents, and one speaker says "agents will replace apps soon" [7].'
        self.assertEqual(credited_sources(answer), [("agents will replace apps soon", [7])])

    def test_source_written_without_brackets_is_understood(self):
        answer = 'Source 26 states: "Cursor, Claude Code, Codex have made delegating work"'
        self.assertEqual(credited_sources(answer),
                         [("Cursor, Claude Code, Codex have made delegating work", [26])])

    def test_a_source_named_after_the_quote_in_the_same_sentence_is_used_last(self):
        answer = '"Agents will replace apps soon," according to source 9. Source 2 disagrees.'
        self.assertEqual(credited_sources(answer), [("Agents will replace apps soon,", [9])])

    def test_a_bracket_with_several_numbers_credits_all_of_them(self):
        answer = 'Both say "the model is cheaper and faster" [3, 4].'
        self.assertEqual(credited_sources(answer), [("the model is cheaper and faster", [3, 4])])

    def test_a_quote_credited_to_nothing_is_left_out(self):
        self.assertEqual(credited_sources('People say "the app era is over now".'), [])

    def test_a_reference_in_the_previous_sentence_is_not_used(self):
        answer = 'See source 3. Someone said "the app era is over now".'
        self.assertEqual(credited_sources(answer), [])


class QuoteInTextTests(unittest.TestCase):
    def test_case_and_punctuation_are_ignored(self):
        self.assertTrue(quote_in_text("So Cursor, claude code -- Codex have made",
                                      "So, Cursor, Claude Code, Codex have made delegating"))

    def test_a_rewritten_sentence_is_not_found(self):
        self.assertFalse(quote_in_text("Cursor and Claude Code made delegating",
                                       "So, Cursor, Claude Code, Codex have made delegating"))

    def test_loose_quoting_of_the_right_source_is_accepted(self):
        """Real model quotes of the right video, measured in T-064."""
        self.assertTrue(quote_in_text(
            "a personal agent that can keep working on assignments",
            "This follows Muse, of course, the personal agent that can keep working on "
            "assignments that I've talked about on this channel."))
        self.assertTrue(quote_in_text(
            "takes actions on your behalf",
            "So, Muse will actually take actions on your behalf. You can connect it"))

    def test_a_quote_from_a_different_video_is_rejected(self):
        self.assertFalse(quote_in_text(
            "I've been working in Claude Code and Codex for months and months and months now",
            "it does a lot of practical, relatively low intelligence tasks really, really well. "
            "Practical help with email, practical help with small shopping."))


class MisattributedQuotesTests(unittest.TestCase):
    """No file on disk for these ids, so each source's own excerpt text is its document."""

    @staticmethod
    def source(doc_id: str, text: str) -> Candidate:
        return Candidate(id=f"{doc_id}:0", text=text,
                         metadata={"source": "youtube", "feed_date": "1999-01-01", "doc_id": doc_id})

    def test_a_swapped_number_is_reported_with_the_source_that_has_the_quote(self):
        sources = {23: self.source("a", "practical help with email and small shopping"),
                   25: self.source("b", "I've been working in Claude Code and Codex for months")}
        answer = 'Source [23] says "I\'ve been working in Claude Code and Codex for months".'
        self.assertEqual(misattributed_quotes(answer, sources),
                         [("I've been working in Claude Code and Codex for months", [23], 25)])

    def test_a_correctly_credited_quote_is_not_reported(self):
        sources = {25: self.source("b", "I've been working in Claude Code and Codex for months")}
        answer = 'Source [25] says "I\'ve been working in Claude Code and Codex for months".'
        self.assertEqual(misattributed_quotes(answer, sources), [])

    def test_a_quoted_title_is_not_reported(self):
        """T-065: found in the probe run - the model quotes a paper's title, and the
        title is not part of the abstract's text."""
        sources = {32: self.source("a", "We study whether training on protein folding helps.")}
        sources[32].metadata["title"] = "Does Learning Protein Folding Generalize to Broader Reasoning?"
        answer = '[32] "Does Learning Protein Folding Generalize to Broader Reasoning?" was published.'
        self.assertEqual(misattributed_quotes(answer, sources), [])

    def test_a_quote_in_no_source_is_reported_with_none(self):
        sources = {1: self.source("a", "practical help with email and small shopping")}
        answer = '"Agents will replace every app by next year" [1].'
        self.assertEqual(misattributed_quotes(answer, sources),
                         [("Agents will replace every app by next year", [1], None)])


class WithTimestampTests(unittest.TestCase):
    def test_replaces_the_excerpts_time_and_starts_two_seconds_early(self):
        self.assertEqual(with_timestamp("https://www.youtube.com/watch?v=avN5R3OhxYs&t=572", 590.48),
                         "https://www.youtube.com/watch?v=avN5R3OhxYs&t=588")

    def test_never_goes_below_zero(self):
        self.assertEqual(with_timestamp("https://www.youtube.com/watch?v=x", 1.0),
                         "https://www.youtube.com/watch?v=x&t=0")


if __name__ == "__main__":
    unittest.main()
