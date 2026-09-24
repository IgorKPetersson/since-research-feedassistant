# T-043 — English relative-time date extraction, verified against real translations

D-016 made the Swedish-only scope of `vg09.date_range`'s relative-time extraction a
real bug, not a risk-register item: the project's core date/ranking feature was
silently off for every non-Swedish question, in a repo meant to be usable anywhere.
This file records two real runs — the original Swedish verification (T-021),
re-run unchanged to confirm no regression, and a new run against real English
translations of the same 15 real questions (`docs/eval-questions.md`), written by
hand once (`scripts/t043_test_english_date_extraction.py`), not machine-translated at
run time.

Same anchor both runs: `TODAY = 2026-09-16` (T-021's own anchor).

## Swedish (`scripts/t021_test_date_extraction_against_eval_questions.py`, re-run)

**Total: right=8  wrong=0  unparseable_ok=7  unparseable_wrong=0** — unchanged from
T-021's original result.

**RIGHT (8/15):**
- F02: 2026-08-16 .. 2026-09-16 — "Vad har hänt med GUI agents den senaste månaden?"
- F04: 2026-09-10 .. 2026-09-16 — "Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta."
- F05: 2026-09-03 .. 2026-09-16 — "Har NeoHorse nämnts de senaste två veckorna?"
- F07: 2026-08-16 .. 2026-09-16 — "Vad säger forskningen om text-to-video den senaste månaden?"
- F10: 2026-09-16 .. 2026-09-16 — "Vad är nytt den 16 september?"
- F11: 2026-09-10 .. 2026-09-16 — "Vad hände i forskningen förra veckan?"
- F13: 2026-09-03 .. 2026-09-16 — "Vad har sagts om OpenAI de senaste två veckorna?"
- F15: 2026-09-10 .. 2026-09-16 — "Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?"

**WRONG (0/15):** none.

**UNPARSEABLE, CORRECT (7/15):** F01, F03, F06 (ranking phrases, "det/de ... senaste",
not a window), F08, F12, F14 (no time phrase at all), F09 ("de senaste veckorna" —
plural, no number, ambiguous by design).

**UNPARSEABLE, WRONG (0/15):** none.

## English (`scripts/t043_test_english_date_extraction.py`, new)

Real, hand-written English translations of the same 15 questions — same real
time-phrase shape as the Swedish original in each case (a bare plural stays a bare
plural, a ranking phrase stays a ranking phrase, a numbered window stays numbered).

**Total: right=8  wrong=0  unparseable_ok=7  unparseable_wrong=0** — identical tally
to the Swedish run, question for question.

**RIGHT (8/15):**
- F02: 2026-08-16 .. 2026-09-16 — "What has happened with GUI agents in the last month?"
- F04: 2026-09-10 .. 2026-09-16 — "In the last week, what has been said about coding agents? Please summarize."
- F05: 2026-09-03 .. 2026-09-16 — "Has NeoHorse been mentioned in the last two weeks?"
- F07: 2026-08-16 .. 2026-09-16 — "What does research say about text-to-video in the last month?"
- F10: 2026-09-16 .. 2026-09-16 — "What's new on September 16th?"
- F11: 2026-09-10 .. 2026-09-16 — "What happened in research last week?"
- F13: 2026-09-03 .. 2026-09-16 — "What has been said about OpenAI in the last two weeks?"
- F15: 2026-09-10 .. 2026-09-16 — "What has happened with AI agents in the last week, in both papers and videos?"

**WRONG (0/15):** none.

**UNPARSEABLE, CORRECT (7/15):**
- F01 — "the two latest" — ranking, not a window
- F03 — "the absolute latest" — ranking, not a window
- F06 — "the latest" — ranking, not a window
- F08 — no time phrase at all
- F09 — "recent weeks" — plural, no number: ambiguous by design (same rule as Swedish)
- F12 — no time phrase at all
- F14 — no time phrase at all

**UNPARSEABLE, WRONG (0/15):** none.

## Ranking detection (`detect_recency_ranking()`), the three real ranking questions

Not covered by the window-extraction scripts above (they test `extract_date_range()`
only) — checked separately, both languages:

| # | Swedish | English | Expected |
|---|---|---|---|
| F01 | True | True | ranking |
| F03 | True | True | ranking |
| F06 | True | True | ranking |
| F02/F05 (window, not ranking) | False | False | not ranking |
| F09 (ambiguous plural) | False | False | not ranking |

## Not covered by the 15 real questions, tested separately

- **"today"** → a single-day window (`extract_date_range("What's new today?", ...)` →
  `(2026-09-16, 2026-09-16)`) — named explicitly in this ticket's own instruction, no
  real eval question happens to use it.
- **Day-of-month word order** ("the 16th of September", not just "September 16th") —
  both real English orders resolve identically.

## Conclusion

English relative-time extraction now resolves the same 8 real windows Swedish
resolves, correctly stays unresolvable on the same 7 (including the one genuinely
ambiguous bare-plural case), and produces zero wrong answers in either direction, in
either language. The Swedish side is provably unchanged — same script, same file,
same real questions, same result as T-021's original run.
