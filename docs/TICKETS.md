# TICKETS

The backlog. `docs/PLAN.md` holds phases and exit criteria; this file holds the work.

IDs are `T-001`, `T-002`, … assigned in order, never reused, never renumbered. Use the
`ticket-write` skill to add one and the `ticket-done` skill to close one.

**Statuses:** `todo` · `in-progress` · `blocked` · `review` · `done`

**Git linkage:** branch `t/T-0NN-slug` · commit `T-0NN: imperative summary` ·
PR title `T-0NN — Title`. One ticket ID per commit.

---

## Open

### T-008 — Context budget for the RAG prompt in docs/DESIGN.md

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-008-context-budget`

**Goal:** know, in measured tokens, how much of `num_ctx=16000` remains for retrieved
chunks once the system prompt, the question, and a reasoning+answer reservation are
accounted for — so chunk size and top-k get chosen against a real number, not a guess.

**Why:** `docs/PLAN.md`'s risk register (added at T-007's `grill-me`, Phase 0 checkpoint)
flags that nobody has estimated whether a real RAG prompt (system + retrieved chunks +
question) stays under `num_ctx=16000` — and KB-005 already proved an undersized `num_ctx`
silently drops the **front** of the prompt with no error. D-005's "Cost" section adds that
`qwen3:30b-a3b`'s reasoning mode consumes real tokens of its own that must be budgeted for,
not assumed away.

**Acceptance criteria**
- [ ] `docs/DESIGN.md` gets a new "Context budget" section giving explicit token counts for:
  system prompt, a representative question, and a reasoning+answer reservation
- [ ] The reasoning+answer reservation is based on a measured sample (`prompt_eval_count`
  and `eval_count` from a real `qwen3:30b-a3b` call with `think:true`, per D-005/KB-007),
  not an estimate
- [ ] The remaining budget for retrieved chunks is expressed both as a token count and as a
  resulting max top-k at an assumed chunk size (e.g. "at ~X tokens/chunk, budget allows
  top-k=Y")
- [ ] The section states what happens if the budget is exceeded (cites KB-005) and how
  retrieved chunks should be ordered in the prompt so the least recoverable content isn't
  first to be dropped, per the risk register's mitigation
- [ ] `docs/PLAN.md`'s risk register row on this topic is updated to point at this section
  as the resolving evidence

**Out of scope:** implementing chunking/retrieval code (T-012); the real evaluation
(Phase 3).

**Depends on:** T-006, T-007
**Notes:** Blocks T-012 — chunk size and top-k must not be finalized before this section
lands, per explicit instruction when Phase 1 was opened.

---

### T-009 — HF + YouTube collectors → normalized document shape

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-009-collectors`

**Goal:** the HF Daily Papers and YouTube collectors both produce documents in one shared
shape (source, url, title, feed date, text — plus arXiv `publishedAt` as extra metadata for
papers), so downstream chunking and storage never need to know which source a document came
from.

**Why:** `docs/PLAN.md` Phase 1's first checklist item. D-001 (transcript source) and D-002
(feed date semantics) are decided but not yet real code.

**Acceptance criteria**
- [ ] A shared document type (source, url, title, feed_date, text, optional
  arxiv_published_at) is defined in code
- [ ] The HF collector produces documents in this shape, using `paper.submittedOnDailyAt` as
  `feed_date` (D-002) and `paper.summary` as `text` (KB-002's field-name correction, not
  `abstract`)
- [ ] The YouTube collector produces documents in this shape, using the video's upload date
  as `feed_date`, captions as `text` when available, falling back to title+description per
  D-001
- [ ] Running each collector against real data produces at least one document with every
  required field populated — no field silently empty when the source data has it
- [ ] Every normalized document a collector produces is written to `data/raw/` (one file per
  document or per run — durable, not just an in-memory return value), so T-012 can build the
  database from these files without re-fetching from YouTube or HF

**Out of scope:** chunking, embedding, storage (T-012); the fallback unit test (T-010);
catch-up logic (T-013).

**Depends on:** T-001, T-002, T-003
**Notes:** `data/raw/` is the durable normalized-document store — T-012 reads from it rather
than calling collectors directly, and T-013's catch-up runs append to it. T-015's backfill
uses this same collector code, so its output lands here too.

