"""T-095: docs/eval-expectations.json v1 is the answer key as written, and stays so."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


class ExpectationsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((DOCS / "eval-expectations.json").read_text(encoding="utf-8"))
        self.key = (DOCS / "eval-questions.md").read_text(encoding="utf-8")

    def test_v1_lists_exactly_the_answer_keys_questions_and_expected_sources(self):
        sections = re.split(r"^### Fr[aå]ga (\d+)\s*$", self.key, flags=re.M)
        v1 = self.data["versions"]["v1"]["questions"]
        self.assertEqual(len(v1), 15)
        for i in range(1, len(sections), 2):
            key, body = f"F{int(sections[i]):02d}", sections[i + 1]
            with self.subTest(question=key):
                self.assertEqual(v1[key]["question"],
                                 re.search(r"^Fr[aå]ga \d+: (.+)$", body, re.M).group(1))
                listed = re.findall(r"\(`([0-9]{4}\.[0-9]{4,5}|[A-Za-z0-9_-]{11})`\)",
                                    body[body.index("**Förväntade källor"):])
                self.assertEqual(v1[key]["expected"], listed)

    def test_later_versions_only_change_f11(self):
        self.assertEqual(list(self.data["versions"]["v2"]["changes"]), ["F11"])
        f11 = self.data["versions"]["v2"]["changes"]["F11"]
        self.assertEqual(f11["filter"], ["2026-09-07", "2026-09-13"])
        self.assertEqual(f11["expected_open_set"]["documents"], 146)

    def test_the_f11_discrepancy_is_recorded(self):
        f11 = self.data["versions"]["v1"]["questions"]["F11"]
        self.assertEqual(f11["filter"], ["2026-09-11", "2026-09-17"])
        self.assertEqual((f11["expected_open_set"]["from"], f11["expected_open_set"]["through"]),
                         ("2026-09-10", "2026-09-16"))
        self.assertIn("32 papers dated 2026-09-10", f11["discrepancy"])


if __name__ == "__main__":
    unittest.main()
