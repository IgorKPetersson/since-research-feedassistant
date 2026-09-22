"""T-031: run all 15 of T-014's real questions through the real pipeline and write a
single human-readable Markdown report - one section per question, with the model's real
answer and sources placed directly alongside the facit's own grading criteria from
docs/eval-questions.md, so grading needs no cross-referencing between files.

No model-based grading, no automated pass/fail scoring - grading is my own
manual step. `today` is set explicitly via vg09.store.latest_feed_date() (D-012), once,
at the top of the run.

Run manually; makes real network/GPU calls against the real production store and real
Ollama. Output goes to docs/eval-results/ - the project's own generated results, not
fetched source data, so unlike data/raw/ this is tracked and committed (my review
first, per this project's own workflow, but the directory itself isn't gitignored).
"""

from __future__ import annotations

import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import latest_feed_date

EVAL_QUESTIONS_PATH = Path("docs/eval-questions.md")
OUTPUT_DIR = Path("docs/eval-results")


def load_questions_with_facit() -> dict[int, dict[str, str]]:
    """Reads docs/eval-questions.md live (not retyped) and returns, per question number,
    the exact question text (T-021's established regex) and its full facit block verbatim
    - everything from its own "### Fråga NN" heading up to the next one."""
    text = EVAL_QUESTIONS_PATH.read_text(encoding="utf-8")

    question_text = {}
    for m in re.finditer(r"^Fr[aå]ga (\d+): (.+)$", text, re.MULTILINE):
        question_text[int(m.group(1))] = m.group(2).strip()

    facit_blocks = {}
    headings = list(re.finditer(r"^### Fr[aå]ga (\d+)\s*$", text, re.MULTILINE))
    for i, m in enumerate(headings):
        n = int(m.group(1))
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[start:end].strip()
        # drop the leading "Fråga NN: ..." line - already shown separately as its own
        # "**Fråga:**" line, so this avoids showing the question text twice
        block = re.sub(r"^Fr[aå]ga \d+: .+\n+", "", block, count=1)
        facit_blocks[n] = block.strip()

    assert question_text.keys() == facit_blocks.keys(), (
        f"question/facit mismatch: {sorted(question_text)} vs {sorted(facit_blocks)}"
    )
    return {
        n: {"question": question_text[n], "facit": facit_blocks[n]}
        for n in sorted(question_text)
    }


def describe_mode(date_range, ranking: bool) -> str:
    if ranking:
        return "Rankningsläge (sortering efter senaste, inget datumfilter)"
    if date_range is not None:
        start, end = date_range
        return f"Datumfilter (tolkat från frågan): {start} .. {end}"
    return "Inget datumfilter, ingen rankning - obegränsad likhetssökning"


def render_question(n: int, question: str, facit: str) -> str:
    today = latest_feed_date()
    date_range = resolve_date_range(question, today)
    ranking = detect_recency_ranking(question)

    retrieval = retrieve(question, date_range=date_range, ranking=ranking)
    start = time.monotonic()
    result = generate_answer(question, retrieval.chunks)
    elapsed = time.monotonic() - start
    citations = build_citations(result.answer, result.source_map)

    pct = 100 * result.prompt_eval_count / 16000
    print(f"    prompt_eval_count={result.prompt_eval_count} ({pct:.0f}% of num_ctx)  "
          f"generate_answer elapsed={elapsed:.1f}s  done_reason={result.done_reason}  "
          f"retries={result.retries}")

    lines = [f"## Fråga {n:02d}", "", f"**Fråga:** {question}", ""]
    lines.append(f"**Tolkat läge:** {describe_mode(date_range, ranking)}")
    lines.append(f"**Kandidater övervägda:** {retrieval.candidates_considered}  ·  "
                 f"**Chunks paketerade:** {len(retrieval.chunks)}  ·  "
                 f"**prompt_eval_count:** {result.prompt_eval_count} ({pct:.0f}% av num_ctx)  ·  "
                 f"**svarstid:** {elapsed:.1f}s  ·  "
                 f"**done_reason:** {result.done_reason}  ·  "
                 f"**omförsök:** {result.retries}"
                 + (" ⚠ OFULLSTÄNDIGT" if result.incomplete else ""))
    lines.append("")
    lines.append("**Svar (modellens riktiga, genererade svar):**")
    lines.append("")
    lines.append(result.answer)
    lines.append("")
    lines.append("**Källor:**")
    lines.append("")
    if not citations.citations:
        lines.append("_Inga källor kunde kopplas till svaret._")
    for c in citations.citations:
        fallback = " _(endast titel/beskrivning)_" if c.is_fallback else ""
        arxiv = f", arXiv {c.arxiv_published_at[:10]}" if c.arxiv_published_at else ""
        lines.append(f"- {c.feed_date} — [{c.title}]({c.url}){arxiv}{fallback}")
    if citations.unlinked_references:
        lines.append("")
        lines.append(
            "_Hänvisningar i svaret som inte kunde kopplas till en källa: "
            + ", ".join(citations.unlinked_references) + "_"
        )
    if citations.descriptive_ranges:
        lines.append("")
        lines.append(
            "_Beskrivande intervall (t.ex. \"alla N källor\") - inte expanderade till "
            "källhänvisningar, D-015: " + ", ".join(citations.descriptive_ranges) + "_"
        )
    lines.append("")
    lines.append("**Facit (docs/eval-questions.md, oförändrat):**")
    lines.append("")
    lines.append(facit)
    lines.append("")
    lines.append("**Bedömning:** ☐ Godkänt  ☐ Fel")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    questions = load_questions_with_facit()
    assert len(questions) == 15, f"expected 15 real questions, found {len(questions)}"

    today = latest_feed_date()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-t031-harness.md"

    header = [
        "# T-031 evaluation harness — real run",
        "",
        f"Ankare (D-012, `vg09.store.latest_feed_date()`): **{today}**",
        "",
        "Ingen modellbedömning, ingen automatisk poängsättning — varje sektion nedan "
        "innehåller frågan, det tolkade läget, det riktiga genererade svaret, källorna, "
        "och facit sida vid sida för manuell bedömning.",
        "",
        "---",
        "",
    ]

    sections = []
    for i, n in enumerate(questions, start=1):
        print(f"[{i}/{len(questions)}] Fråga {n:02d}...")
        sections.append(render_question(n, questions[n]["question"], questions[n]["facit"]))

    out_path.write_text("\n".join(header) + "\n".join(sections), encoding="utf-8")
    print(f"\nSkrev {len(questions)} frågor till {out_path}")


if __name__ == "__main__":
    main()
