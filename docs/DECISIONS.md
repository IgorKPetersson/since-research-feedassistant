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
**Status:** accepted

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

## D-0NN — <template>
**Status:** proposed | accepted | superseded by D-0NN

**Decision:**
**Why:**
**Rejected:**
**Cost:**
**Would change our mind:**
