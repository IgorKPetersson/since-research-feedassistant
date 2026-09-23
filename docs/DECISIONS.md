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

## D-011 — Relative retrieval windows anchor to the whole dataset's real latest content, not a per-source watermark or a single source's cutoff
**Status:** superseded by D-012 (the eval/production anchor split below was never actually
followed in practice - see D-012)

**Decision:** When retrieval (T-022/T-027) resolves a relative window ("senaste veckan", via
`vg09.date_range.resolve_date_range()`), the `today` passed in is
`vg09.store.latest_feed_date()` - the maximum `feed_date` actually present across the whole
Chroma store, both sources combined - not `date.today()`, not either source's own watermark,
and not one source's ingest cutoff used as a stand-in for "now". **This applies to live/
production retrieval only.** Evaluation runs (Phase 3, or any re-run of T-014's 15 real
questions against the frozen dataset) pin `today` **explicitly to 2026-09-16** instead - the
same anchor `docs/eval-questions.md`'s facit was already written and reviewed against -
rather than calling `latest_feed_date()` themselves. The evaluation script sets this anchor
explicitly in its own code, not by relying on whatever `latest_feed_date()` happens to return
against a given snapshot of `data/raw/`. This keeps the already-written facit correct without
rewriting it, and keeps production behavior correct without weakening it for evaluation's
sake - the two callers legitimately want different anchors for different reasons, not one
"right" anchor with an exception.

**Why:** Real, measured finding (Phase 2, T-022's real-question re-run): `YTG0rdHPTDE`
(YouTube, `feed_date` 2026-09-17), the single most relevant real candidate by similarity for
F15 (rank 6 of 1971), was excluded from its filtered candidate pool entirely, because the
window (2026-09-10..2026-09-16) was anchored to HF's cutoff (2026-09-16) - one day before
YouTube's own latest real content. Each source ingests and settles at its own pace (T-013's
per-source watermarks already model this structurally); anchoring a *shared* window to
whichever source happens to be slowest silently excludes genuinely newer content from any
faster one. This isn't specific to this one eval question - it's a property of any two-source
system where ingest cadence differs.

**Rejected:** `date.today()` (the real wall-clock date) - rejected because it would make a
relative window's meaning depend on how long it's been since the last ingest, extending
"senaste veckan" into a tail with no real data at all rather than anchoring to what's actually
available, and would break reproducibility for a re-run against a frozen dataset (T-020) run
on a different real-world day. Either source's own watermark
(`vg09.watermark.read_watermark()`) - rejected because a watermark is deliberately a few days
conservative (T-015's `REOPEN_DAYS=2`, to handle the local-timezone-ahead-of-UTC risk it was
built for) and can lag several days behind that source's own real latest content (confirmed
for real: HF's watermark reads `2026-09-14` while HF's real latest ingested content is
`2026-09-16`) - a watermark answers "how far have we confirmed settled", a different question
than "what's the newest real content we have".

**Cost:** `vg09.store.latest_feed_date()` does a full metadata scan
(`collection.get(include=["metadatas"])`), not an indexed aggregate - Chroma has no native
max() over metadata. Cheap at this project's real scale (~2000 chunks); would need
revisiting only if the corpus grew by orders of magnitude. The eval/production split above
means two code paths compute `today` differently depending on caller, which is one more
thing a future reader has to know rather than a single rule everywhere - documented here and
in `docs/eval-questions.md` specifically so it isn't rediscovered by surprise. Resolved,
not just flagged: `docs/eval-questions.md`'s facit windows (F02/F04/F05/F07/F11/F13/F15,
computed against 2026-09-16) stay correct as written, because evaluation now pins that same
anchor explicitly rather than adopting `latest_feed_date()`'s 2026-09-17 - no facit rewrite
needed.

**Would change our mind:** If ingest cadence ever became fast enough (multiple runs per
session) that "latest feed_date in the store" started drifting meaningfully within a single
retrieval session - not a concern at this project's real daily/weekly ingest cadence.

---

## D-012 — Relative retrieval windows anchor to the dataset's real latest content — one anchor, production and evaluation alike
**Status:** accepted

