# KB-002 — the HF Daily Papers API returns 200 with an empty list on weekends, and the arXiv id is nested under `paper.id`, not top-level

**Area:** HF Daily Papers API
**Status:** verified (upgraded from provisional — see the T-015 reinforcement below)
**Date:** 2026-09-15 (T-003); reinforced 2026-09-16 (T-015)  ·  **From:** T-003, T-015

## Claim
`GET https://huggingface.co/api/daily_papers?date=YYYY-MM-DD` returned HTTP 200 for all of
the last 14 days, including dates more than 10 days in the past, so historical dates work.
The 4 dates with zero entries in that window were exactly the weekend dates — HF Daily
Papers appears not to publish on Saturdays/Sundays, and an empty list is the normal
response for those dates, not an error. Title, abstract and publication date are present,
but not where a naive read of "title, abstract, publication date, arXiv id" would put them:
the abstract is called `summary`, not `abstract`, the arXiv id lives at `paper.id`, not at
the entry's top level, and — the important one — the `publishedAt` field is *not* the date
the `date=` query matched on; `paper.submittedOnDailyAt` is.

## Evidence
Run on 2026-09-15 with `requests==2.34.2`. Script: `scripts/t003_hf_daily_papers.py`,
querying every date from 2026-09-02 to 2026-09-15 inclusive.

| Date | Weekday | Status | Entries |
|---|---|---|---|
| 2026-09-15 | Tue | 200 | 31 |
| 2026-09-14 | Mon | 200 | 26 |
| 2026-09-13 | Sun | 200 | 0 |
| 2026-09-12 | Sat | 200 | 0 |
| 2026-09-11 | Fri | 200 | 26 |
| 2026-09-10 | Thu | 200 | 32 |
| 2026-09-09 | Wed | 200 | 48 |
| 2026-09-08 | Tue | 200 | 12 |
| 2026-09-07 | Mon | 200 | 28 |
| 2026-09-06 | Sun | 200 | 0 |
| 2026-09-05 | Sat | 200 | 0 |
| 2026-09-04 | Fri | 200 | 30 |
| 2026-09-03 | Thu | 200 | 36 |
| 2026-09-02 | Wed | 200 | 29 |

Full raw results: `data/t003_hf_daily_papers.json` (gitignored, not committed, regenerate
by rerunning the script). A trimmed raw sample (first 3 entries of the 2026-09-15 response
only — the full day is ~250KB, mostly author/avatar metadata not worth committing) is
checked in at `docs/kb/samples/daily_papers_2026-09-15_sample.json`.

Confirmed top-level entry keys: `title`, `summary`, `publishedAt`, `paper`, plus
`numComments`, `thumbnail`, `mediaUrls`, `organization`, `submittedBy`,
`isAuthorParticipating`. Confirmed `paper` sub-object keys include `id` (the arXiv id,
e.g. `"2609.11638"`), plus its own duplicate `title`/`summary`/`publishedAt`, `authors`,
`upvotes`, `githubRepo`, `githubStars`, `ai_summary`, `ai_keywords`, `discussionId`,
`projectPage`, `submittedOnDailyAt`, `submittedOnDailyBy`.

## Consequences
The Phase 1 HF collector must read the arXiv id from `paper.id`, not from the entry's top
level, and must treat `summary` as the abstract field (there is no `abstract` key at
either level). A catch-up run must not treat an empty list on a weekend date as a failure
or a sign that the API changed shape — it's the expected response.

**`publishedAt` does not mean what the `date=` query parameter means.** Checked on 3
entries from the `date=2026-09-15` response: top-level `publishedAt` and `paper.publishedAt`
were both several days *before* 2026-09-15 (e.g. `2026-09-10`, `2026-09-11`), while
`paper.submittedOnDailyAt` was `2026-09-15T00:00:00.000Z` on all three — exactly the
queried date. So `publishedAt` looks like the paper's own (arXiv) publication date, and
`submittedOnDailyAt` is the date it was featured on Daily Papers, which is what `date=`
actually selects on. `docs/GOAL.md`'s date-aware retrieval is framed around "publication
date" — the Phase 1 design needs an explicit decision on which of these two dates that
means for filtering and for citations (arXiv `publishedAt`, or the HF `submittedOnDailyAt`
"appeared in the feed" date), because they can differ by several days and picking the wrong
one would silently corrupt every date-range query the whole project is built to answer.

## Confidence and limits
One run, one 14-day window, one point in time. Not tested: whether the weekend gap is
consistent across other weeks/months, whether the API has undocumented rate limits (none
hit in 14 sequential requests), or whether the schema is stable across HF deployments. The
`publishedAt` vs `submittedOnDailyAt` divergence was checked on only 3 entries from a
single date — consistent on all 3, but not exhaustively confirmed across dates or verified
against arXiv's own record for those ids.

**T-015 reinforcement (2026-09-16):** the 8-week HF backfill queried 56 consecutive days
(2026-07-23..2026-09-16) with `scripts/t015_hf_backfill.py`. Every one of the 16 weekend
dates in that window returned an empty list, zero exceptions; every weekday returned real
papers (12-48 per day). No rate limiting or non-200 response was hit across 56 sequential
requests, nor across the repeated re-runs in T-013's later catch-up/verification work
(dozens more requests against the same date range). The weekend-gap pattern and the field
shapes (`paper.id`, `paper.submittedOnDailyAt`) both held with no exceptions at 4x the
original sample size — upgrading this entry's status from provisional to verified. Still not
tested: behavior across a full calendar year (holiday patterns, HF outages), or whether the
API has a rate limit above the volumes seen so far.
