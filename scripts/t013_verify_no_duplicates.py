"""T-013 verification: confirm the simulated-gap round trip left no
duplicates and the previously-removed chunks are back with correct
metadata."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import get_collection  # noqa: E402

GAP_DAYS = {"2026-09-07", "2026-09-08"}

coll = get_collection()
all_rows = coll.get(limit=10000)
ids = all_rows["ids"]

print(f"collection.count() = {coll.count()}")
print(f"len(ids) = {len(ids)}")
print(f"unique ids = {len(set(ids))}")
print(f"No duplicate ids: {len(ids) == len(set(ids))}")

gap_chunks = [
    (id_, meta) for id_, meta in zip(ids, all_rows["metadatas"])
    if meta["feed_date"] in GAP_DAYS
]
print(f"\nChunks now present for the gap days {sorted(GAP_DAYS)}: {len(gap_chunks)} (expected 40)")
by_day = {}
for _id, meta in gap_chunks:
    by_day.setdefault(meta["feed_date"], 0)
    by_day[meta["feed_date"]] += 1
print(f"Per-day breakdown: {by_day}")

# Spot-check one specific chunk's full metadata
sample_id, sample_meta = gap_chunks[0]
print(f"\nSample chunk {sample_id!r}: {sample_meta}")
