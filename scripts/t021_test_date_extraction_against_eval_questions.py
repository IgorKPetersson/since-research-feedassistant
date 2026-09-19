"""T-021: test vg09.date_range.extract_date_range() against the 15 REAL questions in
docs/eval-questions.md - read live from that file, never retyped/paraphrased here.

`TODAY` is the fixed reference date the ticket asked for: settable here, in code, so
this can be re-run against the frozen eval dataset (T-020) and always resolve relative
phrases ("senaste veckan", ...) the same way. 2026-09-16 matches the HF cutoff that
docs/eval-questions.md's own "Time-window conventions" section already anchors every
relative-phrase window to.

Expected windows/None per question are taken from that same "Time-window conventions"
section and from reading each question by hand - not re-derived by the same arithmetic
this script is testing, so the comparison is real rather than circular.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.date_range import extract_date_range

TODAY = date(2026, 9, 16)

WEEK = (date(2026, 9, 10), date(2026, 9, 16))
TWO_WEEKS = (date(2026, 9, 3), date(2026, 9, 16))
MONTH = (date(2026, 8, 16), date(2026, 9, 16))
SEPT_16 = (date(2026, 9, 16), date(2026, 9, 16))

# question number -> (expected window or None, short reason from reading the question)
EXPECTED = {
    1: (None, "no time phrase (\"de tva senaste\" = ranking, not a window)"),
    2: (MONTH, '"den senaste manaden"'),
    3: (None, "no time phrase (\"det absolut senaste\" = ranking, not a window)"),
    4: (WEEK, '"Den senaste veckan" (sentence-initial)'),
    5: (TWO_WEEKS, '"de senaste tva veckorna"'),
    6: (None, "no time phrase (\"det senaste\" = ranking, not a window)"),
    7: (MONTH, '"den senaste manaden"'),
    8: (None, "no time phrase at all"),
    9: (None, '"de senaste veckorna" - plural, no number: ambiguous by design'),
    10: (SEPT_16, '"den 16 september" - absolute date'),
    11: (WEEK, '"forra veckan"'),
    12: (None, "no time phrase at all"),
    13: (TWO_WEEKS, '"de senaste tva veckorna"'),
    14: (None, "no time phrase at all"),
    15: (WEEK, '"den senaste veckan"'),
}


def load_real_questions() -> dict[int, str]:
    text = Path("docs/eval-questions.md").read_text(encoding="utf-8")
    questions = {}
    for m in re.finditer(r"^Fr[aå]ga (\d+): (.+)$", text, re.MULTILINE):
        questions[int(m.group(1))] = m.group(2)
    return questions


def main() -> None:
    questions = load_real_questions()
    assert len(questions) == 15, f"expected 15 real questions, found {len(questions)}"

    right, wrong, unparseable_ok, unparseable_wrong = [], [], [], []

    for n in sorted(questions):
        q = questions[n]
        expected, reason = EXPECTED[n]
        actual = extract_date_range(q, TODAY)

        if expected is None and actual is None:
            unparseable_ok.append((n, q, reason))
        elif expected is None and actual is not None:
            unparseable_wrong.append((n, q, reason, actual))
        elif expected == actual:
            right.append((n, q, expected))
        else:
            wrong.append((n, q, expected, actual))

    print(f"RATT ({len(right)}/15) - extraherat fonster matchar facit:")
    for n, q, exp in right:
        print(f"  F{n:02d}: {exp[0]} .. {exp[1]}  <- {q}")

    print(f"\nFEL ({len(wrong)}/15) - extraherat men fel fonster:")
    for n, q, exp, act in wrong:
        print(f"  F{n:02d}: expected {exp}, got {act}  <- {q}")

    print(f"\nGAR INTE ATT TOLKA, KORREKT ({len(unparseable_ok)}/15) - inget fonster "
          f"pastas, fallback (helt fonster + datumvaljare) blir ratt val:")
    for n, q, reason in unparseable_ok:
        print(f"  F{n:02d}: {reason}  <- {q}")

    print(f"\nGAR INTE ATT TOLKA, FEL ({len(unparseable_wrong)}/15) - forvantades vara "
          f"olostbar men extraherade nagot anda:")
    for n, q, reason, act in unparseable_wrong:
        print(f"  F{n:02d}: {reason}, got {act}  <- {q}")

    print(f"\nTotal: ratt={len(right)} fel={len(wrong)} "
          f"olostbar_korrekt={len(unparseable_ok)} olostbar_fel={len(unparseable_wrong)}")


if __name__ == "__main__":
    main()
