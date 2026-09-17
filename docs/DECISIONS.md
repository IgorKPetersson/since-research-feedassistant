# DECISIONS

Append-only. Never edit a decision — supersede it with a new one and mark the old
`Superseded by D-0NN`.

Write entries as if someone who wasn't there will read them, because they will: a
maintainer, a reviewer, or you in four months.

Format: **what** was decided, **why**, **what was rejected**, **what would change our mind**.

---

## D-001 — Transcript source: captions first, title+description as fallback
**Status:** Superseded by D-006 (fallback still stands; D-006 splits *why* it fires)

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

## D-006 — YouTube fallback splits "captions missing" from "blocked"; only missing falls back
**Status:** accepted

**Decision:** Supersedes D-001's undifferentiated fallback. The YouTube collector now
treats a caption-fetch failure one of two ways, based on its exception type:

- **Missing** — `TranscriptsDisabled`, `NoTranscriptFound`, and anything else under
  `CouldNotRetrieveTranscript` that isn't `RequestBlocked` — a per-video signal that this
  specific video has no captions. Falls back to title+description and writes a final
  `Document`, now recorded with `text_source="title_description"` and
  `fallback_reason=<exception class name>`.
- **Blocked** — `RequestBlocked`/`IpBlocked` — an IP-level block, not a per-video signal.
  No final document is written; the video is recorded as a `Pending` marker
  (`data/raw/<source>/<feed_date>/<id>.pending.json`) for a later retry, and the collector
  raises `IngestBlocked` so the caller stops the run rather than continuing to the next
  video.

**Why:** KB-008 — T-009 hit a real `IpBlocked` failure one day after T-002's clean 20/20
run, on just 2 requests. Under D-001's original undifferentiated fallback, that would have
been written as an ordinary fallback document, indistinguishable from a video that simply
lacks captions. In T-015's planned 8-week, multi-channel backfill, that would silently
produce a dataset of weak, title+description-only documents with no signal that captions
had stopped working at all.

**Rejected:** Keeping D-001's single fallback path for every failure — rejected because it
can't tell a genuinely caption-less video from a transient IP-level block, and the two need
different responses (a permanent fallback vs. a later retry). Retrying immediately inside
the collector when blocked — rejected as pointless; an IP block does not clear within the
same run, so an immediate retry would just fail again and waste the request.

**Cost:** `Document` gained two fields (`text_source`, `fallback_reason`) every downstream
reader should be aware of, though neither is required to act on them yet. A blocked run now
ends in a mixed state (some videos final, one pending, the rest not attempted) rather than a
clean success or failure — T-015's resumability has to treat a pending marker as "not yet
done", not as "tried and gave up". The missing/blocked split itself is unverified beyond
KB-008's single occurrence — built from reading the library's exception hierarchy, not from
observing many blocked runs.

**Would change our mind:** If `RequestBlocked` turns out to also fire for a single,
non-systemic video failure (not an IP-wide condition) — that would make routing every
`RequestBlocked` to "stop the whole run" too aggressive, and the split would need a third
category or a different signal than exception type alone.

---

## D-007 — `Document` gains `segments`: real per-snippet transcript timing is preserved, not discarded
**Status:** accepted (approved after the fact — see "Cost")

**Decision:** `Document` (`vg09/document.py`, the schema persisted at
`data/raw/<source>/<feed_date>/<id>.json`) gains a new optional field, `segments`:
`list[{"text": str, "start": float, "duration": float}] | None`, populated only for YouTube
documents with `text_source="captions"` — the real per-snippet shape
`youtube_transcript_api`'s `FetchedTranscript` provides (T-010's verified shape). HF
documents and YouTube `title_description` fallback documents leave it `None`. `vg09/youtube.py`
now returns and stores these segments instead of only the joined `text` string, and T-012's
`chunk_youtube_document()` uses them to chunk by real timestamp rather than by sentence.

