# PLAN

Phases are gated. **Each phase ends at a checkpoint where the agent stops and I
reviews.** Do not start phase N+1 without explicit go-ahead.

Current phase: **Phase 0**

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
- [ ] **Local model:** run Ollama on the RTX 4090 with one large (~30B class, quantized) and
  one small (~8B) model. Each answers a question from pasted context. Note speed and VRAM
  — T-004 done, KB-003, but the pair is not final: superseded pending T-006 (same-family
  chat pair + embedding model, since they share the GPU). Not ticked until T-006 is done.
- [x] **Vector store:** confirm that date-range filtering works in the chosen store before
  committing to it — T-005, KB-004

**Exit criteria:** each item answered with evidence. Transcript source decided (captions,
or title + description). Model pair and vector store chosen and recorded in
`docs/DECISIONS.md`.
**Checkpoint:** I review findings. **T-006 (needle test + same-family model pair
re-selection) is written but deliberately not started — waits for this review.**

---

## Phase 1 — Ingest (rest of week 1)

- [ ] Collectors for HF and YouTube produce one normalized document shape: source, url,
  title, feed date, text — plus arXiv `publishedAt` as extra metadata for papers (D-002)
- [ ] Chunk, embed and store with feed date as metadata; arXiv `publishedAt` stored
  alongside for citations, never used for filtering (D-002). Re-running is idempotent
- [ ] Catch-up: ingest everything since the last successful run
- [ ] Write the 15–20 evaluation questions with expected sources — **before** retrieval is
  built, so the system isn't tuned to them

**Exit criteria:** running ingest twice gives the same document count. Simulating 7 days
offline, one run catches up.
**Checkpoint:** I review.

---

## Phase 2 — Ask (week 2)

- [ ] Retrieval with an optional date range, taken from the question or set in the UI
- [ ] Answer generation with citations: link, title, date
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
