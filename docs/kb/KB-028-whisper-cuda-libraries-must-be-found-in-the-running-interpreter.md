# KB-028 — If Whisper's CUDA libraries aren't on PATH, the first transcription raises `RuntimeError` and the second hangs with no CPU or GPU activity

**Area:** Local model (faster-whisper) — CUDA setup on Windows
**Status:** verified
**Date:** 2026-10-02  ·  **From:** T-057

## Claim
KB-012's PATH prepend for ctranslate2 looked for the nvidia wheels under
`<repo>/.venv/Lib/site-packages`. With the virtual environment anywhere else, nothing was
prepended. The first `fetch_whisper_transcript()` then raised `RuntimeError` (and the
video fell back to title and description, as designed), but the second call did not
fail: it hung indefinitely, with the process using no CPU and the GPU at 3%.

## Evidence
The app run from a clone with no `.venv` of its own, using another folder's
interpreter. Job log: `Whisper also failed for dDgncbBAA0c (RuntimeError) - falling back
to title+description`, then for the next video the audio downloaded and nothing more for
nine minutes. The job's heartbeat kept beating, so it was reported as running, not
interrupted. After the fix, the same test from a new clone transcribed both videos
(`text_source: whisper`) and finished in 121s.

## Consequences
- `vg09.youtube._add_whisper_cuda_dll_dirs()` takes site-packages from
  `sysconfig.get_paths()`, the running interpreter's own.
- One `RuntimeError` from loading or running the model sets `_whisper_failed`; later
  videos in the same process raise at once, before downloading audio, and go to
  title and description.
- A hung transcription is not detected by the job's heartbeat, which only proves the
  process is alive. There is no timeout on a single transcription.

## Confidence and limits
Seen once, fixed, and the fixed path run once. Why the second call hangs instead of
raising was not investigated. On a machine with no CUDA wheels at all, the same
first-fails-then-skips behaviour is expected but was not run.