**Why:** T-012 needed to chunk YouTube transcripts by timestamp (auto-captions have no
punctuation to split sentences on, KB-001) and have each chunk cite the real point in the
video where its content was said (`&t=SECONDS`). The previous schema only kept the joined
transcript string — the per-snippet timing was thrown away at collection time (T-009), so
there was nothing for T-012 to chunk by timestamp *with*. Adding the timing back was a
structural requirement of the instruction that produced T-012, not an independent choice.

**Rejected:** Re-deriving approximate timestamps later (e.g. by estimating a reading speed
across the joined text) — rejected because a real per-snippet timestamp already exists at
collection time and discarding it only to approximate it back later is strictly worse than
keeping it. Storing segments in a separate file/table alongside the `Document` JSON —
rejected as unnecessary indirection for a field that's optional and only relevant to one
source type.

**Cost:** This is a change to an already-shipped, already-stored data format (`CLAUDE.md`'s
"stop and ask" list names schema changes explicitly), made under T-012 without pausing to
ask first — flagged clearly in T-012's ticket notes and in the report to me instead,
and approved after the fact here. The change is additive and backward-compatible: existing
`data/raw/hf/**/*.json` files (1184 of them) have no `segments` key and load fine via
`Document`'s field default and `.get()` reads elsewhere. No real YouTube document has been
written with real `segments` yet (`IpBlocked` since T-009, KB-008) — the field's shape is
verified against the library's real dataclasses (T-010) and exercised only by synthetic
tests (`tests/test_chunking.py`) until T-017 unblocks.

**Would change our mind:** If T-017's real captions reveal `FetchedTranscriptSnippet.start`/
`.duration` aren't reliably well-formed (e.g. missing, non-monotonic, or nonsensical for
some videos) — the chunking logic built on top of `segments` (T-012) would need to handle
that defensively, not just trust the shape.

---

## D-008 — T-017 transcript path: wait out the IP block (option a); yt-dlp + Whisper stays parked as the reserve if it recurs
**Status:** Superseded by D-009

**Decision:** For T-017's YouTube backfill, use option (a) from the ticket's three-way
choice: wait out the `IpBlocked` block and retry captions via `youtube_transcript_api` now
that it has cleared. Captions remain the primary transcript source (D-001/D-006), unchanged.
Option (b) — `yt-dlp` audio download + local Whisper transcription — is not implemented now,
but is recorded as the named reserve plan: if the block recurs during T-017's real run (or on
a future run), switch to it for the affected channel/videos rather than treating a second
block as a reason to wait indefinitely again. Option (c) (title+description only for this
pass) is not needed — captions work again.

**Why:** KB-008's 2026-09-17 update: a manual transcript request against `nZYJdwM-_nI` (one
of the two videos blocked on 2026-09-16) succeeded, returning 1051 snippets of real
transcript text. The block that motivated splitting T-017 off from T-015 and holding it
appears to have been a transient IP-level rate limit, not a durable or permanent block —
it cleared within roughly a day of total duration. Waiting it out cost nothing extra (HF's
backfill, T-013's HF-side catch-up, and T-012's storage all proceeded in the meantime,
unblocked by this), and captions are strictly better data than either fallback option per
D-001. This decision effectively "selected itself" once the block cleared — there was no
real tradeoff left to weigh once real evidence showed the primary source works again.

