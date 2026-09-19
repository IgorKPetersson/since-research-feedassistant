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
transcript is not naturally this short, so T-012 splits transcripts into timestamp-based
windows (§ below) rather than embedding a whole transcript as one chunk.
**HF confirmed (T-012):** one chunk per paper (the whole abstract) — real production run,
1184 real chunks, all comfortably under the cap by construction (same 20-abstract
distribution T-008 measured). **YouTube still an estimate:** this project has no real
YouTube transcript text yet (`IpBlocked` since T-009, KB-008) — T-012's YouTube chunk-size
target is calibrated from a real qwen3 tokenizer measurement against *synthetic*
caption-style text (real English text, lowercased/depunctuated to mimic KB-001's
no-punctuation auto-captions — see `scripts/t012_caption_token_calibration.py`), targeting
350 of the 400-token cap. Re-check against real transcript-derived chunks once T-017
unblocks and produces real captions.

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

### YouTube chunking: by transcript timestamp, not sentence

T-012. Auto-generated captions have no punctuation (KB-001), so sentence-boundary chunking
isn't reliable. Instead, `vg09/chunking.py` groups consecutive transcript segments (the real
per-snippet `{text, start, duration}` T-010 confirmed `FetchedTranscript` provides) into
windows sized by real character count, closing a window once it reaches
`TARGET_CHUNK_CHARS` (calibrated above). Each chunk records the **real timestamp of its
first segment** (`start_seconds`), and its citation URL is
`{video_url}&t={int(start_seconds)}` — a citation for a YouTube chunk links straight to the
point in the video where that content was said, not just the video as a whole. A
`title_description` fallback document (D-006 — no captions were ever fetched, so there's
nothing to time) produces one whole-document chunk with no timestamp and an unmodified URL.

This can only be exercised against synthetic segment data today (`tests/test_chunking.py`) —
no real YouTube transcript exists yet. Re-verify chunk boundaries and citation timestamps
look sensible against a real video once T-017 unblocks.

### Fallback documents and pending markers in the store

`Pending` markers (`*.pending.json`, T-010) are never embedded — `vg09/store.py`'s
`load_documents()` skips them by filename, same as `_done.json` day-completion markers
(T-015); neither is a document with real `text` to chunk. `title_description` fallback
documents (D-006) **are** embedded — weaker source material is still better than no
citation — but every chunk built from one carries `text_source: "title_description"` (and
`fallback_reason`) in its Chroma metadata, so Phase 2's answer generation and citations can
tell a real transcript-backed claim from a title+description-only one, rather than
presenting both with equal confidence.

## Answer generation (Phase 2 — design notes only, nothing built yet)

Two things worth recording now, before Phase 2 starts, since they follow directly from work
already done in Phase 1:

**Message structure for `/api/chat`.** The system prompt goes in its own
`{"role": "system", ...}` message; retrieved chunks and the question go together in one
`{"role": "user", ...}` message. Verified against the real chat template
(`scripts/t012_check_chat_template.py`, `POST /api/show`): Ollama's Go template for
`qwen3:30b-a3b` unconditionally renders the system block
(`<|im_start|>system ... <|im_end|>`) **before** iterating `.Messages`, regardless of where
a system-role message sits in the `messages` array — so, unlike T-008's raw-string
`/api/generate` experiment (which controlled prompt order by literal string concatenation),
message *order* in the API call does not control rendered prompt order once `/api/chat` is
used. **This changes the truncation mitigation from the Context budget section above**:
under `/api/chat`, KB-005's front-truncation would eat the **system prompt** first, not the
chunks, since the system block is always rendered first. The token-budget packing (this
section, T-008/T-012) is therefore the real defense once `/api/chat` is used — ordering
chunks least-relevant-first inside the user message's own content is still worth doing
(free, and helps if the packing accounting has a bug), but it cannot protect the system
prompt the way raw-string "system last" ordering could. Keeping the system prompt short
(171 tokens, measured) limits how bad a worst-case truncation would be.

**Detect and surface `done_reason == "length"`.** T-008's `num_predict:2000` reasoning+answer
cap is a real ceiling, not just a budget estimate — it *can* cut a genuinely longer answer
off mid-thought. Every answer-generation call must check the response's `done_reason`:
`"stop"` means a real, complete answer (matches how T-008's own measurements were validated
— all real samples ended `"stop"`); `"length"` means the model was still generating when the
cap hit. A `"length"` result must be flagged to the user/UI as incomplete — never displayed
as if it were a finished answer with nothing missing.

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

