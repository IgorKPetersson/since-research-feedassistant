"""T-039: does the smaller chunk budget (11787, down from 13245 - NUM_PREDICT 2542 -> 4000)
cost the top of the ranking anything? T-028's check, redone.

Differences from `scripts/t028_verify_chunk_budget_impact.py`, deliberately:
- Uses the real `vg09.retrieval.pack_to_budget()` twice (once per budget), not a local
  re-implementation of its greedy loop - and since T-038 that function measures the real
  formatted source string ("[N] Title (url, feed date)\\n{text}"), not bare text, which
  T-028's script predates.
- Both budgets are run in the same process against the same candidates, so the anchor
  (`vg09.store.latest_feed_date()`, D-012) is identical by construction (KB-016) instead of
  being a hard-coded date that has to be kept in sync by hand.

Real network+GPU calls (bge-m3 embedding, qwen3 tokenizer via Ollama) against the real
Chroma store. Token counts are memoised so each distinct candidate text is measured once
across both packing runs.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ has no __init__.py

from t031_evaluation_harness import load_questions_with_facit

from vg09 import retrieval
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.store import latest_feed_date

OLD_BUDGET = 13245  # T-030
NEW_BUDGET = retrieval.CHUNK_BUDGET_TOKENS  # T-039
TOP_N = 5

retrieval.count_qwen_tokens = lru_cache(maxsize=None)(retrieval.count_qwen_tokens)


def main() -> None:
    questions = load_questions_with_facit()
    assert len(questions) == 15, f"expected 15 real questions, found {len(questions)}"
    assert NEW_BUDGET == 11787, f"expected T-039's budget, found {NEW_BUDGET}"

    today = latest_feed_date()
    print(f"Anchor (D-012): today={today}  ·  budgets: old={OLD_BUDGET}  new={NEW_BUDGET}\n")
    print("Fråga | packed old -> new | tokens old -> new | top-5 identical | new is prefix of old")

    all_top5_ok = True
    lost_total = 0
    for n in sorted(questions):
        q = questions[n]["question"]
        date_range = resolve_date_range(q, today)
        ranking = detect_recency_ranking(q)

        candidates = retrieval.query_candidates(q, date_range, retrieval.CANDIDATE_POOL_SIZE)
        deduped = retrieval.dedup_by_doc(retrieval.order_candidates(candidates, ranking))

        old_packed, old_total, _ = retrieval.pack_to_budget(deduped, OLD_BUDGET)
        new_packed, new_total, _ = retrieval.pack_to_budget(deduped, NEW_BUDGET)

        ref = [c.id for c in deduped[:TOP_N]]
        top5_ok = [c.id for c in new_packed[:TOP_N]] == ref == [c.id for c in old_packed[:TOP_N]]
        prefix_ok = [c.id for c in new_packed] == [c.id for c in old_packed][: len(new_packed)]
        all_top5_ok &= top5_ok and prefix_ok
        lost_total += len(old_packed) - len(new_packed)

        print(f"F{n:02d}   | {len(old_packed):>3} -> {len(new_packed):<3}       | "
              f"{old_total:>5} -> {new_total:<5}     | {top5_ok!s:<15} | {prefix_ok}")

    print(f"\nTop-{TOP_N} identical under the new budget for all 15 questions and the new "
          f"packed set is always a prefix of the old one: {all_top5_ok}")
    print(f"Chunks dropped by the budget cut, summed over the 15 questions: {lost_total}")


if __name__ == "__main__":
    main()
