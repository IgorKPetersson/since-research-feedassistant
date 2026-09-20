"""T-032: for each of T-014's 15 real questions, run the real pipeline twice - once
date-aware (exactly as `app.py` behaves: the question's own resolved date range/ranking
mode) and once plain (unfiltered similarity search only, `date_range=None`,
`ranking=False` forced) - and show both arms side by side against the same facit, so I
can judge `docs/GOAL.md`'s central claim directly.

No model-based grading, no automated pass/fail scoring. Reuses T-031's question/facit
loader so the two harnesses can't drift apart on what "the 15 real questions" means.

Run manually; makes real network/GPU calls against the real production store and real
Ollama - each question runs the full pipeline twice, so this costs roughly 2x T-031's
real run. Output goes to docs/eval-results/ - the project's own generated results,
tracked and committed (my review first), not fetched source data.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ has no __init__.py

from t031_evaluation_harness import describe_mode, load_questions_with_facit

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import latest_feed_date

OUTPUT_DIR = Path("docs/eval-results")


def render_arm(label: str, question: str, date_range, ranking: bool) -> str:
    retrieval = retrieve(question, date_range=date_range, ranking=ranking)
    start = time.monotonic()
    result = generate_answer(question, retrieval.chunks)
    elapsed = time.monotonic() - start
    citations = build_citations(result.answer, result.source_map)

    pct = 100 * result.prompt_eval_count / 16000
    print(f"    [{label}] prompt_eval_count={result.prompt_eval_count} ({pct:.0f}%)  "
          f"elapsed={elapsed:.1f}s  done_reason={result.done_reason}")

    lines = [f"### {label}", ""]
    lines.append(f"**Tolkat läge:** {describe_mode(date_range, ranking)}")
    lines.append(f"**Kandidater övervägda:** {retrieval.candidates_considered}  ·  "
                 f"**Chunks paketerade:** {len(retrieval.chunks)}  ·  "
                 f"**prompt_eval_count:** {result.prompt_eval_count} ({pct:.0f}% av num_ctx)  ·  "
                 f"**svarstid:** {elapsed:.1f}s  ·  "
                 f"**done_reason:** {result.done_reason}"
                 + (" ⚠ OFULLSTÄNDIGT" if result.incomplete else ""))
    lines.append("")
    lines.append("**Svar:**")
    lines.append("")
    lines.append(result.answer)
    lines.append("")
    lines.append("**Källor (med feed date, för att se varför läget gav detta resultat):**")
    lines.append("")
    if not citations.citations:
        lines.append("_Inga källor kunde kopplas till svaret._")
    for c in citations.citations:
        fallback = " _(endast titel/beskrivning)_" if c.is_fallback else ""
        lines.append(f"- **{c.feed_date}** — [{c.title}]({c.url}){fallback}")
    if citations.unlinked_references:
        lines.append("")
        lines.append(
            "_Hänvisningar i svaret som inte kunde kopplas till en källa: "
            + ", ".join(citations.unlinked_references) + "_"
        )
    lines.append("")
    return "\n".join(lines)


def render_question(n: int, question: str, facit: str) -> str:
    today = latest_feed_date()

    lines = [f"## Fråga {n:02d}", "", f"**Fråga:** {question}", "", "---", ""]

    date_range = resolve_date_range(question, today)
    ranking = detect_recency_ranking(question)
    lines.append(render_arm("Läge A — Datummedveten (produktionens beteende)",
                             question, date_range, ranking))
    lines.append("")

    lines.append(render_arm("Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)",
                             question, None, False))
    lines.append("")

    lines.append("**Facit (docs/eval-questions.md, oförändrat):**")
    lines.append("")
    lines.append(facit)
    lines.append("")
    lines.append("**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    questions = load_questions_with_facit()
    assert len(questions) == 15, f"expected 15 real questions, found {len(questions)}"

    today = latest_feed_date()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-t032-date-aware-vs-plain.md"

    header = [
        "# T-032 comparison — date-aware retrieval vs plain similarity search",
        "",
        f"Ankare (D-012, `vg09.store.latest_feed_date()`): **{today}**",
        "",
        "Samma 15 frågor, samma modell (`qwen3:30b-a3b`), körda genom hela pipelinen två "
        "gånger var: **Läge A** använder frågans egna tolkade datumfönster/rankningsläge "
        "(exakt som produktionen); **Läge B** kör obegränsad ren likhetssökning, inget "
        "datumfilter alls. Ingen modellbedömning, ingen automatisk poängsättning.",
        "",
        "---",
        "",
    ]

    sections = []
    for i, n in enumerate(questions, start=1):
        print(f"[{i}/{len(questions)}] Fråga {n:02d}...")
        sections.append(render_question(n, questions[n]["question"], questions[n]["facit"]))

    out_path.write_text("\n".join(header) + "\n".join(sections), encoding="utf-8")
    print(f"\nSkrev {len(questions)} frågor (2 lägen var) till {out_path}")


if __name__ == "__main__":
    main()
