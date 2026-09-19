# KB-016 — Comparing two retrieval measurements requires pinning the same `today` anchor for both, or the delta is meaningless

**Area:** Retrieval (`vg09.retrieval`, `vg09.date_range`) — measurement methodology
**Status:** verified
**Date:** 2026-09-19 · **From:** T-028

## Claim

`vg09.date_range.resolve_date_range(question, today, ...)` resolves relative phrases
("senaste veckan") relative to whatever `today` is passed. Two runs of the same
before/after comparison (e.g. "did chunk budget X vs. budget Y change the result?") give a
misleading delta if `today` differs between them — the difference gets attributed to the
thing actually being tested, when it was really just two different date windows.

## Evidence

T-027 measured T-014's 15 real questions against the top-5-vs-facit headline using
`today=vg09.store.latest_feed_date()` (2026-09-17 at the time), producing **11/14**. Later,
D-011 (same session) decided evaluation code should instead pin `today=2026-09-16` explicitly
(the anchor `docs/eval-questions.md`'s facit was written against) — a real, deliberate,
separate decision, unrelated to chunk-budget sizing.

In T-028, re-checking whether a smaller chunk budget (13261, down from 13803, after raising
`NUM_PREDICT`) still packs enough real chunks, the first measurement attempt used
`today=2026-09-16` (D-011's eval anchor) instead of `today=2026-09-17` (what the *original*
11/14 was measured against). The headline came back **10/14** — F15 flipped to MISS. This
looked like the budget change had broken something. It hadn't: F15's flip is explained
entirely by `YTG0rdHPTDE` (real `feed_date` 2026-09-17) falling outside a `2026-09-16`-anchored
window again — the exact issue T-027 fixed, reintroduced by the anchor choice alone, nothing
to do with packing or budget. The top-5-vs-facit measurement doesn't even call
`pack_to_budget()` — there was no code path connecting the change under test to the number
that moved.

## Consequences

Before trusting a delta between two retrieval measurements, confirm both runs used the same
`today` (and the same `date_range`/`ranking` resolution generally) — a script comparing "old
vs. new X" should compute `today` **once** and reuse it for both arms, never call
`resolve_date_range()`/`latest_feed_date()` independently per arm. When re-running any of this
project's real-15-question measurements to compare against a past result, check what anchor
that past result actually used (T-027's original 11/14: `today=2026-09-17`; anything grading
against `docs/eval-questions.md`'s facit directly: `today=2026-09-16`, D-011) rather than
assuming "the eval anchor" is a single universal default.

## Confidence and limits

One real occurrence, caught before being reported as a real finding. Only affects
measurement/comparison scripts, not production code — `vg09.retrieval`/`vg09.answer` never
compute `today` themselves (T-021's own design: always an explicit parameter), so this is a
risk for whoever writes the next comparison script, not a latent bug in the shipped pipeline.
