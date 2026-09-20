# KB-018 — The chunk-packing budget under-counted the real prompt sent to the model since T-008; F07 (T-031) was the first real question to tip over it

**Area:** Retrieval (`vg09.retrieval`) — measurement methodology
**Status:** verified
**Date:** 2026-09-20  ·  **From:** T-031 (found it), T-038 (root-caused and fixed it)

## Claim
From T-008's original context-budget design through T-028's revision, `vg09.retrieval.
pack_to_budget()` measured each candidate chunk's token cost as `count_qwen_tokens(c.text)`
— the chunk's bare document text alone. But the real prompt actually sent to the model
(`vg09.answer.build_user_message()`, via what was `_format_source()`) wraps every packed
chunk in `"[N] {title} ({url}, feed date {date})\n{text}"` first — real citation-number,
title, url and feed-date text that this measurement never counted. This was true of every
real answer-generation call this project has made since T-023 first wired `/api/chat` up,
not a new regression — it simply hadn't been severe enough to visibly fail until a real
15-question evaluation run (T-031) happened to hit a question (F07) with enough packed
chunks (44) for the uncounted overhead to exceed what little headroom the reasoning+answer
reservation had left.

## Evidence
T-031's real run (`data/eval_results/2026-09-20-2004-t031-harness.md`, gitignored):
F07's real `done_reason=="length"` with a **completely empty** answer (worse than T-028's
original partial-truncation finding), `prompt_eval_count=15349` against a nominal ~13458
upper bound the budget math assumed (`173+40+13245`) — a 1891-token overrun.

Root-caused, not just observed: `scripts/t038_measure_wrapper_overhead.py`, a real
measurement against the production store (1971 real chunks), found the wrapper costs
**41–83 real qwen3 tokens per chunk** — 41 for the shortest real title/url/date
combination in the store, 83 for the longest (a 189-character HF paper title). Even the
shortest case isn't negligible, since the fixed-ish `https://huggingface.co/papers/...` /
`https://www.youtube.com/watch?v=...` URL text costs real tokens regardless of title
length. Across F07's 44 packed chunks, an average ~43 tokens/chunk of uncounted overhead
(1891 ÷ 44) lines up closely with this real per-chunk range.

## Consequences
`vg09.retrieval.format_source()` (moved from `vg09.answer._format_source()`, T-038) is now
the single source of truth for "what does a packed chunk actually look like in the real
prompt" — used both by `pack_to_budget()`'s real token-counting and by
`build_user_message()`'s real prompt construction, so the two can't drift apart again.
`docs/DESIGN.md`'s "max top-k" ceiling is corrected from `13245 // 400 = 33` (assumed zero
wrapper cost) to `13245 // 488 = 27` (488 = a real observed worst-case chunk: 405 bare
tokens + 83 real wrapper tokens). `CHUNK_BUDGET_TOKENS`'s own reservation arithmetic
(`16000-173-40-2542=13245`) did **not** need to change — it was always a correct answer to
"how much is left for whatever gets packed"; the bug was entirely in what packing believed
a chunk cost, not in the top-level reservation.

## Confidence and limits
The 41–83 token range is real but only two real data points (the store's real shortest and
longest title/url/date combinations at measurement time, 2026-09-20) — not a full
distribution. A future re-ingestion with an even longer real title could push the real
worst case higher than 83; `scripts/t038_measure_wrapper_overhead.py` is written to be
re-run cheaply (two real Ollama calls) rather than trusted to hold forever unmeasured
again — the exact mistake this entry documents.