---

### T-010 — Fallback unit test: simulated caption failure in the real collector

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-010-caption-fallback-test`

**Goal:** the YouTube collector's title+description fallback path (D-001) is verified by a
unit test that simulates a real caption-fetch failure, closing the gap T-002 explicitly left
open.

**Why:** T-002's acceptance criteria accepted the fallback as unverified — all 20 sampled
videos had captions, so the fallback branch was never exercised against a real failure.
T-002's notes and D-001's "Cost" section both name this as a live risk, to be handled inside
the real Phase 1 collector, not the throwaway T-002 script.

**Acceptance criteria**
- [ ] A unit test forces a caption-fetch failure (e.g. `TranscriptsDisabled` or
  `NoTranscriptFound`) against the real YouTube collector from T-009
- [ ] The test asserts the collector falls back to title+description and still produces a
  valid normalized document (T-009's shape) rather than raising or leaving `text` empty
- [ ] The test runs with no live network call (mocked), as part of the regular test suite
- [ ] A second unit test confirms the non-fallback path (captions available) still produces
  the expected document, so the fallback branch is covered without regressing the primary
  path

**Out of scope:** re-testing caption availability against real channels (done, KB-001);
Whisper (parked, `docs/GOAL.md`).

**Depends on:** T-009
**Notes:** Closes the gap explicitly deferred in T-002's acceptance criteria and named in
D-001's "Cost" section.

---

### T-012 — Chunk, embed and store documents with feed date metadata (idempotent)

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-012-chunk-embed-store`

**Goal:** normalized documents from `data/raw/` (T-009's collectors, populated by T-015's
backfill) are chunked, embedded with `bge-m3`, and stored in ChromaDB with feed date as
filterable metadata and arXiv `publishedAt` alongside for citations — and re-running ingest
never creates duplicates.

**Why:** `docs/PLAN.md` Phase 1's second checklist item. D-004 (ChromaDB), D-005 (`bge-m3`)
and D-002 (feed date semantics) need to land in real storage code, with chunk size and top-k
chosen against T-008's measured budget rather than guessed.

**Acceptance criteria**
- [ ] Chunking/embedding reads normalized documents from `data/raw/` rather than calling the
  HF/YouTube collectors directly, so the database can be rebuilt from disk without
  re-fetching from YouTube
