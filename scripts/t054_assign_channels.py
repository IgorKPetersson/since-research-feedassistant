"""T-054: one-time migration - give every YouTube document fetched before T-054 its
`channel`, by listing each configured channel's video ids once and matching.

Rewrites only the `channel` key of matching files under data/raw/youtube/. Safe to
re-run: files that already have a channel are left alone. Reports every video it could
not assign instead of guessing. Makes one real request per channel; run
scripts/t012_build_store.py afterwards so the store's metadata follows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09 import sources
from vg09.document import RAW_DIR
from vg09.youtube import list_video_ids

LIST_COUNT = 200  # well past the ~60 videos a channel could have posted in the window


def main() -> None:
    owner: dict[str, str] = {}
    for handle, url in sources.load().channels.items():
        ids = list_video_ids(url, LIST_COUNT)
        print(f"@{handle}: {len(ids)} videos listed")
        for video_id in ids:
            owner[video_id] = handle

    assigned: dict[str, int] = {}
    already = 0
    unassigned: list[str] = []
    for path in sorted((RAW_DIR / "youtube").rglob("*.json")):
        if path.name.endswith(".pending.json"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("channel"):
            already += 1
            continue
        handle = owner.get(doc["id"])
        if handle is None:
            unassigned.append(f"{doc['id']} ({doc['feed_date']}) {doc['title']}")
            continue
        doc["channel"] = handle
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        assigned[handle] = assigned.get(handle, 0) + 1

    print(f"\nassigned now: {assigned} (total {sum(assigned.values())})")
    print(f"already had a channel: {already}")
    print(f"could not assign: {len(unassigned)}")
    for line in unassigned:
        print(f"  {line}".encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
