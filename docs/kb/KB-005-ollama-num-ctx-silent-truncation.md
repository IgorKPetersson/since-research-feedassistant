# KB-005 — Ollama's default num_ctx is 32768 (not the model's trained max), and content beyond num_ctx is silently dropped from the front with no error

**Area:** Local model (Ollama) — context window
**Status:** verified
**Date:** 2026-09-15  ·  **From:** T-006

## Claim
Ollama 0.34.0 defaults to `num_ctx=32768` when no override is given — not the model's
trained maximum (131072 for `llama3.1:8b`, per `ollama show`), and not the old widely-cited
legacy default of 2048. Setting `num_ctx` above the real prompt size changes nothing about
what's evaluated, only the allocated KV-cache buffer (and therefore VRAM). Setting
`num_ctx` **below** the real prompt size silently drops content from the **front** of the
prompt — no error, no warning, a normal HTTP 200 response — which is the worst case for
this project, since a planted fact, an early retrieved chunk, or early conversation history
is exactly what disappears first.

## Evidence
Run on 2026-09-15, Ollama 0.34.0, `llama3.1:8b`, RTX 4090. Script:
`scripts/t006_needle_test.py`. A haystack with a unique secret
(`"ZEBRA-7742-QUARTZ"`) planted at the very start, filler after it, then a question asking
for that secret back. Sent via `POST /api/generate` three ways:

| Run | `num_ctx` | `ollama ps` CONTEXT | `ollama ps` SIZE | `prompt_eval_count` | Found secret |
|---|---|---|---|---|---|
| No override | (default) | 32768 | 9.2 GB | 9796 | Yes |
| Explicit | 16000 | 16000 | 7.0 GB | 9796 | Yes |
| Explicit, undersized | 4096 | 4096 | 5.3 GB | **2050** | **No** |

All three runs reported `PROCESSOR: 100% GPU` in `ollama ps` — the undersized case isn't a
VRAM/CPU-spillover problem (that's KB-003's separate finding), it's a context-window
problem.

The real prompt was ~9796 tokens per Ollama's own count. A naive word-count estimate aiming
for "~12k tokens" (9024 words × assumed 1.33 tokens/word) predicted ~12032 and overshot —
this repetitive filler text tokenized to only ~1.09 tokens/word in practice (more words fit
per token than assumed, not fewer), so the real count came in about 19% under the estimate.
Word-count-based token budgeting for this kind of repetitive filler runs low, not high — a
naive estimate should not be trusted as a floor. At `num_ctx=4096`, only 2050 tokens were evaluated
(roughly half of `num_ctx`, consistent with the rest of the budget being reserved for the
response) and the model's own answer stated plainly that no secret code word appeared at
the start of the document — it had never seen that part of the prompt. No exception, no
non-200 status, no field in the response body flagging truncation.

## Consequences
Any code path that sets or inherits a `num_ctx` smaller than the actual prompt (system
prompt + retrieved chunks + conversation history + question) will silently lose the
earliest content in that prompt, and nothing in the API response signals it happened — the
response looks like an ordinary, confident answer. For Phase 1/2:
- The ingest/retrieval code must be able to estimate or count the real prompt token size
  before sending it, and either raise a real error or choose `num_ctx` accordingly, rather
  than assuming "it'll fit."
- If retrieved chunks are ever prepended before a system prompt or instructions, the
  chunks — not the instructions — will be the first thing dropped under an undersized
  context, which is a different (and worse) failure mode than losing the instructions.
- `docs/GOAL.md`'s citation requirement ("every answer cites its sources") gives no direct
  protection here: a truncated-away chunk simply won't be in context to cite, and the model
  may still answer fluently from whatever it did see, looking correct while being wrong.

## Confidence and limits
One model (`llama3.1:8b`), one run per `num_ctx` value, one haystack construction (secret
at the very front, English filler). Not tested: whether truncation behaves the same with
the secret placed in the middle or near the end (front-truncation would protect a
late-placed fact and might look like it "works" without ruling out the same underlying
bug), other model families, the `/api/chat` endpoint instead of `/api/generate`, or
whether `qwen2.5`-family models truncate the same way.
