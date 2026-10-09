# KB-041 — yt-dlp returns a shortened channel listing when a page comes back incomplete

**Area:** YouTube ingest — channel listing
**Status:** verified (in yt-dlp's source; not seen happen in a real run)
**Date:** 2026-10-09  ·  **From:** T-091

## Claim
When YouTube returns an incomplete continuation page while yt-dlp lists a channel, yt-dlp
retries and then, by default, only warns ("Incomplete data received") and stops. The
listing it returns is shorter than the channel really is, with no error. A short listing
then looks the same as a small channel. The extractor argument `raise_incomplete_data`
turns the warning into an error.

## Evidence
- `yt_dlp/extractor/youtube/_base.py`, `_extract_response()`: "Incomplete Data should be
  a warning by default when retries are exhausted, while other errors should be fatal."
  The retry manager is fatal only when `raise_incomplete_data` is set; otherwise the
  function returns `None` and the tab extractor stops paging.
- The argument is read with `ie_key='youtube'`, so it is passed as
  `extractor_args={"youtube": {"raise_incomplete_data": ["true"]}}`.
- `tests/test_youtube_backfill.py::ListVideoIdsTests` checks the option is sent.

## Consequence for this project
`vg09.youtube.list_video_ids()` sets the argument (T-091). A broken page now fails the
channel's check, which keeps its interval for the next run. A listing shorter than asked
for can then be read as the whole channel. Not verified against a real incomplete page:
YouTube can't be made to send one on demand.