**Decision:** `vg09.store.latest_feed_date()` (the maximum `feed_date` actually present
across the whole Chroma store, both sources combined) is the `today` every caller of
`vg09.date_range.resolve_date_range()` passes in - production retrieval (`app.py`) and any
evaluation re-run of T-014's questions (T-027, T-028, Phase 3) alike. There is no longer a
separate, hand-pinned evaluation anchor. `docs/eval-questions.md`'s own "Time-window
conventions" section is updated to say so (2026-09-17 for the current frozen dataset, not
2026-09-16) - the facit's actual expected-source content (F01-F15) is unchanged, only the
anchor explanation.

**Why:** D-011 originally split this into two rules - production uses
`latest_feed_date()`, evaluation pins `today` explicitly to 2026-09-16, "the same anchor
docs/eval-questions.md's facit was already written and reviewed against." That split was
never actually followed: T-027's own real re-run of T-014's 15 questions (the run that
produced the 11/14 headline D-011 itself cites) used `today=2026-09-17`, not 2026-09-16;
T-028's later re-confirmation of that same headline did too, by explicit instruction in its
own ticket notes. Found by Phase 2's `grill-me` review (2026-09-20, T-029): D-011's written
rule and the practice it was supposedly describing had already diverged, undetected, across
two tickets.

Investigating why the practice drifted rather than just re-aligning it to the written rule:
the written rule is the one that's wrong. `docs/eval-questions.md`'s own facit windows are
**asymmetric per source** for questions that touch both (e.g. F13: "fönstret
2026-09-03–2026-09-17" for a YouTube-only question - one day past D-011's prescribed
2026-09-16, because YouTube's real latest content is one day newer than HF's). A single
`resolve_date_range(question, today=2026-09-16)` call cannot reproduce that asymmetry - it
returns one `(start, end)` pair applied uniformly to a query that filters both sources at
once (`vg09.retrieval.query_candidates()`'s `where` clause doesn't distinguish source). Pin
`today` to 2026-09-16 as D-011 literally said, and F13/F15-shaped questions lose exactly the
real, newer content D-011 was written to stop excluding - the same `YTG0rdHPTDE` case,
recreated by D-011's own text. `today=2026-09-17` (what was actually run, both times) is the
only anchor that reproduces the facit's own stated windows correctly for those questions;
2026-09-16 is silently wrong for them. The practice was right; the decision log was not.

**Rejected:** Keeping D-011's two-anchor split and just correcting its date (e.g. "pin eval
to 2026-09-17 instead of 2026-09-16") - rejected because the split itself is the defect, not
the specific date. Any hand-pinned eval constant will drift out of sync with
`latest_feed_date()`'s real value again the moment the frozen dataset is ever
re-frozen at a different cutoff (T-020), exactly as D-011's 2026-09-16 silently drifted out
of sync with T-027's real 2026-09-17 the first time it mattered. One rule, sourced from the
data itself, can't drift from the data.

