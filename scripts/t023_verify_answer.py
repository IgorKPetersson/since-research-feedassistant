"""T-023: real, end-to-end verification - a real packed chunk set from T-022/T-027's
retrieval, fed into a real qwen3:30b-a3b /api/chat call, via vg09.answer.generate_answer().

Run manually; makes real network calls to a local Ollama server and reads the real
data/chroma_store. Uses the evaluation anchor (today=2026-09-16, D-011) since this
exercises a real T-014 question.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.answer import generate_answer
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve

TODAY = date(2026, 9, 16)  # D-011: evaluation runs pin this explicitly


def run_question(question: str) -> None:
    date_range = resolve_date_range(question, TODAY)
    ranking = detect_recency_ranking(question)
    print(f"\n=== \"{question}\" ===")
    print(f"date_range={date_range}  ranking={ranking}")

    retrieval = retrieve(question, date_range=date_range, ranking=ranking)
    print(f"candidates_considered={retrieval.candidates_considered}  "
          f"chunks_packed={len(retrieval.chunks)}  total_tokens={retrieval.total_tokens}  "
          f"dropped_oversized={retrieval.dropped_oversized}")

    result = generate_answer(question, retrieval.chunks)
    print(f"done_reason={result.done_reason!r}  incomplete={result.incomplete}  "
          f"prompt_eval_count={result.prompt_eval_count}")
    print(f"reasoning length: {len(result.reasoning)} chars")
    print(f"answer:\n{result.answer}")


if __name__ == "__main__":
    run_question("Har NeoHorse nämnts de senaste två veckorna?")  # F05 - a real,
    # narrow, verifiable question: NeoHorse-1 (2609.08183) is the one real expected
    # source, already confirmed present in T-022's real candidate pool