- [ ] Chunk size is chosen using T-008's documented context budget, with the reasoning cited
- [ ] Each chunk is embedded via an explicit `bge-m3` call (CLAUDE.md hard rule — never
  ChromaDB's default embedder)
- [ ] Each chunk is stored with `feed_date` as filterable metadata (D-002/D-004); for
  papers, `arxiv_published_at` is stored alongside but never used for filtering
- [ ] Running ingest twice over the same `data/raw/` contents produces the same
  document/chunk count both times
- [ ] A query filtered to a feed-date range returns only chunks inside that range, in the
  real schema — not just T-005's throwaway 8-document test collection

**Out of scope:** catch-up logic for missed days (T-013); retrieval/answer generation
(Phase 2).

**Depends on:** T-008, T-009, T-015
**Notes:** T-008 blocks this — chunk size and top-k must not be finalized before T-008's
context-budget section lands, per explicit instruction when Phase 1 was opened. Run order:
T-009 → T-010, T-015 (backfill, own terminal) with T-008 done in parallel while the backfill
runs → T-012 → T-013 → T-014, per explicit instruction when these clarifications were added.

---

### T-015 — Initial 8-week backfill (HF + YouTube)

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-015-initial-backfill`

**Goal:** the last 8 weeks of history from both HF Daily Papers and YouTube are ingested
once, with YouTube fetched in paced, resumable batches so a long historical pull doesn't
trip a blocking response — establishing the dataset that catch-up (T-013) and the
evaluation question set (T-014) both build on.

**Why:** `docs/PLAN.md` Phase 1's catch-up checklist item and `docs/GOAL.md`'s "up to 7 days
offline" success criterion both assume a dataset already exists to catch up onto; nothing
has ingested that starting history yet. T-002/KB-001 already flags YouTube caption fetches
as a resource that can be blocked at volume, and 8 weeks across several channels is enough
requests that the same risk applies — the backfill has to be paced and interruption-safe,
not a single unthrottled loop.

**Acceptance criteria**
- [ ] The HF backfill fetches daily papers for each of the last 8 weeks (56 days) via
  T-009's collector, bounded by `feed_date` (`submittedOnDailyAt`, D-002)
- [ ] The YouTube backfill fetches each chosen channel's videos across the same 8-week
  window in batches, with a pause between batches
- [ ] Each video's outcome (captions fetched, fallback used, or failed) is logged
  individually, not just as an aggregate count
- [ ] Interrupting the run and restarting it resumes from where it left off — already
  completed days/videos are not re-fetched (checked against what's already in `data/raw/`,
  not a separate resume log)
- [ ] If failures cluster (e.g. several consecutive YouTube failures, or any response that
  looks like a block rather than an ordinary miss), the run stops and reports rather than
  continuing to retry
- [ ] The backfill's normalized documents are written to `data/raw/` via T-009's collectors
  (the same durable store T-012 reads from), and its end point (the `feed_date` it completed
  through, per source) is persisted as the starting watermark for T-013's catch-up logic
- [ ] `data/raw/` as it stands at the backfill's end date is the frozen dataset T-014 writes
  its evaluation questions against — no partial/interrupted run is treated as that frozen
  point, only a completed one

**Out of scope:** ongoing catch-up after this point (T-013 consumes this ticket's end
point); chunking/embedding the backfilled documents (T-012 processes whatever has been
collected, from either the backfill or later catch-up runs).

**Depends on:** T-009
**Notes:** Must reach a stable or fully-resumed state before T-013 starts, since T-013's
first watermark is this ticket's end point, not an assumption. Also gates T-014 — the
evaluation question set needs real backfilled data in `data/raw/` to verify expected sources
against.

---

### T-013 — Catch-up ingestion since the last successful run

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-013-catch-up-ingest`

**Goal:** after the PC has been off for up to 7 days, one ingest run catches up everything
missed from HF Daily Papers and YouTube, using feed date to determine what's new.

**Why:** `docs/PLAN.md` Phase 1's catch-up checklist item; `docs/GOAL.md`'s first success
criterion depends on this directly.

**Acceptance criteria**
- [ ] The last successful ingest run's feed-date watermark is persisted durably (not
  in-memory only); the very first watermark is T-015's backfill end point, not an assumed
  or empty starting date
- [ ] A simulated 7-day-offline scenario (watermark set 7 days in the past) results in one
  run fetching all documents with `feed_date` after the watermark, across both sources
- [ ] New documents from a catch-up run are appended to `data/raw/` alongside the backfill's
  existing files, keeping it the single durable normalized-document store T-012 reads from
- [ ] Running catch-up twice in a row with no new data in between adds zero new documents,
  building on T-012's idempotency
- [ ] The watermark only advances after a run completes successfully — a failed/partial run
  doesn't lose track of what's still missing

**Out of scope:** a scheduler or always-on process (explicit non-goal, `docs/GOAL.md`) —
catch-up is triggered manually/on demand.

**Depends on:** T-012, T-015
**Notes:** —

---

### T-014 — Write the 15–20 evaluation questions with expected sources

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-014-eval-questions`

**Goal:** I write 15–20 evaluation questions against the frozen backfilled dataset
(fixed cutoff feed date), and for each one the agent finds the expected source document(s)
and confirms they actually exist in the ingested data — all before retrieval is built, so
the system can't be tuned to them.

**Why:** `docs/PLAN.md` Phase 1's evaluation-questions checklist item; `docs/GOAL.md`'s
evaluation compares date-aware vs plain retrieval, which is only a fair test if the question
set predates the retrieval implementation. Verifying expected sources against T-015's real
backfilled data (rather than asserting them from memory) means the eval set isn't built on
a source that turns out to be missing or garbled.

**Acceptance criteria**
- [ ] The dataset used for question-writing is `data/raw/` as it stood at T-015's backfill
  end date (the frozen cutoff `feed_date`); that date is written down alongside the question
  set so a later re-ingestion doesn't silently change what "current" meant when the
  questions were written
- [ ] I write 15–20 questions spanning all three question types from
  `docs/GOAL.md`: "what's new", "did X come up", "has Q progressed in the last n weeks"
- [ ] For each question, the expected source document(s) (title + url + feed date) are
  looked up and confirmed present in `data/raw/` — not asserted from memory
- [ ] At least two questions are built around a proper noun likely to be garbled by
  YouTube's auto-generated captions, per T-002's notes and KB-001
- [ ] Questions span both sources, and at least one requires combining evidence from both
- [ ] The set is committed to the repo with the frozen cutoff date recorded, dated before
  any retrieval code exists, so the "written before retrieval" ordering is verifiable from
  git history

**Out of scope:** running the evaluation itself (Phase 3); building retrieval (Phase 2).

**Depends on:** T-001, T-015
**Notes:** I write the questions; the agent's job is finding and verifying expected
sources against the real data, not authoring the questions.

---

### T-011 — Separate Qwen3's reasoning from its answer before display

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-011-reasoning-answer-split`  ·  **Phase:** 2

