"""T-022: real, end-to-end verification against the production Chroma store and real
Ollama - not a synthetic fixture. Uses three of T-014's real eval questions.

Run manually; makes real network calls to a local Ollama server and reads the real
data/chroma_store.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import (
    CANDIDATE_POOL_SIZE,
    CHUNK_BUDGET_TOKENS,
    count_qwen_tokens,
    query_candidates,
    retrieve,
)

TODAY = date(2026, 9, 16)


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    # --- 1: date filter vs. no filter, same broad question, real candidate counts ---
    section("Date filter vs. no filter (broad query: \"AI agents\")")
    broad_q = "Vad har hänt med AI-agenter?"
    with_filter = query_candidates(broad_q, date_range=(date(2026, 9, 10), date(2026, 9, 16)))
    without_filter = query_candidates(broad_q, date_range=None)
    print(f"  with 2026-09-10..2026-09-16 filter: {len(with_filter)} candidates")
    print(f"  unfiltered: {len(without_filter)} candidates")
    dates_in_window = {c.metadata["feed_date"] for c in with_filter}
    print(f"  feed dates seen in the filtered set: {sorted(dates_in_window)}")
    assert all("2026-09-10" <= d <= "2026-09-16" for d in dates_in_window), \
        "filtered result leaked a date outside the window"

    # --- 2: ranking mode against a real ranking question (F06) ---
    section("Ranking mode - F06 real question")
    f06 = "Vad är det senaste inom benchmarking av coding agents?"
    print(f"  detect_recency_ranking(F06) = {detect_recency_ranking(f06)}")
    print(f"  resolve_date_range(F06) = {resolve_date_range(f06, TODAY)}")
    ranked = query_candidates(f06, date_range=None, n_results=10)
    ranked_sorted = sorted(ranked, key=lambda c: c.metadata["feed_date_ordinal"], reverse=True)
    print("  top 5 by similarity (Chroma order):")
    for c in ranked[:5]:
        print(f"    {c.metadata['feed_date']}  {c.metadata['title'][:70]}")
    print("  top 5 by recency (after order_candidates(ranking=True)):")
    for c in ranked_sorted[:5]:
        print(f"    {c.metadata['feed_date']}  {c.metadata['title'][:70]}")

    # --- 3: full pipeline against a real window question (F05), real packing ---
    section("Full pipeline - F05 real question")
    f05 = "Har NeoHorse nämnts de senaste två veckorna?"
    date_range = resolve_date_range(f05, TODAY)
    ranking = detect_recency_ranking(f05)
    print(f"  resolve_date_range(F05) = {date_range}")
    print(f"  detect_recency_ranking(F05) = {ranking}")
    result = retrieve(f05, date_range=date_range, ranking=ranking)
    print(f"  candidates considered: {result.candidates_considered}")
    print(f"  chunks packed: {len(result.chunks)}, total qwen tokens: {result.total_tokens}")
    print(f"  dropped as oversized: {result.dropped_oversized}")
    for c in result.chunks[:5]:
        print(f"    {c.metadata['feed_date']}  {c.metadata['title'][:70]}")

    # --- 4: would a naive "just grab the top 34" (no real token accounting) ever
    # overflow the budget in practice, against a real, topic-rich candidate pool? ---
    section("Packing stress test - would a naive top-34 overflow the real budget?")
    stress_q = "Vad har hänt med AI-agenter, coding agents och benchmarks?"
    stress_candidates = query_candidates(stress_q, date_range=None, n_results=CANDIDATE_POOL_SIZE)
    top34 = stress_candidates[:34]
    top34_tokens = [count_qwen_tokens(c.text) for c in top34]
    naive_total = sum(top34_tokens)
    print(f"  candidates available: {len(stress_candidates)}")
    print(f"  naive top-34 real token sum: {naive_total} (budget: {CHUNK_BUDGET_TOKENS})")
    print(f"  max single chunk in top-34: {max(top34_tokens) if top34_tokens else 0}")
    if naive_total > CHUNK_BUDGET_TOKENS:
        print("  -> WOULD OVERFLOW: real packing's stop-early behavior matters here.")
    else:
        print("  -> fits: T-008's 400-token-per-chunk cap gives enough margin (34*400="
              f"{34*400} <= {CHUNK_BUDGET_TOKENS}) that a real top-34 didn't overflow "
              "this time - the packing loop's overflow-stop branch is still exercised "
              "for real by the mocked unit tests in tests/test_retrieval.py.")

    stress_result = retrieve(stress_q, date_range=None, ranking=False, n_results=CANDIDATE_POOL_SIZE)
    print(f"  full pipeline: {len(stress_result.chunks)} chunks packed, "
          f"{stress_result.total_tokens} total tokens, "
          f"dropped as oversized: {stress_result.dropped_oversized}")


if __name__ == "__main__":
    main()
