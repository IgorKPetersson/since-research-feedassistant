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
