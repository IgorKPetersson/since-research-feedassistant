"""T-013 verification: simulate a real gap (a few days the PC was "off" for)
by removing 2026-09-07 and 2026-09-08 from data/raw/hf/ and from the Chroma
store, and rolling the hf watermark back to before them. No YouTube calls.

Run once, then run scripts/t013_catch_up.py and scripts/t012_build_store.py
for real, then scripts/t013_verify_no_duplicates.py to confirm the gap closed
cleanly.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.store import get_collection  # noqa: E402
from vg09.watermark import write_watermark  # noqa: E402

RAW_HF = Path(__file__).resolve().parent.parent / "data" / "raw" / "hf"
GAP_DAYS = ["2026-09-07", "2026-09-08"]


def main() -> None:
    coll = get_collection()
    removed_ids = []

    for day in GAP_DAYS:
        day_dir = RAW_HF / day
        for f in sorted(day_dir.glob("*.json")):
            if f.name == "_done.json":
                continue
            arxiv_id = json.loads(f.read_text(encoding="utf-8"))["id"]
            removed_ids.append(f"hf:{arxiv_id}:0")
        shutil.rmtree(day_dir)
        print(f"Removed {day_dir} entirely (data/raw/ side)")

    coll.delete(ids=removed_ids)
    print(f"Removed {len(removed_ids)} chunks from Chroma")
    print(f"collection.count() after removal = {coll.count()}")

    write_watermark("hf", "2026-09-06")  # one day before the gap
    print("Rolled hf watermark back to 2026-09-06")


if __name__ == "__main__":
    main()
