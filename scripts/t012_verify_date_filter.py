"""T-012: confirm feed-date range filtering works against the REAL production
store (not T-005's throwaway 8-document collection)."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import get_collection  # noqa: E402

RANGE_START = date(2026, 9, 1)
RANGE_END = date(2026, 9, 14)

coll = get_collection()
print(f"collection.count() = {coll.count()}")

filtered = coll.get(
    where={
        "$and": [
            {"feed_date_ordinal": {"$gte": RANGE_START.toordinal()}},
            {"feed_date_ordinal": {"$lte": RANGE_END.toordinal()}},
        ]
    },
    limit=10000,
)
n = len(filtered["ids"])
in_range = all(
    RANGE_START <= date.fromisoformat(m["feed_date"]) <= RANGE_END for m in filtered["metadatas"]
)
print(f"Filtered to [{RANGE_START}, {RANGE_END}]: {n} chunks, all in range: {in_range}")

unfiltered = coll.get(limit=10000)
print(f"Unfiltered: {len(unfiltered['ids'])} chunks")
print(f"Filtered is a strict subset: {n < len(unfiltered['ids'])}")

# text_source metadata check - fallback documents (none exist yet, only
# pending markers which are skipped) would show up here once T-017 lands.
sources = {}
for m in unfiltered["metadatas"]:
    key = m.get("text_source", "(n/a - hf)")
    sources[key] = sources.get(key, 0) + 1
print(f"text_source breakdown: {sources}")
