# DECISIONS

Append-only. Never edit a decision — supersede it with a new one and mark the old
`Superseded by D-0NN`.

Write entries as if someone who wasn't there will read them, because they will: a
maintainer, a reviewer, or you in four months.

Format: **what** was decided, **why**, **what was rejected**, **what would change our mind**.

---

## D-001 — Transcript source: captions first, title+description as fallback
**Status:** accepted

**Decision:** Phase 1 ingest uses YouTube captions (via `youtube-transcript-api`) as the
primary transcript source for a video, falling back to title + description (already
fetched via `yt-dlp` in the same call) when captions are unavailable.

**Why:** T-002 fetched captions for the latest 5 videos each of the 4 chosen channels
(20 videos) and got 20/20 successes, all auto-generated English captions — see
[KB-001](kb/KB-001-youtube-caption-availability.md). `docs/GOAL.md` only permits Whisper if
captions can't be fetched *and* time allows; this evidence doesn't trigger that condition,
so Whisper stays parked.

**Rejected:** Whisper transcription for every video — rejected because captions worked in
this sample and Whisper adds a GPU-time cost and a new dependency the evidence didn't
justify. Title+description as the *only* source — rejected because it's strictly weaker
than a real transcript and captions were available.

**Cost:** The fallback path (title+description) is real data but untested against an
actual caption failure (KB-001's "Confidence and limits"). If a channel later fails
captions in a way the fallback handles badly, that's a live risk, not a closed one.

**Would change our mind:** A chosen channel or a meaningful fraction of new videos
returning `TranscriptsDisabled` / `NoTranscriptFound` in a later run — at that point,
re-evaluate whether Whisper is worth adding for that channel.

---

## D-002 — "Publication date" means feed date; arXiv's own date is metadata only
**Status:** accepted

**Decision:** The date used for all date filtering and catch-up ingestion — what
`docs/GOAL.md` calls "publication date" — is the **feed date**: the date something
appeared in the source we watch. For HF Daily Papers that's `paper.submittedOnDailyAt`; for
YouTube it's the video's upload date. A paper's original arXiv `publishedAt` is stored as
extra metadata and shown in citations, but is never used for filtering or catch-up.

**Why:** T-003 found that HF Daily Papers' `date=` query parameter matches
`submittedOnDailyAt`, not `publishedAt` — the two can differ by several days (KB-002). The
HF daily selection includes papers already published on arXiv earlier, so filtering on
`publishedAt` would hide papers that just appeared in the feed — exactly the "what's new"
case the project exists to answer. Feed date is also the only date YouTube naturally has;
using two different date semantics per source would be worse than picking one that works
for both.

**Rejected:** Filtering on arXiv `publishedAt` for papers — rejected because it would
silently drop or misdate papers relative to when the user could actually have found them in
the feed, undermining "did anyone cover X this week" style questions. A per-source date
semantic (feed date for YouTube, arXiv date for papers) — rejected as needless complexity
for one shared retrieval/filtering path, and confusing for citations and evaluation
questions that span both sources.

**Cost:** A paper's citation shows two dates when they differ (feed date used for
retrieval, arXiv date shown alongside) — the UI and evaluation question set must display
both clearly enough that "when was this published" isn't ambiguous to the user.

**Would change our mind:** Evidence that questions like "has Q progressed in the last n
weeks" need the arXiv date instead (e.g. a user expects "last n weeks" to mean "written in
the last n weeks", not "appeared in the feed in the last n weeks") — that would need
re-opening this decision, not silently switching fields in code.

---

## D-003 — Model pair for evaluation: llama3.1:8b (small) and qwen2.5:32b (large)
**Status:** superseded by D-005

**Decision:** Use `llama3.1:8b` as the small model and `qwen2.5:32b` as the large model for
the large-vs-small evaluation in `docs/GOAL.md`, both at Ollama's default quantization and
settings for now.

**Why:** T-004 confirmed both run on the RTX 4090 via Ollama 0.34.0 and answer correctly
from pasted context (see KB-003). Both are widely used, well-documented model families,
which matters for a course project others may need to reproduce.

**Rejected:** No other model sizes/families were pulled or tested — this is the first pair
that fit the ~8B/~30B brief in `docs/PLAN.md`, not a comparison winner. Larger quantized
options (e.g. 70B-class) were not attempted given KB-003 already shows `qwen2.5:32b`
spilling onto CPU at 24GB; a bigger model would spill further and likely cost more in speed
than it buys in quality for this project's scope.

**Cost:** KB-003's findings are a real cost, not just a note: `qwen2.5:32b` runs 20% on CPU
at its default 32768 context (not fully GPU-resident), and the two models do not
comfortably co-reside in 24GB — switching between them for the large-vs-small evaluation
will pay a reload cost each time. If evaluation runtime becomes a problem, revisit
`num_ctx` for the large model before switching model choice.

