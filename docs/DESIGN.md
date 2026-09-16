# DESIGN

<How the system is built. This is the document read before touching architecture, the data
model or core logic. Keep it current — a design doc that lies is worse than none.>

## Architecture

```
<A diagram, even an ASCII one. Boxes and arrows beat three paragraphs.>
```

<One paragraph on what is deliberately absent — no backend, no queue, no cache — because
absences are what people accidentally add back.>

## Context budget (RAG prompt, `num_ctx=16000`)

T-008. Answers all go through `qwen3:30b-a3b` at the explicit `num_ctx=16000` D-005 fixed.
That one number is a single shared budget for the *entire* KV cache — Ollama/llama.cpp
allocate it once at load time (KB-007's "Correction") and it holds prompt tokens and
generated tokens together, not two separate pools. With conversation history a non-goal
(`docs/GOAL.md`), the prompt has exactly four parts sharing that budget: **system prompt +
retrieved chunks + question + generated reasoning/answer**. Every number below is a real
measurement against the actual models via Ollama (`scripts/t008_context_budget.py`,
raw results in `data/t008_context_budget.json`, gitignored) — never estimated from words or
characters (KB-005 already showed a word-count estimate can be off by ~20% in either
direction). Two different tokenizers matter for two different reasons, and both were
measured, not assumed equal:

- **qwen3's own tokenizer** governs the real `num_ctx=16000` budget, since that's the model
  actually generating the answer. Counted via `POST /api/generate` with `num_predict: 1`
  and reading `prompt_eval_count` — cheap and exact. (`num_predict: 0` was tried first and
  turned out to *not* mean "generate nothing" — it produced a full 485-token generation on a
  9-word prompt; `num_predict: 1` is the correct minimal-cost call. See KB-009.)
- **bge-m3's own tokenizer** governs what fits inside one embeddable chunk (its own context
  window is 8192 tokens, KB-007). Counted via `POST /api/embed`, which also returns a real
  `prompt_eval_count` for the embedding model's own tokenizer.

### System prompt and question

