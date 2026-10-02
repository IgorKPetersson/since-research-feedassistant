# KB-023 — In live UI runs on 2026-09-24, retrieval took ~40–100s per question while generation took 9–17s; cause not established

**Area:** Local model (Ollama) — latency of the embedding step
**Status:** superseded by KB-024 — the observation was real, but the cause was not model
unloading: every request to `localhost` cost about 2 seconds, and retrieval makes ~30
**Date:** 2026-09-24  ·  **From:** T-045/T-046 screenshot runs / session 2026-09-24 § 11

## Claim
Across four live runs of the same question in the Streamlit UI, the pipeline strip sat
at "Candidates …" (retrieval not finished) for roughly 40–100s, then generation took
8.8–17.2s (the UI's own "Time" tile). Retrieval embeds one short question with `bge-m3`
and queries Chroma, which should take seconds. At one point during a stuck retrieval,
Ollama's `/api/ps` listed **only** `qwen3:30b-a3b` (20.07GB, `size_vram` = full size),
with `bge-m3` not loaded.

## Evidence
- Timings come from Playwright polling (click time vs. when the Candidates tile filled
  in), so they're approximate, ±10s. Runs at 18:08, 18:11, 18:13 and 20:41 local time.
- `/api/ps` read once, around 18:10, while the first run was still retrieving.
- Ollama version 0.34.4 (`/api/version`). README says tested against 0.34.0.

## Consequences
Not acted on. If first-question latency matters for the report or the demo, measure it
properly first: time `embed_batch()` alone, check `/api/ps` before and after, and try
an explicit `keep_alive` on both models. Don't assume KB-007's "both fit at once" means
both *stay* loaded.

## Confidence and limits
Observed on one day, on one machine, with approximate timings. The cause is unknown:
candidates include Ollama unloading `bge-m3` to load the 20GB chat model and reloading
it per question, a first-use slowdown after an Ollama upgrade, or something unrelated.
Earlier sessions' UI runs weren't timed this way, so there's no baseline to compare
against.
