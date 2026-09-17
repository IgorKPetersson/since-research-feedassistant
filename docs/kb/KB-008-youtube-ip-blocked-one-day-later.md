# KB-008 — IpBlocked is channel-scoped and durable for @NateBJones/@ColeMedin, not a session volume cap

**Area:** YouTube ingest — captions
**Status:** provisional (channel-scoped reading is now well-supported by 24 consecutive
paced requests, but *why* these two channels specifically remains unexplained)
**Date:** 2026-09-16 (T-009 occurrence); 2026-09-16, later same day (manual re-check by me,
still blocked); 2026-09-17 (manual re-check by me, block cleared for one video); 2026-09-17,
later same day (T-017's real paced backfill run, block recurred on the first `@NateBJones`
video); 2026-09-17, still later (T-019's 24-request re-run, `@NateBJones`/`@ColeMedin` 100%
blocked throughout)  ·  **From:** T-009, me, T-017, T-019

## Claim
On 2026-09-16, `youtube_transcript_api.fetch()` raised `IpBlocked` (a subclass of
`RequestBlocked`, itself a subclass of `CouldNotRetrieveTranscript`) for both videos
attempted against `@theAIsearch`, on the same machine that got 20/20 successes across 4
channels the day before (KB-001, 2026-09-15). This is a real, unprompted occurrence of the
exact risk KB-001's "Confidence and limits" section named as untested: "YouTube's caption
availability and rate limiting can vary."

## Evidence
`scripts/t009_run_collectors.py`, run 2026-09-16 against `@theAIsearch`'s latest 2 videos
(`9RtywbN--QE`, `nZYJdwM-_nI`). Both raised `IpBlocked` from
`YouTubeTranscriptApi().fetch(video_id)`. First run crashed uncaught (T-009's original code
only caught `TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable` - three of many
subclasses of `youtube_transcript_api._errors.CouldNotRetrieveTranscript`, not the shared
parent). Fixed to catch `CouldNotRetrieveTranscript` itself; re-run then triggered the D-001
title+description fallback correctly for both videos, producing valid normalized documents
(confirmed non-empty `text`, `title` present at its start).

No configuration changed between the two runs - same machine, same network, ~24h apart, well
under any per-day request volume that would look adversarial (20 video-metadata + 20
transcript calls on the 15th; 2 + 2 on the 16th).

**Update, same day, manual re-check by me (not an agent call - explicit instruction was no
further agent-initiated YouTube calls after this ticket):** a single manual transcript
request against `nZYJdwM-_nI` (one of the same two videos from the run above) still raised
`IpBlocked`. The traceback shows the video-listing step (`yt-dlp`, channel/video metadata)
succeeded; only the caption-text fetch (`YouTubeTranscriptApi().fetch()`) failed. This
localizes the block to the transcript-fetch call specifically - yt-dlp's metadata listing is
not (yet) affected, at least for this one video, on this IP, at this point in time. The
block had not cleared within the same day.

**Update, 2026-09-17, manual re-check by me:** a manual transcript request against the same
video, `nZYJdwM-_nI`, succeeded - 1051 snippets returned, containing real transcript text
(not empty, not an error page). This is the same video that was `IpBlocked` on 2026-09-16
(both the original run and the same-day re-check). The block cleared sometime between the
2026-09-16 same-day re-check and this 2026-09-17 check - somewhere under roughly 24 hours of
total duration, consistent with an IP-level rate-limit block rather than a permanent ban.
This is the evidence D-008 rests its "wait it out" choice on.

## Consequences
This is the first **real** trigger of D-001's title+description fallback path - T-002 only
confirmed the fallback data was *available*, never exercised by an actual failure. That gap
is now closed by evidence, ahead of T-010's planned unit test (which still needs to write a
test that doesn't depend on hitting a real block on a given day).

More importantly for **T-015's backfill**: `IpBlocked` is not a per-video signal like
`NoTranscriptFound` - it's an IP-level block that will fail *every* subsequent request until
it clears. T-015's acceptance criteria ("stop and report on blocking signals" rather than
retry through it) is not a hypothetical precaution; this is what it will see, possibly
immediately. T-015 should treat `RequestBlocked`/`IpBlocked` specifically (not just any
`CouldNotRetrieveTranscript`) as the stop-and-report signal, since falling back to
title+description for every video in an 8-week, multi-channel backfill without surfacing
that captions stopped working entirely would silently produce a much weaker dataset than
intended, with no error.