A representative (draft, to be refined when Phase 2 actually builds answer generation)
system prompt — instructs the model to answer only from the provided sources, cite title +
URL + feed date per claim, respect a date range implied by the question, and stay concise —
tokenizes to **171 qwen3 tokens**. Three real questions, one per `docs/GOAL.md` question
type, tokenized to 19, 21 and 22 tokens. **Reserved: 40 tokens** (rounded up from the
observed max with headroom for a longer real question from T-014's eval set).

### Reasoning + answer reservation

Measured by actually running the three representative questions end-to-end against real
retrieved context (4-5 real HF Daily Papers abstracts each, from `data/raw/hf/`; no
synthetic filler), `think:true`, `num_predict:-1` (unbounded, to observe the model's natural
stopping point — every run ended with `done_reason:"stop"`, i.e. a real EOS, not a cutoff).
`eval_count` is the *total* generated length (reasoning + answer combined — Qwen3 generates
the reasoning trace as real tokens before the answer, consuming the same KV cache, even
though Ollama returns them as two separate string fields per KB-007). Run twice (sampling
is stochastic — `eval_count` for the same question varies noticeably between runs, which is
itself the reason a single sample wouldn't have been trustworthy):

| Question type | Sources | `eval_count`, run 1 | `eval_count`, run 2 |
|---|---|---|---|
| "what's new" | 5 | 1150 | 993 |
| "did X come up" | 4 | 515 | 663 |
| "has Q progressed" | 4 | 708 | 868 |

Max observed across both runs: 1150. **Reserved: 2000 tokens**, set as `num_predict:2000` on
every real answer-generation call — not just a budget line item but an actual hard ceiling,
so the reservation is a guarantee, not a hope. (~74% headroom over the observed max; six
samples across two runs already show real run-to-run variance, and the system prompt asks
for concision, so a stricter cap risks cutting off a real answer more than a looser one
risks blowing the budget.)

### Remaining budget for retrieved chunks

```
16000 (num_ctx)
 - 171 (system prompt)
 -  40 (question, reserved)
 - 2000 (reasoning + answer, reserved via num_predict cap)
 = 13789 tokens available for retrieved chunks
```

### Chunk size and max top-k

Real per-source token cost, measured on **all 20** real HF abstracts available (not just the
3 used above), under both tokenizers:

| | qwen3 tokens | bge-m3 tokens |
|---|---|---|
| min | 161 | 185 |
| median | 307 | 362 |
| max | 363 | 416 |
| mean | 290 | 348 |

bge-m3 tokenizes the same real text to consistently more tokens than qwen3 (~15-20% more at
the median/max here) — the two are not interchangeable, which is exactly why both were
measured on the same real text rather than assumed equal. Neither ceiling comes anywhere
close to bge-m3's own 8192-token embedding limit at this chunk size, so bge-m3's window is
not the binding constraint here.

**Chunk size: capped at 400 qwen3 tokens.** A whole HF Daily Papers abstract is a natural
chunk unit and already fits this cap with room to spare (max observed 363). This cap is a
hard requirement on T-012's chunking, not just a description of HF's abstracts: a YouTube
transcript is not naturally this short, so T-012 must split any source text longer than this
into paragraph/window-sized sub-chunks — never embed a whole transcript as one chunk.
**Not yet measured**: this project has no real YouTube transcript text yet (T-009's runs hit
`IpBlocked`, KB-008) — the 400-token cap is sized from HF abstracts only, and should be
re-checked against real transcript-derived chunks once T-015's backfill produces some.

**Max top-k: 34** = `13789 // 400`, floored — the number of 400-token chunks that
provably fit the remaining budget in the worst case (every chunk at the cap). This is a
ceiling, not a target: the real retrieval call should still request whatever top-k the
retrieval design wants (likely far fewer than 34 for answer quality), with 34 only as the
hard stop this budget allows.

### What happens if retrieved chunks don't fit

34 is a worst-case ceiling, not a promise that any given top-k will fit — a bug in T-012's
chunking, or a chunk that slipped past the 400-token cap, could still produce a set of
chunks that doesn't. The answer-generation code (Phase 2, but binding on how T-012 exposes
chunks) must:

1. **Pack chunks by real measured token count, not by count alone.** Sum each candidate
   chunk's real qwen3 token count (same `num_predict:1` technique) in relevance-descending
   order, and stop adding once the running total would exceed the 13789-token chunk budget
   — regardless of whether that happens before or after 34 chunks.
2. **Order the assembled prompt so the least-recoverable content is added last, not
   first.** KB-005: content beyond `num_ctx` is silently dropped from the **front**, with no
   error. So the prompt is built as `[chunks, least-relevant-first] + [system prompt] +
   [question]` — never system-prompt-first. If the packing step above ever has a bug and the
   assembled prompt still overflows, the casualty is the least relevant chunk, not the
   instructions telling the model to cite sources, and not the question itself.
3. **A single oversized chunk that can't fit even alone is dropped, not sent.** Better to
   answer with one fewer citation than to send a prompt already known to overflow.
4. **Every real call still checks itself, per `CLAUDE.md`'s hard rule:** compare the
   response's real `prompt_eval_count` against `num_ctx` afterward and warn on truncation
   risk — this is a backstop for when 1-3 have a bug, not a replacement for them.

## Core model

<The central data structure or domain model, in code. If there is one thing the project
must get right, it is described here.>

```
<type definitions>
```

## Key flows

<For each important operation: what triggers it, what it touches, what it produces. A table
works well when there are several.>

| Trigger | Operation | Effect |
|---|---|---|
| <…> | <…> | <…> |

## Data model

```sql
<schema, or the storage layout>
```

<Why it is shaped this way. What a migration would cost.>

## Interfaces and contracts

<Anything two parts of the system agree on: API shapes, events, file formats. Changes here
are stop-and-ask territory.>

## What we deliberately don't build

- <…>