**Would change our mind:** If Phase 2 answer generation needs materially faster large-model
latency than the ~19s warm response seen here, or if the reload cost between models makes
the evaluation script impractically slow — either would justify trying a smaller `num_ctx`,
a different quantization, or a different large model, and updating this decision with that
evidence.

---

## D-004 — Vector store: ChromaDB (embedded, no server)
**Status:** accepted

**Decision:** Use ChromaDB's embedded `PersistentClient` as the vector store for Phase 1,
storing feed date (D-002) as a numeric field (an ordinal or timestamp) for range filtering
alongside similarity search.

**Why:** T-005 confirmed ChromaDB combines a metadata range filter with similarity search
correctly — a query filtered to a feed-date range returned a strict, correctly-bounded
subset of the unfiltered results (KB-004). It runs fully local and embedded, satisfying
`docs/GOAL.md`'s non-goals (no Docker, no server, no always-on process).

**Rejected:** LanceDB and sqlite-vec were not tested — ChromaDB was chosen up front as the
most commonly used option for this kind of RAG setup, with the most available
documentation for a course project others may need to reproduce, and the first candidate
tried already met the bar. This is not a comparison result; if ChromaDB later proves
inadequate at real scale, LanceDB is the next candidate to try, not a rejected one.

**Cost:** ChromaDB's default embedding function is not bundled — it downloads an ~80MB
model to a user-level cache on first use (KB-004), outside the project and
`requirements.txt`. This must be called out in the README (`docs/GOAL.md`'s "fresh clone
reaches a first answer" criterion needs network access for this, not just for model APIs),
and is a one-time cost per machine, not a recurring one.

**Would change our mind:** Filtering or query performance degrading unacceptably at
realistic document counts (hundreds to thousands of chunks) — untested here, only a
hand-built 8-document collection.

---

## D-005 — Model stack: qwen3:8b + qwen3:30b-a3b (VRAM-differentiated, same family) + bge-m3 embedding
**Status:** accepted

**Decision:** Replace D-003's pair with `qwen3:8b` and `qwen3:30b-a3b`, both from the same
family, run at an explicit `num_ctx=16000`. Use `bge-m3` as the embedding model instead of
ChromaDB's silent default (D-004's "Cost" section — the default embedder itself is
unchanged as the store decision, but the embedding *model* is now a deliberate choice, not
an inherited default). The two chat models are described by **VRAM footprint** (~6GB vs
~20GB), not "small vs large" — `qwen3:30b-a3b` is MoE with far fewer active parameters per
token than the dense `qwen3:8b`, so calling it "large" is misleading about compute cost
even though its VRAM footprint is bigger.

**Why:** T-004's pair (`llama3.1:8b` + `qwen2.5:32b`) mixed families, confounding size with
family in the planned evaluation, and `qwen2.5:32b` didn't fit 24GB VRAM at its default
context (KB-003). T-006 confirmed `qwen3:30b-a3b` at `num_ctx=16000` **and** `bge-m3`
loaded simultaneously both run 100% GPU with ~2.4GB headroom to spare (KB-007) — the bar
D-003 never met. `bge-m3` also fixes KB-006's 256-token silent-truncation ceiling (its own
context window is 8192) and is genuinely multilingual, confirmed by a correct Swedish-query
retrieval against English text (KB-007) — relevant to `docs/GOAL.md`'s known limitation
that Swedish questions may retrieve worse than English ones.

**Rejected:** Gemma3 (27b + 4b) — same-family but not MoE, and the jump from 4b to 27b is
bigger than Qwen3's 8b→30b-a3b, with no evidence it would fit 24GB any better than
`qwen2.5:32b` did. The `qwen2.5:14b` + `qwen2.5:7b` fallback named in the ticket was not
needed since `qwen3` cleared the VRAM bar on the first attempt.

**Cost:** `qwen3:30b-a3b`'s reasoning (`think`) mode adds real latency and cannot be cleanly
disabled — `think:false` does not suppress the model's chain-of-thought, it only merges it
into the `response` field instead of separating it into `thinking` (KB-007). Getting a
clean final-answer-only string requires `think:true` and reading only `response`, at
whatever latency cost that carries (one sample here: 10.4s vs 7.7s for the same question -
not a reliable benchmark, just a directional cost to plan around). `bge-m3`'s retrieval
quality was checked on one illustrative example, not the project's real evaluation
questions.

**Would change our mind:** VRAM headroom (~2.4GB) proving too tight once real document
chunks and longer conversations grow the KV cache beyond this test's single-question probe
— `num_ctx=16000` is a ceiling, not measured live usage. If that happens, the next lever is
a smaller `num_ctx` before changing model choice again.

---

## D-0NN — <template>
**Status:** proposed | accepted | superseded by D-0NN

**Decision:**
**Why:**
**Rejected:**
**Cost:**
**Would change our mind:**