**Goal:** any code that calls a Qwen3 chat model and shows or stores its output keeps the
reasoning (chain-of-thought) and the final answer as two distinct values, never one merged
string.

**Why:** KB-007/D-005 found `think:false` does not suppress reasoning — it merges it into
the response/content field instead of separating it into `thinking`. A clean answer-only
string requires `think:true`, reading `thinking` and the answer as separate fields (D-005's
"Cost" section). Nothing that displays or stores a Qwen3 response should accidentally show
raw chain-of-thought as if it were the answer.

**Acceptance criteria**
- [ ] A shared utility takes a raw Ollama chat/generate response called with `think:true`
  and returns `(reasoning, answer)` as two separate strings
- [ ] A unit test covers the response shape KB-007 confirmed (reasoning in `thinking`, not
  merged into content, when `think:true` is used)
- [ ] A unit test covers the failure mode KB-007 found: the utility either detects a merged
  `think:false` response, or the code path is guarded to never call with `think:false`
- [ ] Phase 2's answer-generation code goes through this utility rather than reading the raw
  response field directly
- [ ] `docs/DESIGN.md`'s "Interfaces and contracts" section documents this as a project-wide
  contract

**Out of scope:** anything else in the answer-generation pipeline (retrieval, prompt
assembly, citations) — this is only the reasoning/answer split.

**Depends on:** T-006, T-007
**Notes:** Moved from Phase 1 to Phase 2 — no Phase 1 code calls an LLM, so there was no
real caller to build this utility against yet. Phase 2's answer generation is its first
caller; see `docs/PLAN.md`'s Phase 2 checklist.

---

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

---

### T-002 — YouTube captions feasibility test

**Status:** done
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
- [x] The title + description fallback is confirmed available for at least one video that
  has no captions → **accepted as not fully met, deferred rather than blocking.** 20/20
  videos had captions, so there was no real failure to exercise the fallback against in this
  throwaway script; only that `yt-dlp` returns non-empty `title`/`description` for every
  video was confirmed (KB-001). I accepted D-001 on the strength of the 100%-success
  result. **Deferred to Phase 1:** the fallback path must be verified with a unit test that
  simulates a failed caption fetch inside the real ingest/collector code, not re-tested here.
  That requirement belongs on the Phase 1 collector ticket when it's written.
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the transcript-source choice,
  with the evidence cited → D-001

**Out of scope:** the real ingest pipeline, chunking, storage — this only establishes
whether the source works.

**Depends on:** T-001
**Notes:** Added `yt-dlp` and `youtube-transcript-api` (see `requirements.txt`) — approved
by me up front. KB-001 additionally records that all 20 captions were
auto-generated (not manual), which risks misspelled proper nouns (model/company/people
names) — the Phase 1 evaluation question set must include at least a couple of questions
built around a proper noun likely to be garbled by auto-captions, to actually measure this
rather than assume it's fine.

---

### T-003 — HF Daily Papers API feasibility test

**Status:** done
**Size:** S  ·  **Branch:** `t/T-003-hf-daily-papers`

**Goal:** know that the HF Daily Papers API gives the fields the project needs, for both
recent and past dates.

