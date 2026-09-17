"""T-013 verification (YouTube half): simulate a real gap by removing
2026-09-10's 3 real video documents (1 captions: q9tpIc8PVKM/theAIsearch, 2
whisper: SGodxQHnVxc + n5bZHETCiJA/NateBJones - a real mix of both transcript
paths) from data/raw/youtube/ and from the Chroma store, then rolling the
youtube watermark back to the day before.

Mirrors scripts/t013_simulate_gap.py's HF pattern exactly. Run once, then
scripts/t013_youtube_catch_up.py and scripts/t012_build_store.py for real,
then scripts/t013_verify_youtube_no_duplicates.py to confirm the gap closed
cleanly.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import get_collection  # noqa: E402
from vg09.watermark import write_watermark  # noqa: E402

RAW_YOUTUBE = Path(__file__).resolve().parent.parent / "data" / "raw" / "youtube"
GAP_DAY = "2026-09-10"


def main() -> None:
    coll = get_collection()

    day_dir = RAW_YOUTUBE / GAP_DAY
    removed_video_ids = []
    for f in sorted(day_dir.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        removed_video_ids.append((doc["id"], doc["text_source"]))
    shutil.rmtree(day_dir)
    print(f"Removed {day_dir} entirely (data/raw/ side): {removed_video_ids}")

    where = {"$and": [{"source": "youtube"}, {"feed_date": GAP_DAY}]}
    matches = coll.get(where=where)
    removed_chunk_ids = matches["ids"]
    coll.delete(ids=removed_chunk_ids)
    print(f"Removed {len(removed_chunk_ids)} chunks from Chroma for {GAP_DAY}")
    print(f"collection.count() after removal = {coll.count()}")

    write_watermark("youtube", "2026-09-09")  # one day before the gap
    print("Rolled youtube watermark back to 2026-09-09")


if __name__ == "__main__":
    main()
