"""T-039: how long does qwen3:30b-a3b's reasoning actually get, and how often would
reasoning+answer exceed T-028's `num_predict` of 2542?

Re-runs the exact production pipeline (same retrieval, same prompt, same `num_ctx`,
default sampling) for the four T-032 arms that hit `done_reason=="length"` plus four
arms that did not, but with `num_predict` raised to 8000 and the response streamed, so
reasoning tokens and answer tokens can be counted separately. One streamed chunk is one
generated token; `eval_count` from the final chunk cross-checks the sum (it was consistently
3 higher than reasoning+answer chunks - special tokens). Nothing in the repo is modified.

Real network+GPU calls, ~25 s each. The run recorded in
docs/eval-results/2026-09-22-t039-reasoning-probe.jsonl (32 samples) is what
docs/DESIGN.md's T-039 table is computed from. It was made with a scratchpad copy of this
script that differed only in hard-coded paths and in comparing against `NUM_PREDICT`
directly (then 2542) instead of the `cap_to_compare` argument; this repo copy has not
itself been re-run.

Usage: python scripts/t039_reasoning_length_probe.py <output.jsonl>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ has no __init__.py

import requests

from t031_evaluation_harness import load_questions_with_facit
from vg09.answer import OLLAMA, SYSTEM_PROMPT, build_user_message, number_sources
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import CHAT_MODEL, NUM_CTX, retrieve
from vg09.store import latest_feed_date

PROBE_CAP = 8000

# The probe was run when NUM_PREDICT was 2542 and CHUNK_BUDGET_TOKENS 13245 - the packed
# context of these arms is only the same as in T-032's original run under that budget.
# (question no, arm, samples, role)
PLAN = [(6, "A", 5, "trunc"), (7, "A", 5, "trunc"), (11, "B", 5, "trunc"), (14, "A", 5, "trunc"),
        (1, "A", 3, "ctrl"), (4, "A", 3, "ctrl"), (5, "A", 3, "ctrl"), (15, "A", 3, "ctrl")]


def main(out: Path, cap_to_compare: int) -> None:
    questions = load_questions_with_facit()
    today = latest_feed_date()

    for n, arm, samples, role in PLAN:
        q = questions[n]["question"]
        dr = resolve_date_range(q, today) if arm == "A" else None
        rk = detect_recency_ranking(q) if arm == "A" else False
        r = retrieve(q, date_range=dr, ranking=rk)
        smap = number_sources(r.chunks)
        msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(q, smap)}]
        for s in range(samples):
            t0 = time.monotonic()
            think = ans = 0
            last: dict = {}
            with requests.post(f"{OLLAMA}/api/chat", stream=True, timeout=(10, 300), json={
                    "model": CHAT_MODEL, "messages": msgs, "stream": True, "think": True,
                    "options": {"num_ctx": NUM_CTX, "num_predict": PROBE_CAP}}) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    d = json.loads(line)
                    m = d.get("message", {})
                    if m.get("thinking"):
                        think += 1
                    if m.get("content"):
                        ans += 1
                    if d.get("done"):
                        last = d
            # T-041: the project's hard rule - every real Ollama call checks its real
            # prompt_eval_count against num_ctx and warns on truncation risk. This was
            # the one real call site in the repo that skipped it, found by adversarial review.
            pec = last.get("prompt_eval_count")
            if pec is not None:
                if pec >= NUM_CTX:
                    print(f"  !! TRUNCATION RISK: t039_reasoning_length_probe "
                          f"prompt_eval_count={pec} >= num_ctx={NUM_CTX}")
                elif pec >= 0.9 * NUM_CTX:
                    print(f"  !! close to num_ctx: t039_reasoning_length_probe "
                          f"prompt_eval_count={pec} ({100 * pec / NUM_CTX:.0f}% of "
                          f"num_ctx={NUM_CTX})")
            rec = dict(q=n, arm=arm, role=role, sample=s, chunks=len(r.chunks),
                       pec=last.get("prompt_eval_count"), think_chunks=think, answer_chunks=ans,
                       eval_count=last.get("eval_count"), done_reason=last.get("done_reason"),
                       total_would_exceed_cap=(last.get("eval_count", 0) > cap_to_compare),
                       elapsed=round(time.monotonic() - t0, 1))
            with out.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            print(rec, flush=True)
    print("DONE")


if __name__ == "__main__":
    # 2542 = the cap the recorded run compared against; the live NUM_PREDICT is now higher.
    main(Path(sys.argv[1]), cap_to_compare=2542)
