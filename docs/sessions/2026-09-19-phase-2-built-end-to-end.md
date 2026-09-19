# Session tree · 2026-09-19 · Phase 2 built end to end, then two real bugs found and fixed by using it

**Tickets:** T-014, T-020, T-026, T-021, T-022, T-027, T-011, T-023, T-024, T-025, T-028 ·
**Handoff:** docs/HANDOFF.md § 2026-09-19
**Read this if you want to know:** why `NUM_PREDICT` is 2542 not 2000, why citations resolve
by bracketed number instead of `[Title, date]`, why there are two different `today` anchors
in this codebase, or why F02/F06 still miss in the eval measurement.

## 1. T-014 closed: F14/F15 (cross-source questions), then a grill-me of all Phase 1
   - 1.1 Two new eval questions requiring both HF and YouTube sources written and verified
     · outcome: T-014 done, Phase 1's eval-questions checkbox ticked
   - 1.2 grill-me found six issues, triaged: fix two now (T-020), defer four
     · outcome: T-020 opened for the frozen-dataset proof + yt-dlp timeout; rest deferred to
       `docs/PLAN.md`'s risk register

## 2. T-020: prove the frozen dataset hasn't drifted  [T-020]
   - 2.1 SHA-256 manifest of every `data/raw/` file, committed; the zip archive itself lives
     outside the repo (`C:\AIProjects\VG-09-frozen\`)
     · outcome: `scripts/t020_verify_eval_dataset.py` can prove drift later without needing
       the archive itself for routine checks

## 3. T-026 → T-021: date-range extraction  [T-021]
   - 3.1 Rule-based Swedish parser, tested against all 15 real T-014 questions live from the
     doc (not retyped): 8/15 resolved, 0 wrong, 7/15 correctly unparseable
     · outcome: `vg09/date_range.py`. Two of the seven "unparseable" ones (F01/F03/F06) turned
       out to be a *different question type* (ranking, not a window) - not a parsing miss
   - 3.2 Confirmed: calendar-month subtraction (not 30 days), bare plural = ambiguous
     · outcome: both design choices kept as-is

## 4. T-022: retrieval - filter, sort, pack  [T-022]
   - 4.1 Real 15-question re-run through actual retrieval found F02/F14/F15 "missing" their
     expected sources in the top 5
     · outcome: investigated before building more - see §5

## 5. Investigation: why do F02/F14/F15 miss?  [T-022]
   - 5.1 Existence check + real Chroma distance ranks + English-translation test
     · outcome: three distinct causes, not one: (a) one video's many chunks crowding the
       top-5 [→ T-027 dedup fix], (b) a real window-anchor mismatch excluding a genuinely
       relevant video [→ T-027 anchor fix], (c) a real semantic/register gap (dense HF
       abstracts vs. broad conversational questions) that is NOT a bug - recorded in the risk
       register for Phase 3 to measure, deliberately not fixed

## 6. T-027: dedup + whole-dataset anchor  [T-027]
   - 6.1 Cap chunks per doc at 2; anchor `today` to the real max feed_date across both
     sources, not either source's cutoff/watermark
     · outcome: headline went 9/14 → 11/14 (F04 counted correct-by-design). F02 still misses
       - The cap is not tuned against one known question; left as is
   - 6.2 D-011 amended: eval code pins `today=2026-09-16` explicitly; production uses
     `latest_feed_date()` (2026-09-17) - two different, both deliberate, anchors
     · outcome: `docs/eval-questions.md`'s already-written facit windows stay correct without
       rewriting them

## 7. T-011 → T-023: the real answer-generation call  [T-011, T-023]
   - 7.1 T-011 built first (T-023's hard dependency, wasn't done yet)
     · outcome: `vg09/llm.py`, raises on empty `thinking` (KB-007's real think=false shape)
   - 7.2 Real end-to-end run found the model cites by bracketed *position* ("source [27]"),
     not the `[Title, date]` format the system prompt asked for
     · outcome: flagged for T-024 rather than fought

## 8. T-024: citations from positional references  [T-024]
   - 8.1 System prompt rewritten to ask for exactly what the model already does; re-measured
     157 tokens (was 171) - budget updated to match
     · outcome: real F05 answer's `[27]`/`[4]` both resolved correctly, real `&t=` preserved
   - 8.2 Real limitation found on F12: model wrote "reviewed sources [1] to [38]" - both
     numbers resolved as false-positive citations on a correct "not mentioned" answer
     · outcome: not fixed - recorded in the risk register, can't tell citation from
       description by bracket shape alone without a stricter format

## 9. T-025: the chat UI  [T-025]
   - 9.1 Real browser smoke test (Playwright) of all three GOAL.md question types
     · outcome: F02's real run hit a genuine `done_reason=="length"` unplanned - this became
       T-028's finding 1, found by using the feature, not by looking for it
   - 9.2 Empty-state verified without touching the real 1971-chunk store - a throwaway script
     pointed `vg09.store.STORE_PATH` at a fresh temp dir first
     · outcome: real production data never at risk

   - 10.1 I ran the UI themselves, found truncation + multi-number citations broken
     · outcome: exactly the kind of finding only real use surfaces - three real repro runs of
       the same question measured reasoning alone at 61.5-92.1% of the 2000 cap
   - 10.2 Citation fix: bracket split on comma, each number resolved independently, unless
     not all pieces are digits (preserves the old single-non-numeric-bracket behavior)
     · outcome: real `[1, 2, 3]`-shaped bracket against real chunk metadata resolved to 3
       real documents (previously would have been 1)
   - 10.3 Chosen: "raise NUM_PREDICT" over "shorter reasoning" - new value derived from
     the measurement (1842 + 400 + 300 = 2542), not a round number
     · outcome: 3 more real runs of the same question, `done_reason=="stop"` every time
   - 10.4 Chunk-budget-sufficiency re-check across all 15 questions - **interrupted**
     · outcome: first attempt used the wrong `today` anchor and gave a false 10/14 (see
       KB-016) - caught, corrected script re-launched, not confirmed finished before this
       session ended on a token warning
