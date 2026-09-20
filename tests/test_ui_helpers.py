"""Unit tests for vg09.ui_helpers (T-025, T-029)."""

from __future__ import annotations

import unittest
from datetime import date

from vg09.ui_helpers import describe_retrieval_mode, escape_markdown_link_text

# T-029: a real title, not synthetic - copied verbatim from
# data/raw/youtube/2026-09-16/S2VJU5DQqlU.json's "title" field (data/raw/ is
# gitignored per D-004, so the test embeds the real string rather than reading it
# live - same pattern test_llm.py/test_chunking.py use for other real-shaped data).
REAL_PARENTHETICAL_TITLE = "He Built The Ultimate Spy Tool (Free and Open-Source)"


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
    def test_manual_override_wins_even_with_an_interpreted_window_present(self):
        override = (date(2020, 1, 1), date(2020, 1, 31))
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=override)
        self.assertIn("manuellt", result)
        self.assertIn("2020-01-01", result)

    def test_interpreted_window_shown_when_no_override(self):
        interpreted = (date(2026, 9, 10), date(2026, 9, 16))
        result = describe_retrieval_mode(interpreted, ranking=False, manual_override=None)
        self.assertIn("tolkat", result)
        self.assertIn("2026-09-10", result)
        self.assertIn("2026-09-16", result)

    def test_ranking_mode_shown_when_no_window_and_no_override(self):
        result = describe_retrieval_mode(None, ranking=True, manual_override=None)
        self.assertIn("rankning", result)

    def test_unfiltered_when_nothing_fired(self):
        result = describe_retrieval_mode(None, ranking=False, manual_override=None)
        self.assertIn("Inget datumfilter", result)


if __name__ == "__main__":
    unittest.main()
