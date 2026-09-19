"""Unit tests for vg09.answer (T-023).

No live network calls: requests.post is mocked at the boundary, same pattern the rest
of this project's tests use. A real end-to-end verification against real Ollama lives
in scripts/t023_verify_answer.py, not here.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from vg09.answer import SYSTEM_PROMPT, build_user_message, generate_answer
from vg09.retrieval import Candidate


def make_chunk(title: str, text: str, feed_date: str = "2026-09-16") -> Candidate:
    return Candidate(
        id=f"hf:{title}:0",
        text=text,
        metadata={"title": title, "url": f"https://example.com/{title}", "feed_date": feed_date},
    )


def fake_response(content="An answer.", thinking="Some reasoning.", done_reason="stop",
                   prompt_eval_count=500):
    return {
        "message": {"role": "assistant", "content": content, "thinking": thinking},
        "done_reason": done_reason,
        "prompt_eval_count": prompt_eval_count,
    }


class BuildUserMessageTests(unittest.TestCase):
    def test_chunks_appear_least_relevant_first_question_last(self):
        most_relevant = make_chunk("most relevant", "text A")
        least_relevant = make_chunk("least relevant", "text B")
        message = build_user_message("what happened?", [most_relevant, least_relevant])

        pos_least = message.index("least relevant")
        pos_most = message.index("most relevant")
        pos_question = message.index("Question: what happened?")
        self.assertLess(pos_least, pos_most)  # least-relevant chunk comes first
        self.assertLess(pos_most, pos_question)  # question comes after all sources

    def test_source_includes_title_url_and_feed_date(self):
        chunk = make_chunk("A Paper", "abstract text", feed_date="2026-09-10")
        message = build_user_message("q", [chunk])
        self.assertIn("A Paper", message)
        self.assertIn("https://example.com/A Paper", message)
        self.assertIn("2026-09-10", message)
        self.assertIn("abstract text", message)

    def test_empty_chunks_produces_an_honest_no_sources_note(self):
        message = build_user_message("q", [])
        self.assertIn("No sources were retrieved", message)
        self.assertIn("Question: q", message)


class GenerateAnswerTests(unittest.TestCase):
    def _run(self, chunks=None, **response_overrides):
        mock_resp = MagicMock()
        mock_resp.json.return_value = fake_response(**response_overrides)
        with patch("vg09.answer.requests.post", return_value=mock_resp) as mock_post:
            result = generate_answer("what happened?", chunks or [])
        return result, mock_post

    def test_system_prompt_sent_as_its_own_message(self):
        _, mock_post = self._run()
        messages = mock_post.call_args.kwargs["json"]["messages"]
        self.assertEqual(messages[0], {"role": "system", "content": SYSTEM_PROMPT})
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(len(messages), 2)

    def test_think_is_always_true(self):
        _, mock_post = self._run()
        self.assertTrue(mock_post.call_args.kwargs["json"]["think"])

    def test_num_predict_is_exactly_2000(self):
        _, mock_post = self._run()
        self.assertEqual(mock_post.call_args.kwargs["json"]["options"]["num_predict"], 2000)

    def test_num_ctx_is_16000(self):
        _, mock_post = self._run()
        self.assertEqual(mock_post.call_args.kwargs["json"]["options"]["num_ctx"], 16000)

    def test_stop_is_a_complete_answer(self):
        result, _ = self._run(done_reason="stop")
        self.assertFalse(result.incomplete)
        self.assertEqual(result.done_reason, "stop")

    def test_length_is_flagged_incomplete(self):
        result, _ = self._run(done_reason="length")
        self.assertTrue(result.incomplete)
        self.assertEqual(result.done_reason, "length")

    def test_reasoning_and_answer_come_back_split(self):
        result, _ = self._run(content="The final answer.", thinking="Thinking it through.")
        self.assertEqual(result.answer, "The final answer.")
        self.assertEqual(result.reasoning, "Thinking it through.")

    def test_prompt_eval_count_is_returned(self):
        result, _ = self._run(prompt_eval_count=1234)
        self.assertEqual(result.prompt_eval_count, 1234)

    def test_a_think_false_shaped_response_raises_via_t011s_contract(self):
        """generate_answer never silently accepts a merged-reasoning response - it
        goes through vg09.llm.split_reasoning_and_answer(), which raises on an empty
        thinking field (T-011/KB-007)."""
        with self.assertRaises(ValueError):
            self._run(thinking="")


if __name__ == "__main__":
    unittest.main()
