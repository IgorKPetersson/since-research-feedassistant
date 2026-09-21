# KB-019 — qwen3:30b-a3b's reasoning length varies widely between samples of the same prompt; three samples of one question badly understated the tail

**Area:** Local model behaviour (`qwen3:30b-a3b`, `think=true`) — generation budget
**Status:** verified
**Date:** 2026-09-22  ·  **From:** T-032 (4 of 30 real calls truncated), T-039 (measured it)

## Claim
With `think=true`, the reasoning trace is real generated tokens that share the
`num_predict` cap with the answer. For an *identical* prompt, the reasoning length varies by
up to ~1.6× between samples (F06-A: 1795 to 2685 tokens), and across questions the tail
reaches at least 2864 reasoning tokens / 3118 reasoning+answer tokens. A cap sized from a
handful of samples of one question (T-028: 1842 worst of 3 → 2542) is exceeded regularly:
5 of 32 real runs here were above 2542, and 4 of 30 real calls in T-032 came back with
`done_reason=="length"` and an empty answer (the reasoning alone had used the cap).

## Evidence
`scripts/t039_reasoning_length_probe.py`, raw samples in
`docs/eval-results/2026-09-22-t039-reasoning-probe.jsonl`: the four T-032 arms that
truncated (F06-A, F07-A, F11-B, F14-A) × 5 samples and four arms that did not (F01-A, F04-A,
F05-A, F15-A) × 3, real retrieval and prompt, `num_predict` 8000, streamed, one chunk =
one token. Every run ended `done_reason=="stop"`.

| Arm | Reasoning tokens | Reasoning + answer |
|---|---|---|
| F06-A | 1795 – 2685 | 2040 – 2873 |
| F07-A | 1773 – 2864 | 2083 – 3118 |
| F11-B | 1632 – 2177 | 1858 – 2413 |
| F14-A | 1054 – 1640 | 1311 – 2060 |
| 4 controls | 1076 – 1841 | 1184 – 2107 |

Not explained by prompt size or chunk count: F14-A and F11-B had the largest prompts
(12906/12913 tokens) and the lowest reasoning. F14's arms A and B had byte-identical
prompts; A was truncated and B was not. Question type shifts the average somewhat (F07, an
open-ended synthesis question, reasoned longest) but not predictably.

## Consequences
`NUM_PREDICT` 4000 (882 over the highest total measured), `CHUNK_BUDGET_TOKENS` 11787, and
one automatic retry on `done_reason=="length"` (T-039, D-014). See `docs/DESIGN.md`
§ Reasoning + answer reservation.

## Confidence and limits
32 samples over 8 arms is still a finite sample; 4000 is a margin over the observed
maximum, not a proven bound, and is why the retry exists. The sample was drawn only from
arms that had truncated plus four that had not — not a random sample of all questions, so
the *frequency* (5 of 32) overstates how often an arbitrary question exceeds 2542; the
*existence and size of the tail* is what is solid. Only measured for `qwen3:30b-a3b`;
`qwen3:8b` (T-033) reasons differently and would need its own measurement before reusing
these numbers. Measured with Ollama's default sampling (no explicit temperature/seed).
