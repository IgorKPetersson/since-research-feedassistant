"""Unit tests for vg09.source_filter (T-068)."""

from __future__ import annotations

import unittest

from vg09.source_filter import detect_source


class DetectSourceTests(unittest.TestCase):
    def test_paper_words_mean_hugging_face(self):
        for q in ("What were the most important papers yesterday?",
                  "Was there any paper about protein folding in the last two weeks?",
                  "Any arXiv abstracts on RL?",
                  "Which publications covered RL last week?",
                  "Vilka artiklar handlade om robotar?",
                  "Nämns LEGO i någon artikel?"):
            self.assertEqual(detect_source(q), "hf", q)

    def test_video_words_mean_youtube(self):
        for q in ("Give me the three latest videos and what they were about.",
                  "Which YouTuber said what about Meta's Muse?",
                  "What did the channels say about GPT-6?",
                  "What was in the latest video?",
                  "Vad sa de i videon?",
                  "Har Palantir nämnts i någon video?",  # eval question 12
                  "Vilka kanaler pratade om Muse?"):
            self.assertEqual(detect_source(q), "youtube", q)

    def test_video_as_a_research_topic_is_not_a_source(self):
        """Eval question 3 and 7: "video generation" and "text-to-video" are topics,
        and the expected answers are papers."""
        for q in ("Vad är det absolut senaste inom Video genereation?",
                  "What's the latest in video generation?",
                  "Any news on text-to-video?",
                  "What's new in the latest video model?",
                  "Vad är det senaste inom video generation?"):
            self.assertIsNone(detect_source(q), q)

    def test_both_kinds_of_word_or_neither_means_no_filter(self):
        for q in ("Which papers did the YouTubers discuss?",
                  "What's new this week?",
                  "Has anyone talked about GPT-6?"):
            self.assertIsNone(detect_source(q), q)

    def test_research_is_a_topic_not_a_source(self):
        """T-078: my two questions, which showed "Papers only (the question
        mentions papers)" without mentioning papers, and eval questions 7 and 11."""
        for q in ("What's new in AI agent research this week?",
                  "How has research on coding agents developed over the last month?",
                  "What's new in AI research?",
                  "Vad säger forskningen om text-to-video den senaste månaden?",
                  "Vad hände i forskningen förra veckan?"):
            self.assertIsNone(detect_source(q), q)


if __name__ == "__main__":
    unittest.main()
