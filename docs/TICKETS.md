# TICKETS

The backlog. `docs/PLAN.md` holds phases and exit criteria; this file holds the work.

IDs are `T-001`, `T-002`, … assigned in order, never reused, never renumbered. Use the
`ticket-write` skill to add one and the `ticket-done` skill to close one.

**Statuses:** `todo` · `in-progress` · `blocked` · `review` · `done`

**Git linkage:** branch `t/T-0NN-slug` · commit `T-0NN: imperative summary` ·
PR title `T-0NN — Title`. One ticket ID per commit.

---

## Open

### T-002 — YouTube captions feasibility test

**Status:** review
**Size:** M  ·  **Branch:** `t/T-002-youtube-captions`

**Goal:** know, with evidence from this machine, whether captions can be fetched for the
chosen YouTube channels — the input the transcript-source decision rests on.

**Why:** `docs/PLAN.md` Phase 0 exit criteria requires the transcript source decided
(captions vs. title+description) before Phase 1 ingest is built; `docs/GOAL.md` non-goals
gate Whisper on this test failing.

**Acceptance criteria**
- [x] A script fetches captions for the latest videos of 3–5 chosen channels (at least 3
  videos attempted per channel) → `scripts/t002_youtube_captions.py`, run against all 4
  channels, 5 videos each (20 total)
- [x] For each attempt, success/failure and error type (no captions, blocked, other) is
  recorded → per-video result in `data/t002_youtube_captions.json` (gitignored, local only)
- [x] Success rate and error types are written to `docs/kb/` via `kb-entry` →
  [KB-001](kb/KB-001-youtube-caption-availability.md)
- [ ] The title + description fallback is confirmed available for at least one video that
  has no captions → **not met as literally stated.** 20/20 videos had captions, so there
  was no real failure to test the fallback against. Confirmed instead that `yt-dlp`'s same
  call returns non-empty `title`/`description` for every video (see KB-001), which is
  necessary but not sufficient — the fallback path itself has never actually run.
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the transcript-source choice,
  with the evidence cited → D-001

**Out of scope:** the real ingest pipeline, chunking, storage — this only establishes
whether the source works.

**Depends on:** T-001
**Notes:** Added `yt-dlp` and `youtube-transcript-api` (see `requirements.txt`) — approved
by me for this ticket up front. Left in `review` rather than `done` because of the
unmet criterion above; needs my call on whether the strong 100%-success result is
enough to accept D-001 as-is, or whether the fallback should be exercised against a
deliberately caption-less video before this closes.

---

### T-003 — HF Daily Papers API feasibility test

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-003-hf-daily-papers`

**Goal:** know that the HF Daily Papers API gives the fields the project needs, for both
recent and past dates.

**Why:** `docs/PLAN.md` Phase 0 requires confirming which fields exist and that past dates
work, before Phase 1 builds a collector on top of the API.

**Acceptance criteria**
- [ ] A script calls `/api/daily_papers?date=` for each of the last 14 days
- [ ] For each response, presence of title, abstract, publication date and arXiv id is
  confirmed (or the missing ones are named)
- [ ] At least one date more than 10 days in the past returns data, confirming historical
  dates work
- [ ] One raw JSON response is saved into the repo (per the risk register: "raw JSON is
  saved")
- [ ] Findings (field shapes, gaps, rate limits if hit) are written to `docs/kb/` via
  `kb-entry`

**Out of scope:** normalizing the response into the Phase 1 document shape — this only
confirms the raw API's behaviour.

**Depends on:** T-001
**Notes:** —

---

### T-004 — Local model test on the RTX 4090 (Ollama)

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-004-local-model`

**Goal:** know that one large (~30B class, quantized) and one small (~8B) model both run on
this PC via Ollama and can answer a question from pasted context, with speed and VRAM
recorded.

**Why:** `docs/PLAN.md` Phase 0 requires the model pair chosen and recorded before later
phases build retrieval and evaluation around them.

**Acceptance criteria**
- [ ] One ~30B-class quantized model and one ~8B model are pulled and run via Ollama on the
  RTX 4090
- [ ] Each model is given the same test question with pasted context and produces an answer
- [ ] Response time and peak VRAM usage are recorded for each model
- [ ] Findings are written to `docs/kb/` via `kb-entry`
- [ ] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen model pair, with the
  evidence cited

**Out of scope:** the retrieval/answer-generation pipeline (Phase 2) — this only confirms
the models run and answer from pasted context.

**Depends on:** T-001
**Notes:** Ollama and the two model pulls are already implied by `docs/PLAN.md`'s hardware
section, not a new dependency decision — no need to stop and ask for these specifically.

---

### T-005 — Vector store date-range filtering test

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-005-vector-store-date-filter`

**Goal:** know that a candidate vector store can filter by publication-date metadata
combined with similarity search, before committing to it for Phase 1.

**Why:** `docs/GOAL.md`'s claim under test is that date-aware retrieval beats plain
similarity search; that only works if the store can filter by date range at all.
`docs/PLAN.md` Phase 0 requires this confirmed before committing to a store.

**Acceptance criteria**
- [ ] A small test collection of documents with varying publication dates (as metadata) is
  inserted into a candidate vector store
- [ ] A query demonstrates similarity search restricted to a date range, returning only
  documents inside that range
- [ ] A second query without the date filter is run against the same data to confirm the
  filtered and unfiltered results differ as expected
- [ ] Findings are written to `docs/kb/` via `kb-entry`
- [ ] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen vector store, with
  the evidence cited

**Out of scope:** the production schema for Phase 1 storage — this is a throwaway test
collection.

**Depends on:** T-001
**Notes:** Adding a vector store library is a new dependency — per `CLAUDE.md` "In-loop",
stop and ask before adding it.

## Done

### T-001 — Commit GOAL/PLAN and point CLAUDE.md at them

**Status:** done
**Size:** S  ·  **Branch:** — (see note)

**Goal:** the repo's docs describe a real project instead of an empty placeholder, and that
state is committed so it survives.

**Why:** `docs/GOAL.md` and `docs/PLAN.md` were filled in but uncommitted, and
`CLAUDE.md`'s "What this is" section still said the repo was undefined. Every later ticket
depends on this being true and in git.

**Acceptance criteria**
- [x] `CLAUDE.md`'s "What this is" section is rewritten to give the one-sentence summary
  from `docs/GOAL.md` and points to `docs/GOAL.md` (goal) and `docs/PLAN.md` (phases)
  instead of saying the repo is empty/undefined
- [x] `CLAUDE.md` no longer contains the placeholder line "VG-09 is an empty repository —
  no code, README or stated goal exists yet"
- [x] `git log` shows one commit, message `T-001: ...`, containing `CLAUDE.md`,
  `docs/GOAL.md`, `docs/PLAN.md`, and `docs/TICKETS.md` (with this ticket set) — commit
  `56a9f09`
- [x] `git status` is clean after the commit
- [x] The commit message carries a `T-001` prefix so the pre-commit hook accepted it

**Out of scope:** `docs/DESIGN.md`, the "Stack" and "Hard rules" sections of `CLAUDE.md` —
those stay placeholders until Phase 0 produces real architecture decisions.

**Depends on:** —
**Notes:** Committed directly to `master` as the repo's root commit rather than on
`t/T-001-bootstrap-docs` — there was no prior commit to branch from, so the branch
convention starts properly with T-002. The root commit also swept in the rest of the
harness scaffolding (`.claude/`, `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`,
`docs/kb/INDEX.md`, `docs/sessions/README.md`, `docs/skill-template.md`), all of it
untracked placeholder content with nothing to review — not scope creep, just what "first
commit of a new repo" means.
