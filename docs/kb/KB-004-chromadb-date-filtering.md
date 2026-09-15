# KB-004 — ChromaDB's `where` filter combined with similarity search correctly restricts results by feed-date range, but the default embedding model is a silent first-use download

**Area:** Vector store (ChromaDB)
**Status:** provisional
**Date:** 2026-09-15  ·  **From:** T-005

## Claim
ChromaDB 1.5.9's embedded `PersistentClient` (no server, no Docker) supports combining a
similarity query with a numeric metadata range filter, and it works as expected: filtering
to a feed-date range (D-002) returns a strict, correctly-bounded subset of the unfiltered
top results. Separately, ChromaDB's default embedding function is not bundled — it silently
downloads an ~80MB model the first time anything is embedded, to a cache outside the
project.

## Evidence
Run on 2026-09-15 with `chromadb==1.5.9`. Script:
`scripts/t005_vector_store_date_filter.py`. 8 test documents inserted, all about
"retrieval" topics (so similarity alone can't separate old from new), with `feed_date`
spanning 2026-06-01 to 2026-09-14. Each document's metadata carries both `feed_date` (ISO
string, for display) and `feed_date_ordinal` (`date.toordinal()`, an int) — the ordinal is
the field actually filtered on, since ISO date strings aren't guaranteed to compare
correctly under Chroma's `$gte`/`$lte`.

Same query (`"retrieval quality for time-sensitive questions"`), two ways:

- **Unfiltered**, top 8: includes documents from June and August (e.g. `d1` 2026-06-01,
  `d3` 2026-08-01), ranked purely by embedding distance.
- **Filtered** to `feed_date_ordinal` in `[2026-09-01, 2026-09-14]` via
  `where={"$and": [{"feed_date_ordinal": {"$gte": ...}}, {"feed_date_ordinal": {"$lte": ...}}]}`:
  4 results, every one confirmed inside the range, and the result set differs from the
  unfiltered one (it drops the pre-September documents even where they'd otherwise have
  ranked in the top 8).

Full output: `data/t005_vector_store_date_filter.json` (gitignored).

Separately: the first call that embeds any text triggered a download of
`all-MiniLM-L6-v2/onnx.tar.gz` (~80MB) to
`~/.cache/chroma/onnx_models/` — a user-level cache directory, not inside the project, the
`.venv`, or tracked in `requirements.txt`. This is Chroma's default embedding function
downloading its own model weights on first use, not a pip package.

## Consequences
The date-range + similarity filtering pattern this project's core claim depends on
(`docs/GOAL.md`) works in ChromaDB with no server. Phase 1's document schema should store
feed date as a comparable numeric field (an ordinal, or a Unix timestamp — either works;
this test used `toordinal()`) alongside a human-readable string, not rely on string
comparison for the filter.

The silent embedding-model download is a real risk for two of `docs/GOAL.md`'s stated
properties: "a fresh clone reaches a first answer by following the README only" needs
network access on that first run for this download (not just for the model APIs), and it
should be called out in the README rather than discovered as a mysterious pause. It's a
one-time cost per machine (cached after), so it doesn't affect the "PC off for 7 days,
catch-up" story once the cache exists.

## Confidence and limits
One run, one small hand-built test collection (8 documents, all same topic-family), one
query. Not tested: filtering behavior at realistic scale (hundreds/thousands of documents),
concurrent writes, what happens across a Chroma version upgrade, or whether the default
embedding model is good enough for this project's real evaluation questions (KB-001 already
flags a related but separate concern — retrieval quality against auto-caption spelling
errors). This only establishes that the filtering mechanism itself works, not that
`all-MiniLM-L6-v2` is the right embedding model for Phase 1.
