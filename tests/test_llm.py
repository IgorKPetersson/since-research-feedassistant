"""Unit tests for vg09.llm (T-011).

Response shapes match KB-007's real, measured evidence exactly (from real
/api/generate and /api/chat calls against qwen3:30b-a3b) - not invented shapes.
"""

from __future__ import annotations

import unittest

from vg09.llm import split_reasoning_and_answer


class SplitReasoningAndAnswerTests(unittest.TestCase):
    def test_think_true_shape_splits_cleanly(self):
        """KB-007's real think:true /api/chat result: thinking and content are two
        separate, clean fields - content never carries any reasoning text."""
        response = {
            "message": {
                "thinking": "Okay, the user is asking what causes rain. Let me think "
                             "through the water cycle...",
                "content": "Rain is caused by water vapor condensing in clouds and "
                            "falling as precipitation.",
            }
        }
        reasoning, answer = split_reasoning_and_answer(response)
        self.assertTrue(reasoning.startswith("Okay, the user is asking"))
        self.assertEqual(
            answer,
            "Rain is caused by water vapor condensing in clouds and falling as precipitation.",
        )
        self.assertNotIn("Okay, the user is asking", answer)

    def test_think_false_shape_is_detected_and_raises(self):
        """KB-007's real think:false /api/chat result: thinking is empty, and the
        reasoning narrative is merged straight into content instead - this must be
        detected and refused, never silently treated as a clean answer."""
        response = {
            "message": {
                "thinking": "",
                "content": "Okay, the user is asking what causes rain. Hmm, this "
                            "seems like a basic science question... Rain is caused "
                            "by water vapor condensing.",
            }
        }
        with self.assertRaises(ValueError):
            split_reasoning_and_answer(response)

    def test_missing_thinking_key_entirely_is_also_detected(self):
        """Defensive: some other endpoint/version might omit the key outright rather
        than leaving it empty - treated the same way, not a KeyError surprise."""
        response = {"message": {"content": "An answer with no thinking field at all."}}
        with self.assertRaises(ValueError):
            split_reasoning_and_answer(response)


if __name__ == "__main__":
    unittest.main()
