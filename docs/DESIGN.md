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

T-008's original draft system prompt tokenized to 171 qwen3 tokens. **Finalized by T-024**
(`vg09.answer.SYSTEM_PROMPT`) after a real run (T-023) found the model doesn't reliably
follow a "cite like [Title, YYYY-MM-DD]" instruction — it cites the bracketed *source
number* shown in the prompt instead. The instruction now asks for exactly that (cite by
number; T-024 resolves the number back to a real citation), which happens to be slightly
shorter: 157 qwen3 tokens, re-measured for real. Otherwise unchanged — answer only from
the provided sources, respect a date range implied by the question, stay concise. Three real
questions, one per `docs/GOAL.md` question type, tokenized to 19, 21 and 22 tokens.
**Reserved: 40 tokens** (rounded up from the observed max with headroom for a longer real
question from T-014's eval set).

**Amended by T-030/D-013:** an explicit "always answer in English, even if the question is
asked in a different language" instruction was added — a deliberate language policy, not
left to whatever the model happens to do by default (D-013). Re-measured for real after the
change: **173 qwen3 tokens** (was 157).

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

Max observed across both runs: 1150. T-008's original reservation was 2000 tokens (~74%
headroom over that max).

**Superseded by T-028: raised to 2542 tokens, after a real truncation I found.** A real
user question ("Vad har hänt med AI-agenter senaste veckan?", 20 packed chunks) hit
`done_reason=="length"` in the real chat UI (T-025) — the *reasoning*, not the answer, was
eating the 2000-token cap. Three real re-runs of that exact question (same retrieved context,
only sampling varied) measured reasoning alone, separately from the answer:

| Run | `done_reason` | reasoning tokens | % of the old 2000 cap | answer tokens |
|---|---|---|---|---|
| 1 | `stop` | 1230 | 61.5% | 272 |
| 2 | `length` | **1842** | **92.1%** | 176 (cut off mid-word) |
| 3 | `stop` | 1349 | 67.5% | 322 |

T-008's original table measured *combined* reasoning+answer length across different question
types; this table is the first time reasoning and answer were measured **separately** for the
*same* question, and shows reasoning alone — not the answer — is what threatens the cap.

**New reservation: 2542 tokens**, derived from this measurement, not a round number:
`1842` (worst observed reasoning) `+ 400` (room for a full answer — real complete answers
measured 176-322 tokens) `+ 300` (margin — roughly half the 612-token spread already observed
across just three samples, hedging against further variance without inflating the chunk
budget more than three real data points can justify) `= 2542`. Set as `num_predict:2542`
(`vg09.answer.NUM_PREDICT`) on every real call — an actual hard ceiling, not just a budget
line item.

**Superseded by T-039: raised to 4000 tokens, plus one automatic retry.** T-028's three
samples were of *one* question, and the worst of them (1842) was treated as if it bounded
the whole tail. It didn't: T-032's real 15×2 run still hit `done_reason=="length"` on 4 of 30
calls (F06-A, F07-A, F11-B, F14-A), each with an empty answer — the reasoning alone had used
the whole cap. A read-only probe then re-ran those four arms 5× each and four
non-truncated arms 3× each (32 real runs, same retrieval, prompt and `num_ctx`; `num_predict`
raised to 8000 and the response streamed, so reasoning tokens and answer tokens were counted
separately, exactly, instead of inferred; `scripts/t039_reasoning_length_probe.py`, raw
samples in `docs/eval-results/2026-09-22-t039-reasoning-probe.jsonl`):

| Arm (packed chunks) | Reasoning tokens, per sample | Reasoning + answer | Runs over 2542 |
|---|---|---|---|
| F06-A (35) | 1795, 1821, 2056, 2145, 2685 | 2040–2873 | 1 of 5 |
| F07-A (37) | 1773, 2350, 2669, 2772, 2864 | 2083–3118 | 4 of 5 |
| F11-B (36) | 1632, 1662, 1753, 1936, 2177 | 1858–2413 | 0 of 5 |
| F14-A (34) | 1054, 1156, 1158, 1332, 1640 | 1311–2060 | 0 of 5 |
| 4 controls (22–38) | 1076–1841 (median 1249) | 1184–2107 | 0 of 12 |

Highest total across all 32 runs: **3118**. 5 of 32 runs (all in the four arms that had
truncated) exceeded 2542; in F06-A and F07-A, 4 of 10 runs exceeded it with reasoning alone.
Every run ended `done_reason=="stop"` at this cap. What this does and does not show:

