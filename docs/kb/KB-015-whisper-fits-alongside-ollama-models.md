# KB-015 — faster-whisper fits alongside qwen3:30b-a3b + bge-m3, resident together, with real headroom to spare

**Area:** Local model (faster-whisper) — joint VRAM residency with Ollama
**Status:** verified
**Date:** 2026-09-17  ·  **From:** T-019

## Claim
With `qwen3:30b-a3b` (`num_ctx=16000`) and `bge-m3` both loaded and 100% GPU-resident via
Ollama (D-005's pair), running `faster-whisper` (`small`, `float16`, GPU) transcription
alongside them does **not** evict either model and does **not** run out of VRAM. Real peak
usage: 23646 MiB out of 24564 MiB total — **~918 MiB (~0.9 GB) of headroom remaining** at the
busiest moment. This resolves the gap KB-013 explicitly flagged (its VRAM number was
measured with Ollama idle, not loaded).

## Evidence
`scripts/t019_joint_vram_test.py`: loaded `qwen3:30b-a3b` and `bge-m3` via real Ollama calls
first (confirmed via `ollama ps`: both 100% GPU, matching D-005/KB-007's own setup), baseline
VRAM at that point 23190 MiB. Then loaded and ran `faster-whisper` against the same real
audio file T-018 already downloaded (`YTG0rdHPTDE.webm`, no re-download) - transcription
succeeded in 41.8s (546 segments, consistent with KB-013's earlier isolated 39.7s). VRAM
polled every 1s throughout via `nvidia-smi`; peak 23646 MiB. `ollama ps` immediately
afterward still showed both models 100% GPU-resident with time remaining on their keep-alive
- neither was evicted to make room.

Interesting secondary observation: Whisper's VRAM delta here (~456 MiB, 23190→23646) was
smaller than KB-013's isolated measurement (~1.1-1.15 GB, no Ollama loaded). Not
investigated further - plausibly shared CUDA context/driver overhead already paid for by the
Ollama process, or measurement noise between runs. Either reading is consistent with
"it fits."

## Consequences
T-019's Whisper integration into `vg09/youtube.py` can hold the `WhisperModel` resident for
an entire backfill run (loading it once, reusing it across every video needing the Whisper
path) rather than loading and releasing it per-video - there's real, measured headroom for
this on the reference machine (RTX 4090, 24GB), even in the worst case where the large chat
model and the embedding model are both already loaded. The per-video load/unload fallback
design named as a contingency in T-019's ticket is not needed on this machine.

## Confidence and limits
One run, one video, one machine, this specific model trio at these specific
sizes/quantizations. ~0.9 GB headroom is real but not large - a bigger Whisper model size
(`medium`/`large-v3`, not tested), a longer or higher-resolution audio file, or future growth
in the chat models' `num_ctx` could close this gap. If VRAM errors ever appear during a real
Whisper-path backfill run, this is the first budget to re-check, and the per-video
load/unload fallback becomes the real answer rather than a documented-but-unused option.
