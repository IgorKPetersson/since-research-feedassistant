"""T-030/D-013: real, end-to-end verification that a question asked in Swedish still
produces an answer in English - the language policy is enforced in `vg09.answer.
SYSTEM_PROMPT`, not just asserted statically in a unit test.

Run manually; makes real network calls against the real production store and real
Ollama. Anchor: `vg09.store.latest_feed_date()`, per D-012 (production and evaluation
share one anchor now - no hand-pinned date here).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.answer import generate_answer
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import latest_feed_date

# Real Swedish questions, spanning more than one T-014 question type - not retyped from
# docs/eval-questions.md verbatim (those are the frozen eval set), but the same real
# shape and topic (F13/F15-adjacent).
QUESTIONS = [
    "Vad har hänt med AI-agenter den senaste veckan?",
    "Har Palantir nämnts i någon video?",
]


def looks_english(text: str) -> bool:
    """Cheap, real signal rather than a language-detection dependency: common Swedish
    letters/words that essentially never appear in an English answer of any length."""
    swedish_markers = ["å", "ä", "ö", " och ", " är ", " inte ", " den ", " det "]
    lowered = text.lower()
    return not any(m in lowered for m in swedish_markers)


def main() -> None:
    today = latest_feed_date()
    print(f"Anchor (D-012, latest_feed_date()): {today}\n")

    all_english = True
    for question in QUESTIONS:
        date_range = resolve_date_range(question, today)
        ranking = detect_recency_ranking(question)
        retrieval = retrieve(question, date_range=date_range, ranking=ranking)
        result = generate_answer(question, retrieval.chunks)

        english = looks_english(result.answer)
        all_english = all_english and english
        print(f"=== \"{question}\" (asked in Swedish) ===")
        print(f"answer:\n{result.answer}\n")
        print(f"looks_english: {english}\n")

    print(f"All {len(QUESTIONS)} answers in English: {all_english}")


if __name__ == "__main__":
    main()
