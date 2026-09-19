# PLAN

Phases are gated. **Each phase ends at a checkpoint where the agent stops and I
reviews.** Do not start phase N+1 without explicit go-ahead.

Current phase: **Phase 2** (started 2026-09-19, by my explicit go-ahead). Phase 2's
checklist below is now backed by tickets T-011, T-021–T-025 in `docs/TICKETS.md` — all
`todo`, none executed yet; writing tickets is not starting the work they describe.

Total time: 3 weeks. The checkboxes below are umbrellas, not work items. When a phase
starts, turn its checkboxes into tickets in `docs/TICKETS.md` using the `ticket-write`
skill. A checkbox is ticked when all of its tickets are done — never before. Run `grill-me`
at every checkpoint before declaring a phase complete.

Hardware: i9-14900K, RTX 4090 (24 GB VRAM), 64 GB RAM, Windows 11. The PC is off at night.

---

## Phase 0 — Ground truth (days 1–2)

Test the assumptions everything else rests on, cheaply, before building anything on top.

- [x] **YouTube captions:** from this PC, fetch captions for the latest videos of each chosen
  channel (3–5 channels). Record success rate and error types in `docs/kb/` — T-002, KB-001
- [x] **HF Daily Papers:** fetch the last 14 days via `/api/daily_papers?date=`. Confirm
  which fields exist (title, abstract, publication date, arXiv id) and that past dates work
  — T-003, KB-002
- [x] **Local model:** run Ollama on the RTX 4090 with a same-family chat pair
  (`qwen3:8b` + `qwen3:30b-a3b`, VRAM-differentiated per D-005) plus a deliberately chosen
  embedding model (`bge-m3`), both verified 100% GPU-resident together at `num_ctx=16000`.
  — T-004 (chat models run), T-006 (same-family pair, embedding model, VRAM headroom),
  KB-003, KB-005, KB-006, KB-007, D-005 (supersedes D-003)
- [x] **Vector store:** confirm that date-range filtering works in the chosen store before
  committing to it — T-005, KB-004

**Exit criteria:** each item answered with evidence. Transcript source decided (captions,
or title + description). Model pair and vector store chosen and recorded in
`docs/DECISIONS.md`.
**Checkpoint:** I review findings. All four items done, including T-006's model-stack
revision. Phase 1 has not started — waits for this review.

---

## Phase 1 — Ingest (rest of week 1)

- [x] Collectors for HF and YouTube produce one normalized document shape: source, url,
  title, feed date, text — plus arXiv `publishedAt` as extra metadata for papers (D-002) —
  T-009, KB-008
- [x] Chunk, embed and store with feed date as metadata; arXiv `publishedAt` stored
  alongside for citations, never used for filtering (D-002). Re-running is idempotent —
  T-012, 1184/1184/1184 (docs/chunks/collection.count()) stable across two real runs
- [x] Initial backfill: 8 weeks of HF Daily Papers history, fetched and resumable — T-015,
  1184 papers, 2026-07-23..2026-09-16, watermark `2026-09-15`. YouTube's backfill is split
  into its own item below, blocked on a decision
- [x] YouTube backfill: 4 weeks of history (cut from 8, T-017), fetched paced and resumable,
  captions first then local Whisper on a caption block rather than stopping the run — T-017
  (theAIsearch/mreflow, real captions) → D-008/D-009/D-010 (transcript-path decisions) → T-018
  (Whisper feasibility) → T-019 (NateBJones/ColeMedin via Whisper, 24/24, watermark
  2026-09-17). Window intentionally 4 weeks, not 8 — extending it is unstarted work, not a
  blocker
- [x] Catch-up: ingest everything since the last successful run, per source, using each
  source's own backfill end point as its first starting watermark — T-013, both halves done
  and verified for real. HF: simulated a 2-day gap, closed it end to end, no duplicates.
  YouTube (completed after T-019 gave it a real transcript path): simulated a 1-day gap
  mixing both transcript paths, closed it end to end into Chroma, no duplicates - and caught
  a real chunking bug (`fallback_reason` dropped) along the way, fixed and verified
- [x] Write the 15–20 evaluation questions with expected sources, against a frozen dataset
  (fixed cutoff date) — **before** retrieval is built, so the system isn't tuned to them.
  HF-side drafting can start once T-015 lands; the freeze itself waits on T-017 — T-014,
  `docs/eval-questions.md`, 15 questions, frozen cutoff HF 2026-09-16/YouTube 2026-09-17,
  every source verified against real `data/raw/`, committed before any retrieval code exists

**Run order:** T-009 → T-010, then T-015 (HF backfill, run in its own terminal) with T-008
done in parallel while it runs → T-012 → T-013 (HF side) → T-014 (HF-side drafting). T-017
(YouTube backfill) and the rest of T-013/T-014 resume once the transcript-path decision
lands.

**Exit criteria:** running ingest twice gives the same document count. Simulating 7 days
offline, one run catches up.
**Checkpoint:** I review.

---

## Phase 2 — Ask (week 2)

