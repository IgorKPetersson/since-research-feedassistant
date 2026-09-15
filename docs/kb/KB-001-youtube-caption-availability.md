# KB-001 — auto-generated English captions were available for all 20 sampled videos across the 4 chosen channels

**Area:** YouTube ingest — captions
**Status:** provisional
**Date:** 2026-09-15  ·  **From:** T-002

## Claim
For the latest 5 videos each of @theAIsearch, @mreflow, @NateBJones and @ColeMedin (20
videos total), `youtube-transcript-api` successfully returned a transcript for every one.
All 20 were auto-generated English captions (`is_generated=True`); none were manual
captions. No `TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable` or other error
occurred in this sample.

## Evidence
Run on 2026-09-15 with `yt-dlp==2026.8.19` and `youtube-transcript-api==1.2.4` (see
`requirements.txt`). Script: `scripts/t002_youtube_captions.py`. Per-channel, the script
lists the latest 5 videos via `yt_dlp.YoutubeDL(extract_flat=False, playlistend=5)` against
`https://www.youtube.com/@<handle>/videos`, then calls
`YouTubeTranscriptApi().fetch(video_id)` for each. Raw output (video ids, titles, upload
dates, per-video success/error/language) is in `data/t002_youtube_captions.json`
(gitignored — not committed).

Result: 20/20 succeeded, all `language_code="en"`, all `is_generated=True`.

Latest upload date per channel at time of run:
- theAIsearch — 2026-09-15
- mreflow — 2026-09-11
- NateBJones — 2026-09-14
- ColeMedin — 2026-09-15

Separately confirmed the same `yt-dlp` call returns `title` and `description` for every
video (checked one sample: description 2018 characters) — the title+description fallback
has real data behind it even though no failure in this run exercised it.

## Consequences
The Phase 1 collector can plan on captions as the primary transcript source for these
channels, with title+description as a fallback that is available but currently untested
against a real caption failure. `docs/GOAL.md`'s Whisper non-goal condition ("unless
captions can't be fetched") is not triggered by this evidence.

## Confidence and limits
One run, one point in time, 20 videos across 4 channels — all channels the project actually
uses, which is what matters here, but still a small, non-adversarial sample. Not tested:
channels/videos with captions disabled, age-restricted or region-locked videos, non-English
content, or repeated runs over time (YouTube's caption availability and rate limiting can
vary). If a later channel or video fails, that failure is the first real test of the
title+description fallback — don't assume it works end-to-end until then.