- *Sampling variance is real and large*: the same prompt gave 1795–2685 reasoning tokens
  (F06-A), and F14-A's original truncated run and its identical-prompt B arm (same 34
  chunks, same 12906 prompt tokens) disagreed. F06-A and F07-A also completed cleanly in
  T-031 with byte-identical context.
- *It is not the prompt size or chunk count*: F14-A and F11-B had the largest prompts and
  among the lowest reasoning in the probe.
- *The question moves the average, not reliably*: the four controls (F01, F04, F05, F15)
  reasoned a median 1249 tokens against 1808 in the four truncated arms, and F07 ("what
  does the research say about text-to-video in the last month") reasoned longest (median
  2669) — but F14-A, also truncated originally, had the lowest reasoning in the probe
  (median 1158) and F15, a broad control, reached 1841. A tendency at best, not a rule
  that could be used to predict which questions need more room.
- *T-028's number was not wrong arithmetic, it was too few samples*: `1842 + 400 + 300`
  was derived correctly from what was measured; three samples of one question could not
  contain a tail that five questions × 3–5 samples then showed reaching 2864.

**New reservation: 4000 tokens** (`vg09.answer.NUM_PREDICT`) — 882 over the highest
reasoning+answer total measured (3118), which is a heuristic over a finite sample, not a
proven bound. That is why it is paired with **one automatic retry**
(`vg09.answer.MAX_RETRIES`, D-014) when the first answer still ends `"length"`; see
*Detect and surface `done_reason == "length"`* below. The cost is real: the reservation
comes out of the chunk budget one-for-one, 1458 tokens.

**Effect of the smaller chunk budget, checked for real** (`scripts/t039_verify_chunk_budget_impact.py`,
output in `docs/eval-results/2026-09-22-t039-chunk-budget-impact.txt`; same real
`pack_to_budget()` with T-038's formatted-source measurement run at both budgets in one
process, anchor 2026-09-17, all 15 real questions): the first 5 packed chunks are
**identical under 11787 and 13245 for all 15 questions**, and the smaller packed set is
always a strict prefix of the larger — the budget cut only ever removes chunks from the
bottom of the ranking. 9 of the 15 questions lose 3–5 chunks (35 in total, e.g. F01 38 →
34, F08 37 → 32); the other 6 (F04, F05, F10, F11, F13, F15 — already under the new budget
at their old packed size) are unchanged.

### Remaining budget for retrieved chunks

```
16000 (num_ctx)
 -  173 (system prompt, T-030's English-answer-instruction wording)
 -   40 (question, reserved)
 - 4000 (reasoning + answer, T-039's measured reservation)
 = 11787 tokens available for retrieved chunks
```

(171/13789/2000/13803/157/13261/2542/13245 in earlier tickets' own historical records, e.g.
T-008/T-022/T-024/T-028's acceptance-criteria evidence, describe the numbers as they stood
when those tickets closed — not rewritten after the fact; this section and
`vg09.retrieval.CHUNK_BUDGET_TOKENS`/`vg09.answer.NUM_PREDICT` are the current, live
numbers.)

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

**Chunk size: capped at 400 qwen3 tokens** for a chunk's own *document text* — but this is
no longer the whole story once a chunk is actually packed into a prompt (see the T-038
correction immediately below). A whole HF Daily Papers abstract is a natural chunk unit and
already fits this cap with room to spare in general (median 307, though a real production
chunk was later found at 405 — see T-038 below; this cap bounds T-012's chunking target,
not a hard per-chunk assertion). This cap is a hard requirement on T-012's chunking, not
just a description of HF's abstracts: a YouTube transcript is not naturally this short, so
T-012 splits transcripts into timestamp-based windows (§ below) rather than embedding a
whole transcript as one chunk.
**HF confirmed (T-012):** one chunk per paper (the whole abstract) — real production run,
1184 real chunks, essentially all under the cap by construction (same 20-abstract
distribution T-008 measured; T-038 later found one real chunk at 405, 5 over the nominal
cap — the abstract-based chunking target, not an enforced hard ceiling). **YouTube still an
estimate:** this project has no real YouTube transcript text yet (`IpBlocked` since T-009,
KB-008) — T-012's YouTube chunk-size target is calibrated from a real qwen3 tokenizer
measurement against *synthetic* caption-style text (real English text,
lowercased/depunctuated to mimic KB-001's no-punctuation auto-captions — see
`scripts/t012_caption_token_calibration.py`), targeting 350 of the 400-token cap. Re-check
against real transcript-derived chunks once T-017 unblocks and produces real captions.