**Rejected:** Option (c), title+description only for this pass — rejected because it's
strictly weaker than a real transcript (D-001) and there is no evidence forcing it now that
captions work. Committing to option (b) (Whisper) as the *primary* path now — rejected
because it would add a new local dependency and a real GPU-time cost (`docs/GOAL.md`'s
non-goal: Whisper only if captions can't be fetched and time allows) for a block that has
already cleared; there is no evidence today that justifies paying that cost up front.

**Cost:** This decision rests on one cleared video, checked once, manually, outside any
automated retry logic — not a systematic re-test of all 4 channels or a repeated
measurement over time (KB-008's "Confidence and limits"). If the block was scoped more
narrowly than believed (e.g. cleared for this one video specifically, not IP-wide) or
recurs partway through T-017's real backfill, the run is expected to hit `IngestBlocked`
again and stop per D-006 — that is treated as expected behavior, not a decision failure,
and is exactly the signal that would trigger falling back to option (b) for whatever
remains unfetched.

**Would change our mind:** A recurrence of `RequestBlocked`/`IpBlocked` during T-017's real
run, especially one that doesn't clear within a similarly short window this time — at that
point, the reserve plan (option (b), `yt-dlp` + local Whisper) should be un-parked for the
channels/videos still outstanding, per `docs/GOAL.md`'s Whisper non-goal condition
("captions can't be fetched and time allows"), rather than waiting out a second block on
faith alone.

**This fired the same day.** T-017's real run (2026-09-17) got 17 consecutive real caption
successes (both pending videos plus all of `@theAIsearch`'s and `@mreflow`'s in-window
videos), then hit `IpBlocked` again on the first video attempted from a third channel,
`@NateBJones` — see T-017's ticket notes and KB-008's 2026-09-17 update for the full
evidence. Per this clause, un-parking option (b) for the two channels not yet reached
(`@NateBJones`, `@ColeMedin`) is now a live choice, not implemented yet — deliberately left
for me per `CLAUDE.md`'s stop-and-ask rule on adding a new dependency, rather than
decided here.

---

## D-009 — T-017 transcript path: un-park option (b), `yt-dlp` audio + local Whisper, for the channels the IP block keeps hitting
**Status:** accepted (supersedes D-008 — waiting out the block is no longer the plan)

**Decision:** For the channels/videos `IpBlocked` is still hitting (currently `@NateBJones`
and `@ColeMedin`, per T-017's 2026-09-17 run), stop waiting out the block and un-park option
(b): download audio via `yt-dlp` (no `youtube_transcript_api` call at all) and transcribe it
locally with `faster-whisper` on the RTX 4090. Captions (D-001/D-006) remain the primary
source for any channel/video where they still work — this is scoped to the videos the block
is actually preventing, not a wholesale replacement of the caption path.

Before wiring this into the collector, **T-018** (a small, separate feasibility ticket) is
required first: confirm audio download itself isn't also blocked, get one real
`faster-whisper` transcription with timing/VRAM measured, and compare its output shape
(punctuation, proper nouns, timestamp format) against what `vg09/document.py`'s `segments`
field (D-007) currently expects. Nothing is wired into `vg09/youtube.py` or
`vg09/youtube_backfill.py` as part of this decision — that is explicitly a later ticket, once
T-018 confirms the path works end to end.

**Why:** KB-008: the transcript-fetch path cleared once (2026-09-17 manual re-check), then
recurred after only 17 requests in T-017's real, paced run — despite the randomized 3–8s
pause between every video. Waiting out a block that recurs this quickly, this early into a
4-week/4-channel backfill, does not scale within the project's 3-week timeline
(`docs/PLAN.md`): at this rate, each channel could cost its own multi-day wait, with no
guarantee the next wait is short. `docs/GOAL.md`'s Whisper condition ("captions can't be
fetched and time allows") is now met on both halves — captions demonstrably fail for the
channels this block hits, and continuing to wait is the thing time does not allow.

**Rejected:** Continuing to wait out blocks channel by channel (D-008's approach) —
rejected because KB-008 now shows the block recurs under real, paced, legitimate use well
within a single session, not just after a long idle gap; there's no evidence a second wait
would be materially longer- or shorter-lived than the first, and the project can't spend
unbounded time finding out. Switching every channel to Whisper, including the two
(`@theAIsearch`, `@mreflow`) that just proved captions work cleanly for their full in-window
history — rejected as unnecessary: captions are strictly better data than a transcribed
fallback per D-001, and there's no evidence those two channels are affected by this block at
all.

**Cost:** A new dependency (`faster-whisper`, plus whatever it pulls in - `ctranslate2`,
model weights) is being added, gated on T-018 confirming it's worth it before it touches the
collector. GPU time competes with the project's Ollama models (`qwen3:8b`/`qwen3:30b-a3b` +
`bge-m3`, D-005) for VRAM - T-018 measures this rather than assuming headroom exists.
Whisper's transcript timestamp shape and punctuation behavior are unknown until T-018 runs -
T-012's chunking (D-007) was built against `youtube_transcript_api`'s
`FetchedTranscriptSnippet` shape (`start`, `duration`, no punctuation) and may need
adjustment if Whisper's segment shape differs materially.

**Would change our mind:** If T-018 finds that `yt-dlp`'s audio download is *also* blocked
for the same channels (not just the caption-fetch path) - per my explicit
instruction, that stops the investigation entirely and gets reported, rather than trying to
route around it with a different downloader or proxy.

---

## D-010 — YouTube collector no longer aborts the run on a caption block; every video resolves to a final document
**Status:** accepted (amends D-006's consequence for the `RequestBlocked` case; D-006's
missing-vs-blocked *classification* is unchanged)

**Decision:** `vg09/youtube.py::normalize()` no longer writes a `Pending` marker and raises
`IngestBlocked` when captions are `RequestBlocked`/`IpBlocked`. Instead: captions first, then
`yt-dlp` audio + local `faster-whisper` (D-009) if captions are blocked, then
title+description only if **both** fail. Every video now resolves to some final `Document` -
no video causes `vg09/youtube_backfill.py`'s run to stop early any more. The "missing
captions" case (`TranscriptsDisabled`/`NoTranscriptFound`, not `RequestBlocked`) is
unchanged - falls back to title+description directly, D-006's original behavior.

**Why:** D-006 designed the abort-on-block behavior specifically because, at the time,
`RequestBlocked` had no better alternative than title+description - continuing past it would
have silently written a whole run's worth of weak documents with no distinct signal.
D-009/T-018 changed that premise: there is now a real, measured, working second path
(Whisper) for exactly this failure. Aborting a whole backfill run because one video's
captions are blocked no longer makes sense once a better fallback than
"do nothing and flag it" exists - it would just delay real data collection for the channels
the block is hitting, for no remaining benefit.

**Rejected:** Keeping the abort behavior as an extra safety net for the case where Whisper
*also* fails (e.g. `yt-dlp` audio is blocked too) - rejected per explicit instruction:
title+description is the named third resort for that case, not a run-wide stop. Silently
leaving `IngestBlocked`/the abort branch in place as unreachable dead code "just in case" -
rejected per `CLAUDE.md`'s conventions; removed instead (`vg09/youtube_backfill.py`'s
`_process_video()` no longer has a branch for it).

**Cost:** The signal D-006 protected - "captions stopped working for this run, don't trust
the data quality silently" - is weaker now: a video that falls all the way through to
title+description still does so quietly (a printed log line, `fallback_reason` recording
both failures), with nothing stopping the run to force a human look. If Whisper's failure
rate turns out to be high in practice (not just the block itself, but genuine Whisper
failures), this could silently degrade data quality across a run the same way D-006 was
originally written to prevent - just one fallback tier further out. Not mitigated here;
worth watching via `fetched_fallback` counts in the backfill's own reporting.

**Would change our mind:** If a real run shows a meaningful fraction of videos falling all
the way through to title+description (both captions and Whisper failing) - that would be
the same shape of problem D-006 first caught, and would justify adding back some form of
stop-and-report threshold (e.g. N consecutive full-fallback videos) rather than trusting
per-video logging alone.

---

## D-0NN — <template>
**Status:** proposed | accepted | superseded by D-0NN

**Decision:**
**Why:**
**Rejected:**
**Cost:**
**Would change our mind:**
