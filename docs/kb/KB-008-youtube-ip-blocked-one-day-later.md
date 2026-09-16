# KB-008 — the same machine went from 20/20 caption successes to 100% `IpBlocked` one day later, and the block was still live on a manual re-check the same day

**Area:** YouTube ingest — captions
**Status:** provisional
**Date:** 2026-09-16 (T-009 occurrence); 2026-09-16, later same day (manual re-check by me)  ·  **From:** T-009, me

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

## Confidence and limits
Two occurrences (T-009's run, and one manual re-check), one channel (`@theAIsearch`), three
videos total, one machine, same day. Not confirmed: whether other channels or videos are
also blocked right now, how long the block typically lasts, whether it's IP-wide (affecting
anything else on this network) or scoped to this specific caller pattern, or whether
yt-dlp's metadata listing would also eventually get blocked under sustained use even though
it wasn't here. Revisit this entry once T-017 (YouTube backfill, currently blocked pending a
transcript-path decision) actually runs and either confirms the block persists or finds it's
cleared.
