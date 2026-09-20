"""T-028's last open acceptance criterion: does the smaller chunk budget (13261, down
from 13803) cost real recall, and does the top-5-vs-facit headline (11/14, T-027) still
hold?

Anchor: `today=2026-09-17` throughout - the SAME anchor T-027's own 11/14 headline was
measured against (`vg09.store.latest_feed_date()`'s real value, D-011). This is
deliberately NOT `docs/eval-questions.md`'s D-011 grading anchor (2026-09-16) - that
anchor answers a different, already-settled question (how the facit's own written
windows were computed) and must not be conflated with this one. A first attempt at this
script used 2026-09-16 by mistake and produced a misleading 10/14 - see T-028's ticket
notes.

Real network+GPU calls against the real Chroma store and real Ollama. To avoid doubling
those calls, each deduped candidate's real qwen3 token count is measured exactly once,
then the two budgets are simulated locally against that same cached count, using the
identical greedy stop-early algorithm `vg09.retrieval.pack_to_budget()` implements (a
candidate over budget alone is skipped, not fatal; the first candidate that would push
the running total over budget stops packing there).
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import (
    Candidate,
    count_qwen_tokens,
    dedup_by_doc,
    order_candidates,
    query_candidates,
)

TODAY = date(2026, 9, 17)  # T-027's real anchor - NOT D-011's 2026-09-16 grading anchor
OLD_BUDGET = 13803  # pre-T-028
NEW_BUDGET = 13261  # T-028 (NUM_PREDICT 2000 -> 2542)


def load_real_questions() -> dict[int, str]:
    text = Path("docs/eval-questions.md").read_text(encoding="utf-8")
    questions = {}
    for m in re.finditer(r"^Fr[aå]ga (\d+): (.+)$", text, re.MULTILINE):
        questions[int(m.group(1))] = m.group(2)
    return questions


def simulate_pack(candidates: list[Candidate], tokens: list[int], budget: int):
    packed_ids: list[str] = []
    dropped_oversized: list[str] = []
    total = 0
    for c, t in zip(candidates, tokens):
        if t > budget:
            dropped_oversized.append(c.id)
            continue
        if total + t > budget:
            break
        packed_ids.append(c.id)
        total += t
    return packed_ids, total, dropped_oversized


# T-027's own named checkpoints - the two questions it called out by exact real
# candidate-pool position - so this run can be confirmed to reproduce the same
# real ranking, not just a similar-looking headline number.
F15_EXPECTED_YOUTUBE_DOC = "YTG0rdHPTDE"
F06_EXPECTED_HF_DOC = "2609.08149"


def main() -> None:
    questions = load_real_questions()
    assert len(questions) == 15, f"expected 15 real questions, found {len(questions)}"

    print(f"Anchor: today={TODAY} (T-027's own anchor, NOT D-011's eval-grading anchor)")
    print(f"Budgets compared: old={OLD_BUDGET}  new={NEW_BUDGET}\n")

    rows = []
    top5_by_question: dict[int, list[Candidate]] = {}

    for n in sorted(questions):
        q = questions[n]
        date_range = resolve_date_range(q, TODAY)
        ranking = detect_recency_ranking(q)

        candidates = query_candidates(q, date_range=date_range)
        ordered = order_candidates(candidates, ranking)
        deduped = dedup_by_doc(ordered)

        tokens = [count_qwen_tokens(c.text) for c in deduped]

        old_ids, old_total, old_dropped = simulate_pack(deduped, tokens, OLD_BUDGET)
        new_ids, new_total, new_dropped = simulate_pack(deduped, tokens, NEW_BUDGET)

        top5 = deduped[:5]
        top5_by_question[n] = top5
        # direct proof, not assumption: the new budget's packed set still contains
        # every one of the top-5 candidates, in the same order
        top5_ids = [c.id for c in top5]
        top5_survives_new_budget = top5_ids == new_ids[: len(top5_ids)]

        changed = len(old_ids) != len(new_ids)
        rows.append(
            (n, q, date_range, ranking, len(candidates), len(deduped),
             len(old_ids), old_total, len(new_ids), new_total, changed,
             top5_survives_new_budget)
        )

        print(f"F{n:02d}: range={date_range} ranking={ranking}")
        print(f"      candidates={len(candidates)} deduped={len(deduped)}")
        print(f"      old(budget={OLD_BUDGET}): packed={len(old_ids)} tokens={old_total} "
              f"dropped_oversized={len(old_dropped)}")
        print(f"      new(budget={NEW_BUDGET}): packed={len(new_ids)} tokens={new_total} "
              f"dropped_oversized={len(new_dropped)}")
        if changed:
            print(f"      !! PACKED COUNT CHANGED: {len(old_ids)} -> {len(new_ids)}")
        print(f"      top-5 unchanged under new budget: {top5_survives_new_budget}")
        print()

    print("=== Summary: packed-chunk-count impact of the budget cut ===")
    any_changed = False
    for (n, q, _, _, _, _, old_n, _, new_n, _, changed, _) in rows:
        if changed:
            any_changed = True
            print(f"  F{n:02d}: {old_n} -> {new_n} chunks  <- {q}")
    if not any_changed:
        print("  No question's packed chunk count changed between the old and new budget.")

    print("\n=== T-027 checkpoint reproduction (direct, not assumed) ===")
    f15_top5_ids = [c.id for c in top5_by_question[15]]
    f15_hit = any(F15_EXPECTED_YOUTUBE_DOC in cid for cid in [c.metadata.get("doc_id", "")
                                                               for c in top5_by_question[15]])
    print(f"  F15 top-5 doc_ids: {[c.metadata.get('doc_id') for c in top5_by_question[15]]}")
    print(f"  F15: {F15_EXPECTED_YOUTUBE_DOC} in top-5 -> {f15_hit} "
          "(T-027 found this HIT, ranked 2nd)")

    f06_hit = any(F06_EXPECTED_HF_DOC in c.metadata.get("doc_id", "")
                  for c in top5_by_question[6])
    all_f06_ids = [c.metadata.get("doc_id") for c in top5_by_question[6]]
    print(f"  F06 top-5 doc_ids: {all_f06_ids}")
    print(f"  F06: {F06_EXPECTED_HF_DOC} in top-5 -> {f06_hit} (T-027 found this MISS)")


if __name__ == "__main__":
    main()
