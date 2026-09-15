# TICKETS

The backlog. `docs/PLAN.md` holds phases and exit criteria; this file holds the work.

IDs are `T-001`, `T-002`, … assigned in order, never reused, never renumbered. Use the
`ticket-write` skill to add one and the `ticket-done` skill to close one.

**Statuses:** `todo` · `in-progress` · `blocked` · `review` · `done`

**Git linkage:** branch `t/T-0NN-slug` · commit `T-0NN: imperative summary` ·
PR title `T-0NN — Title`. One ticket ID per commit.

---

## Open

### T-007 — Verify KB-007's think claim, write CLAUDE.md hard rules, grill-me Phase 0

**Status:** todo
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
- [ ] The exact JSON request body sent in KB-007's `think:false` test (from
  `scripts/t006_model_stack.py`) is quoted, confirming `think` was a top-level field, not
  nested under `options`
- [ ] The same think:true/false comparison is re-run against `/api/chat` (not
  `/api/generate`) with `think` at the top level, to check whether the endpoint explains
  KB-007's result
- [ ] If reasoning is actually suppressed when sent via `/api/chat`, a new KB entry is
  written recording that, and KB-007 is marked `superseded by KB-0NN` (not edited in
  place); if KB-007's finding holds even via `/api/chat`, that is recorded too, not
  silently dropped
- [ ] `CLAUDE.md`'s "Hard rules" section states, as enforceable rules: `num_ctx` is always
  set explicitly on every Ollama call, never left to the default (KB-005); every LLM call
  compares `prompt_eval_count` against the `num_ctx` it sent and warns when truncation risk
  is present; embeddings are always created with `bge-m3`, passed explicitly — ChromaDB's
  default embedder is never used (KB-006)
- [ ] `CLAUDE.md`'s "Stack" section names the choices made in D-001, D-002, D-004 and D-005
  (transcript source, feed date semantics, vector store, model stack)
- [ ] `grill-me` (design-decision mode) is run on Phase 0 as a whole — the four tickets and
  five decisions together, not any one in isolation — and its findings are recorded;
  anything Fatal or Serious is fixed or explicitly deferred as a new ticket, not silently
  dropped

**Out of scope:** any Phase 1 work.

**Depends on:** T-002, T-003, T-004, T-005, T-006
**Notes:** Bundles three different kinds of work (verification, doc update, adversarial
review) into one ticket per my explicit instruction — normally this would be split.
**Do not start before I say so** — written during the Phase 0 checkpoint review,
same as T-006 was.

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
