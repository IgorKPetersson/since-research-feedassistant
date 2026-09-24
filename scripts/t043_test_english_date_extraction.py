"""T-043: test vg09.date_range.extract_date_range() against real English translations
of the same 15 real questions T-021 tested in Swedish (docs/eval-questions.md).

Same TODAY, same methodology, same categories (right/wrong/unparseable_ok/
unparseable_wrong) as scripts/t021_test_date_extraction_against_eval_questions.py, so
the two runs are directly comparable. The translations are written here, once, by
hand - not machine-translated at run time and not re-derived from the same logic this
script tests, so the comparison stays real rather than circular. Each preserves the
original's real time-phrase shape (a bare plural stays a bare plural, "last N weeks"
stays a number, "det senaste" stays a ranking phrase) since that shape is exactly what
this module's patterns are matched against.
"""

from __future__ import annotations

from datetime import date

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.date_range import extract_date_range

TODAY = date(2026, 9, 16)  # same anchor T-021 used

WEEK = (date(2026, 9, 10), date(2026, 9, 16))
TWO_WEEKS = (date(2026, 9, 3), date(2026, 9, 16))
MONTH = (date(2026, 8, 16), date(2026, 9, 16))
SEPT_16 = (date(2026, 9, 16), date(2026, 9, 16))

# question number -> (real English translation, expected window or None, reason)
CASES = {
    1: ("In the area of recursive self-improvement, what are the two latest news "
        "items and what are they about?",
        None, '"the two latest" = ranking, not a window'),
    2: ("What has happened with GUI agents in the last month?",
        MONTH, '"in the last month"'),
    3: ("What is the absolute latest in video generation, and is it hardware- or "
        "software-related?",
        None, '"the absolute latest" = ranking, not a window'),
    4: ("In the last week, what has been said about coding agents? Please summarize.",
        WEEK, '"In the last week" (sentence-initial)'),
    5: ("Has NeoHorse been mentioned in the last two weeks?",
        TWO_WEEKS, '"the last two weeks"'),
    6: ("What is the latest in benchmarking of coding agents?",
        None, '"the latest" = ranking, not a window'),
    7: ("What does research say about text-to-video in the last month?",
        MONTH, '"in the last month"'),
    8: ("Is LEGO mentioned in any article, and if so, summarize what it's about?",
        None, "no time phrase at all"),
    9: ("Has AutoDev been mentioned in recent weeks?",
        None, '"recent weeks" - plural, no number: ambiguous by design'),
    10: ("What's new on September 16th?",
         SEPT_16, '"September 16th" - absolute date'),
    11: ("What happened in research last week?",
         WEEK, '"last week"'),
    12: ("Has Palantir been mentioned in any video?",
         None, "no time phrase at all"),
    13: ("What has been said about OpenAI in the last two weeks?",
         TWO_WEEKS, '"the last two weeks"'),
    14: ("Has anything been said about open-source alternatives to major AI tools, "
         "both in videos and in articles?",
         None, "no time phrase at all"),
    15: ("What has happened with AI agents in the last week, in both papers and "
         "videos?",
         WEEK, '"the last week"'),
}


def main() -> None:
    right, wrong, unparseable_ok, unparseable_wrong = [], [], [], []

    for n in sorted(CASES):
        q, expected, reason = CASES[n]
        actual = extract_date_range(q, TODAY)

        if expected is None and actual is None:
            unparseable_ok.append((n, q, reason))
        elif expected is None and actual is not None:
            unparseable_wrong.append((n, q, reason, actual))
        elif expected == actual:
            right.append((n, q, expected))
        else:
            wrong.append((n, q, expected, actual))

    print(f"RIGHT ({len(right)}/15) - extracted window matches expected:")
    for n, q, exp in right:
        print(f"  F{n:02d}: {exp[0]} .. {exp[1]}  <- {q}")

    print(f"\nWRONG ({len(wrong)}/15) - extracted something, but the wrong window:")
    for n, q, exp, act in wrong:
        print(f"  F{n:02d}: expected {exp}, got {act}  <- {q}")

    print(f"\nUNPARSEABLE, CORRECT ({len(unparseable_ok)}/15) - no window claimed, "
          f"fallback (full window + date picker) is the right call:")
    for n, q, reason in unparseable_ok:
        print(f"  F{n:02d}: {reason}  <- {q}")

    print(f"\nUNPARSEABLE, WRONG ({len(unparseable_wrong)}/15) - expected unresolvable "
          f"but something was extracted anyway:")
    for n, q, reason, act in unparseable_wrong:
        print(f"  F{n:02d}: {reason}, got {act}  <- {q}")

    print(f"\nTotal: right={len(right)} wrong={len(wrong)} "
          f"unparseable_ok={len(unparseable_ok)} unparseable_wrong={len(unparseable_wrong)}")


if __name__ == "__main__":
    main()
