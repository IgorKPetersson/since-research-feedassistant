"""T-013 verification (YouTube half): confirm the simulated-gap round trip
left no duplicates and the previously-removed videos are back with correct
metadata - whichever transcript path each one actually took this time."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import get_collection  # noqa: E402

GAP_DAY = "2026-09-10"
GAP_VIDEO_IDS = {"q9tpIc8PVKM", "SGodxQHnVxc", "n5bZHETCiJA"}

coll = get_collection()
all_rows = coll.get(limit=10000)
ids = all_rows["ids"]

print(f"collection.count() = {coll.count()}")
print(f"len(ids) = {len(ids)}")
print(f"unique ids = {len(set(ids))}")
print(f"No duplicate ids: {len(ids) == len(set(ids))}")

gap_chunks = [
    (id_, meta) for id_, meta in zip(ids, all_rows["metadatas"])
    if meta.get("source") == "youtube" and meta.get("feed_date") == GAP_DAY
]
print(f"\nChunks now present for {GAP_DAY}: {len(gap_chunks)}")

by_video = {}
for _id, meta in gap_chunks:
    by_video.setdefault(meta["doc_id"], []).append((_id, meta.get("text_source"), meta.get("fallback_reason")))

for video_id in sorted(GAP_VIDEO_IDS):
    chunks = by_video.get(video_id, [])
    text_sources = {c[1] for c in chunks}
    print(f"  {video_id}: {len(chunks)} chunk(s), text_source={text_sources}, "
          f"fallback_reason={chunks[0][2] if chunks else None}")

missing = GAP_VIDEO_IDS - set(by_video)
print(f"\nMissing video ids (should be empty): {missing}")