**Why:** `docs/PLAN.md` Phase 0 requires confirming which fields exist and that past dates
work, before Phase 1 builds a collector on top of the API.

**Acceptance criteria**
- [x] A script calls `/api/daily_papers?date=` for each of the last 14 days →
  `scripts/t003_hf_daily_papers.py`, 2026-09-02 through 2026-09-15, all HTTP 200
- [x] For each response, presence of title, abstract, publication date and arXiv id is
  confirmed (or the missing ones are named) → all present, but not where assumed: abstract
  is `summary` not `abstract`, arXiv id is `paper.id` not top-level — see
  [KB-002](kb/KB-002-hf-daily-papers-shape.md)
- [x] At least one date more than 10 days in the past returns data, confirming historical
  dates work → 2026-09-02/03/04 all returned entries
- [x] One raw JSON response is saved into the repo → trimmed to 3 entries at
  `docs/kb/samples/daily_papers_2026-09-15_sample.json` (the full day is ~250KB of mostly
  author/avatar metadata, not worth committing in full)
- [x] Findings written to `docs/kb/` via `kb-entry` → KB-002

**Out of scope:** normalizing the response into the Phase 1 document shape — this only
confirms the raw API's behaviour.

**Depends on:** T-001
**Notes:** No new dependency needed — `requests` was already a transitive dependency from
T-002. The 4 weekend dates in the 14-day window returned an empty list (HF Daily Papers
doesn't publish on Sat/Sun) — that's expected, not a bug. The `publishedAt` vs
`paper.submittedOnDailyAt` divergence this ticket surfaced was resolved by me as
**D-002**: "publication date" throughout the project means feed date
(`submittedOnDailyAt` for papers, YouTube upload date for videos); arXiv `publishedAt` is
stored as extra metadata and shown in citations only. `docs/GOAL.md` and `docs/PLAN.md`
Phase 1 updated to match.

---

### T-004 — Local model test on the RTX 4090 (Ollama)

**Status:** done
**Size:** S  ·  **Branch:** `t/T-004-local-model`

**Goal:** know that one large (~30B class, quantized) and one small (~8B) model both run on
this PC via Ollama and can answer a question from pasted context, with speed and VRAM
recorded.

**Why:** `docs/PLAN.md` Phase 0 requires the model pair chosen and recorded before later
phases build retrieval and evaluation around them.

**Acceptance criteria**
- [x] One ~30B-class quantized model and one ~8B model are pulled and run via Ollama on the
  RTX 4090 → `llama3.1:8b` and `qwen2.5:32b`, Ollama 0.34.0
- [x] Each model is given the same test question with pasted context and produces an
  answer → `scripts/t004_local_model.py`, both answered correctly
- [x] Response time and peak VRAM usage are recorded for each model → cold and warm timings
  recorded; VRAM readings come with an honest methodology caveat (see KB-003 — `nvidia-smi`
  measures total GPU memory, not per-process)
- [x] Findings are written to `docs/kb/` via `kb-entry` →
  [KB-003](kb/KB-003-ollama-vram-and-timing.md)
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen model pair, with the
  evidence cited → D-003

**Out of scope:** the retrieval/answer-generation pipeline (Phase 2) — this only confirms
the models run and answer from pasted context.

**Depends on:** T-001
**Notes:** Ollama was already installed on this machine (0.34.0); confirmed via
`nvidia-smi` that this session is running on the real RTX 4090 from `docs/PLAN.md`'s
hardware section, not a generic sandbox — so the GPU-dependent result is real, not
simulated. Two findings worth carrying into Phase 2 planning (both in KB-003): a cold-start
run made the large model look faster than the small one (it was disk-load overhead, not
inference — always compare warm timings), and `qwen2.5:32b` doesn't fit entirely in 24GB
VRAM at its default context (20% spills to CPU), and the two models evict each other rather
than co-residing.

---

### T-005 — Vector store date-range filtering test

**Status:** done
**Size:** M  ·  **Branch:** `t/T-005-vector-store-date-filter`

**Goal:** know that a candidate vector store can filter by feed-date metadata
combined with similarity search, before committing to it for Phase 1.

**Why:** `docs/GOAL.md`'s claim under test is that date-aware retrieval beats plain
similarity search; that only works if the store can filter by date range at all.
`docs/PLAN.md` Phase 0 requires this confirmed before committing to a store.

**Acceptance criteria**
- [x] A small test collection of documents with varying feed dates (as metadata, per D-002)
  is inserted into a candidate vector store → 8 docs in ChromaDB, `feed_date` spanning
  2026-06-01 to 2026-09-14
- [x] A query demonstrates similarity search restricted to a date range, returning only
  documents inside that range → all 4 filtered results confirmed inside
  [2026-09-01, 2026-09-14]
- [x] A second query without the date filter is run against the same data to confirm the
  filtered and unfiltered results differ as expected → confirmed, filtered set is a strict
  subset dropping the June/August documents
- [x] Findings are written to `docs/kb/` via `kb-entry` →
  [KB-004](kb/KB-004-chromadb-date-filtering.md)
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen vector store, with
  the evidence cited → D-004

**Out of scope:** the production schema for Phase 1 storage — this is a throwaway test
collection.

**Depends on:** T-001
**Notes:** Candidate (ChromaDB) chosen with me before installing, per `CLAUDE.md`
"In-loop" — asked, got ChromaDB over LanceDB/sqlite-vec, then installed. KB-004 flags a
real cost worth remembering: Chroma's default embedding model isn't bundled, it's an
~80MB silent download on first use to a user-level cache outside the project — needs a
README mention for the "fresh clone reaches a first answer" success criterion.

---

### T-006 — Needle test and same-family model pair + embedding model re-selection

**Status:** done
**Size:** M  ·  **Branch:** `t/T-006-model-pair-revision`

**Goal:** know Ollama's real context-window behavior (num_ctx, silent truncation), and
replace T-004's model pair with a same-family chat pair plus a deliberately chosen
embedding model, all verified to share the RTX 4090's 24GB VRAM without evicting each
other.

**Why:** T-004 paired `llama3.1:8b` with `qwen2.5:32b` — different families, which
confounds size with family in the planned large-vs-small evaluation (`docs/GOAL.md`).
KB-003 also showed `qwen2.5:32b` spills 20% onto CPU at its default context. KB-004 flagged
that ChromaDB's default embedding model was accepted silently, not chosen — and it shares
the same GPU as the chat models, so it has to be verified alongside them, not assumed to
just fit. Bundled as one ticket rather than several because the needle test's num_ctx
finding is a direct input to the chat-pair check (16k context), and the embedding model's
VRAM footprint is a direct input to whether the chat pair actually leaves room for it — not
independent concerns.

**Acceptance criteria**
- [x] A needle-in-haystack test (~12k tokens of filler with one unique fact planted at the
  very start, then a question requiring that fact back) is run against at least one
  currently-pulled model. `docs/kb/` gets a `kb-entry` documenting what `num_ctx` Ollama
  actually used for that request, how `num_ctx` is set, and whether content beyond
  `num_ctx` is silently truncated or surfaced as an error/warning → `llama3.1:8b`,
  [KB-005](kb/KB-005-ollama-num-ctx-silent-truncation.md): default is 32768, undersized
  `num_ctx` silently drops the front of the prompt, no error
- [x] ChromaDB's default embedding model is checked for its real max sequence length and
  whether text beyond that length is silently truncated → 256 tokens,
  [KB-006](kb/KB-006-chroma-default-embedder-256-token-limit.md): silently truncated,
  confirmed via source reading and two empirical tests (identical embeddings for a
  differing tail; `collection.add()` accepts an overlong doc with no error)
- [x] Before downloading anything: candidate same-family chat pairs AND a candidate
  multilingual embedding model presented to me for approval → asked via
  `AskUserQuestion`; I chose `qwen3:30b-a3b` + `qwen3:8b` over Gemma3 27b+4b, with
  `bge-m3` as the only real multilingual embedding candidate found in Ollama's library
- [x] Once approved: chat pair pulled, large model at explicit `num_ctx=16000` shows 100%
  GPU via `ollama ps`, confirmed by `nvidia-smi`; embedding model pulled and tested with a
  Swedish question against English text → all confirmed,
  [KB-007](kb/KB-007-qwen3-bge-m3-stack.md): correct top match, cosine 0.6810 vs next-best
  0.3821
- [x] With the large chat model and the embedding model **both** loaded, `ollama ps`
  confirms both resident simultaneously without evicting each other, real VRAM headroom
  recorded → both 100% GPU, `nvidia-smi` 22100-22118 MiB / 24564 MiB, ~2.4GB headroom,
  stable before and after a real generation call
- [x] If no same-family chat pair meets the GPU bar, the fallback is tried → **not
  needed**, `qwen3` cleared the bar on the first attempt; per my explicit
  condition, this would have required stopping to report before falling back, not an
  automatic switch
- [x] `docs/DECISIONS.md` gets a new decision recording the full stack, `D-003` marked
  superseded → **D-005** (as anticipated — D-004 was ChromaDB from T-005), `D-003` marked
  `Superseded by D-005`

**Out of scope:** re-running the actual large-vs-small evaluation (Phase 2) — this only
re-establishes the stack and its context-window/VRAM behaviour.

**Depends on:** T-004, T-005
**Notes:** I added three conditions when approving the chat pair: (1) stop and report
rather than auto-falling-back if the VRAM bar wasn't met with the embedding model also
loaded — not triggered, bar was met; (2) test `think:false` and note the timing
difference — done, KB-007 also found `think:false` doesn't suppress reasoning, it just
merges it into `response`; (3) frame D-005 by VRAM footprint (~6GB vs ~20GB), not
large/small, since `qwen3:30b-a3b` (MoE) has fewer active parameters per token than the
dense `qwen3:8b` — done. `docs/PLAN.md`'s "Local model" Phase 0 checkbox re-ticked now that
this is done.

---

### T-007 — Verify KB-007's think claim, write CLAUDE.md hard rules, grill-me Phase 0

**Status:** done
**Size:** M  ·  **Branch:** `t/T-007-phase0-checkpoint`

**Goal:** close the Phase 0 checkpoint's three loose ends — confirm KB-007's `think:false`
finding wasn't an artifact of the wrong endpoint, turn Phase 0's findings into enforceable
project rules, and get an adversarial pass on Phase 0 as a whole before Phase 1 starts.

**Why:** KB-007's `think:false` test used `/api/generate`; Ollama's `think` parameter may
behave differently on `/api/chat`, so the finding needs re-checking via the correct
endpoint before it's trusted. `CLAUDE.md`'s "Hard rules" and "Stack" sections are still
placeholders even though Phase 0 now has concrete findings (KB-005, KB-006) and decisions
(D-001–D-005) to derive them from. `docs/PLAN.md` requires a `grill-me` pass at every
checkpoint before declaring a phase complete, and that hasn't been run on Phase 0 as a
whole yet — only on individual tickets as they closed.

**Acceptance criteria**
- [x] The exact JSON request body sent in KB-007's `think:false` test is quoted → confirmed
  `think` was already top-level, not nested under `options`:
  `{"model": "qwen3:30b-a3b", "prompt": "...", "stream": false, "think": false, "options": {"num_ctx": 16000}}`
- [x] The same comparison re-run against `/api/chat` → `scripts/t007_verify_think_chat.py`,
  identical shape of result: `think:false` leaves `thinking` empty but the reasoning
  narrative appears inside `message.content` anyway
- [x] Finding recorded → KB-007 held up on the second endpoint too (not superseded);
  updated in place with the `/api/chat` confirmation, since the claim itself wasn't wrong,
  just under-evidenced on one endpoint. Separately, while checking this, found and
  **corrected** a real error in KB-007's own "Confidence and limits": it speculated VRAM
  headroom might shrink under a longer conversation because "the KV cache grows with
  actual usage" — verified directly that this is false (`nvidia-smi`: 21410 MiB at a
  trivial prompt vs 21431 MiB at an 8002-token prompt, same `num_ctx=16000` — no meaningful
  growth). Ollama pre-allocates the KV cache for the full `num_ctx` at load
