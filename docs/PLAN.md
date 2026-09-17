# PLAN

Phases are gated. **Each phase ends at a checkpoint where the agent stops and I
reviews.** Do not start phase N+1 without explicit go-ahead.

Current phase: **Phase 1**

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
- [ ] Catch-up: ingest everything since the last successful run, per source, using each
  source's own backfill end point as its first starting watermark — T-013, HF half done and
  verified for real (simulated a 2-day gap, closed it via the real pipeline end to end, no
  duplicates). YouTube now has a real watermark (T-019) but `catch_up_youtube()` itself is
  still unexercised against it — real YouTube catch-up verification remains open
- [ ] Write the 15–20 evaluation questions with expected sources, against a frozen dataset
  (fixed cutoff date) — **before** retrieval is built, so the system isn't tuned to them.
  HF-side drafting can start once T-015 lands; the freeze itself waits on T-017

**Run order:** T-009 → T-010, then T-015 (HF backfill, run in its own terminal) with T-008
done in parallel while it runs → T-012 → T-013 (HF side) → T-014 (HF-side drafting). T-017
(YouTube backfill) and the rest of T-013/T-014 resume once the transcript-path decision
lands.

**Exit criteria:** running ingest twice gives the same document count. Simulating 7 days
offline, one run catches up.
**Checkpoint:** I review.

---

## Phase 2 — Ask (week 2)

- [ ] Retrieval with an optional date range, taken from the question or set in the UI
- [ ] Answer generation with citations: link, title, date — every call site that reads a
  Qwen3 model's output must separate its reasoning from the final answer before displaying
  or storing it (moved from Phase 1: no Phase 1 code calls an LLM, so there was no caller
  to build the utility against yet) — T-011
- [ ] Chat UI, including the empty state "no data yet — run ingest"

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
| Real RAG prompt (system + retrieved chunks + question) exceeds `num_ctx=16000`, silently dropping the **front** of the prompt with no error (KB-005) — if retrieved chunks are placed there, the exact evidence citations depend on vanishes with no signal | Low — measured, not estimated (T-008): system prompt 171 + question 40 + reasoning/answer 2000 (`num_predict` cap) leaves 13789 tokens, max top-k 34 at a 400-token chunk cap; see `docs/DESIGN.md` § Context budget | Resolved for chunk size/top-k via T-008's measured budget. Residual risk: the 400-token chunk cap is sized from HF abstracts only — no real YouTube transcript text exists yet (KB-008) to confirm chunking holds once T-015 backfills real transcripts. Prompt ordering (chunks least-relevant-first, system+question last) and a real per-call `prompt_eval_count` vs `num_ctx` check remain the defense-in-depth backstop |