**T-038 correction — the packing budget under-counted every real chunk's actual prompt cost
since T-008.** A packed chunk isn't sent to the model as its bare 400-token-capped document
text alone: `vg09.retrieval.format_source()` (used identically by both packing-time
measurement and real prompt construction, since T-038) wraps it in
`"[N] {title} ({url}, feed date {date})\n{text}"` first — real citation-number, title, url
and date text that the original packing measurement (`count_qwen_tokens(c.text)` alone)
never counted. Real measurement against the production store
(`scripts/t038_measure_wrapper_overhead.py`) found this wrapper costs **41-83 real qwen3
tokens per chunk** — 41 for the shortest real title in the store, 83 for the longest (189
real characters: "Specification-first convergence with an AI coding agent: a case study
of..."), dominated by the fixed-ish `https://huggingface.co/papers/...`/`https://
www.youtube.com/watch?v=...` URL length even for a short title, not negligible either way.
This is why a real question (T-031's F07, 44 packed chunks) could reach a real
`prompt_eval_count` of 15349 — far more than the ~13458 the budget math assumed as an upper
bound — silently eating into the reasoning+answer reservation and leaving the real answer
empty. See KB-018.

**`CHUNK_BUDGET_TOKENS`'s own reservation formula did not need to change** (T-038; the
numbers in this paragraph are T-038's, since superseded by T-039's `4000` / `11787` —
`16000-173-40-4000=11787`) — `16000-173-40-
2542=13245` was always the correct answer to "how many tokens are left over for whatever
gets packed"; the bug was in what packing *thought* a chunk cost, not in this arithmetic.
`vg09.retrieval.pack_to_budget()` now measures each candidate's real formatted cost
directly (`count_qwen_tokens(format_source(c, ...))`), so it naturally packs fewer chunks
per question and the real total sent to the model correctly stays within 13245 — no
separate "recomputed budget constant" was needed once the measurement itself was fixed.

**Max top-k: 24** = `11787 // 488`, floored (T-039; T-038's figure below was 27 at the
old 13245 budget). The T-038 derivation, still valid apart from the budget:
**27** = `13245 // 488`, floored — **corrected from the previous 33**
(`13245 // 400`, which assumed zero wrapper overhead). 488 is the real worst-case chunk
cost actually observed in the production store (`scripts/t038_measure_wrapper_overhead.py`):
405 (a real chunk's own document text, itself already over the nominal 400 cap) + 83 (that
same chunk's real wrapper overhead) = 488. This is a ceiling, not a target: the real
retrieval call should still request whatever top-k the retrieval design wants (likely far
fewer than 27 for answer quality), with 27 only as the hard stop this budget allows. A
future re-ingestion with an even longer real title could push this real worst case higher
still — re-measure with `scripts/t038_measure_wrapper_overhead.py` if that's ever suspected,
rather than assuming 488 holds forever.

### What happens if retrieved chunks don't fit

24 is a worst-case ceiling, not a promise that any given top-k will fit — a bug in T-012's
chunking, or a chunk that slipped past the 400-token cap, could still produce a set of
chunks that doesn't. The answer-generation code (Phase 2, but binding on how T-012 exposes
chunks) must:

1. **Pack chunks by the real measured cost of what actually gets sent to the model, not by
   count and not by bare document text alone (T-038).** Sum each candidate's real qwen3
   token count of its full formatted source text (`vg09.retrieval.format_source()` —
   citation number, title, url, feed date, and the chunk's own text, exactly as it will
   appear in the real prompt) in relevance-descending order, and stop adding once the
   running total would exceed the chunk budget (11787, `vg09.retrieval.CHUNK_BUDGET_TOKENS`,
   T-039) — regardless of whether that happens before or after 24 chunks.
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
(157 tokens, measured — T-024's finalized wording) limits how bad a worst-case truncation
would be.

**Detect and surface `done_reason == "length"`.** The reasoning+answer cap
(`vg09.answer.NUM_PREDICT`, 4000 since T-039, 2542 from T-028 before that) is a real ceiling, not just a budget estimate —
it *can* cut a genuinely longer answer off mid-thought, and did for real before T-028's raise
(a `done_reason=="length"` I found in the live chat UI, T-025). Every answer-generation
call must check the response's `done_reason`: `"stop"` means a real, complete answer (matches
how T-008's own original measurements were validated — all real samples ended `"stop"`, at
the smaller scale they were tested at); `"length"` means the model was still generating when the
cap hit. A `"length"` result must be flagged to the user/UI as incomplete — never displayed
as if it were a finished answer with nothing missing.

