# PLAN

Phases are gated. **Each phase ends at a checkpoint where the agent stops and I
reviews.** Do not start phase N+1 without explicit go-ahead.

Phase 2 complete (started 2026-09-19, closed 2026-09-20, by my explicit go-ahead both
times). All of Phase 2's tickets (T-011, T-021–T-025, T-027, T-028) are `done`, its
checklist below is ticked, `grill-me` ran against the whole phase (2026-09-20) and every
finding it raised was triaged and fixed (**T-029**: D-011→D-012's eval-anchor correction,
`raise_for_status()` on the two Ollama call sites that lacked it, `app.py`'s override-
contract reuse, citation-title escaping — one deferred to the risk register, `latest_
feed_date()`'s double scan per interaction). **T-030** (D-013: answers always in English,
regardless of question language) landed the same session, after the phase's own tickets
were otherwise done.

Current phase: **Phase 3** (started 2026-09-20, by my explicit go-ahead). Its ticket set
was written as **T-031**–**T-036**, per this file's own "turn checkboxes into tickets when
a phase starts" rule below; **T-039**–**T-041** were added mid-phase (real findings from
running the earlier tickets, not planned upfront). Status as of 2026-09-23: **T-031**
through **T-041** are all `done`, both real comparisons run and graded by me -
**T-032** (date-aware vs plain: A bättre 8, B bättre 0, Likvärdiga 5, Båda fel 2) and
**T-033** (`qwen3:30b-a3b` vs `qwen3:8b`: A bättre 4, B bättre 0, Likvärdiga 9, Båda fel 2 -
notable: the smaller model was slower on average despite fewer active parameters, dense vs
MoE per D-005; where it lost, it consistently enumerated rather than ranked/narrowed; it
drifted into Chinese mid-answer once despite D-013's English-answer instruction; F12/F14
were missed by both models in both comparisons - a retrieval gap, not a model-size effect).
`docs/PLAN.md`'s own third Phase 3 checklist item, "Live demonstration and presentation —
run `defense-prep`" (first written as "Report and presentation"; there is no written
report, I 2026-10-02), is my own remaining work, not delegated. **Phase 3
is not being declared complete here** - the demonstration and presentation remain, by
explicit instruction.

Added 2026-09-23/24, by explicit instruction, outside the original Phase 3 checklist:
**T-042**–**T-047**, the UI redesign (English UI per D-016), English date parsing
(T-043), and the app's name and identity, **"Since"** (display name only; the repo, the
`vg09` package and `COLLECTION_NAME` are unchanged). T-042–T-047 are all on `main` (T-047,
the README, was merged and pushed 2026-10-02). Of `docs/GOAL.md`'s Definition of done,
items 1–4 are met; only item 5, the live demonstration and presentation, remains.

Added 2026-10-02, by explicit instruction: a finishing pass (**T-049** retrieval latency,
**T-050** accent contrast, **T-051** one action submits a question, **T-039** closed),
the presentation draft (**T-048**, `docs/presentation.md`, not yet read by me), and
the Sources page (**T-052**–**T-058**, D-017): sources chosen and fetched in the app
instead of in code and the terminal. All on `main`. A fresh clone was taken through the
Sources page to a first answer (T-057), with one week of history and one channel.
**Open:** T-056's stale-data marker has not been seen in a browser.

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