**Cost:** None beyond D-011's own already-accepted cost (a full metadata scan,
cheap at ~2000 chunks). Removes the "two code paths compute `today` differently depending on
caller" cost D-011's own Cost section flagged as itself a real cost - one caller path is
strictly simpler than two. `docs/eval-questions.md`'s "Time-window conventions" section and
its own D-011 callout box need correcting to cite `latest_feed_date()`/2026-09-17, not
2026-09-16 - documentation-only, not a facit rewrite, but not a perfect match either: flagged
honestly rather than overclaimed. For source-crossing/YouTube-touching questions
(F13/F15-shaped), 2026-09-17 is exactly what the facit's own written windows already assumed
- that part reconciles exactly. For HF-only window questions (F02/F04/F05/F07/F11), the
individually-written window text (e.g. F02: "2026-08-16–2026-09-16") is one calendar day
earlier than what a literal `resolve_date_range(..., today=2026-09-17)` call now computes -
`resolve_date_range()` takes one anchor, not a per-source pair, so it cannot reproduce the
facit's asymmetric windows exactly for every question at once. This extra day is harmless in
practice for the current frozen dataset specifically - HF's real content stops at 2026-09-16
regardless of where the window's edge falls, so grading outcomes for T-027/T-028's real
re-runs were unaffected (confirmed: neither run's HIT/MISS count changed because of it) - but
it is a real, acknowledged gap between the written per-question facit text and what the code
now literally computes, not a coincidence resolved away by this decision.

**Would change our mind:** Same condition D-011 already named - ingest cadence fast enough
that "latest feed_date in the store" drifts meaningfully within a single session. Also: if a
future frozen-dataset snapshot's facit windows are ever written to be symmetric across
sources on purpose (not the current asymmetric case), a hand-pinned eval anchor might become
appropriate again - not the situation today.

---

## D-013 — Answers are always in English; questions may be asked in any language
**Status:** accepted

**Decision:** `vg09.answer.SYSTEM_PROMPT` (T-023/T-024) explicitly instructs the model to
answer in English regardless of the language the question was asked in - "Always answer in
English, even if the question is asked in a different language." This applies only to the
answer's output language. The question side is unaffected and unchanged: a question can
still be asked in any language, because `bge-m3`'s embedding (D-005) is multilingual by
construction and already retrieves correctly across languages - verified for real in T-006
and exercised throughout T-014's eval set, which deliberately includes Swedish questions
(F01-F15 are all written in Swedish) retrieving correctly against English-language sources.
This decision pins down the *answer's* language explicitly, in code, rather than leaving it
to whatever the model happens to do by default when the question and sources are in
different languages from each other.

**Why:** my explicit instruction (2026-09-20): the project ships as OSS under Apache-2
(`docs/GOAL.md` §"Definition of done": public GitHub repo with an Apache-2 `LICENSE`) and
is meant to be usable internationally, not just by Swedish speakers - the international-
usability framing is my own stated rationale for this decision, not something
`docs/GOAL.md` already said outright; recorded here so it isn't lost. Its sources (HF Daily
Papers abstracts, YouTube transcripts) are themselves English, so an
English answer stays closest to the source material's own wording rather than requiring a
lossy translation step the model would have to perform silently and unverifiably. Without
an explicit instruction, a Qwen3 chat model's default behavior is to mirror the question's
own language (observed informally across this project's own real runs, e.g. T-028's Swedish
example question producing a Swedish answer) - correct for a single-user Swedish deployment,
wrong for an internationally-usable OSS project, and not something to leave to chance.

**Rejected:** Detecting the question's language and answering in kind (mirror the question)
- rejected because it's exactly the *opposite* of what OSS usability needs here: a
non-Swedish-speaking contributor or user asking a question in their own language would get
an answer in that language too, unreadable to anyone else evaluating or reviewing the
project's output regardless of who asked. Translating each source excerpt into the
question's language before generation - rejected as unnecessary complexity and a new,
unverified translation-quality risk; the sources are already English, and D-013 only pins
the answer's language, not a requirement to translate evidence text.