**One automatic retry (T-039/D-014).** The cut-off is sampling variance in reasoning length
(see the 32-run measurement above), so `generate_answer()` repeats an identical call once
when the first ends `"length"`. `AnswerResult.retries` says whether that happened; the UI
shows a notice whenever it did, and the evaluation output logs the count per call and in
total. If the retry is also `"length"`, that second response is returned flagged incomplete
exactly as before — never a third attempt. Each attempt independently checks
`prompt_eval_count` against `num_ctx`.

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
  rule-based, stdlib-only parser (no LLM call, no new dependency), matching exactly the
  relative-time vocabulary T-014's real 15-question eval set uses in Swedish ("senaste N
  veckorna/dagarna/månaderna", "senaste veckan"/"månaden" without a number, "förra veckan",
  "den D `<månad>`") **and, since T-043, its real English equivalents** ("the last/past N
  weeks/days/months", "last week"/"this week"/"last month" without a number, "September 16"/
  "the 16th of September", "today"). English doesn't reuse the Swedish regexes translated
  1:1 — Swedish's "senaste" does double duty (window and ranking, disambiguated by what
  follows it); English already has separate natural words for the two jobs ("last"/"past"
  for a window, "latest"/"most recent" for ranking), so T-043 uses those instead of
  overloading one word. `today` is always an explicit parameter, `date.today()` is never
  read inside the module, so a re-run against the frozen eval dataset (T-020) resolves the
  same way regardless of the real wall-clock date.
- `None` — from either path, either language — means **no date filter**: retrieval runs
  unfiltered, per T-021's explicit rule that no range is ever invented. A bare plural with
  no number ("de senaste veckorna" / "recent weeks") is treated the same way in both
  languages: genuinely ambiguous, not a number to guess at.
- Real result against T-014's 15 real questions, `today=2026-09-16`
  (`scripts/t021_test_date_extraction_against_eval_questions.py`, Swedish; `scripts/
  t043_test_english_date_extraction.py`, real hand-written English translations of the
  same 15 — `docs/eval-results/2026-09-24-t043-english-date-extraction.md`): **identical
  tally in both languages** — 8/15 resolve to a concrete window matching
  `docs/eval-questions.md`'s own written conventions exactly, 7/15 correctly resolve to
  `None` (no time phrase, or a ranking word like "det senaste"/"the latest" that isn't a
  window) — 0 wrong extractions, 0 unexpected extractions on the unparseable ones, in
  either language.
- **Found real, not fixed by T-043 (out of scope for T-042, the ticket that surfaced
  it):** before T-043, this parser was Swedish-only — a real, live-discovered gap
  (T-042's own verification: an English question about "the last two weeks" resolved to
  no date filter at all). D-016 (UI text switches to English) made this the project's
  core feature being silently off for non-Swedish questions, not just a theoretical risk
  — T-043 closed it the same session it was found.

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

**Reasoning/answer split is a project-wide contract, not an answer-generation implementation
detail (T-011).** `vg09.llm.split_reasoning_and_answer(response) -> (reasoning, answer)` is
the *only* sanctioned way any code reads a Qwen3 chat response's text. KB-007's real, measured
finding: `think:false` does not suppress reasoning — it leaves `message["thinking"]` empty and
merges the chain-of-thought narrative straight into `message["content"]` instead, with no
field to detect that after the fact. Consequences:

- Every real call to a Qwen3 chat model in this project passes `think=True` explicitly, never
  `False` — there is no code path that's allowed to call with `think=False` and separately
  guard against the merged shape; the split utility is the single point that would catch it if
  one ever slipped through (`message["thinking"]` empty → raises, rather than silently
  returning merged reasoning+answer text as if it were a clean answer).
- No call site reads `response["message"]["content"]` directly and treats it as "the answer" —
  every real caller (T-023's answer-generation call, and anything built later that shows or
  stores a Qwen3 response) goes through this function first.

