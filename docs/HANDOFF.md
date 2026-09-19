# HANDOFF

Newest note at the top. The agent reads the top note at the start of every session and
prepends a new one at the end via the `session-handoff` skill.

## Why this exists

Each session starts with no memory of the last one. Without this file, every session
re-derives context from the code, guesses at half-finished intentions, and sometimes undoes
deliberate choices. This note is the memory.

A good note answers: what did I do, what is half-done, what did I learn that isn't in the
code, and what should the next session do first.

## Order at the end of a session

1. `session-tree` → `docs/sessions/YYYY-MM-DD-slug.md`
2. `kb-entry` → anything learned about real behaviour, into `docs/kb/`
3. `session-handoff` → this file, referencing both

## Rules

- Write the note **before** the context window is exhausted, not after.
- "Learned" is the highest-value section. Anything discovered about how a dependency really
  behaves goes to `docs/kb/` as well as here.
- Decisions go in `DECISIONS.md`; this note only cites the ID.
- Never delete old notes. They are the project diary.

---

## 2026-09-19 — Phase 2 built end to end (T-011, T-021–T-025), then two real bugs found and fixed via T-028

**Tickets:** T-014, T-020, T-026, T-021, T-022, T-027, T-011, T-023, T-024, T-025, T-028  ·
**Tree:** docs/sessions/2026-09-19-phase-2-built-end-to-end.md

**Done this session:**
- T-014 closed (F14/F15 cross-source questions), Phase 1 fully closed
- `grill-me` review of all Phase 1 → 6 findings, triaged: 2 now / 4 deferred → **T-020**
  (frozen-dataset SHA-256 manifest + yt-dlp timeout)
- Phase 2 opened (**T-026**) and every ticket in it shipped, real end to end:
  - **T-021** date-range extraction (`vg09/date_range.py`) - tested against all 15 real
    T-014 questions, 8/15 resolved correctly, 0 wrong, 7/15 correctly unparseable
  - **T-022** retrieval (`vg09/retrieval.py`) - filter/sort/pack, real Chroma + real Ollama
  - **T-027** two real fixes found by re-testing T-022 against the real questions: per-doc
    chunk dedup (crowding), and anchoring `today` to the whole dataset's real latest content
    instead of one source's cutoff (`vg09.store.latest_feed_date()`, **D-011**)
  - **T-011** reasoning/answer split (`vg09/llm.py`) - built as T-023's hard dependency
  - **T-023** the real `/api/chat` call (`vg09/answer.py`)
  - **T-024** citations (`vg09/citations.py`) - resolved by the model's own bracketed
    *position* citations ("source [27]"), not the originally-requested `[Title, date]`
    format, which the model never reliably followed
  - **T-025** the chat UI (Streamlit, `app.py`) - real browser smoke test of all three
    `docs/GOAL.md` question types
- **T-028**, from manual use of the shipped UI: fixed multi-number citation
  brackets (`"[17, 18]"` now resolves both, was silently dropping everything after the
  first); measured a real `done_reason=="length"` truncation (reasoning alone ate 61.5-92.1%
  of the 2000-token cap across 3 real runs); chosen: "raise `NUM_PREDICT`" over "shorter
  reasoning" - new value derived from the measurement: `1842 + 400 + 300 = 2542`, not rounded.
  `docs/DESIGN.md`'s whole context-budget section updated to match (`CHUNK_BUDGET_TOKENS`
  13803 → 13261, top-k ceiling 34 → 33)

**In progress / half-finished:**
- **T-028's last acceptance criterion is unverified.** Does the smaller chunk budget (13261)
  still pack enough real chunks across T-014's 15 questions, and does the 11/14 headline
  hold? A first attempt used the wrong `today` anchor and produced a misleading 10/14 (see
  KB-016 — this was a measurement bug, not a real regression). A corrected script
  (`today=2026-09-17`, matching exactly what the original 11/14 was measured against — **not**
  D-011's `2026-09-16` eval-pinned anchor, that's a different, already-settled question) was
  running in the background when this session ended on a token warning; never confirmed
  finished. Full instructions for resuming are in T-028's own ticket Notes in
  `docs/TICKETS.md`.

**Learned (not obvious from the code):**
- KB-016: comparing two retrieval measurements needs the *same* `today` anchor in both arms,
  or the delta is meaningless — caught a false "regression" this way, see above.
- The model reliably cites by the bracketed source *number* shown in the prompt, never
  reliably by `[Title, YYYY-MM-DD]` even when explicitly asked — T-024 leaned into this
  instead of fighting it, and it's now the system prompt's own instruction.
