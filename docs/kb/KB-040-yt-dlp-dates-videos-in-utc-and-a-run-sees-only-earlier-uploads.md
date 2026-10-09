# KB-040 — yt-dlp dates a video in UTC, and a run only sees what was uploaded before it

**Area:** YouTube ingest — catch-up window
**Status:** verified
**Date:** 2026-10-09  ·  **From:** T-090

## Claim
1. yt-dlp's `upload_date` is a UTC date (`YYYYMMDD`). The ingest job's "today" is the
   local date. In Sweden, local time runs one or two hours ahead of UTC, so just after
   local midnight a new video still carries the previous day's date.
2. A run marks the YouTube watermark with its own date. Before T-090 the next catch-up
   started the day after it, so any video uploaded later that same day was never listed
   again and was lost for good. The app updates once a day on opening (D-018), which
   made this the normal case, not an edge case.
3. A channel's listing is in publication order, and `_list_channel()` stops at the first
   unknown video dated before the window. If a later-listed video carries an older date,
   the walk stops there and in-window videos below it are not reached. Fixed by T-091,
   which walks the whole listing (D-021).

## Evidence
- `yt_dlp/extractor/common.py` in the installed version: "upload_date: Video upload date
  in UTC (YYYYMMDD)."
- 2026-10-09 20:20, a read-only listing of the five configured channels after that day's
  16:01 update: three videos dated 2026-10-08 and 2026-10-09 were not on disk. The old
  start (watermark + 1 day = 2026-10-10) excluded all three. The new two-day recheck
  fetched all three (Whisper tier), and a second run fetched nothing.
- `tests/test_youtube_backfill.py::LateUploadRecheckTests` reproduces claims 1 and 2;
  the test for the window's bound hit claim 3 by accident when it published an older
  date after a newer one.

## Consequence for this project
YouTube catch-up starts at `catch_up_start(watermark)`: the watermark day and the day
before it (`RECHECK_DAYS = 2`). Videos already on disk cost nothing to recheck. A video
dated more than a day before the watermark that appears later is still missed, and so
is one hidden behind an out-of-order listing entry (claim 3). T-093 owns the timezone
policy; claim 3 is a candidate for T-091.
