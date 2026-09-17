# Knowledge base — index

What this project knows about **the world**: verified behaviour, measurements, dead ends,
workarounds and constraints. Decisions live in `docs/DECISIONS.md`; design intent lives in
`docs/DESIGN.md`; session narrative lives in `docs/HANDOFF.md` and `docs/sessions/`.

Written and read via the `kb-entry` skill. **Read the relevant area before starting work in
it.** An entry not listed here does not exist, because nobody browses directories.

Entries are `docs/kb/KB-0NN-slug.md`. IDs sequential, never reused. A wrong entry is never
edited in place — it is superseded by a new one and marked.

## Areas

- YouTube ingest — fetching channel video lists and captions
- HF Daily Papers API — fetching and shape of the papers feed
- Local model (Ollama) — running models on the RTX 4090
- Local model (faster-whisper) — GPU audio transcription, CUDA setup on Windows
- Vector store (ChromaDB) — embedded local store, date-range filtering

## Entries

| ID | Claim | Area | Status | Date |
|---|---|---|---|---|
| [KB-001](KB-001-youtube-caption-availability.md) | Auto-generated English captions available for all 20 sampled videos across the 4 chosen channels | YouTube ingest — captions | provisional | 2026-09-15 |
| [KB-002](KB-002-hf-daily-papers-shape.md) | HF Daily Papers returns 200 with an empty list on weekends; arXiv id is at `paper.id`; `publishedAt` ≠ the date `date=` matched on (`paper.submittedOnDailyAt` is) | HF Daily Papers API | verified | 2026-09-15/16 |
| [KB-003](KB-003-ollama-vram-and-timing.md) | qwen2.5:32b doesn't fit entirely in 24GB VRAM at default context (80/20 GPU/CPU split); cold-start timing is misleading; the two models don't comfortably co-reside | Local model (Ollama) | provisional | 2026-09-15 |
| [KB-004](KB-004-chromadb-date-filtering.md) | ChromaDB's `where` filter combined with similarity search correctly restricts by feed-date range; default embedding model is a silent ~80MB first-use download outside the project | Vector store (ChromaDB) | provisional | 2026-09-15 |
| [KB-005](KB-005-ollama-num-ctx-silent-truncation.md) | Ollama's default num_ctx is 32768, not the model's trained max; content beyond num_ctx is silently dropped from the front, no error | Local model (Ollama) — context window | verified | 2026-09-15 |
| [KB-006](KB-006-chroma-default-embedder-256-token-limit.md) | Chroma's default embedder silently truncates at 256 tokens; its own "too long" error can never fire | Vector store (ChromaDB) — default embedding model | verified | 2026-09-15 |
| [KB-007](KB-007-qwen3-bge-m3-stack.md) | qwen3:30b-a3b (16k ctx) + bge-m3 both run 100% GPU simultaneously; `think:false` doesn't suppress reasoning, just merges it into the answer field | Local model (Ollama) — model stack | verified | 2026-09-15 |
| [KB-008](KB-008-youtube-ip-blocked-one-day-later.md) | `IpBlocked` cleared (1051 real snippets on manual re-check), then recurred after 17 consecutive real successes in T-017's real paced run — volume- or channel-novelty-triggered, not yet distinguished | YouTube ingest — captions | provisional | 2026-09-16/17 |
| [KB-009](KB-009-ollama-num-predict-zero-is-not-zero.md) | `num_predict:0` does not mean "generate nothing" — produced 485 tokens on a 9-word prompt; use `num_predict:1` for a cheap tokenizer-count call instead | Local model (Ollama) — generation options | verified | 2026-09-16 |
| [KB-010](KB-010-patch-target-must-match-the-importing-module.md) | Patching `vg09.document.RAW_DIR` doesn't redirect `vg09.hf_papers`'s own imported copy of the name — silently deleted 4 real `_done.json` markers via an under-isolated test before being caught and repaired | Testing — `unittest.mock.patch` target selection | verified | 2026-09-16 |
| [KB-011](KB-011-ollama-chat-template-system-always-first.md) | Ollama's chat template renders the system message first regardless of its position in `messages` — message order doesn't control prompt order the way raw `/api/generate` string concatenation does | Local model (Ollama) — `/api/chat` message rendering | verified | 2026-09-16 |
| [KB-012](KB-012-ctranslate2-cuda-dll-needs-path-not-add-dll-directory.md) | ctranslate2's CUDA loading ignores `os.add_dll_directory()` on Windows — only a real `PATH` prepend of the pip-installed nvidia-cublas/cudnn wheels' `bin/` dirs works | Local model (faster-whisper) — CUDA setup on Windows | verified | 2026-09-17 |
| [KB-013](KB-013-faster-whisper-timing-vram-and-segment-shape.md) | faster-whisper `small`/GPU transcribed a 30.8-min video in 39.7s at ~1.1GB VRAM (isolated, not with Ollama loaded); segment shape is `{text, start, end}`, not `{text, start, duration}` | Local model (faster-whisper) — timing, VRAM, output shape | provisional | 2026-09-17 |
| [KB-014](KB-014-real-auto-captions-do-have-punctuation.md) | Real fetched auto-captions DO have punctuation/capitalization, contradicting `vg09/chunking.py`'s unverified "no punctuation" premise; real proper-noun garbling examples found ("Palunteer", "Open AAI", "Sunno V6") | YouTube ingest — captions | verified | 2026-09-17 |

_One row per entry, newest at the bottom, added in the same commit as the entry itself._

## What belongs here

- Verified behaviour that contradicts documentation — always write it
- A measurement, with numbers and conditions
- A dead end and the reason it failed
- A non-obvious workaround, its cost, and what would let us drop it
- A platform, licence, quota or library constraint discovered the hard way

## What does not

- Vendor documentation that behaved as documented — link instead of copying
- Our decisions → `DECISIONS.md`
- Session narrative → `HANDOFF.md`, `sessions/`
- Design intent → `DESIGN.md`