**Cost:** The English-answer instruction adds 16 real qwen3 tokens to `SYSTEM_PROMPT`
(173, up from T-024's 157, re-measured for real via the same `num_predict:1` method
T-008/T-024 used) - `docs/DESIGN.md`'s budget math and `vg09.retrieval.CHUNK_BUDGET_TOKENS`
updated to match (13245, down from 13261). Max top-k stays 33 (13245 // 400 - the same
400-token band as 13261's 33, so no further consequence). T-014's eval facit
(`docs/eval-questions.md`) is written and graded in Swedish - a strict re-grading against
this decision would need a note that a passing answer is now expected in English even
though the facit's own descriptive text stays Swedish; not rewritten here, flagged for
whoever next re-runs or re-grades that eval set (Phase 3).

**Would change our mind:** If the project's actual userbase turns out to be exclusively or
overwhelmingly Swedish-speaking and English answers create real friction - not the
situation this decision is made for (OSS/Apache-2 public repo, explicit international-
usability intent per my own stated reasoning above).

---

## D-014 — Answer generation reserves 4000 tokens and retries once when the answer is cut off
**Status:** accepted

**Decision:** `vg09.answer.NUM_PREDICT` is 4000 (was 2542, T-028), and `generate_answer()`
repeats an identical call once (`MAX_RETRIES = 1`) when the first response ends with
`done_reason == "length"`. `AnswerResult.retries` records whether a retry happened. If the
retry is also cut off, that second response is returned flagged incomplete, as before;
there is never a third attempt. The chat UI shows a notice whenever a retry happened, and
the evaluation scripts log the retry count per call. `CHUNK_BUDGET_TOKENS` follows from the
reservation: `16000 - 173 - 40 - 4000 = 11787` (was 13245).

**Why:** T-032's real run truncated 4 of 30 calls with empty answers. T-039's 32-run probe
(KB-019) showed reasoning length varies widely between samples of the same prompt, with
totals up to 3118 tokens — beyond T-028's cap, which was sized from three samples of one
question. A higher cap makes truncation rare; the retry handles the remainder because the
cause is sampling variance, not something about the prompt, so an identical second call
usually completes. I approved both on 2026-09-22.

**Rejected:** Raising the cap alone — 4000 is a margin over a finite sample, not a proven
bound, and an empty answer is the worst failure this pipeline has. Retrying more than once
— a question that does not complete in two attempts should say so, not spend a minute
looping. Reducing the model's reasoning (a shorter-reasoning prompt or `think` budget) —
T-028 already considered this and I chose to raise the cap instead; not revisited.
Compensating with a smaller system prompt or question reservation — those are measured
minimums, not slack.

**Cost:** 1458 fewer tokens for retrieved chunks (max top-k 27 → 24 in the worst case);
`scripts/t039_verify_chunk_budget_impact.py` checks the effect on real packing. A retry
doubles that call's latency (roughly 15-35 s more on the RTX 4090).

**Would change our mind:** Real usage where retries are frequent (the retry rate is
logged in the evaluation output), which would mean the cap is still too low; or a change
to the model or its sampling settings, which invalidates KB-019's measurements.

---

## D-015 — A citation bracket naming at most 5 numbers resolves as a citation; more is a descriptive enumeration, not evidence
**Status:** accepted

**Decision:** `vg09.citations.build_citations()` (T-040) now parses a numeric range inside
a bracket (`"1-20"`, `"21-22"`) the same way it already parsed a comma-separated list
(T-028): each number is checked against `source_map` individually - **but only when the
bracket names at most `DESCRIPTIVE_BRACKET_THRESHOLD = 5` numbers in total, summed across
every comma-separated piece** (a bare number contributes 1, a range contributes its own
span). A bracket naming more than that is not expanded into one citation per number at all
- it's collected into a new `CitationResult.descriptive_ranges` list instead, deduplicated,
first-seen order. It is **not** added to `unlinked_references` either: it was never a
failed citation attempt, so reporting it as one would be as misleading as expanding it. A
bracket mixing a short piece with a long range (`"[1, 5-31]"`) is treated as descriptive as
a whole - a bracket dominated by "reviewed all sources" isn't meaningfully still citing its
smaller piece.

**Follow-up (T-041, 2026-09-23):** the rule as originally implemented checked each piece's
*own* span against the threshold, not the bracket's total - a range ("[1-31]", one piece,
span 31) was caught, but the identical claim spelled out as 31 individual comma-separated
bare numbers ("[1,2,3,...,31]") was not, since a bare number's own span is always 1. Found
by a Phase 3 `/grill-me` review, not hypothetical, though not yet observed in real model
output either. Fixed by summing every piece's span across the whole bracket before
comparing to the threshold - the decision itself (the number 5, the reasoning below) is
unchanged; only the counting method now matches what "at most 5 numbers named in one
bracket" was always meant to say.