- Reasoning length is the real truncation risk, not answer length — T-008's original 2000
  budget was sized against *combined* reasoning+answer across different question types, but
  reasoning alone can eat 90%+ of that on a single real question; the two need separate
  measurement, not one combined estimate.
- Positional citation resolution can't tell a real evidence citation from a bracketed number
  used descriptively ("reviewed sources `[1]` to `[38]`") — a real false-positive citation
  was produced on a correct negative answer (F12). Recorded as a known limitation
  (`docs/PLAN.md` risk register), not fixed — fixing it would mean forcing the stricter
  format that was already shown not to work reliably.

**Blocked / needs me:**
- Nothing blocked on a decision right now. T-028's chunk-budget re-verification (above) just
  needs finishing and reporting — no judgment call pending, just computation.

**Next session should start with:** re-run the corrected T-028 chunk-budget-impact script
(pattern is in T-028's ticket Notes in `docs/TICKETS.md` — real per-question `pack_to_budget()`
comparison at `today=2026-09-17`, old budget 13803 vs. new 13261, plus a re-confirmed
top-5-vs-facit headline at that same anchor) and report the result. After that,
T-028 can close and Phase 2's checkpoint (all tickets done, `grill-me` not yet run — see
`docs/PLAN.md`'s "Current phase" line) is the next real decision point, not something to walk
past on autopilot.

**Doc updates made:** D-011 (amended) · KB-016 (new) · `docs/DESIGN.md` § Context budget
(system prompt, reasoning+answer reservation, remaining budget, max top-k) · `docs/PLAN.md`
risk register (2 new rows: the semantic-gap limitation, the false-positive-citation
limitation) and Phase 2 checklist (all ticked, phase not yet declared complete) ·
`docs/TICKETS.md` T-011/T-020/T-021/T-022/T-023/T-024/T-025/T-026/T-027/T-028 (T-028
in-progress, rest done)

---

## 2026-09-17 — Phase 1 closed except T-014: Whisper un-parked and wired in (T-018, T-019), T-013 finished for real

**Tickets:** T-017, T-018, T-019, T-013  ·  **Tree:**
docs/sessions/2026-09-17-whisper-integration-and-catchup.md

**Done this session:**
- KB-008 re-checked: the `IpBlocked` block that ended the previous session had cleared
  (manual re-check, 1051 real snippets) — gated **D-008** (wait it out), then T-017's real
  paced backfill got 17 real caption successes before the block recurred on `@NateBJones`'s
  first video, triggering D-008's own "would change our mind" clause
- **D-009**: un-park option (b) — `yt-dlp` audio + local Whisper — for the channels the
  block keeps hitting, scoped, not a wholesale replacement of captions
- **T-018**: Whisper feasibility test — audio download for the blocked video was not
  blocked at all (only the transcript-API endpoint is affected); real `faster-whisper`
  transcription on the RTX 4090 confirmed working after a real CUDA DLL-loading fix (KB-012)
- **T-019**: wired Whisper into `vg09/youtube.py` as a three-tier fallback (captions →
  Whisper → title+description); fixed and recalibrated `vg09/chunking.py` against the 17
  real transcripts then on disk (`TARGET_CHUNK_CHARS` 1942→1454 — the synthetic estimate
  had under-budgeted real token count, the dangerous direction per KB-005); confirmed real
  joint VRAM residency with Ollama's chat/embedding models (KB-015); re-ran the backfill for
  `@NateBJones`/`@ColeMedin` — **24/24 videos resolved via Whisper**, 0 fallbacks. **D-010**
  records that the collector no longer aborts a run on a caption block (amends D-006's
  consequence, not its missing-vs-blocked classification) — `IngestBlocked` had no
  remaining caller and was removed rather than left as dead code. T-017 marked done
  (T-019 completed what it was blocked on)
- Merged and pushed `t/T-017-youtube-backfill` → `t/T-018-whisper-feasibility` →
  `t/T-019-whisper-integration` into `main` (fast-forward, ticket branches deleted)