- [x] `CLAUDE.md`'s "Hard rules" filled in with the three rules (num_ctx always explicit,
  every call compares `prompt_eval_count` to `num_ctx`, embeddings always `bge-m3` never
  Chroma's default)
- [x] `CLAUDE.md`'s "Stack" section updated with D-001, D-002, D-004, D-005
- [x] `grill-me` (design-decision mode) run on Phase 0 as a whole. Findings:
  - **Serious, fixed:** KB-007's VRAM-growth speculation was wrong — corrected above with
    real evidence, not just reworded
  - **Serious, deferred (not silently dropped):** the real risk hiding behind the VRAM
    question is token budget, not VRAM — nobody has estimated whether a real RAG prompt
    (system + retrieved chunks + history + question) stays under `num_ctx=16000`, and
    KB-005 already proved silent front-truncation is real. Added to `docs/PLAN.md`'s risk
    register with a concrete mitigation (estimate token counts before finalizing Phase 1
    chunk size / retrieval top-k)
  - **Minor, reported not fixed:** D-002's "feed date" label covers two structurally
    different real-world events (HF's curatorial feed-inclusion date vs. YouTube's actual
    upload date) — not wrong, but worth remembering when designing citations, so the label
    doesn't imply more uniformity than the underlying sources actually have

**Out of scope:** any Phase 1 work.