**`data/raw/<source>/<feed_date>/`** (T-009/T-015/T-017): the durable normalized-document
store every other stage reads from, never re-fetching from YouTube/HF to rebuild anything.
- `<id>.json` — a final `Document` (`vg09/document.py`): `id`, `source`, `url`, `title`,
  `feed_date`, `text`, `arxiv_published_at` (papers only), `text_source`
  (`"captions"`|`"title_description"`, YouTube only), `fallback_reason` (D-006),
  `segments` (`[{text, start, duration}]`, YouTube captions only — preserves real per-snippet
  timing for T-012's timestamp chunking)
- `<id>.pending.json` — a `Pending` marker (T-010/D-006): a video whose caption fetch was
  blocked, not genuinely missing. Never chunked/embedded (T-012 skips by filename).
- `_done.json` — a day-completion marker (T-015, HF only). Not a document.

**ChromaDB store** (`data/chroma_store`, collection `vg09_chunks`, T-012): one row per
`Chunk` (`vg09/chunking.py`). Metadata carries `feed_date_ordinal` (`date.toordinal()`, an
**int** — KB-004: ISO date strings aren't guaranteed to compare correctly under Chroma's
`$gte`/`$lte`) alongside the human-readable `feed_date` string, plus `doc_id`, `source`,
`url`, `title`, and — only when present — `text_source`, `fallback_reason`,
`arxiv_published_at`, `start_seconds` (Chroma metadata values must be primitives; `None`
fields are omitted, never passed). Written via `collection.upsert()`, not `add()`, keyed by
deterministic chunk ids (`{source}:{doc_id}:{index}`) — idempotent by construction.

**Never call `collection.query(query_texts=...)` or `collection.add(documents=...)` without
also passing `embeddings=`/`query_embeddings=`.** Either silently invokes ChromaDB's default
embedding function (CLAUDE.md hard rule: never use it — KB-006's 256-token silent
truncation). Always embed via `vg09.store.embed_batch()` (explicit `bge-m3`,
`num_ctx=8192`) first, then pass the vectors in directly. Caught by self-review while
building T-012's smoke test, before it could have reached the real store.

**Date range: the UI ↔ retrieval contract (T-021).** `vg09.date_range.resolve_date_range
(question, today, manual_override=None) -> tuple[date, date] | None` is the single function
T-022 (retrieval) and T-025 (the chat UI) both call to get the date range a query should be
filtered by:

- `manual_override`, whenever the UI's date picker sets one, **always wins** over whatever
  was (or wasn't) extracted from the question text — never the reverse.
- With no override, the question text is parsed by `extract_date_range()` — a small,
  rule-based, stdlib-only Swedish parser (no LLM call, no new dependency), matching exactly
  the relative-time vocabulary T-014's real 15-question eval set uses ("senaste N
  veckorna/dagarna/månaderna", "senaste veckan"/"månaden" without a number, "förra veckan",
  "den D `<månad>`"). `today` is always an explicit parameter, `date.today()` is never read
  inside the module, so a re-run against the frozen eval dataset (T-020) resolves the same
  way regardless of the real wall-clock date.
- `None` — from either path — means **no date filter**: retrieval runs unfiltered, per
  T-021's explicit rule that no range is ever invented. A bare plural with no number ("de
  senaste veckorna") is treated the same way: genuinely ambiguous, not a number to guess at.
- Real result against T-014's 15 real questions (`scripts/t021_test_date_extraction_against_
  eval_questions.py`, `today=2026-09-16`): 8/15 resolve to a concrete window matching
  `docs/eval-questions.md`'s own written conventions exactly, 7/15 correctly resolve to
  `None` (no time phrase, or a ranking word like "det senaste" that isn't a window) — 0
  wrong extractions, 0 unexpected extractions on the unparseable ones.

**Filtering by date and sorting by date are two different mechanisms, not one (T-021/T-022).**
Three of T-021's real `None` results (F01 "de två senaste nyheterna", F03 "det absolut
senaste", F06 "det senaste") aren't missing a time phrase — they're a different question
*type* than the other 12. "senaste N veckorna"/"den D `<månad>`" name a **bounded window**:
retrieval should exclude everything outside it (a filter). "det/de senaste [N]" names a
**ranking**: "show me the most recent ones", with no boundary at all — every document is a
candidate, ordered by feed date descending, and the answer is whichever come out on top. A
window filter answers the first kind correctly and would silently produce nothing useful for
the second (there's no boundary to filter to), and a recency sort would be the wrong tool for
"what happened last month" (a sort has no cutoff, so it doesn't exclude anything outside the
month). Both mechanisms exist independently in retrieval (T-022):

- **Filter** (`resolve_date_range()`, above) narrows the candidate set to a `feed_date_ordinal`
  range before/while ranking by similarity. Produces nothing when the question names no
  window (`None`) — retrieval runs date-unfiltered.
- **Sort** re-orders an already similarity-matched candidate set by `feed_date_ordinal`
  descending instead of by similarity score, triggered by ranking language in the question
  (`vg09.date_range.detect_recency_ranking()`, T-022) — F01/F03/F06 are its real test cases.
  Produces nothing (falls back to plain similarity order) when the question names no ranking
  language either.

A question can trigger either, both (rare — "the most recent one from last month"), or
neither (plain semantic lookup, e.g. F08/F12/F14's "did X come up") — the two mechanisms
compose, they don't replace each other, and building one is never a substitute for the other.

## What we deliberately don't build

- <…>
