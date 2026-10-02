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
- Retrieval (`vg09.retrieval`, `vg09.date_range`) — measurement methodology
- Vector store (ChromaDB) — embedded local store, date-range filtering
- UI (Streamlit / markdown rendering) — rendering free-text into markdown safely
- UI (Streamlit) — theming and custom CSS injection
- UI — typeface (Google Fonts)

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
| [KB-008](KB-008-youtube-ip-blocked-one-day-later.md) | `IpBlocked`'s trigger is still unclear (volume/channel-scoping/intermittency all partially fit); a previously-clean channel later blocked, and `yt-dlp` audio download failed once too — D-009's 3-tier fallback makes this not matter for data collection | YouTube ingest — captions | provisional | 2026-09-16/17 |
| [KB-009](KB-009-ollama-num-predict-zero-is-not-zero.md) | `num_predict:0` does not mean "generate nothing" — produced 485 tokens on a 9-word prompt; use `num_predict:1` for a cheap tokenizer-count call instead | Local model (Ollama) — generation options | verified | 2026-09-16 |
| [KB-010](KB-010-patch-target-must-match-the-importing-module.md) | Patching `vg09.document.RAW_DIR` doesn't redirect `vg09.hf_papers`'s own imported copy of the name — silently deleted 4 real `_done.json` markers via an under-isolated test before being caught and repaired | Testing — `unittest.mock.patch` target selection | verified | 2026-09-16 |
| [KB-011](KB-011-ollama-chat-template-system-always-first.md) | Ollama's chat template renders the system message first regardless of its position in `messages` — message order doesn't control prompt order the way raw `/api/generate` string concatenation does | Local model (Ollama) — `/api/chat` message rendering | verified | 2026-09-16 |
| [KB-012](KB-012-ctranslate2-cuda-dll-needs-path-not-add-dll-directory.md) | ctranslate2's CUDA loading ignores `os.add_dll_directory()` on Windows — only a real `PATH` prepend of the pip-installed nvidia-cublas/cudnn wheels' `bin/` dirs works | Local model (faster-whisper) — CUDA setup on Windows | verified | 2026-09-17 |
| [KB-013](KB-013-faster-whisper-timing-vram-and-segment-shape.md) | faster-whisper `small`/GPU transcribed a 30.8-min video in 39.7s at ~1.1GB VRAM (isolated, not with Ollama loaded); segment shape is `{text, start, end}`, not `{text, start, duration}` | Local model (faster-whisper) — timing, VRAM, output shape | provisional | 2026-09-17 |
| [KB-014](KB-014-real-auto-captions-do-have-punctuation.md) | Real fetched auto-captions DO have punctuation/capitalization, contradicting `vg09/chunking.py`'s unverified "no punctuation" premise; real proper-noun garbling examples found ("Palunteer", "Open AAI", "Sunno V6") | YouTube ingest — captions | verified | 2026-09-17 |
| [KB-015](KB-015-whisper-fits-alongside-ollama-models.md) | faster-whisper fits alongside qwen3:30b-a3b + bge-m3 both loaded (D-005) — real peak 23646/24564 MiB, ~0.9GB headroom, neither Ollama model evicted | Local model (faster-whisper) — joint VRAM residency | verified | 2026-09-17 |
| [KB-016](KB-016-comparing-retrieval-measurements-needs-the-same-today-anchor.md) | Comparing two retrieval measurements (e.g. old vs. new chunk budget) needs the same `today` anchor for both, or the delta is meaningless — a real mixup produced a false "regression" | Retrieval — measurement methodology | verified | 2026-09-19 |
| [KB-017](KB-017-commonmark-link-text-only-needs-bracket-and-backslash-escaping.md) | A markdown `[text](url)` link's text portion only needs `[`, `]` and backslash escaped under CommonMark — parentheses inside `[text]` are safe unescaped, unlike inside `(url)` | UI (Streamlit / markdown rendering) | verified | 2026-09-20 |
| [KB-018](KB-018-packing-budget-undercounted-the-real-prompt-since-t008.md) | The chunk-packing budget measured only a chunk's bare text, never the real `"[N] Title (url, feed date)\n"` wrapper actually sent to the model — under-counted since T-008; real overhead measured at 41-83 tokens/chunk; F07 (T-031) was the first real question to tip over it | Retrieval — measurement methodology | verified | 2026-09-20 |
| [KB-019](KB-019-qwen3-reasoning-length-has-a-heavy-tail-across-samples.md) | `qwen3:30b-a3b`'s reasoning length varies up to ~1.6× between samples of the same prompt and reaches 2864 tokens (totals 3118); T-028's 3 samples of one question badly understated the tail — 5 of 32 probe runs exceeded 2542 | Local model behaviour — generation budget | verified | 2026-09-22 |
| [KB-020](KB-020-streamlit-top-level-theme-section-removes-the-theme-toggle.md) | A top-level `[theme]` in `.streamlit/config.toml` removes the viewer's Light/Dark toggle and ignores the OS preference; `[theme.light]` + `[theme.dark]` keep it | UI (Streamlit) — theming | verified | 2026-09-24 |
| [KB-021](KB-021-streamlit-custom-css-injection-gotchas.md) | Custom CSS loses to Streamlit's markdown font/link rules unless scoped under `[data-testid]` with `!important`; the broad selector breaks Material icons; `st.html()` strips `<link>` (use `@import`); `page_icon` takes an `.svg` path | UI (Streamlit) — custom CSS injection | verified | 2026-09-24 |
| [KB-022](KB-022-instrument-sans-heaviest-weight-is-700.md) | Instrument Sans on Google Fonts tops out at 700; `wght@800` returns HTTP 400 | UI — typeface (Google Fonts) | verified | 2026-09-24 |
| [KB-023](KB-023-ui-retrieval-took-40-100s-per-question-cause-unknown.md) | Live UI retrieval took ~40–100s per question vs 9–17s generation; `bge-m3` was seen unloaded; cause not established | Local model (Ollama) — embedding latency | superseded by KB-024 | 2026-09-24 |
| [KB-024](KB-024-localhost-costs-two-seconds-per-ollama-request-on-windows.md) | Addressing Ollama as `localhost` costs ~2s per request on Windows (IPv6 tried first, Ollama on IPv4 only); `127.0.0.1` does not — `retrieve()` 68.6s → 1.4s; every wall-clock time recorded before 2026-10-02 includes this overhead | Local model (Ollama) — request latency | verified | 2026-10-02 |
| [KB-025](KB-025-windows-refuses-to-replace-a-file-another-process-has-open.md) | On Windows, `os.replace()` onto a file another process has open raises `PermissionError` — killed the first real ingest job mid-run; writes and reads of the shared status file now retry | Windows file handling — status file shared by two processes | verified | 2026-10-02 |
| [KB-026](KB-026-chroma-client-goes-stale-when-another-process-writes-the-store.md) | A Chroma `PersistentClient` goes stale when another process writes the store: queries fail with "Error finding id" during and after the write while counts still look right; dropping the cached client fixes it without a restart | Vector store (ChromaDB) — one store, two processes | verified | 2026-10-02 |
| [KB-027](KB-027-first-question-after-a-whisper-update-hung-on-ollama-once.md) | The first question about a minute after an update that used Whisper waited 120s on Ollama once, then worked; cause not established | Local model (Ollama) — sharing the GPU with Whisper | provisional | 2026-10-02 |
| [KB-028](KB-028-whisper-cuda-libraries-must-be-found-in-the-running-interpreter.md) | If Whisper's CUDA libraries aren't on PATH the first transcription raises `RuntimeError` and the second hangs with no CPU or GPU activity; the lookup assumed `<repo>/.venv` and now uses the running interpreter's site-packages | Local model (faster-whisper) — CUDA setup on Windows | verified | 2026-10-02 |

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
