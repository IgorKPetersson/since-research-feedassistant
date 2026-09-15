# KB-007 — qwen3:30b-a3b (16k ctx) and bge-m3 both run 100% GPU simultaneously; Ollama's `think:false` doesn't suppress reasoning, it just merges it into the answer field

**Area:** Local model (Ollama) — model stack (chat pair + embedding)
**Status:** verified
**Date:** 2026-09-15  ·  **From:** T-006

## Claim
`qwen3:30b-a3b` at an explicit `num_ctx=16000` and `bge-m3` can be loaded on the RTX 4090
at the same time with **both** at 100% GPU — no CPU spillover for either, unlike
`qwen2.5:32b` in KB-003. The real axis distinguishing this chat pair is VRAM footprint
(~6GB vs ~20GB), not "large vs small" — `qwen3:30b-a3b` is MoE with far fewer active
parameters per token than the dense `qwen3:8b`. Separately: passing `think:false` to
`/api/generate` does not suppress Qwen3's chain-of-thought, it only stops Ollama from
separating it into the dedicated `thinking` field — the reasoning text still comes out,
merged into `response`. Cross-lingual retrieval via `bge-m3` works: a Swedish query
correctly ranked the right English sentence highest among unrelated ones.

## Evidence
Ollama 0.34.0, RTX 4090. Scripts: `scripts/t006_needle_test.py`, `scripts/t006_model_stack.py`.

**VRAM fit**, `ollama ps` after loading both:
```
NAME             SIZE     PROCESSOR    CONTEXT
bge-m3:latest    664 MB   100% GPU     8192
qwen3:30b-a3b    20 GB    100% GPU     16000
```
`nvidia-smi`: 22100-22118 MiB used / 24564 MiB total (~2.4GB headroom), measured both
before and after a real generation call (not just a trivial probe) — stable.

**`think` parameter**, same question ("What causes rain?") to `qwen3:30b-a3b`:

| | `think:true` (default) | `think:false` |
|---|---|---|
| Time | 10.4s | 7.7s |
| `eval_count` | 1591 tokens | 1259 tokens |
| `thinking` field | 4087 chars of reasoning | empty |
| `response` field | 2873 chars, final answer only | 5329 chars, **reasoning narrative merged in** (starts "Okay, the user is asking... Hmm, this seems like...") |

**Cross-lingual retrieval**: Swedish query `"Vad orsakar regn?"` ("What causes rain?")
embedded via `bge-m3`, compared by cosine similarity against 4 English sentences (rain,
stock market, cats, an ML paper). Ranking: rain sentence `0.6810`, stock market `0.3821`,
cats `0.3409`, ML paper `0.2965` — correct sentence clearly first.

## Consequences
This stack (KB-007) plus KB-005 (num_ctx) and KB-006 (Chroma's default embedder's 256-token
limit — `bge-m3` should be used instead, since it comfortably shares the GPU and supports a
much longer 8192-token input) together replace T-004/D-003's pair for the project going
forward — see D-005. **Do not rely on `think:false` for a clean answer string** — if the
project ever wants a final-answer-only output from Qwen3, the correct approach is
`think:true` (default) and reading only the `response` field, not `think:false`; the latter
would need the reasoning narrative stripped out of `response` some other way, which wasn't
attempted here. The `~35%` time difference between the two think modes is one sample and
should not be treated as a reliable benchmark number.

## Confidence and limits
One machine, one run of each configuration, one question for the think-mode comparison, one
query for the cross-lingual test. Not tested: `qwen3:8b`'s own behavior with `think`,
whether the VRAM headroom holds under a longer real conversation (KV cache grows with
actual usage, not just the allocated `num_ctx` buffer size — 16000 is the ceiling, not the
live usage), or `bge-m3`'s accuracy on the project's real evaluation questions rather than
one illustrative example.
