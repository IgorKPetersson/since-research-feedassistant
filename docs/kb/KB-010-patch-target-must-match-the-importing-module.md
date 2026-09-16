# KB-010 — patching `vg09.document.RAW_DIR` does not redirect `vg09.hf_papers`'s own copy of the same name, and the miss silently touched real project data

**Area:** Testing — `unittest.mock.patch` target selection
**Status:** verified
**Date:** 2026-09-16  ·  **From:** T-013

## Claim
`vg09/hf_papers.py` does `from vg09.document import RAW_DIR, Document` at import time. This
binds `vg09.hf_papers.RAW_DIR` to the *value* `RAW_DIR` held at that moment — a separate name
in a separate module's namespace, not a live reference back to `vg09.document.RAW_DIR`.
Patching `vg09.document.RAW_DIR` (e.g. via `unittest.mock.patch`) redirects every function
defined *inside* `vg09/document.py` (`raw_path()`, `Document.write()`, ...), but does
**nothing** for `vg09/hf_papers.py`'s own functions that read its own copy of the name
(`day_marker_path()`, `is_day_done()`, `mark_day_done()`, `clear_day_marker()`) — they keep
reading and writing the real `data/raw/` directory regardless of the patch.

## Evidence
Writing `tests/test_sync.py` (T-013), two tests patched only `vg09.document.RAW_DIR` (plus
`vg09.watermark.WATERMARK_DIR`) to a temp directory, expecting full isolation - matching the
pattern that worked for `tests/test_youtube.py`'s `Document`/`Pending` tests. It didn't:
`hf_papers.clear_day_marker()` (called inside `sync_hf`'s reopen-window branch) deleted the
**real** `_done.json` markers for `data/raw/hf/2026-09-09` through `2026-09-12` - four real,
previously-completed backfill days from T-015 - because those calls resolved
`vg09.hf_papers.RAW_DIR`, not the patched `vg09.document.RAW_DIR`. Caught immediately after
running the suite by checking `data/raw/hf/` directly (`find ... -exec test -f _done.json`),
which showed the four markers missing. No document JSON files were lost - only the
completion markers - because `Document.write()` itself (called via `collect_day()`) *is*
defined in `vg09.document` and *was* correctly redirected to the temp dir. Repaired by
re-running the real backfill script: all four days re-fetched with identical paper counts to
the original run (48, 32, 26, 0), confirming no real data was actually lost, and
`collection.count()` in the Chroma store was unaffected throughout (1184 before and after).

Fix: patch **both** `vg09.document.RAW_DIR` and `vg09.hf_papers.RAW_DIR` to the same temp
path whenever a test exercises anything in `vg09.hf_papers` that touches paths.

## Consequences
Any module that does `from vg09.document import RAW_DIR` (or imports any other
module-level constant "by value" this way) needs its **own** patch target in tests that
touch it - patching only the origin module is not enough and fails silently (no error, no
warning; the code runs, it just operates on the wrong directory). Before writing a test that
patches a path/constant, grep for every module that imports it directly (`from module import
NAME`) rather than referencing it as `module.NAME`, and patch each one. This will recur for
any future module that imports `RAW_DIR`, `WATERMARK_DIR`, or similar constants this way
(e.g. a future YouTube-side sync module for T-017).

## Confidence and limits
One occurrence, caught and repaired the same session. Checked (`grep -rn "from vg09.document
import\|from vg09.watermark import" vg09/`): `vg09/store.py` also does
`from vg09.document import RAW_DIR` (used in `load_documents()`) and has the identical
exposure - any future test of `vg09.store` that patches only `vg09.document.RAW_DIR` will
have the same silent gap. `vg09/youtube.py` imports `Document`/`Pending`/`clear_pending` (not
`RAW_DIR` itself) and is fine, since its calls go through those classes' own methods, which
*are* defined in `vg09.document` and correctly pick up the patch there.
