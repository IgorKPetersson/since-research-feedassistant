# Session tree · 2026-09-16 · Phase 1 — Ingest, T-016 through T-013

**Tickets:** T-016, T-009, T-010, T-008, T-015, T-017 (written, blocked), T-012, T-013 ·
**Handoff:** docs/HANDOFF.md § 2026-09-16
**Read this if you want to know:** why YouTube ingest is blocked, where D-006/D-007 came
from, why the HF backfill watermark sits 2 days back, or why `data/raw/` is structured the
way it is.
**Previous:** docs/sessions/2026-09-15-phase-0.md

## 1. Opening Phase 1  [T-016]
   - 1.1 PLAN.md phase flipped to Phase 1; GOAL.md gets conversation history as a non-goal
     · outcome: done
   - 1.2 First ticket set written: T-008 (context budget), T-009 (collectors), T-010
     (fallback test), T-012, T-013, T-014
     · outcome: written, none started
   - 1.3 Review round 1: T-011 (reasoning/answer split) moved to Phase 2 — no Phase 1
     caller for it; T-015 (backfill) added ahead of T-013; T-014 reframed as hand-written questions,
     with agent-verified sources
     · outcome: TICKETS.md revised before anything committed
   - 1.4 Review round 2: `data/raw/` established as the durable document contract
     (T-009/T-015 write, T-012 reads, T-013 appends, T-014's freeze point); run order
     recorded
     · outcome: T-016 closed, docs-only

## 2. HF + YouTube collectors  [T-009]
   - 2.1 `vg09/document.py` (shared `Document` shape, `data/raw/` persistence),
     `vg09/hf_papers.py`, `vg09/youtube.py` written
     · outcome: done
   - 2.2 First verification run crashed: YouTube transcript fetch raised `IpBlocked`, one
     day after T-002's clean 20/20 (2026-09-15 → 2026-09-16)
     - 2.2.1 Original code only caught 3 of `CouldNotRetrieveTranscript`'s subclasses, not
       the shared parent — crashed instead of falling back
       · outcome: fixed to catch the parent class; KB-008 written
   - 2.3 grill-me: the fallback discarded *why* captions failed, which the next ticket
     would need
     · outcome: fixed — log the exception type at the point of fallback

## 3. Missing vs blocked split  [T-010]
   - 3.1 Requirement: distinguish "captions missing" (falls back, final doc) from
     "blocked" (no final doc, `Pending` marker, abort the run) — real trigger for this was
     T-009's own `IpBlocked` hit
     · outcome: `vg09/youtube.py` restructured; `Document` gains `text_source`/
       `fallback_reason`
   - 3.2 3 mocked unit tests written (missing, blocked, caption-success against the real
     `FetchedTranscript` shape — never actually run before this)
     · outcome: all pass, no live YouTube calls
   - 3.3 grill-me: a video blocked once then resolved later would leave a stale
     `*.pending.json` marker next to its new final document
     · outcome: fixed — `clear_pending()`, 4th test added
   - 3.4 D-001 superseded by **D-006** (missing/blocked split, documented)
     · outcome: done

## 4. Context budget, measured  [T-008]
   - 4.1 System prompt (171 tokens), question (40 reserved), reasoning+answer (2000
     reserved via `num_predict` cap, measured from 6 real runs, 515-1150 observed)
     · outcome: `docs/DESIGN.md` § Context budget written
   - 4.2 Chunk size/top-k: 400-qwen3-token cap (measured on all 20 real HF abstracts), max
     top-k 34
     · outcome: done; flagged as HF-only, YouTube unmeasured
   - 4.3 Tried `num_predict:0` to cheaply count tokens — it does NOT mean "generate
     nothing" (485 tokens on a 9-word prompt)
     · outcome: **KB-009**; switched to `num_predict:1`
   - 4.4 grill-me on the measurement script itself: `/api/embed` call never set `num_ctx`
     explicitly; nothing compared `prompt_eval_count` against `num_ctx`
     · outcome: both fixed (CLAUDE.md hard rules), full measurement re-run, numbers held

## 5. "No YouTube calls" and the T-015/T-017 split  [T-015, T-017]
   - 5.1 One manual transcript request (`nZYJdwM-_nI`) — still `IpBlocked`;
     traceback showed `yt-dlp` listing succeeded, only the caption fetch failed
     · outcome: **KB-008 updated** (not superseded — same claim, more evidence): block is
       scoped to the transcript-fetch call specifically
   - 5.2 T-015 split: HF-only backfill (runnable now) + new **T-017** (YouTube backfill,
     `status: blocked`, decision due 2026-09-18 among wait-it-out / local Whisper /
     title+description-only)
     · outcome: T-013/T-014 updated to per-source dependency chains so neither waits on
       T-017 to start
   - 5.3 T-015 run for real: 1184 papers, 56 days (2026-07-23..2026-09-16), all 16 weekend
     days cleanly empty (KB-002 at scale)
     · outcome: watermark `2026-09-15`; resumability verified by deleting 3 real day
       markers and confirming exactly those 3 + today re-fetched
   - 5.4 Found: only re-checking "today" isn't enough — Sweden runs ahead of UTC,
     a post-midnight run could close a day still open on HF's server clock
     · outcome: fixed — 2-day reopen window (`REOPEN_DAYS=2`), watermark moved to
       `2026-09-14`; stale marker from before the fix cleared and re-verified live

## 6. Chunk, embed, store  [T-012]
   - 6.1 HF: one chunk per paper. YouTube: chunk by transcript timestamp, not sentence
     (auto-captions have no punctuation, KB-001) — citation gets `&t=SECONDS`
     · outcome: `vg09/chunking.py` written
   - 6.2 Checked `data/t002_youtube_captions.json` for real timestamped caption text —
     it only ever saved counts, never real snippets
     · outcome: no real caption data exists anywhere in the repo; chunk-size target
       calibrated from a real qwen3-tokenizer measurement against *synthetic*
       caption-style text instead of guessed
   - 6.3 Timestamp chunking requires per-snippet timing `Document` never stored — schema
     change (`segments` field) made within T-012 and flagged
     · outcome: `/api/show`'s real chat template checked separately (confirms `/api/chat`
       always renders system first, regardless of message order — changes T-008's
       truncation-ordering mitigation, noted in DESIGN.md's new Phase 2 section)
   - 6.4 Self-review caught a `query_texts=` slip in a smoke-test script — would have
     silently invoked Chroma's default embedder (the hard rule)
     · outcome: fixed before it reached the real store; documented in DESIGN.md's
       Interfaces section as a standing gotcha
   - 6.5 Real run: 1184 documents → 1184 chunks → `collection.count()=1184`, stable across
     two runs; date-range filter verified against the real production store
     · outcome: done
   - 6.6 `/deep-review`: schema change flagged as the one process issue (CLAUDE.md's
     stop-and-ask list names stored-data-format changes explicitly)
     · outcome: reported prominently rather than reverted — **approved after the fact,
       recorded as D-007** (start of next session's continuation, § 7)

## 7. D-007 and catch-up  [T-013]
   - 7.1 D-007 written: `segments` schema change, why, what was rejected, the cost of not
     asking first
     · outcome: done
   - 7.2 T-015's day-by-day logic factored into `vg09/sync.py` (`sync_hf`) so backfill and
     catch-up share one implementation
     - 7.2.1 Refactor introduced an off-by-one (57-day window instead of 56)
       · outcome: caught by comparing real output before it shipped; fixed
   - 7.3 `vg09/catchup.py`: per-source watermarks; YouTube watermark checked but never
     acted on — module never imports `vg09.youtube` at all (structural guarantee, not just
     convention)
     · outcome: done, tested
   - 7.4 Writing `tests/test_sync.py`, patched only `vg09.document.RAW_DIR` (matching the
     pattern that worked for YouTube tests) — didn't work for `hf_papers`'s day-marker
     functions, which import `RAW_DIR` by value into their own module
     - 7.4.1 The under-isolated test's reopen-window logic deleted 4 **real** `_done.json`
       markers (2026-09-09..12) before being caught
       · outcome: **KB-010** written; real backfill re-run to repair (identical paper
         counts came back, no data lost); `vg09/store.py` checked for the same exposure
   - 7.5 Real end-to-end verification: removed 2 real days (40 papers) from `data/raw/hf/`
     *and* the live Chroma store, rolled the watermark back, ran the real pipeline
     · outcome: catch-up re-fetched both days exactly; store rebuild returned
       `collection.count()` to 1184; duplicate check confirmed 1184 unique ids; ran twice
       more to confirm stability

## 8. Session close
   - 8.1 Session-tree, kb-entry pass, session-handoff, commit + push
     · outcome: this file + docs/HANDOFF.md + push to origin/main
