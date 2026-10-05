# KB-031 — Generic "what's new" questions match news videos so strongly that a 60-candidate pool holds no papers

**Area:** Retrieval — bge-m3 ranking under the per-document limit
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-067, T-068 / session 2026-10-05 § 6.2–6.3

## Claim
With `bge-m3`, a question like "What's new this week?" ranks chunks of news videos that
literally say "what's new this week" far above any paper abstract. The top 60 candidates
came from 6 videos; with at most 2 chunks per document (T-027), only 12 excerpts were left,
38% of the budget, and no papers. Naming "papers" in the question is not enough to
counter it: "the most important papers yesterday" got 0 papers even at 400 candidates.

## Evidence
2026-10-05 probe of 18 questions against the live store (search only):
- "What's new this week?": 248 paper chunks in the window; the first ranked 71st.
  60 candidates → 12 excerpts, 0 papers, 38%. 200 candidates → 32 excerpts, 18 papers, 97%.
- With 200 candidates every probe question filled 96–99% of the budget; 11 of 18 packed
  sets changed, the 7 already full did not. Median retrieval 1.06 s → 1.27 s.
- "papers yesterday": 0 papers at 60, 200 and 400 candidates.

## Consequences
- `CANDIDATE_POOL_SIZE` is 200 (T-067). The 60 dated from before the per-document limit.
- A question that names papers or videos is filtered to that source (T-068), since ranking
  alone can't do it.
- A larger pool doesn't fix everything: F14 (T-069) still cited only YouTube at 200
  candidates. That is a semantic gap, recorded in `docs/PLAN.md`'s risk register.

## Confidence and limits
One store snapshot (through 2026-10-05), 18 questions. The rank of the first paper depends
on how many news videos in the window use the question's wording, so it will vary week to
week.
