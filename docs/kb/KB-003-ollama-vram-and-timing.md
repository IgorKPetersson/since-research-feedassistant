# KB-003 — qwen2.5:32b does not fit entirely in 24GB VRAM at its default context length, and single-model cold-start timing is misleading

**Area:** Local model (Ollama) on the RTX 4090
**Status:** provisional
**Date:** 2026-09-15  ·  **From:** T-004

## Claim
Both `llama3.1:8b` (small, ~8B) and `qwen2.5:32b` (large, ~30B class) run via Ollama 0.34.0
and answer correctly from pasted context. But two things are easy to get wrong from a
single naive run: (1) a cold-start timing comparison can rank the models backwards, and
(2) `qwen2.5:32b` does not actually fit entirely in the RTX 4090's 24GB VRAM at its default
context length — Ollama silently splits it 80% GPU / 20% CPU.

## Evidence
Run on 2026-09-15, Ollama 0.34.0, RTX 4090 (24564 MiB VRAM per `nvidia-smi`, ~2.3GB already
in use by other running apps as a baseline). Both models pulled at default quantization:
`llama3.1:8b` (4.9GB on disk), `qwen2.5:32b` (19GB on disk). Script:
`scripts/t004_local_model.py`, one question with pasted context sent to each model via
`POST /api/generate` (stream=false), GPU memory polled every 0.5s during each call via
`nvidia-smi --query-gpu=memory.used`.

**Cold run (models just pulled, calling each for the first time):**

| Model | Time | Peak GPU mem (total, see caveat) |
|---|---|---|
| llama3.1:8b | 35.0s | 11.5 GB |
| qwen2.5:32b | 27.4s | 24.0 GB |

Taken at face value this says the large model is faster than the small one, which is
implausible. A second, warm run immediately after (models already loaded) gave the real
picture:

**Warm run (same session, models already loaded once):**

| Model | Time | Peak GPU mem (total, see caveat) |
|---|---|---|
| llama3.1:8b | 5.9s | 24.0 GB |
| qwen2.5:32b | 18.9s | 23.9 GB |

The small model's 35.0s cold time was almost entirely one-time disk-load overhead (5.9s of
it was actual inference); the large model's cold time looked artificially competitive by
comparison. **A single untimed cold call is not a valid speed comparison between models.**

Both answers were correct in both runs (correctly named `paper.submittedOnDailyAt` and
`paper.id` from the pasted context).

`ollama ps`, checked after these runs, showed:
```
NAME           SIZE    PROCESSOR          CONTEXT   UNTIL
qwen2.5:32b    28 GB   20%/80% CPU/GPU    32768     4 minutes from now
```
`llama3.1:8b` was no longer listed at all, well before its 5-minute `keep_alive` should
have expired — it appears to have been evicted to make room for `qwen2.5:32b`.

## Consequences
- **GPU memory readings in the table above are not per-model.** `nvidia-smi
  memory.used` is total GPU memory, and once a second model starts loading, the first
  model's memory can still be counted (or, as seen here, the first model gets evicted
  mid-measurement). The only clean single-model reading in this run was the very first
  cold call, before anything else was loaded (small model: ~9GB above the ~2.3GB
  baseline). Any future VRAM measurement needs `ollama ps` (which reports per-model size
  and CPU/GPU split) as the source of truth, not `nvidia-smi` alone.
- **`qwen2.5:32b` at its default 32768-token context does not fit in 24GB** — Ollama's own
  scheduler puts 20% of it on CPU. This is silent: neither the response quality nor the
  wall-clock time (18.9s warm) obviously signals that part of the model is running off the
  GPU. If Phase 2 needs faster large-model inference, a smaller `num_ctx` or a smaller/more
  aggressively quantized model should be tried and compared, rather than assuming "warm and
  answering correctly" means "fully on GPU."
- **The two models don't comfortably co-reside.** Running the large model appears to evict
  the small one. The planned evaluation (date-aware vs plain retrieval, large vs small
  model) will pay a model-reload cost every time it switches between them — worth
  accounting for in the evaluation script's expected runtime, not treated as a bug if it
  shows up there.

## Confidence and limits
One machine, one Ollama version, one run each of cold/warm, one question. Not tested:
repeated timing runs for variance, other quantization levels, a smaller `num_ctx` for the
large model, or behavior under concurrent requests. The "evicted" claim about
`llama3.1:8b` is inferred from it disappearing from `ollama ps` earlier than its
`keep_alive` window — plausible given Ollama's documented VRAM-based scheduling, but not
confirmed by reading Ollama's scheduler logs directly.
