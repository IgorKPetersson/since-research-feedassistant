"""Unit tests for vg09.quote_links (T-063). The segments are real: copied from
data/raw/youtube/2026-10-02/avN5R3OhxYs.json (gitignored), the video behind my
report that a "Claude Code" quote was 18 seconds after the link's start."""

from __future__ import annotations

import unittest

from vg09.quote_links import find_quote_start, quotes_in, with_timestamp

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


class WithTimestampTests(unittest.TestCase):
    def test_replaces_the_excerpts_time_and_starts_two_seconds_early(self):
        self.assertEqual(with_timestamp("https://www.youtube.com/watch?v=avN5R3OhxYs&t=572", 590.48),
                         "https://www.youtube.com/watch?v=avN5R3OhxYs&t=588")

    def test_never_goes_below_zero(self):
        self.assertEqual(with_timestamp("https://www.youtube.com/watch?v=x", 1.0),
                         "https://www.youtube.com/watch?v=x&t=0")


if __name__ == "__main__":
    unittest.main()
