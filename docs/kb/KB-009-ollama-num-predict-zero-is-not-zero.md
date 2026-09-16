# KB-009 — Ollama's `num_predict:0` does not mean "generate nothing" — it generated 485 tokens on a 9-word prompt

**Area:** Local model (Ollama) — generation options
**Status:** verified
**Date:** 2026-09-16  ·  **From:** T-008

## Claim
`options.num_predict: 0` to `/api/generate` does **not** cap generation at zero tokens. On
`qwen3:30b-a3b`, a trivial prompt ("The quick brown fox jumps over the lazy dog.") with
`num_predict: 0` produced `eval_count: 485` — a full, apparently-unbounded generation, not
an empty one. `num_predict: 1` behaves as expected: `eval_count: 1`, empty `response`.
`prompt_eval_count` (the token count of the *input* prompt) was identical in both cases
(20 tokens) — that field is unaffected by `num_predict` either way, which is what makes it
a reliable tokenizer-count technique in the first place (see T-008's context-budget work).

## Evidence
Ollama 0.34.0, `qwen3:30b-a3b`, RTX 4090. `scripts/t008_smoke_test.py`:

| `num_predict` | `prompt_eval_count` | `eval_count` | `response` |
|---|---|---|---|
| `0` | 20 | **485** | ~2000-char real answer about pangrams |
| `1` | 20 | 1 | `""` (empty) |

## Consequences
Any code that intended "measure the prompt's token count without paying for generation" by
setting `num_predict: 0` is instead paying for a full, uncapped generation every time — a
real, avoidable cost (T-008 hit this while trying to build a cheap tokenizer-counting
helper). Use `num_predict: 1` for that purpose instead — one wasted generated token, not
hundreds. More broadly: `0` is not a safe stand-in for "off" across every Ollama numeric
option; each one needs checking rather than assumed from its type.

## Confidence and limits
One model, one prompt, one run per value. Not tested: whether `num_predict: 0` behaves the
same on `/api/chat`, on other models (`qwen3:8b`, `llama3.1:8b`), or whether it's actually
equivalent to `-1` (infinite) rather than some other unbounded default — only that it is
clearly not zero.
