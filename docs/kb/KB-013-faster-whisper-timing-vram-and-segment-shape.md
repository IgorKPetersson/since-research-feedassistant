# KB-013 — faster-whisper (small, GPU) transcribes a 30-minute video in ~40s at ~1.1GB VRAM, but its segment shape isn't `youtube_transcript_api`'s

**Area:** Local model (faster-whisper) — timing, VRAM, output shape
**Status:** provisional (one video, one model size, isolated from Ollama)
**Date:** 2026-09-17  ·  **From:** T-018

## Claim
`faster-whisper`'s `small` model, `float16`, on the RTX 4090, transcribed a real 1848-second
(30.8 min) YouTube video's downloaded audio in 39.7 seconds of wall-clock transcription time
(model load: 1.0s, measured separately) - roughly 46x real-time. Peak VRAM during
transcription was ~4536 MiB against a ~3390-3400 MiB baseline (no Ollama models loaded at
the time) - call it **~1.1-1.15 GB** for the Whisper model itself at this size/precision.
Its segment shape is `{text, start, end}` (both floats, seconds), not
`youtube_transcript_api`'s `{text, start, duration}` that `vg09/document.py`'s `segments`
field (D-007) and `vg09/chunking.py` currently expect.

## Evidence
`scripts/t018_whisper_feasibility.py`, run against `YTG0rdHPTDE` (downloaded via `yt-dlp`,
`bestaudio` format, no post-processing, no `ffmpeg` re-encode - `faster-whisper`/PyAV decoded
the native `.webm` audio directly). Real GPU run (KB-012's `PATH` fix applied), not CPU
fallback - confirmed by `device="cuda"` succeeding rather than raising. VRAM measured via
`nvidia-smi --query-gpu=memory.used` polled every 2s across the whole run; `ollama ps`
confirmed empty (no chat/embedding models resident) immediately before starting, so this is
Whisper's footprint **in isolation**, not measured alongside `qwen3:30b-a3b` + `bge-m3`
(D-005's ~2.4GB headroom at `num_ctx=16000`) - ~1.1GB would fit inside that headroom on
paper, but this has not been verified with all three loaded together.

First 3 real segments returned by `model.transcribe(...)`:
```
Segment(start=0.0, end=4.52, text=" We didn't change anything in the product and all of a sudden just like went vertical.")
Segment(start=4.52, end=6.24, text=" And it was because the agents had found it.")
Segment(start=6.24, end=11.08, text=" In that world, how do we scale trust?")
```
546 segments total for the full video. Compare a real `youtube_transcript_api` snippet
(`data/raw/youtube/2026-09-16/S2VJU5DQqlU.json`):
```
{"text": "What if anybody could have the power of", "start": 0.08, "duration": 4.16}
{"text": "Palunteer on their home computer? That's", "start": 1.68, "duration": 4.24}
```
Note the auto-caption snippets *overlap* (the second starts at 1.68s, inside the first
snippet's 0.08-4.24s span) - they are short phrase fragments, not sequential sentences.
Whisper's segments are full sentences, non-overlapping, and roughly 2-19s each in this
sample - coarser-grained but semantically coherent, versus auto-captions' ~4s fragments.

## Consequences
Converting a Whisper segment to the schema `vg09/document.py`'s `segments` field expects is
a trivial `duration = end - start` per segment - no blocker there. But `vg09/chunking.py`'s
`chunk_youtube_document()` was built assuming auto-caption-shaped short, punctuation-free
fragments (see KB-014 - that "no punctuation" premise is itself now contradicted by real
data); Whisper's longer, complete, punctuated sentences are a different enough shape that
the chunking function should be re-examined against real Whisper segments before this path
is wired into the collector, not assumed to work unchanged just because the field names can
be mapped.

VRAM-wise, nothing here blocks adopting Whisper for the channels KB-008's block is hitting -
~1.1GB is small next to D-005's headroom - but this needs a real joint-residency check (both
Ollama models loaded, then run Whisper) before relying on that, the same way D-005/KB-007
verified qwen3 + bge-m3 jointly rather than assuming it from separate numbers.

## Confidence and limits
One video, one model size (`small`), one precision (`float16`), one run, no repeated
measurement, no comparison against other Whisper model sizes (`base`, `medium`, `large-v3`)
which would trade speed/VRAM for accuracy. Not measured concurrently with Ollama models
loaded. English-language video only - no signal yet on Swedish or other non-English
transcription quality/timing with this model size.