**Citations are resolved from the model's own positional references, not forced into a
different format (T-024).** A real run (T-023) found the model doesn't reliably follow a
"cite like `[Title, YYYY-MM-DD]`" instruction — it cites the bracketed *source number* shown
for each source in the prompt instead ("source [27]"). `vg09.answer.SYSTEM_PROMPT` now asks
for exactly that; `vg09.answer.number_sources()` is the single place source numbering happens
(the same mapping builds the prompt and resolves citations afterward, via
`vg09.citations.build_citations()`), so a number always means the same chunk on both ends. A
bracketed reference that can't be resolved — an out-of-range number, or any other bracket
shape — is collected as unlinked, never silently dropped. **Partially fixed (T-040/D-015):**
a numeric *range* (`[1-20]`) is now distinguished from a real multi-source citation by
count — at most 5 numbers resolves like a comma list, more than that is collected separately
as a descriptive enumeration (`CitationResult.descriptive_ranges`), not expanded into false
citations and not reported as unlinked either. **Residual limitation, not fixed:** this is a
count heuristic, not real understanding — a *short* bracket the model used descriptively
(e.g. "sources `[1]` and `[2]`" meaning "the first two", not evidence for a claim) still
can't be told apart from a genuine citation; only the long-range shape T-024's real F12 run
and T-032's real F10/F12 grading actually produced is covered.

## Sources page: user-chosen sources and in-app ingest (T-052–T-057, D-017)

**Problem:** the YouTube channels are a hardcoded list in `vg09/channels.py`, and ingest
is three terminal commands. Someone who clones the repo gets the author's four channels
and has to edit code to change them.

**Serves:** `docs/GOAL.md`'s "simple to install" and Definition of done item 1; beyond the
original Definition of done, added by explicit instruction (2026-10-02).

**Behaviour:**
1. The app has a second page, **Sources**, next to the question page.
2. It lists Hugging Face Daily Papers (on/off, weeks of history) and each YouTube
   channel with its real document count and latest feed date.
3. A channel is added by pasting its address or `@handle`. The address is checked
   against YouTube before it is saved. Its content becomes searchable after the next
   update, and the page says so.
4. Removing a channel removes its documents from the store and from `data/raw/`, after
   a confirmation. It stops being fetched.
5. **Update now** starts ingest in the background, with a warning that it takes minutes
   and a progress line. Questions can be asked meanwhile against what is already
   stored. New content is searchable once the store has been rebuilt at the end.
6. With no data and no saved configuration, the app opens on Sources with the four
   default channels pre-selected as suggestions.
7. The header marks the data as stale when the latest feed date is more than two days old.
8. **Update on opening (T-059, D-018):** the first page load of each browser session
   starts the same background update when the setting "Update when the app opens" is on
   (default), sources have been saved, nothing is running and no update finished today.
   The header follows the job every 3 seconds ("Updating… <step>"), reloads its counts
   when the job finishes without rerunning the page, and says in plain words when the
   last update failed ("Ollama isn't running" for a refused connection to port 11434).

**Not included:** scheduled ingest with the app closed (still a non-goal, D-018); choosing individual papers or
filtering Hugging Face by topic; sources other than HF Daily Papers and YouTube;
more than one ingest job at a time.

**Design impact:**
- `data/sources.json` (new, user-local, gitignored): `{"update_on_open" (T-059; absent
  reads as true), "hf": {"enabled", "backfill_weeks"},
  "youtube": {"backfill_weeks", "channels": [{"handle", "url"}]}}`. Read and written
  only through `vg09/sources.py`. When the file is missing, `vg09/channels.py`'s four
  channels are the defaults, so the terminal commands in the README keep working.
- `Document` gains an optional `channel` field and chunk metadata gains `channel`, so a
  channel's documents can be counted and removed. **A stored-format change**, additive;
  existing videos are assigned by a one-time migration that lists each configured channel.
- Ingest runs as a separate process started by the app (`vg09/ingest_job.py`), which
  writes its progress to `data/ingest_status.json`. A separate process, not a thread:
  Streamlit reruns the script on every interaction and would lose a thread's handle,
  and the job must survive the browser tab closing.
- `app.py` becomes two pages via Streamlit's own navigation.

**Verification:** each ticket's criteria; at the end a fresh clone with no `data/` is
taken through Sources in a real browser: change the channel list, update, ask a question.

**Risks:** YouTube blocking caption requests during an in-app update (already handled
by the Whisper fallback, but slow — the progress line must show it); the job process
dying without updating its status file (the status carries the process id and a
heartbeat time, and a stale one is reported as interrupted, not as running).

## What we deliberately don't build

- <…>
