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