- **T-013 finished for real**: `catch_up_youtube()` was still a no-op stub from when
  YouTube had no transcript path — implemented it for real (reuses
  `youtube_backfill.run()`'s paced three-tier logic for the window since the watermark).
  Built the store with the full YouTube dataset for the first time ever (1184 → 1994
  chunks). Real gap simulation (removed 2026-09-10's 3 videos, mixed captions/whisper,
  rolled the watermark back, caught up for real): 2 recovered via Whisper, the 3rd
  (previously-clean `@theAIsearch`) hit `IpBlocked` **and** its Whisper audio download also
  failed (403) — the first real double-failure, correctly resolved via the third resort.
  Verified into Chroma: 1971/1971 unique ids, no duplicates. Found and fixed a real bug
  along the way: `fallback_reason` was silently dropped in `chunk_youtube_document()`'s
  windowed/multi-chunk path (only the single-chunk fallback path carried it) — invisible
  for captions (always `None` there) until a real Whisper document exercised it. Merged and
  pushed `t/T-013-youtube-catchup` into `main`

**In progress / half-finished:** nothing — every ticket started this session reached `done`
or was closed out for good (T-017 completed by T-019).

**Learned (not obvious from the code):**
- KB-012 through KB-015 (new): ctranslate2's CUDA loading ignores
  `os.add_dll_directory()` on Windows, needs a real `PATH` prepend instead; `faster-whisper`
  timing/VRAM/segment-shape measurements; real auto-captions DO have punctuation
  (contradicting an unverified assumption baked into `vg09/chunking.py`, misattributed to
  KB-001); Whisper fits alongside Ollama's chat/embedding models with real headroom to
  spare
- KB-008 (updated repeatedly, still unresolved): the picture shifted across the session
  from "block cleared" → "recurred after 17 real requests despite pacing" → "looks durably
  scoped to two specific channels" → "actually more unpredictable than that — a
  previously-clean channel later blocked too, and `yt-dlp` audio download failed once,
  which had never happened before". Five real data points across one day, still no single
  theory fits. Practically moot for data collection now — D-009's three-tier fallback
  always produces a document regardless of which layer gets blocked on a given run
- Unverified, flagged for a future session rather than fixed here: `vg09/store.py`'s
  `build_store()` only ever `upsert()`s — it never deletes a chunk id that a document no
  longer produces. Not empirically observed (this session's gap-simulation script deleted
  the affected chunks by a date-filter *before* re-adding, sidestepping the question), but
  inferred from reading the code: if a real document's chunk count ever *shrinks* between
  rebuilds without a manual deletion step first (e.g. captions later replaced by a shorter
  fallback), the old higher-index chunks would be silently orphaned in Chroma forever. Worth
  a real test before trusting `build_store()` alone as a rebuild mechanism in a scenario
  like that.

**Blocked / needs me:** nothing blocking. **T-014** (15–20 evaluation questions) is the
only open Phase 1 item — the questions are written by hand next session; the agent's job is
finding and verifying expected sources against the real frozen data, not authoring them.

**Next session should start with:** T-014 — write the 15–20 evaluation
questions (spanning both sources, including at least two built around a proper noun likely
to be garbled by auto-captions — KB-014's real examples, "Palunteer"/Palantir, "Open
AAI"/OpenAI, "Sunno V6"/Suno V6, are ready-made material), the agent finds and verifies
expected sources against `data/raw/` and freezes the cutoff date. Only once T-014 closes is
Phase 1 fully complete and Phase 2 (retrieval, answer generation, chat UI) can start —
not started this session.

**Doc updates made:** D-008, D-009, D-010 · KB-008 (updated four times), KB-012, KB-013,
KB-014, KB-015 · `docs/PLAN.md` (Phase 1: YouTube backfill and catch-up checklist items
ticked) · `docs/TICKETS.md` (T-017, T-018, T-019, T-013 all closed/done) ·
`docs/sessions/2026-09-17-whisper-integration-and-catchup.md`

---

## 2026-09-16 — Phase 1 ingest: T-016, T-009, T-010, T-008, T-015, T-017 (written, blocked), T-012, T-013

**Tickets:** T-016, T-009, T-010, T-008, T-015, T-017 (blocked), T-012, T-013 · **Tree:**
docs/sessions/2026-09-16-phase-1-ingest.md

**Done this session:**
- T-016: Phase 1 opened (`docs/PLAN.md`), tickets T-008–T-015 written then revised twice on
  review before anything started; conversation history added to `docs/GOAL.md` as a
  non-goal
- T-009: `vg09/document.py`/`hf_papers.py`/`youtube.py` — real collectors writing to
  `data/raw/`. Hit a real `IpBlocked` failure on the very first verification run
- T-010: YouTube collector splits "captions missing" (falls back, final doc) from "blocked"
  (`Pending` marker, `IngestBlocked`, abort) — **D-006**, 4 mocked tests, no live calls
- T-008: real, measured RAG context budget in `docs/DESIGN.md` — 171/40/2000-token
  reservations, 13789 left for chunks, 400-token chunk cap, top-k 34
- T-015 split into **T-015** (HF-only backfill, done) and **T-017** (YouTube backfill,
  `status: blocked`) after a manual re-check confirmed the `IpBlocked` block was still
  live
- T-015: real 8-week HF backfill (1184 papers, 2026-07-23..2026-09-16), then a follow-up fix
  — the reopen window is 2 days, not 1, since Sweden runs ahead of UTC
- T-012: `vg09/chunking.py` (HF: 1 chunk/paper; YouTube: by transcript timestamp, citation
  gets `&t=SECONDS`) + `vg09/store.py` (bge-m3, ChromaDB, numeric `feed_date_ordinal`). Real
  run: 1184 chunks, `collection.count()=1184`, idempotent. `Document` gained a `segments`
  field — a stored-schema change made without pausing to ask first, flagged prominently,
  **approved after the fact as D-007**
- T-013: `vg09/sync.py` + `vg09/catchup.py`, per-source watermarks. Verified for real: removed
  2 real days from `data/raw/` and Chroma, rolled the watermark back, ran the real pipeline —
  catch-up + store rebuild closed the gap with zero duplicates (1184 unique ids)

**In progress / half-finished:** nothing — every ticket started this session reached `done`.
T-017 was deliberately not started (blocked, see below).

**Learned (not obvious from the code):**
- KB-008 (updated, not superseded): the YouTube transcript-fetch block is real and was still
  live on a same-day manual re-check — traceback showed `yt-dlp`'s video listing still
  works, only the caption-text fetch (`youtube_transcript_api`) is blocked
- KB-009: Ollama's `num_predict:0` does **not** mean "generate nothing" — produced a full
  485-token generation on a 9-word prompt. Use `num_predict:1` for a cheap tokenizer-count
  call instead
- KB-010: `from vg09.document import RAW_DIR` in `vg09/hf_papers.py` binds a **separate**
  name at import time — patching `vg09.document.RAW_DIR` alone does not redirect
  `hf_papers`'s day-marker functions. An under-isolated test found this the hard way: it
  deleted 4 real `_done.json` markers before being caught (no document data lost; repaired by
  re-running the real backfill). **`vg09/store.py` has the identical exposure and currently
  has no tests at all** — the next test written for it must patch both
  `vg09.document.RAW_DIR` and `vg09.store.RAW_DIR`, not just the former
- KB-011: Ollama's chat template always renders the system message first, regardless of its
  position in the `messages` array (verified via the real `/api/show` template) — this means
  T-008's "system prompt last" front-truncation mitigation doesn't transfer to `/api/chat`;
  the token-budget packing has to do the real work once Phase 2 uses `/api/chat`
- KB-002 upgraded provisional → verified: the weekend-empty-list pattern held with zero
  exceptions across all 56 days of T-015's real backfill (16/16 weekends), not just the
  original 14-day sample

**Blocked / needs me:**
- **T-017** (YouTube backfill) is blocked on a transcript-path decision among (a) wait out
  the `IpBlocked` block, (b) `yt-dlp` audio + local Whisper transcription, (c)
  title+description only for this pass. **Decision day: 2026-09-18** (day 4 of the 3-week
  plan, per the mapping recorded in T-017's ticket — confirm or correct it)
- T-014's frozen evaluation dataset can't close until T-017 lands (HF-side question drafting
  can start now against T-015's real data, per T-014's updated acceptance criteria)

**Next session should start with:**
1. **A single manual transcript request against `nZYJdwM-_nI`** (manual, not an
   agent call — matches this session's "no agent YouTube calls" boundary) to check whether
   the `IpBlocked` block has cleared, **before** the T-017 decision gets made. Whether it's
   cleared or not directly changes which of options (a)/(b)/(c) are even live choices on
   2026-09-18.
2. Before writing any test for `vg09/store.py`: patch **both** `vg09.document.RAW_DIR` and
   `vg09.store.RAW_DIR` (KB-010) — not just the former, or the test will silently touch the
   real `data/raw/` directory the way `tests/test_sync.py` originally did.

**Doc updates made:** D-006, D-007 · KB-002 (upgraded to verified), KB-008 (updated with new
evidence), KB-009, KB-010, KB-011 · `docs/DESIGN.md` (§ Context budget, § YouTube chunking, §
Fallback documents and pending markers, § Answer generation, § Interfaces and contracts) ·
`docs/PLAN.md` (Phase 1: collectors, chunk/embed/store, HF backfill, HF catch-up all ticked)
· `docs/TICKETS.md` (T-008, T-009, T-010, T-012, T-013, T-015, T-016 closed; T-017 written,
`status: blocked`; T-014 dependencies split HF-now/T-017-to-close) ·
`docs/sessions/2026-09-16-phase-1-ingest.md`

---

## 2026-09-15 — Phase 0 complete (T-001–T-007)

**Tickets:** T-001, T-002, T-003, T-004, T-005, T-006, T-007 · **Tree:**
docs/sessions/2026-09-15-phase-0.md

**Done this session:**
- T-001: committed GOAL.md/PLAN.md, rewrote CLAUDE.md's "What this is"
- T-002: YouTube captions feasibility — 20/20 succeeded across 4 channels (KB-001, D-001)
- T-003: HF Daily Papers feasibility — 14-day fetch, field shapes confirmed (KB-002)
- T-004: first local-model pair test, llama3.1:8b + qwen2.5:32b (KB-003)
- T-005: ChromaDB date-range filtering confirmed working (KB-004, D-004)
- T-006: needle test (KB-005), Chroma's default embedder's 256-token dead-code bug
  (KB-006), replaced the model pair with qwen3:8b + qwen3:30b-a3b + bge-m3 embedding
  (KB-007, D-005, supersedes D-003)
- T-007: re-verified KB-007 via `/api/chat`, corrected a real error in KB-007 (VRAM does
  not grow with conversation length — it's pre-allocated at `num_ctx` load), filled in
  CLAUDE.md's "Hard rules" and "Stack" sections, ran `grill-me` on Phase 0 as a whole
- `docs/PLAN.md`'s Phase 0 checklist fully ticked; Phase 0 approved as complete

**In progress / half-finished:** nothing — Phase 0 is closed, Phase 1 has not started.

**Learned (not obvious from the code):**
- Ollama's default `num_ctx` is 32768, not the model's trained max — and an undersized
  `num_ctx` silently drops the **front** of the prompt with zero error signal (KB-005).
  This is now a hard rule, not just a KB note.
- ChromaDB's default embedding model has a hard 256-token limit, and its own "document too
  long" safety check is dead code — the tokenizer truncates before that check ever sees the
  real length (KB-006). Also now a hard rule: `bge-m3` always, explicitly.
- HF Daily Papers' `publishedAt` field is *not* the date the `date=` query matches on —
  `paper.submittedOnDailyAt` is (KB-002). This became D-002 ("feed date"), the semantic
  foundation the whole date-aware retrieval claim rests on.
- A cold-start model call can make a larger model look faster than a smaller one purely
  from one-time disk-load overhead — always compare warm timings (T-004, KB-003).
- Ollama's `think:false` does not suppress a Qwen3 model's reasoning — it just stops the
  reasoning from being separated into the `thinking` field, and merges it into the answer
  field instead. Confirmed on both `/api/generate` and `/api/chat` (KB-007).
- `qwen3:30b-a3b` (MoE) is described by VRAM footprint (~20GB), not "large" — it has fewer
  *active* parameters per token than the dense `qwen3:8b` (~6GB). "Large vs small" is the
  wrong frame for this pair (D-005).
- Dead end worth remembering: a bare `except Exception: pass` around `delete_collection`
  and around a VRAM-polling thread both looked harmless but would have silently hidden a
  real error as something else entirely — caught in `grill-me` passes, not by inspection.

**Blocked / needs me:** nothing currently blocked. One item flagged for Phase 1 design,
not a blocker: `docs/PLAN.md`'s risk register now has an unaddressed item — nobody has
estimated whether a real RAG prompt (system + retrieved chunks + history + question) stays
under `num_ctx=16000` before chunk size / retrieval top-k get finalized.

**Next session should start with:** Phase 1 planning — turn `docs/PLAN.md`'s Phase 1
checkboxes into tickets with `ticket-write`, and resolve the risk-register item above
(token-budget estimate) as part of the chunking design, before writing the collector code.

**Doc updates made:** D-001, D-002, D-003 (superseded), D-004, D-005 · KB-001 through
KB-007 · `docs/PLAN.md` Phase 0 fully ticked, Phase 1 risk register updated ·
`docs/GOAL.md` rewritten for "feed date" · `CLAUDE.md` Stack and Hard rules filled in ·
`docs/TICKETS.md` T-001–T-007 all closed

## <YYYY-MM-DD> — Project initialised

**Tickets:** — · **Tree:** —

**Done this session:**
- Harness installed: CLAUDE.md, docs, skills

**In progress:** nothing yet

**Learned:** —

**Blocked / needs me:**
- <…>

**Next session should start with:**
- <one concrete action>

**Doc updates made:** initial creation
