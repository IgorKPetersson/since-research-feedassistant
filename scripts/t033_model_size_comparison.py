"""T-033: for each of T-014's 15 real questions, the real production retrieval
(date-aware, exactly as `app.py` behaves) runs *once* - then the same packed chunks are
sent through both chat models in D-005's VRAM-differentiated pair (`qwen3:30b-a3b`,
`qwen3:8b`), so only the model varies, never what it was given to work with.

No model-based grading, no automated pass/fail scoring. Reuses T-031's question/facit
loader, and T-032's per-arm rendering shape (svarstid/done_reason/omförsök, källor,
unlinked/descriptive-range notes), adapted for two models instead of two retrieval
modes.

Run manually; makes real network/GPU calls against the real production store and real
Ollama. Every question alternates model (A then B), so every single call is a real
model switch - Ollama unloads the previous model and loads the other one (KB-003's
original finding about this pair) - elapsed time per call is measured and reported for
real, not assumed away. Output goes to docs/eval-results/.
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
from vg09.retrieval import CHAT_MODEL, NUM_CTX, retrieve
from vg09.store import latest_feed_date

OUTPUT_DIR = Path("docs/eval-results")

MODEL_LARGE = CHAT_MODEL  # qwen3:30b-a3b, ~20GB VRAM, MoE - D-005, production's default
MODEL_SMALL = "qwen3:8b"  # ~6GB VRAM, dense - D-005's other half of the pair

# T-039: (retries made, still cut off after the last attempt) for every arm run, so the
# output header can state totals without re-parsing the rendered text.
ARM_STATS: list[tuple[int, bool]] = []
# T-033: real elapsed time per call, per model - every call is a real model switch
# (questions alternate A/B), so this is real reload-inclusive latency, not raw
# generation time alone (KB-003's original finding about this specific pair).
ELAPSED_BY_MODEL: dict[str, list[float]] = {MODEL_LARGE: [], MODEL_SMALL: []}


def render_arm(label: str, model: str, question: str, chunks) -> str:
    start = time.monotonic()
    result = generate_answer(question, chunks, model=model)
    elapsed = time.monotonic() - start
    ELAPSED_BY_MODEL[model].append(elapsed)
    citations = build_citations(result.answer, result.source_map)
    ARM_STATS.append((result.retries, result.incomplete))

    pct = 100 * result.prompt_eval_count / NUM_CTX
    print(f"    [{label}] model={model} prompt_eval_count={result.prompt_eval_count} "
          f"({pct:.0f}%)  elapsed={elapsed:.1f}s  done_reason={result.done_reason}  "
          f"retries={result.retries}")

    lines = [f"### {label} (`{model}`)", ""]
    lines.append(f"**prompt_eval_count:** {result.prompt_eval_count} ({pct:.0f}% av num_ctx)  ·  "
                 f"**svarstid (inkl. ev. modellbyte):** {elapsed:.1f}s  ·  "
                 f"**done_reason:** {result.done_reason}  ·  "
                 f"**omförsök:** {result.retries}"
                 + (" ⚠ OFULLSTÄNDIGT" if result.incomplete else ""))
    lines.append("")
    lines.append("**Svar:**")
    lines.append("")
    lines.append(result.answer)
    lines.append("")
    lines.append("**Källor:**")
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
    if citations.descriptive_ranges:
        lines.append("")
        lines.append(
            "_Beskrivande intervall (t.ex. \"alla N källor\") - inte expanderade till "
            "källhänvisningar, D-015: " + ", ".join(citations.descriptive_ranges) + "_"
        )
    lines.append("")
    return "\n".join(lines)


def render_question(n: int, question: str, facit: str) -> str:
    today = latest_feed_date()
    date_range = resolve_date_range(question, today)
    ranking = detect_recency_ranking(question)
    # T-033's own point: retrieval runs ONCE, shared between both arms below, so only
    # the model varies - never the retrieved chunks.
    retrieval = retrieve(question, date_range=date_range, ranking=ranking)

    lines = [f"## Fråga {n:02d}", "", f"**Fråga:** {question}", ""]
    lines.append(f"**Tolkat läge (delat mellan båda modellerna):** "
                 f"{describe_mode(date_range, ranking)}")
    lines.append(f"**Kandidater övervägda:** {retrieval.candidates_considered}  ·  "
                 f"**Chunks paketerade:** {len(retrieval.chunks)} (identiska för båda "
                 f"modellerna nedan)")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append(render_arm("Modell A — ~20GB VRAM, MoE, D-005", MODEL_LARGE, question,
                             retrieval.chunks))
    lines.append("")
    lines.append(render_arm("Modell B — ~6GB VRAM, dense, D-005", MODEL_SMALL, question,
                             retrieval.chunks))
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
    out_path = OUTPUT_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-t033-model-size-comparison.md"

    sections = []
    for i, n in enumerate(questions, start=1):
        print(f"[{i}/{len(questions)}] Fråga {n:02d}...")
        sections.append(render_question(n, questions[n]["question"], questions[n]["facit"]))

    calls = len(ARM_STATS)
    retries_made = sum(r for r, _ in ARM_STATS)
    still_cut = sum(1 for _, incomplete in ARM_STATS if incomplete)
    totals = (f"Körningar: {calls}  ·  omförsök gjorda: {retries_made} "
              f"({sum(1 for r, _ in ARM_STATS if r)} körningar)  ·  fortfarande avklippta "
              f"efter omförsök: {still_cut}")

    def model_stats(model: str) -> str:
        times = ELAPSED_BY_MODEL[model]
        avg = sum(times) / len(times)
        return f"`{model}`: min {min(times):.1f}s · max {max(times):.1f}s · avg {avg:.1f}s"

    reload_note = (
        "Svarstider per modell, inklusive eventuellt modellbyte (varje fråga växlar "
        "modell A->B, så varje anrop är en potentiell omladdning, KB-003): "
        + model_stats(MODEL_LARGE) + "  ·  " + model_stats(MODEL_SMALL)
    )

    header = [
        "# T-033 comparison — qwen3:30b-a3b vs qwen3:8b (D-005's VRAM-differentiated pair)",
        "",
        f"Ankare (D-012, `vg09.store.latest_feed_date()`): **{today}**",
        "",
        "Samma 15 frågor, samma verkliga produktions-retrieval (datummedveten, exakt som "
        "produktionen) - hämtningen körs EN gång per fråga, och exakt samma paketerade "
        "chunks skickas till båda modellerna: endast modellen varierar, inte vad den fick "
        "att arbeta med. Ingen modellbedömning, ingen automatisk poängsättning.",
        "",
        f"**{totals}**",
        "",
        f"**{reload_note}**",
        "",
        "---",
        "",
    ]

    out_path.write_text("\n".join(header) + "\n".join(sections), encoding="utf-8")
    print(f"\n{totals}")
    print(reload_note)
    print(f"Skrev {len(questions)} frågor (2 modeller var) till {out_path}")


if __name__ == "__main__":
    main()