- [x] Retrieval with an optional date range, taken from the question or set in the UI —
  T-021 (date range), T-022 (similarity search + T-008's token-budget packing), T-027
  (dedup + whole-dataset window anchor, found by real re-testing)
- [x] Answer generation with citations: link, title, date — every call site that reads a
  Qwen3 model's output must separate its reasoning from the final answer before displaying
  or storing it (moved from Phase 1: no Phase 1 code calls an LLM, so there was no caller
  to build the utility against yet) — T-011 (reasoning/answer split), T-023 (the
  `/api/chat` call itself, per KB-011/T-008), T-024 (citations)
- [x] Chat UI, including the empty state "no data yet — run ingest" — T-025

**Exit criteria:** the three question types in `docs/GOAL.md` work end to end with sources —
met, real browser smoke test against all three (T-025's ticket entry has the detail: F05
"did X come up", F06 "what's new"/ranking, F02 "has Q progressed").
**Checkpoint:** I reviewed 2026-09-20, `grill-me` ran, every finding triaged (T-029).
Phase 2 declared complete; Phase 3 opened the same session, by explicit go-ahead.

---

## Phase 3 — Prove and publish (week 3)

- [x] Evaluation script: date-aware vs plain retrieval, large vs small model. Results table
  committed — **T-031** (harness, D-012's anchor explicit, human-gradable output — grading
  is manual, never a model), **T-032** (date-aware vs plain, `docs/GOAL.md`'s central
  claim) `done`, graded (A better 8, B better 0, equivalent 5, both wrong 2). **T-033**
  (`qwen3:30b-a3b` vs `qwen3:8b`, D-005's VRAM-differentiated pair) `done`, graded
  2026-09-23 (A better 4, B better 0, equivalent 9, both wrong 2) —
  `docs/eval-results/2026-09-23-1516-t033-model-size-comparison.md`. Both comparisons now
  real, run, and graded. **T-069** re-ran the date-aware vs plain comparison on 2026-10-05
  against a store rebuilt from the frozen archive, with the app as it stands after
  T-061–T-068; graded by me: A better 7, B better 1, equivalent 5, both wrong 2 —
  `docs/eval-results/2026-10-05-1443-t069-frozen-date-aware-vs-plain.md`. B's one win
  (F06) is a ranking error, not a date-filter failure: A put "Benchmark Radar" and a news
  video's "Real Suite" above SWE-Bench Pro Verified, the ranking the answer key calls
  wrong. F14 failed in both arms again (only YouTube cited, no HF paper) even with 200
  candidates — see the semantic-gap row in the risk register
- [x] README, Apache-2 `LICENSE`, and a fresh-clone test following the README only —
  **T-034**, depends on **T-035** (project rename, "VG-09" → "research-feed-assistant" —
  scoped to user-facing naming only; the `vg09` package/import path and the Chroma
  `COLLECTION_NAME` stored-data identifier are explicitly out of scope, flagged for a
  separate decision). Both done 2026-09-22: rename landed (`CLAUDE.md`, `app.py`), README +
  Apache-2.0 `LICENSE` written, and a real fresh-clone test (isolated scratch clone, real
  HF+YouTube backfill including the Whisper fallback path, real `bge-m3` embedding, real
  browser question) reached a real answer with real citations end to end — nothing in the
  README needed fixing
- [ ] Live demonstration and presentation — **T-048** (Slidev deck in Since's own design,
  D-019), **T-070** (demo questions in the running app on the day, then `defense-prep`).
  No written report: the deliverable is a live demo and presentation (me, 2026-10-02)
- [ ] Security baseline and overview — **T-071**–**T-077** (`docs/DESIGN.md` § Security
  baseline, D-020). Added 2026-10-05: the app must not be reachable
  purpose and results in the repo

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
| bge-m3 embeds broad conversational questions closer to spoken/YouTube-transcript text than to dense scientific HF abstracts, regardless of language - real, measured (T-022's re-run of T-014's 15 real questions): the same 5 HF papers ranked far outside a 60-candidate pool (600-1600 of 1971) for F14/F15's broad questions in *both* Swedish and English (rank barely moved, sometimes got worse in English), even though the abstracts literally contain the query's own topic words ("agent", "open-source") - ruling out translation as the cause. **T-069 (2026-10-05) also rules out pool size:** F14 failed the same way for the sixth time across three graded runs (T-032 ×2, T-069) - both arms cited only YouTube and no HF paper - even with 200 candidates instead of 60 (T-067). The cause is the semantic gap between the question and the abstracts, not how many candidates are fetched | Confirmed, not hypothetical | **Not fixed** - this is a result to measure in Phase 3's date-aware-vs-plain evaluation, not a retrieval bug. If Phase 3's results look weak for HF-heavy questions, this register entry is why, before assuming the retrieval pipeline itself is broken. A larger candidate pool is not a mitigation (T-069); a question that names papers is (T-068's source filter), a broad one is not |
| T-024's positional citation resolution (`vg09.citations.build_citations()`) can't tell a real evidence citation apart from a bracketed number the model used descriptively - real, observed: a real F12 answer ("not mentioned") contained "reviewed all 38 sources (from `[1]` to `[38]`)", and both numbers were resolved as if they were cited evidence, producing 2 false-positive citations on a correct negative answer | Confirmed once, real; frequency unknown | **Partially fixed (T-040/D-015, 2026-09-22).** The predicted risk materialized again, twice, in T-032's real graded re-run: F10-A's `[1-20]` and F12-A's `[1-31]`. A count threshold (at most 5 numbers resolves as a citation, more is a descriptive enumeration, `CitationResult.descriptive_ranges`) now catches the *range*-shaped case. **Still open:** a short bracket used descriptively (e.g. `[1]` and `[2]` meaning "the first two", not a comma-list or range) is still indistinguishable from a real citation - watch for that shape specifically if it turns up |
| Real RAG prompt (system + retrieved chunks + question) exceeds `num_ctx=16000`, silently dropping the **front** of the prompt with no error (KB-005) — if retrieved chunks are placed there, the exact evidence citations depend on vanishes with no signal | Low — measured, not estimated: 173 (system, T-030) + 40 (question) + 2542 (reasoning/answer, T-028) leaves 13245, max top-k 27 at a real measured worst-case chunk cost (488, T-038); see `docs/DESIGN.md` § Context budget | **This risk materialized for real once** (T-031's F07, `prompt_eval_count=15349`, empty answer) before being fixed: `pack_to_budget()` had measured only bare chunk text, never the real citation-wrapper text actually sent (KB-018) — fixed in T-038, re-verified across all 15 real questions (max real `prompt_eval_count` 81% of `num_ctx`, no truncation). Residual risk, corrected here (stale since T-019, noticed while editing this row): the "no real YouTube transcript text exists yet" clause was true at Phase 1 open but stopped being true once T-019 recalibrated the chunk-size cap against 17 real transcripts (max real chunk 395/400 qwen3 tokens) — not still open. Prompt ordering (chunks least-relevant-first, system+question last) and a real per-call `prompt_eval_count` vs `num_ctx` check remain the defense-in-depth backstop |
| ~~`vg09/store.py` has no automated tests...~~ **Closed by T-036** (2026-09-22): `EmbedBatchTests` (`tests/test_store.py`) asserts `embed_batch()`'s real request body always includes `model="bge-m3"` and an explicit `num_ctx` (mocked at `requests.post`), plus a `raise_for_status`-before-`.json()` test matching T-029's pattern for the project's other two Ollama call sites. No defect found — the code already complied | Resolved | — |
| ~~`vg09/youtube_backfill.py` (pacing, resumability, ...) has no automated tests...~~ **Closed by T-036** (2026-09-22): `tests/test_youtube_backfill.py` (9 tests, fully mocked, no network/GPU/real sleep) covers resumability (`document.exists()` skips a re-fetch, confirmed across two runs), pacing (pause happens between each pair of consecutive attempts, drawn from the real random source, skipped entirely for already-done videos), and watermark-write-on-completion (written only after the full window, stays unwritten if a video's `normalize()` call raises mid-run, still written if a single channel's listing fails since that's a handled case, not an interruption). No defect found — the code already behaved as designed | Resolved | — |
| `vg09/youtube.py::normalize()`'s Whisper branch catches bare `except Exception` — a real code defect in `fetch_whisper_transcript()` would be misreported as an ordinary Whisper failure and silently produce a weaker `title_description` document, with no alert. Self-flagged in D-010's own Cost section as an accepted, watched risk; found again by Phase 1's `grill-me` review (2026-09-19) | Low today (no known defect); D-010's own "would change our mind" clause already names the failure mode to watch for | Deferred to Phase 3, T-020's triage. Add a threshold alert on `fetched_fallback` counts (e.g. N consecutive full-fallback videos) per D-010's own suggestion |
| F14's "God's Eye View"/Palantir YouTube citation (`docs/eval-questions.md`) is a softer fit for "stora AI-verktyg" than its Suno-alternative sibling citation — Palantir is a data/intel platform, not squarely an AI tool. Found by Phase 1's `grill-me` review (2026-09-19) | Low — the facit already accepts either citation, so this doesn't block grading | Deferred to Phase 3. If F14 is ever re-graded strictly, prefer the Suno-alternative (`9RtywbN--QE`) citation, or add a stronger second HF+YouTube pair |
| `app.py` calls `vg09.store.latest_feed_date()` up to three times per UI interaction (status bar, sidebar manual-picker defaults when the checkbox is on, question resolution), plus `vg09.store.corpus_stats()` once (T-042's status bar, another full scan) — every call is its own full Chroma metadata scan (D-011/D-012's own accepted cost for `latest_feed_date()`; `corpus_stats()` is the same shape, T-042). Found by Phase 2's `grill-me` review (2026-09-20) for `latest_feed_date()`; `corpus_stats()` added to this same row rather than a new one (2026-09-23) since it's the identical cost pattern, not a new risk. Explicitly deferred, not fixed, by my instruction when T-029 was scoped | Low today (~2000 chunks, cheap per D-012's Cost section); rises only if the corpus grows by orders of magnitude, same condition D-012 already names | Deferred, no ticket yet. If the corpus ever grows enough for this to matter, cache one `latest_feed_date()`/`corpus_stats()` result per script run (Streamlit reruns the whole script per interaction, so a plain module-level cache won't survive between runs — would need `st.session_state` or similar) |
| ~~`vg09.date_range`'s relative-time extraction matches only Swedish phrases...~~ **Closed by T-043** (2026-09-24, same-session follow-up after D-016 made this a real bug, not a risk): real English patterns added for "last/past N weeks/days/months", "last week"/"this week"/"last month" (no number), "September 16"/"the 16th of September", "today", and "latest"/"most recent" for ranking — a deliberate, idiomatic adaptation, not a 1:1 regex translation (English already has separate natural words for the window vs. ranking jobs Swedish's "senaste" does with one). Verified against real hand-written English translations of all 15 of T-014's real questions: **identical tally to the original Swedish run — right=8, wrong=0, unparseable_ok=7, unparseable_wrong=0** (`docs/eval-results/2026-09-24-t043-english-date-extraction.md`). The Swedish run was re-executed unchanged in the same session to confirm no regression: same script, same file, same 8/0/7/0 result | Resolved | — |
