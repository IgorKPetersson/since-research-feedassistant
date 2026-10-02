"""T-048: run the presentation's demo questions through the real pipeline and print each
answer with its sources and timings, so the expected answers in docs/presentation.md are
checked against the data actually in the store. Real calls; nothing is written.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import latest_feed_date

QUESTIONS = [
    "Har Opus 5.5 nämnts de senaste två veckorna?",
    "Vad är nytt den 2 oktober?",
    "Vad har hänt med GUI agents den senaste månaden?",
    "Har Palantir nämnts i någon video?",
]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    today = latest_feed_date()
    print(f"anchor: {today}")
    for question in QUESTIONS:
        date_range = resolve_date_range(question, today)
        ranking = detect_recency_ranking(question)
        start = time.monotonic()
        retrieval = retrieve(question, date_range=date_range, ranking=ranking)
        retrieve_s = time.monotonic() - start
        start = time.monotonic()
        result = generate_answer(question, retrieval.chunks)
        generate_s = time.monotonic() - start
        citations = build_citations(result.answer, result.source_map)
        print(f"\n=== {question}")
        print(f"range={date_range} ranking={ranking} packed={len(retrieval.chunks)} "
              f"retrieve={retrieve_s:.1f}s generate={generate_s:.1f}s "
              f"done={result.done_reason} retries={result.retries}")
        print(result.answer)
        for c in citations.citations:
            print(f"  - {c.feed_date} {c.title}")


if __name__ == "__main__":
    main()