Whether this block is transient (clears within hours/days) or durable is not yet known -
still not cleared as of the same-day manual re-check. Since the block appears scoped to the
transcript-fetch call rather than yt-dlp's metadata listing, an HF-only backfill (T-015) and
a YouTube *metadata-only* pass (titles, descriptions, upload dates - no captions) are not
blocked by this; only the caption text itself is. This is exactly why T-015 is being split:
HF's backfill can run now, and YouTube's transcript path is deferred to a new ticket (T-017)
pending a decision among waiting it out, local Whisper transcription, or title+description
only.

**Update, 2026-09-17, later the same day — T-017's real paced backfill run
(`scripts/t017_youtube_backfill.py`):** with the block believed cleared (per the manual
re-check above) and D-008's decision to wait it out, the real backfill ran with a randomized
3-8s pause between videos. It retried both pending videos first (`nZYJdwM-_nI`,
`9RtywbN--QE` - both succeeded, real captions), then proceeded through `@theAIsearch`'s
remaining 6 in-window videos and all 9 of `@mreflow`'s - 17 consecutive real caption fetches
succeeded with **zero fallbacks**. The very next request - the first video attempted from a
**third** channel, `@NateBJones` (`YTG0rdHPTDE`, uploaded today, 2026-09-17, never
previously attempted by this project) - raised `IpBlocked` again. The collector's
stop-on-block behavior (D-006) worked exactly as designed: no fallback document was written,
a `Pending` marker was written for `YTG0rdHPTDE`, and the run aborted immediately rather than
continuing to `@ColeMedin`. No exception, no partial/corrupt document.

This changes the picture from "block clears after ~1 day and stays cleared" to "block clears,
but recurs under real sustained (if paced) use, somewhere between 17 and 18 requests in this
one session." Two readings are both still open: (a) the block is volume-sensitive within a
session, regardless of pacing - 17 successes is close to no coincidence with the number
of requests, so a lower per-session cap may exist; (b) the block is coincidentally
per-channel or per-something-else, and `@NateBJones` (a channel that had zero prior calls
against it this project, unlike `@theAIsearch` and `@mreflow`) triggering on its very first
request is itself the signal, not the running total. Nothing here distinguishes the two -
both are consistent with one data point.

**Update, 2026-09-17, still later the same day — T-019's re-run with Whisper wired in
(D-009/D-010):** re-ran the same backfill immediately after T-019's collector changes
landed. Every single caption attempt against `@NateBJones` (16 videos) and `@ColeMedin`
(8 videos) - **24 requests total, paced with the same 3-8s/longer-pause schedule** - raised
`IpBlocked`. Zero successes, zero exceptions to the pattern. Meanwhile `@theAIsearch` and
`@mreflow` needed no new caption calls at all this run (already fully fetched by the earlier
run) - so this doesn't newly confirm they're still clear, but nothing contradicts it either.
This is much stronger evidence than the single first-video data point above: the block, at
least as of this run, looks **durable and channel/scope-specific** to `@NateBJones` and
`@ColeMedin` rather than a volume-sensitive session cap that a paced retry could out-wait -
24 consecutive paced requests over several minutes never once cleared. All 24 resolved via
the Whisper fallback (D-009) with zero errors and zero title+description fallbacks needed -
see T-019's ticket notes for the full run.

## Confidence and limits
Four blocked occurrences (T-009's run, the 2026-09-16 same-day manual re-check, T-017's
2026-09-17 real run, and T-019's 24-request re-run) and one cleared occurrence (the
2026-09-17 manual re-check against one specific video, `nZYJdwM-_nI` - which itself then
belonged to `@theAIsearch`, a channel that turned out fine anyway). Two channels have real
caption successes across their full in-window history (`@theAIsearch`: 7/7; `@mreflow`:
9/9), two channels are 100% blocked across every video attempted so far (`@NateBJones`:
0/16; `@ColeMedin`: 0/8). The channel-scoped reading is now much better supported than the
volume-threshold reading - 24 paced requests against the blocked channels never cleared,
where 17 requests against the clean channels never blocked. Still not confirmed: *why*
these two channels specifically are blocked (nothing else distinguishes them from
`@theAIsearch`/`@mreflow` in this project's code), whether the block will ever clear for
them, or whether a *new* channel added later would be blocked on its first request the way
`@NateBJones` was. T-019's Whisper path (D-009) makes this largely moot for data collection
going forward - captions are attempted first every time, so if the block ever clears for
these channels, real captions resume automatically with no code change needed.
