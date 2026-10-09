# KB-042 — Chroma's `$contains` is case-sensitive; `$regex` takes `(?i)`

**Area:** Vector store (ChromaDB) — text filters
**Status:** verified
**Date:** 2026-10-09  ·  **From:** T-095

## Claim
1. `where_document={"$contains": "NeoHorse"}` matches the exact case only: on the frozen
   store "NeoHorse" finds 1 chunk and "neohorse" finds 0.
2. `where_document={"$regex": "(?i)neohorse"}` matches case-insensitively, and the same
   filter works in `collection.get()` and `collection.query()` together with a `where`
   metadata filter and a query embedding. A word-boundary pattern such as
   `(?i)(?:^|\W)NeoHorse(?:\W|$)` keeps "Agen" from matching inside "Agents".
3. `query()` with a `where_document` filter ranks only the matching chunks by embedding,
   so "the best chunks that contain this name" is one call.

## Evidence
- chromadb 1.5.9, the frozen evaluation store (1971 chunks), 2026-10-09:
  `$contains` "NeoHorse" 1, "neohorse" 0, "AutoDev" 0, "LEGO" 1, "Palunteer" 1;
  `$regex` "(?i)neohorse" 1.
- `tests/test_mixed_retrieval.py` runs the regex, the date filter and the word boundary
  against an in-memory Chroma collection.

## Consequence for this project
`vg09.retrieval.name_candidates()` and `vg09.scope` use `$regex` with `(?i)` and word
boundaries (`vg09.exact_names.name_regex()`), never `$contains`.
