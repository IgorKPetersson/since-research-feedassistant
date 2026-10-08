# Session tree · 2026-09-17 · Whisper un-parked, wired in, and YouTube catch-up closed for real

**Tickets:** T-017, T-018, T-019, T-013 · **Handoff:** docs/HANDOFF.md § 2026-09-17
**Read this if you want to know:** why Whisper exists in this codebase at all, why the
collector no longer aborts on a caption block, or why `TARGET_CHUNK_CHARS` changed twice in
one day.

## 1. KB-008: is the IpBlocked block still live?  [T-017]
   - 1.1 Manual re-test of `nZYJdwM-_nI` - block had cleared
     · outcome: KB-008 updated with the 2026-09-17 clear. Directly gated D-008.

## 2. D-008: wait out the block (option a)  [T-017]
   - 2.1 Decision recorded, option (b) (Whisper) named as the explicit reserve if it recurs
     · outcome: accepted, later superseded

## 3. T-017's real paced backfill  [T-017]
   - 3.1 4-week window, 3-8s pacing, pending videos retried first
     · outcome: 17/17 succeeded (both pending + theAIsearch + mreflow)
   - 3.2 Block recurred on `@NateBJones`'s very first video
     · outcome: run aborted per D-006, `Pending` marker written. This is the event that
       triggered D-008's "would change our mind" clause.

## 4. D-009: un-park Whisper for real  [T-017]
   - 4.1 Decision: activate option (b), scoped to the channels the block hits
     · outcome: accepted, supersedes D-008. Required T-018 (feasibility) before any
       collector change.

## 5. T-018: does yt-dlp audio + faster-whisper even work?  [T-018]
   - 5.1 Audio download for the blocked video - not blocked at all
     · outcome: feasible. Only the transcript-API endpoint is affected.
   - 5.2 CUDA DLL loading failed via `os.add_dll_directory()`
     · outcome: fixed via a real `PATH` prepend instead - KB-012, a genuine Windows/
       ctranslate2 quirk, verified the hard way (ctypes.WinDLL loaded fine standalone,
       ctranslate2 still failed until PATH itself changed)
   - 5.3 Timing/VRAM measured in isolation
     · outcome: 39.7s for a 30.8-min video, ~1.1GB VRAM - KB-013
   - 5.4 Dead end / unexpected finding: real auto-captions DO have punctuation
     · outcome: contradicts `vg09/chunking.py`'s docstring (misattributed to KB-001) -
       KB-014, flagged per the project's reality-contradicts-docs rule, not silently fixed
       here (that came later, § 6.1)

## 6. T-019: wire Whisper into the collector  [T-019]
   - 6.1 Fix chunking.py's punctuation premise + recalibrate against real captions
     · outcome: real ratio (4.16-4.61 chars/token) was *worse* than the synthetic
       estimate (5.55-6.71) - the dangerous direction per KB-005. `TARGET_CHUNK_CHARS`
       1942→1454. Verified against the largest real transcript: max chunk 395/400 tokens.
   - 6.2 Real joint VRAM test: Whisper + qwen3:30b-a3b + bge-m3 together
     · outcome: fits, ~0.9GB headroom, neither Ollama model evicted - KB-015. Per-video
       load/unload fallback named in the ticket was not needed.
   - 6.3 `vg09/youtube.py`: three-tier fallback (captions → Whisper → title+description)
     · outcome: `IngestBlocked`/abort-on-block retired and removed as dead code (D-010,
       amends D-006's consequence, not its missing/blocked classification)
   - 6.4 Real re-run for `@NateBJones`/`@ColeMedin`
     · outcome: 24/24 videos resolved via Whisper, 0 fallbacks, 0 errors. Both channels
       turned out to be 100% blocked on captions this run - KB-008 updated again.
   - 6.5 T-017 marked done (T-019 completed what it was blocked on)

## 7. Merge and push the T-017/T-018/T-019 stack
   - 7.1 Fast-forward merge to `main`, pushed to origin, ticket branches deleted
     · outcome: done, clean linear history preserved (project convention)

## 8. T-013: does catch_up_youtube() actually work?  [T-013]
   - 8.1 Discovered `catch_up_youtube()` was still a no-op stub from when YouTube had no
     real transcript path
     · outcome: implemented for real, reusing `youtube_backfill.run()`'s paced logic with
       an explicit `start`/`today` window (same factoring idea as `sync_hf`)
   - 8.2 Built the store with the full YouTube dataset for the first time
     · outcome: 1184 (HF-only) → 1994 chunks (41 YouTube documents, 810 chunks)
   - 8.3 Real gap simulation: removed 2026-09-10's 3 videos (1 captions, 2 whisper),
     rolled the watermark back, ran catch-up for real
     · outcome: 2 recovered via Whisper as expected; the 3rd (`q9tpIc8PVKM`,
       previously-clean `@theAIsearch`) hit `IpBlocked` **and** its Whisper audio
       download failed (`403`) - fell through to title+description, the first real
       double-failure case. KB-008 updated again - the "durably channel-scoped" reading
       from § 6.4 is now weaker; the true trigger is still unknown after 5 real sessions.
   - 8.4 Verified into Chroma: 1971/1971 unique ids, no duplicates
     · outcome: closed the loop, matching HF's earlier verification shape exactly
   - 8.5 Real bug found: `fallback_reason` dropped in the windowed chunking path
     · outcome: fixed (`vg09/chunking.py`), regression test added, confirmed against all
       24 real Whisper documents in the store after a rebuild. Invisible for captions
       (always `None` there) until a real Whisper document exercised the code path.
   - 8.6 T-013 marked fully done (both HF and YouTube halves verified for real)

## 9. Merge and push T-013
   - 9.1 Fast-forward merge to `main`, pushed, branch deleted
     · outcome: done

## 10. Phase 1 status review
   - 10.1 Every Phase 1 checklist item done except T-014 (eval questions, written by hand)
     · outcome: Phase 2 not started yet
