# KB-026 — A Chroma `PersistentClient` goes stale when another process writes the same store: similarity queries fail with "Error finding id" until the client is dropped

**Area:** Vector store (ChromaDB) — one store, two processes
**Status:** verified
**Date:** 2026-10-02  ·  **From:** T-056

## Claim
With ChromaDB 1.5.9's embedded `PersistentClient`, a process that opened the store before
another process added to it can no longer run similarity queries: `collection.query()`
raises `chromadb.errors.InternalError: Error executing plan: Internal error: Error
finding id`. This holds both while the other process is writing and after it has
finished and exited. Metadata reads (`count()`, `get()`) keep working and show the new
totals, which makes the store look healthy. A new process queries the same store without
error.

## Evidence
The app (process A) was open; the ingest job (process B) added 38 chunks.
- Question in A while B was writing: `Error finding id`.
- Question in A 25 seconds after B finished: the same error, while A's header already
  showed the new count (2891 chunks).
- The same query from a fresh process: 5 results, including the new chunk.
- After `SharedSystemClient.clear_system_cache()` in A, with no restart: the question
  retrieved 60 candidates and the answer cited the newly added video.

## Consequences
- `vg09.store.reset_client()` drops Chroma's cached client;
  `vg09.ingest_job.refresh_store_if_updated()` calls it from the app when a job has
  finished since the app last looked.
- The app refuses questions while the job is in its store-writing stage
  (`is_writing_store()`), and catches `ChromaError` for the moment in between.
- The job writes only chunks the store lacks (`build_store(only_new=True)`), which cut
  that stage from about 45 seconds to 4.
- Anything else that writes the store while the app is open — `scripts/t012_build_store.py`
  from a terminal — leaves the app in the same state, with nothing to trigger the reset.
  The README says not to do that; restarting the app fixes it.

## Confidence and limits
Reproduced twice (during and after a write) and the fix confirmed once, on Windows with
ChromaDB 1.5.9. `clear_system_cache()` is not documented as a supported way to reopen a
store; it only empties the client cache, and the old client's resources are left to
garbage collection. Whether repeated resets leak memory or file handles over a long
session was not measured.
