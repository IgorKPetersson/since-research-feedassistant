# KB-025 — On Windows, `os.replace()` onto a file another process has open raises `PermissionError`

**Area:** Windows file handling — a status file shared between two processes
**Status:** verified
**Date:** 2026-10-02  ·  **From:** T-055

## Claim
Writing a file atomically as "write a temporary file, then `os.replace()` it over the
real one" is not safe on Windows when another process reads the real file at intervals:
if the reader has it open at that instant, `os.replace()` raises
`PermissionError: [WinError 5] Access is denied`. On POSIX the same call succeeds.

## Evidence
The first real run of `vg09/ingest_job.py`, with a second process reading
`data/ingest_status.json` every two seconds: after about five minutes and several hundred
successful rewrites, the job logged `stage index failed: PermissionError(13, 'Åtkomst
nekad')` 980 passages into rebuilding the store, and died. Its last status still said
"running", and it was correctly reported as interrupted once its heartbeat went stale.
After adding a retry, two full runs driven from the app (which polls the same file
every two seconds) completed with no error.

## Consequences
`vg09.ingest_job._retrying()` wraps both the replace and the read, retrying
`PermissionError` every 50 ms for up to two seconds. The unit tests could not have found
this: they run in one process.

## Confidence and limits
One failure observed, then none in two runs with the retry. The collision window is
milliseconds wide, so "none in two runs" is weak evidence on its own; the retry is what
makes it safe, not the absence of a repeat.
