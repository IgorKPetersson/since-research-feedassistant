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
- Vector store (ChromaDB) — embedded local store, date-range filtering

## Entries

| ID | Claim | Area | Status | Date |
|---|---|---|---|---|
| [KB-001](KB-001-youtube-caption-availability.md) | Auto-generated English captions available for all 20 sampled videos across the 4 chosen channels | YouTube ingest — captions | provisional | 2026-09-15 |
| [KB-002](KB-002-hf-daily-papers-shape.md) | HF Daily Papers returns 200 with an empty list on weekends; arXiv id is at `paper.id`; `publishedAt` ≠ the date `date=` matched on (`paper.submittedOnDailyAt` is) | HF Daily Papers API | provisional | 2026-09-15 |
| [KB-003](KB-003-ollama-vram-and-timing.md) | qwen2.5:32b doesn't fit entirely in 24GB VRAM at default context (80/20 GPU/CPU split); cold-start timing is misleading; the two models don't comfortably co-reside | Local model (Ollama) | provisional | 2026-09-15 |
| [KB-004](KB-004-chromadb-date-filtering.md) | ChromaDB's `where` filter combined with similarity search correctly restricts by feed-date range; default embedding model is a silent ~80MB first-use download outside the project | Vector store (ChromaDB) | provisional | 2026-09-15 |
| [KB-005](KB-005-ollama-num-ctx-silent-truncation.md) | Ollama's default num_ctx is 32768, not the model's trained max; content beyond num_ctx is silently dropped from the front, no error | Local model (Ollama) — context window | verified | 2026-09-15 |
| [KB-006](KB-006-chroma-default-embedder-256-token-limit.md) | Chroma's default embedder silently truncates at 256 tokens; its own "too long" error can never fire | Vector store (ChromaDB) — default embedding model | verified | 2026-09-15 |
| [KB-007](KB-007-qwen3-bge-m3-stack.md) | qwen3:30b-a3b (16k ctx) + bge-m3 both run 100% GPU simultaneously; `think:false` doesn't suppress reasoning, just merges it into the answer field | Local model (Ollama) — model stack | verified | 2026-09-15 |
| [KB-008](KB-008-youtube-ip-blocked-one-day-later.md) | Same machine went from 20/20 caption successes to 100% `IpBlocked` one day later — first real trigger of the D-001 fallback, and the exact signal T-015's backfill must stop and report on | YouTube ingest — captions | provisional | 2026-09-16 |

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