- [ ] Retrieval with an optional date range, taken from the question or set in the UI —
  T-021 (date range), T-022 (similarity search + T-008's token-budget packing)
- [ ] Answer generation with citations: link, title, date — every call site that reads a
  Qwen3 model's output must separate its reasoning from the final answer before displaying
  or storing it (moved from Phase 1: no Phase 1 code calls an LLM, so there was no caller
  to build the utility against yet) — T-011 (reasoning/answer split), T-023 (the
  `/api/chat` call itself, per KB-011/T-008), T-024 (citations)
- [ ] Chat UI, including the empty state "no data yet — run ingest" — T-025

**Exit criteria:** the three question types in `docs/GOAL.md` work end to end with sources.
**Checkpoint:** I review.

---

## Phase 3 — Prove and publish (week 3)

- [ ] Evaluation script: date-aware vs plain retrieval, large vs small model. Results table
  committed
- [ ] README, Apache-2 `LICENSE`, and a fresh-clone test following the README only
- [ ] Report and presentation — run `defense-prep`

**Exit criteria:** every item in the Definition of done in `docs/GOAL.md` is met.
**Checkpoint:** I review. Project complete.

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| YouTube blocks caption requests | Medium | Tested in Phase 0. Fallback: title + description. Whisper is parked |
| Extracting a date range from free text is unreliable | Medium | A date-range control in the UI as a fallback |
| HF Daily Papers API changes shape | Low | Collector is isolated in one module; raw JSON is saved |
| Local model invents content beyond the sources | Medium | Answers must cite sources; evaluation checks it |
| Scope creep | High | § Parked in `docs/GOAL.md`. One ticket at a time |
| Phase 0 or 1 overruns | Medium | Cut from Phase 2 UI polish, never from evaluation |
| bge-m3 embeds broad conversational questions closer to spoken/YouTube-transcript text than to dense scientific HF abstracts, regardless of language - real, measured (T-022's re-run of T-014's 15 real questions): the same 5 HF papers ranked far outside a 60-candidate pool (600-1600 of 1971) for F14/F15's broad questions in *both* Swedish and English (rank barely moved, sometimes got worse in English), even though the abstracts literally contain the query's own topic words ("agent", "open-source") - ruling out translation as the cause | Confirmed, not hypothetical | **Not fixed** - this is a result to measure in Phase 3's date-aware-vs-plain evaluation, not a retrieval bug. If Phase 3's results look weak for HF-heavy questions, this register entry is why, before assuming the retrieval pipeline itself is broken |
| Real RAG prompt (system + retrieved chunks + question) exceeds `num_ctx=16000`, silently dropping the **front** of the prompt with no error (KB-005) — if retrieved chunks are placed there, the exact evidence citations depend on vanishes with no signal | Low — measured, not estimated (T-008): system prompt 171 + question 40 + reasoning/answer 2000 (`num_predict` cap) leaves 13789 tokens, max top-k 34 at a 400-token chunk cap; see `docs/DESIGN.md` § Context budget | Resolved for chunk size/top-k via T-008's measured budget. Residual risk: the 400-token chunk cap is sized from HF abstracts only — no real YouTube transcript text exists yet (KB-008) to confirm chunking holds once T-015 backfills real transcripts. Prompt ordering (chunks least-relevant-first, system+question last) and a real per-call `prompt_eval_count` vs `num_ctx` check remain the defense-in-depth backstop |
| `vg09/store.py` has no automated tests, but implements two of `CLAUDE.md`'s three hard rules (explicit `bge-m3`, explicit `num_ctx`) — a future refactor could silently drop either with nothing to catch it before a real run. Found by Phase 1's `grill-me` review (2026-09-19) | Low today (code hasn't changed since T-012 shipped it); rises with any future edit to `embed_batch()`/`chunk_metadata()` | Deferred to Phase 3, T-020's triage. Add a test asserting `embed_batch()`'s request body always includes `model="bge-m3"` and an explicit `num_ctx` before Phase 3 closes |
| `vg09/youtube_backfill.py` (pacing, resumability, pending-retry, watermark-write-on-completion) has no automated tests — the riskiest orchestration code in the ingest pipeline, verified only by real production runs. Self-flagged in T-019's own notes, never followed up; found again by Phase 1's `grill-me` review (2026-09-19) | Low today (stable since T-019); rises if `run()` is ever changed without a real end-to-end run to catch a regression | Deferred to Phase 3, T-020's triage. Add a mocked resumability/pacing/watermark test before the next real change to `youtube_backfill.py` |
| `vg09/youtube.py::normalize()`'s Whisper branch catches bare `except Exception` — a real code defect in `fetch_whisper_transcript()` would be misreported as an ordinary Whisper failure and silently produce a weaker `title_description` document, with no alert. Self-flagged in D-010's own Cost section as an accepted, watched risk; found again by Phase 1's `grill-me` review (2026-09-19) | Low today (no known defect); D-010's own "would change our mind" clause already names the failure mode to watch for | Deferred to Phase 3, T-020's triage. Add a threshold alert on `fetched_fallback` counts (e.g. N consecutive full-fallback videos) per D-010's own suggestion |
| F14's "God's Eye View"/Palantir YouTube citation (`docs/eval-questions.md`) is a softer fit for "stora AI-verktyg" than its Suno-alternative sibling citation — Palantir is a data/intel platform, not squarely an AI tool. Found by Phase 1's `grill-me` review (2026-09-19) | Low — the facit already accepts either citation, so this doesn't block grading | Deferred to Phase 3. If F14 is ever re-graded strictly, prefer the Suno-alternative (`9RtywbN--QE`) citation, or add a stronger second HF+YouTube pair |
