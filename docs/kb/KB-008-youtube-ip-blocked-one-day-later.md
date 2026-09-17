# KB-008 — IpBlocked clears and recurs: 17 paced requests succeeded, the 18th blocked again

**Area:** YouTube ingest — captions
**Status:** provisional (the clear-then-recur pattern is now two data points on the "recurs"
side of it, still not enough to characterize what actually triggers it)
**Date:** 2026-09-16 (T-009 occurrence); 2026-09-16, later same day (manual re-check by me,
still blocked); 2026-09-17 (manual re-check by me, block cleared); 2026-09-17, later same day
(T-017's real paced backfill run, block recurred after 17 successful requests)  ·  **From:**
T-009, me, T-017

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

## Confidence and limits
Three blocked occurrences (T-009's run, the 2026-09-16 same-day manual re-check, and T-017's
2026-09-17 real run) and one cleared occurrence (the 2026-09-17 manual re-check, ~1 hour
before T-017 ran and hit the block again). Two channels now have real caption successes
(`@theAIsearch`: 7/7 in-window videos across this project's history; `@mreflow`: 9/9), one
channel (`@NateBJones`) blocked on its very first-ever request from this project, and
`@ColeMedin` remains completely untested. Not confirmed: a volume threshold within a
session, whether it's per-channel/per-video-novelty rather than cumulative, how long *this*
second block will take to clear, or whether repeating T-017's run tomorrow would reproduce
the same ~17-request ceiling, a different one, or none at all. This directly triggers
D-008's "would change our mind" clause - a real recurrence during T-017's run - and is now a
decision point for me on whether to un-park option (b) (`yt-dlp` + local Whisper) for
whatever channels/videos remain, rather than waiting out a second block on faith alone.
