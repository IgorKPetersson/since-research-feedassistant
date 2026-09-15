# KB-006 — ChromaDB's default embedding model silently truncates at 256 tokens; its own "too long" error can never fire

**Area:** Vector store (ChromaDB) — default embedding model
**Status:** verified
**Date:** 2026-09-15  ·  **From:** T-006

## Claim
ChromaDB's default embedding function (`all-MiniLM-L6-v2` via ONNX) has a hard 256-token
limit, and text beyond that is **silently dropped**, not rejected. The library's own source
contains a check that looks like it guards against overlong input
(`if len(doc_tokens.ids) > self.max_tokens(): raise ValueError(...)`), but it can never
actually fire: the tokenizer truncates to 256 tokens *before* that check runs, so
`len(doc_tokens.ids)` is never more than 256 by the time it's measured. Reading only that
check would wrongly suggest overlong documents raise an error.

## Evidence
`chromadb==1.5.9`, source at
`.venv/Lib/site-packages/chromadb/utils/embedding_functions/onnx_mini_lm_l6_v2.py`:
- Line 213-214: `tokenizer.enable_truncation(max_length=256)` /
  `tokenizer.enable_padding(..., length=256)` — truncation is configured on the tokenizer
  itself.
- `max_tokens()` returns `256`.
- `_forward()` calls `self.tokenizer.encode(d)` (already truncated to 256 by the line
  above), then checks `len(doc_tokens.ids) > self.max_tokens()` and raises if so — a check
  against a value that was already capped at 256 one line earlier, so it is unreachable.

Confirmed empirically, two ways:
1. Two documents built to be identical for their first ~256+ tokens and different only in
   their tail produced **byte-identical embeddings** (L2 distance `0.0`), while two
   genuinely different short documents produced a real distance (`1.34`) — proof the tails
   were never seen by the model, not just under-weighted.
2. `collection.add()` (the real API surface used in `scripts/t005_vector_store_date_filter.py`)
   accepted a ~700-word document with no error, warning, or truncation signal in the
   response.

## Consequences
Any document or chunk longer than roughly 256 word-piece tokens (well under a typical
paper abstract, and far under a full paper or video transcript) stored via Chroma's
**default** embedding function is silently reduced to its first ~256 tokens for embedding
purposes — retrieval quality for anything relying on content past that point (e.g. a
detail buried mid-abstract, or most of a long transcript) is unmeasured and likely bad,
with zero error signal. `docs/DESIGN.md`/Phase 1 chunking must either keep chunks
comfortably under 256 tokens, or replace the default embedder with one that has a longer
context and is chosen deliberately (see T-006's other criteria on picking an embedding
model on purpose, e.g. for multilingual support) rather than inherited silently.

## Confidence and limits
Based on reading the installed library's actual source (not documentation) plus two direct
empirical confirmations on this machine, `chromadb==1.5.9`. Not verified: whether this
matches Chroma's behavior in other recent versions, or whether truncation is head-truncation
in all cases (this test only checked that a differing *tail* was ignored — consistent with
truncation from the end, the opposite direction from KB-005's Ollama finding, so the two
should not be assumed to behave the same way).
