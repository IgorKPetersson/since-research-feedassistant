# KB-027 — The first question about a minute after an update that used Whisper waited 120s on Ollama once; cause not established

**Area:** Local model (Ollama) — sharing the GPU with Whisper
**Status:** provisional
**Date:** 2026-10-02  ·  **From:** T-056

## Claim
After an in-app update that transcribed one video with Whisper, the first question,
asked about a minute after the job finished, got through embedding and the Chroma query
and then waited on a token-count call until its 120-second timeout; the app showed
"Ollama isn't responding". The same question about a minute later answered in 7 seconds.

## Evidence
Seen once, in the browser run for T-056. Right afterwards, from a fresh process,
`scripts/t049_time_retrieval_steps.py` found only `qwen3:30b-a3b` loaded (`bge-m3` had
been unloaded), loaded `bge-m3` in 1.3s, and completed a whole retrieval in 2.1s.

## Consequences
None acted on. KB-015 found Whisper fits beside both Ollama models, but that was measured
with all three resident, not with a model being reloaded after the Whisper process exits.
If it recurs, check `/api/ps` before and after the Whisper stage, and consider a warm-up
call to both models at the end of the job.

## Confidence and limits
One observation, not reproduced, and the cause is a guess. It may be unrelated to Whisper.
