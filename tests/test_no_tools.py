"""Unit tests for T-075 (D-020): the model never gets tools.

Every request the app sends to Ollama is captured and checked: it goes to 127.0.0.1, to
one of the three endpoints the app uses, and carries no tool or function definitions.
A source scan backs this up, so a tool added in a new function is caught too."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from vg09.answer import generate_answer
from vg09.retrieval import Candidate, count_qwen_tokens
from vg09.store import embed_batch

ALLOWED = {"http://127.0.0.1:11434/api/chat", "http://127.0.0.1:11434/api/generate",
           "http://127.0.0.1:11434/api/embed"}
TOOL_KEYS = {"tools", "functions", "tool_choice", "function_call"}


def captured(module: str, call, response: dict):
    mock_resp = MagicMock()
    mock_resp.json.return_value = response
    with patch(f"vg09.{module}.requests.post", return_value=mock_resp) as post:
        call()
    return [(c.args[0] if c.args else c.kwargs["url"], c.kwargs["json"]) for c in post.call_args_list]


class OllamaRequestTests(unittest.TestCase):
    def check(self, requests_sent):
        self.assertTrue(requests_sent)
        for url, body in requests_sent:
            self.assertIn(url, ALLOWED)
            self.assertFalse(TOOL_KEYS & set(body), body.keys())
            for message in body.get("messages", []):
                self.assertNotEqual(message.get("role"), "tool")

    def test_the_answer_call_has_no_tools(self):
        chunk = Candidate(id="d:0", text="t", metadata={"title": "T", "url": "https://huggingface.co/papers/1",
                                                         "feed_date": "2026-10-05"})
        self.check(captured("answer", lambda: generate_answer("q?", [chunk]), {
            "message": {"role": "assistant", "content": "A [1].", "thinking": "Reasoning."},
            "done_reason": "stop", "prompt_eval_count": 10}))

    def test_the_token_count_call_has_no_tools(self):
        self.check(captured("retrieval", lambda: count_qwen_tokens("text"), {"prompt_eval_count": 3}))

    def test_the_embedding_call_has_no_tools(self):
        self.check(captured("store", lambda: embed_batch(["text"]),
                            {"embeddings": [[0.0]], "prompt_eval_count": 1}))


class SourceScanTests(unittest.TestCase):
    def test_no_module_defines_tools_for_a_model(self):
        package = Path(__file__).resolve().parent.parent / "vg09"
        pattern = re.compile(r"""["'](tools|functions|tool_choice|function_call)["']\s*:""")
        hits = [f"{p.name}: {m.group(0)}" for p in package.glob("*.py")
                for m in pattern.finditer(p.read_text(encoding="utf-8"))]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