**Why:** real data from grading T-032's re-run (2026-09-22) gave three concrete shapes to
draw the line between: F10-A's `[21-22]` (2 numbers) is a genuine two-source citation that
T-028's comma-only splitting couldn't resolve, silently dropping a real cited video into
`unlinked_references`; F10-A's `[1-20]` ("All 20 papers and videos listed... were published
on September 16 [1-20]") and F12-A's `[1-31]` ("Palantir has not been mentioned in any of
the provided sources [1-31]") are both the model describing the whole set of sources it was
given, not citing evidence for a specific claim - exactly the false-positive shape T-024's
own ticket predicted from a real F12 run ("reviewed all 38 sources (from `[1]` to `[38]`)")
and `docs/PLAN.md`'s risk register flagged as worth watching in Phase 3. A count-based
threshold is checkable directly against these three real numbers (2, 20, 31) without
needing to parse or understand the surrounding sentence.

**Rejected:** Expanding every range regardless of length - directly reproduces T-024's
predicted false-positive-citation risk, now provably real (F12-A would have produced 31
fabricated citations on a correct "not mentioned" answer). Leaving ranges unlinked, as
before this decision - silently drops real citations like F10-A's `[21-22]`, the same class
of silent data loss T-028 already fixed for commas. A semantic check (does the sentence
around the bracket sound like a citation or a description?) - I explicitly picked a
count threshold instead; no NLP step exists in this pipeline to make a semantic check
reliable, and a fixed threshold is trivially testable while a semantic heuristic is not.

**Cost:** `DESCRIPTIVE_BRACKET_THRESHOLD = 5` is a judgment call fitted to three real data
points (2 real, 20 and 31 descriptive), not derived from a larger sample - a future real
bracket naming, say, 6-10 numbers that genuinely is a multi-source citation would be
misclassified as descriptive and under-cited (safer direction: reported nowhere as a false
positive, but also not surfaced as a citation). `CitationResult.descriptive_ranges` is a new
field production (`app.py`) and both evaluation scripts (T-031/T-032) now render explicitly,
so nothing that used to be visible (as unlinked) silently disappears.

**Would change our mind:** A real range of 6+ numbers that turns out to be a genuine
multi-source citation, not a description - would mean the threshold is too low. A
descriptive range of 5 or fewer numbers that gets expanded into false citations - would mean
the threshold is too high, or that a count alone can't carry this distinction and a
different signal (e.g. the sentence's own wording) is needed after all.

---

## D-016 — UI-facing text switches from Swedish to English
**Status:** accepted

**Decision:** Every UI-facing string in `app.py` (labels, buttons, captions, notices,
the status bar and pipeline strip T-042 adds) is written in English. Applies to
pre-existing labels this ticket touches too, not just new ones - no mixed-language UI.
`vg09.ui_helpers.describe_retrieval_mode()`'s output text is English as of this decision
(its logic - which mode fired, and why - is unchanged, D-016 is a text-only decision).

**Why:** asked directly of me during T-042 (the UI redesign), per that ticket's
own explicit instruction to stop and ask rather than assume. D-013 already settled that
*answers* are always English regardless of the question's language, reasoned from this
project shipping as public Apache-2 OSS meant to be usable internationally - the same
reasoning applies to the UI chrome around those answers. Leaving the UI in Swedish while
every answer is English was already an inconsistency D-013's own Cost section flagged as
residual and unresolved.

**Rejected:** Keeping Swedish - was the status quo default (every existing `app.py`
label), rejected once asked directly, for the same reason D-013 gave: this is public OSS,
not a single Swedish-speaking user's private tool. A mixed UI (old labels Swedish, new
T-042 labels English) - rejected explicitly; inconsistency-by-accretion is worse than
either single-language choice.

**Cost:** Every existing Swedish string in `app.py` needed translating as part of T-042,
not just the new UI sections - a larger diff than a UI-only redesign would otherwise need,
but bundled into the same ticket rather than deferred, since a half-translated UI would be
worse than either full state. Nothing else in the repo (docs, tickets, code comments) is
affected - this decision is scoped to what a user of the running app actually sees.

**Would change our mind:** If the project's real userbase turns out to be exclusively or
overwhelmingly Swedish-speaking and this creates real friction - the same clause D-013
already names, not met by anything currently known.

---

## D-0NN — <template>
**Status:** proposed | accepted | superseded by D-0NN

**Decision:**
**Why:**
**Rejected:**
**Cost:**
**Would change our mind:**