**Depends on:** T-002, T-003, T-004, T-005, T-006
**Notes:** Bundled three different kinds of work into one ticket per my explicit
instruction. The most valuable output wasn't the planned verification (KB-007's claim held
up) — it was the review process surfacing and fixing a real error in KB-007's own
speculative caveat, and identifying a Serious token-budget risk for Phase 1 that nothing
upstream had flagged. Phase 0 is now genuinely complete; Phase 1 has not been started.

---

### T-016 — Open Phase 1: PLAN/GOAL updates and the Phase 1 ticket set

**Status:** done
**Size:** S  ·  **Branch:** — (docs-only, see note)

**Goal:** Phase 1 is formally open and its work exists as checkable tickets instead of only
as `docs/PLAN.md`'s umbrella checkboxes, so work can start from a backlog rather than from a
chat instruction.

**Why:** `docs/PLAN.md` requires turning a phase's checkboxes into tickets via `ticket-write`
when the phase starts; T-007's handoff named this as the next session's first action.
`docs/GOAL.md` also needed conversation history recorded as an explicit non-goal/parked item
before Phase 1 scope could be considered settled, since it bears on the context-budget work
in T-008.

**Acceptance criteria**
- [x] `docs/PLAN.md`'s "Current phase" is set to Phase 1
- [x] `docs/GOAL.md` gets conversation history added under Non-goals and Parked
- [x] Tickets T-008 through T-015 written for Phase 1's checklist items, each with
  observable acceptance criteria and correct `Depends on` chains
