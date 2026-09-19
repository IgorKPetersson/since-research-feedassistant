"""T-024: real, end-to-end verification - a real answer (T-023) through
vg09.citations.build_citations(), against the real production store and real Ollama.

Run manually; makes real network calls. Uses the evaluation anchor (D-011,
today=2026-09-16) since this exercises a real T-014 question.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve

TODAY = date(2026, 9, 16)


def run_question(question: str) -> None:
    date_range = resolve_date_range(question, TODAY)
    ranking = detect_recency_ranking(question)
    retrieval = retrieve(question, date_range=date_range, ranking=ranking)

    result = generate_answer(question, retrieval.chunks)
    print(f"\n=== \"{question}\" ===")
    print(f"answer:\n{result.answer}\n")

    citations = build_citations(result.answer, result.source_map)
    print(f"citations ({len(citations.citations)}):")
    for c in citations.citations:
        fallback = " [FALLBACK]" if c.is_fallback else ""
        arxiv = f", arxiv {c.arxiv_published_at}" if c.arxiv_published_at else ""
        print(f"  - {c.title} ({c.feed_date}{arxiv}){fallback}\n    {c.url}")
    print(f"unlinked references: {citations.unlinked_references}")


if __name__ == "__main__":
    run_question("Har NeoHorse nämnts de senaste två veckorna?")  # F05 - real, narrow,
    # verifiable: NeoHorse-1 (2609.08183) is the one expected source
    run_question("Har Palantir nämnts i någon video?")  # F12 - a real YouTube citation,
    # to confirm a real &t= timestamp survives into the citation unmodified
