"""T-005: vector store date-range filtering feasibility test.

Inserts a small test collection into a local, embedded ChromaDB store
with a feed-date metadata field (per D-002 - feed date, not arXiv/original
publish date), then runs the same similarity query with and without a
date-range filter to confirm filtering actually restricts results.

Uses ChromaDB's PersistentClient (no server, no Docker - matches
docs/GOAL.md's non-goals). Throwaway collection under data/, not the
Phase 1 production schema.
"""

import json
from datetime import date
from pathlib import Path

import chromadb

STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "t005_chroma_store"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# All documents are about "retrieval" or "agents" so similarity search alone
# can't distinguish old from new - only the date filter can.
DOCS = [
    {"id": "d1", "text": "A new paper on date-aware retrieval for RAG systems.", "feed_date": date(2026, 6, 1)},
    {"id": "d2", "text": "A survey of retrieval-augmented generation techniques.", "feed_date": date(2026, 6, 15)},
    {"id": "d3", "text": "Improving retrieval accuracy with hybrid search methods.", "feed_date": date(2026, 8, 1)},
    {"id": "d4", "text": "A benchmark for evaluating retrieval quality over time.", "feed_date": date(2026, 8, 20)},
    {"id": "d5", "text": "Agentic retrieval pipelines for long-context questions.", "feed_date": date(2026, 9, 1)},
    {"id": "d6", "text": "Retrieval strategies for time-bound question answering.", "feed_date": date(2026, 9, 10)},
    {"id": "d7", "text": "A new autonomous coding agent released this week.", "feed_date": date(2026, 9, 12)},
    {"id": "d8", "text": "Comparing retrieval methods on recency-sensitive queries.", "feed_date": date(2026, 9, 14)},
]

QUERY_TEXT = "retrieval quality for time-sensitive questions"
# "last 2 weeks" relative to the latest feed_date in the set (2026-09-14)
RANGE_START = date(2026, 9, 1)
RANGE_END = date(2026, 9, 14)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(STORE_PATH))
    # Reset to a clean slate on every run rather than accumulating duplicate
    # inserts across runs.
    if "t005_docs" in [c.name for c in client.list_collections()]:
        client.delete_collection("t005_docs")
    coll = client.get_or_create_collection("t005_docs")

    coll.add(
        ids=[d["id"] for d in DOCS],
        documents=[d["text"] for d in DOCS],
        metadatas=[
            {
                "feed_date": d["feed_date"].isoformat(),
                "feed_date_ordinal": d["feed_date"].toordinal(),
            }
            for d in DOCS
        ],
    )

    unfiltered = coll.query(query_texts=[QUERY_TEXT], n_results=8)
    filtered = coll.query(
        query_texts=[QUERY_TEXT],
        n_results=8,
        where={
            "$and": [
                {"feed_date_ordinal": {"$gte": RANGE_START.toordinal()}},
                {"feed_date_ordinal": {"$lte": RANGE_END.toordinal()}},
            ]
        },
    )

    def summarize(result) -> list[dict]:
        return [
            {"id": id_, "feed_date": meta["feed_date"], "distance": round(dist, 4)}
            for id_, meta, dist in zip(
                result["ids"][0], result["metadatas"][0], result["distances"][0]
            )
        ]

    unfiltered_summary = summarize(unfiltered)
    filtered_summary = summarize(filtered)

    print(f"Query: {QUERY_TEXT!r}\n")
    print("Unfiltered (top hits, any date):")
    for r in unfiltered_summary:
        print(f"  {r['id']}  {r['feed_date']}  distance={r['distance']}")

    print(f"\nFiltered to [{RANGE_START.isoformat()}, {RANGE_END.isoformat()}]:")
    for r in filtered_summary:
        print(f"  {r['id']}  {r['feed_date']}  distance={r['distance']}")

    unfiltered_ids = {r["id"] for r in unfiltered_summary}
    filtered_ids = {r["id"] for r in filtered_summary}
    all_filtered_in_range = all(
        RANGE_START <= date.fromisoformat(r["feed_date"]) <= RANGE_END for r in filtered_summary
    )
    differ = unfiltered_ids != filtered_ids

    print(f"\nAll filtered results within range: {all_filtered_in_range}")
    print(f"Filtered and unfiltered result sets differ: {differ}")

    out = {
        "query": QUERY_TEXT,
        "range": [RANGE_START.isoformat(), RANGE_END.isoformat()],
        "unfiltered": unfiltered_summary,
        "filtered": filtered_summary,
        "all_filtered_in_range": all_filtered_in_range,
        "results_differ": differ,
    }
    out_path = DATA_DIR / "t005_vector_store_date_filter.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
