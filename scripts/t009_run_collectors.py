"""T-009: run the real HF and YouTube collectors against live data.

Confirms both collectors produce normalized Document objects with every
required field populated, and that they land in data/raw/. This is a small,
manual verification run - not the full historical pull (that's T-015's
backfill) and not a test suite (no test framework exists yet).

Makes real network calls; run it manually.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09 import hf_papers, youtube  # noqa: E402
from vg09.channels import CHANNELS  # noqa: E402
from vg09.document import raw_path  # noqa: E402

REQUIRED_FIELDS = ("id", "source", "url", "title", "feed_date", "text")


def check_document(doc) -> list[str]:
    missing = [f for f in REQUIRED_FIELDS if not getattr(doc, f)]
    return missing


def run_hf() -> None:
    print("== HF Daily Papers ==")
    # Today may be a weekend with zero entries (KB-002); walk back to find a
    # day that actually has papers.
    d = date.today()
    docs = []
    for _ in range(7):
        docs = hf_papers.collect_day(d)
        if docs:
            break
        d -= timedelta(days=1)

    if not docs:
        print("  No HF papers found in the last 7 days - unexpected, investigate.")
        return

    print(f"  {d.isoformat()}: {len(docs)} papers collected")
    sample = docs[0]
    missing = check_document(sample)
    path = raw_path(sample.source, sample.feed_date, sample.id)
    print(f"  sample id={sample.id!r} feed_date={sample.feed_date} title={sample.title!r}")
    print(f"  written to {path} (exists={path.exists()})")
    print(f"  missing required fields: {missing or 'none'}")


def run_youtube() -> None:
    print("\n== YouTube ==")
    handle, url = next(iter(CHANNELS.items()))
    docs = youtube.collect_channel(url, count=2)

    if not docs:
        print(f"  No videos collected for {handle} - unexpected, investigate.")
        return

    print(f"  {handle}: {len(docs)} videos collected")
    for doc in docs:
        missing = check_document(doc)
        path = raw_path(doc.source, doc.feed_date, doc.id)
        fallback_used = "\n\n" in doc.text and doc.title in doc.text[: len(doc.title) + 4]
        print(f"  id={doc.id!r} feed_date={doc.feed_date} title={doc.title!r}")
        print(f"  written to {path} (exists={path.exists()})")
        print(f"  missing required fields: {missing or 'none'}  fallback_shape={fallback_used}")


if __name__ == "__main__":
    run_hf()
    run_youtube()