- [x] T-011 (separate Qwen3's reasoning from its answer) written, then on my review moved
  to Phase 2 — no Phase 1 code calls an LLM, so Phase 1 had no real caller for it;
  `docs/PLAN.md`'s Phase 2 checklist updated to reference it
- [x] T-015 (initial 8-week backfill) added ahead of T-013 on my review, since catch-up
  needs a real starting watermark rather than an assumed one; T-013 and T-014 updated to
  depend on it
- [x] T-014 rewritten on my review to reflect I writing the questions and the
  agent verifying expected sources against the frozen backfilled dataset, rather than the
  agent drafting the questions
- [x] `data/raw/` established as the durable normalized-document contract on my review:
  T-009 and T-015 write there, T-012 reads from there (never re-fetching from YouTube to
  rebuild the database), T-013 appends there, and T-014's frozen dataset is defined as
  `data/raw/` as it stood at T-015's backfill end date
- [x] Run order recorded on my review — T-009 → T-010, T-015 (backfill, own terminal)
  with T-008 in parallel → T-012 → T-013 → T-014 — in both `docs/PLAN.md`'s Phase 1 section
  and T-012's notes
- [x] None of T-008–T-015 executed — this ticket covers only the planning artifacts

**Out of scope:** doing any of T-008 through T-015's actual work.

**Depends on:** T-007
**Notes:** Three-pass ticket-writing: the first pass (T-008–T-014) was revised after my
review into a second set (T-008–T-015, plus T-011 moved to Phase 2), then a third pass added
the `data/raw/` storage contract and run order — all before any of T-008–T-015 was committed
or started, per explicit instruction to hold all commits until review.
