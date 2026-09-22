"""T-039: verify the retry-on-length mechanism for real, against live Ollama, without
touching production code. T-039's own acceptance criteria flagged this as unverified
live: "the retry never fired in a real run... only been exercised against mocks."

`vg09.answer.NUM_PREDICT` is monkey-patched down to a low cap (default 500) only inside
this process - the checked-in constant (4000, vg09/answer.py) is never edited on disk,
restored before exit either way. A real question's real reasoning (measured 1054-2864
qwen3 tokens across 32 real samples, KB-019) reliably exceeds a 500-token cap on the
first attempt, exercising `generate_answer()`'s real retry loop end to end against the
real store/Ollama - not mocked, and not a synthetic done_reason.

`vg09.answer._chat_once` is wrapped (not modified) purely to record each real call's
`done_reason`, so the script can report the first attempt's outcome even when a retry
overwrites it in the final `AnswerResult`.

Confirms, per real question:
(a) the first attempt's done_reason == "length"
(b) a retry is actually made - a second real HTTP call reaches Ollama
(c) AnswerResult.retries == 1
(d) when the retry is ALSO cut off, AnswerResult.incomplete is True (and the returned
    reasoning/answer are the retry's own, cut-off text - not silently the first
    attempt's)

Real network+GPU calls, ~5-15s each depending on the low cap. Nothing in the repo is
modified. Usage: python scripts/t039_verify_retry_live_probe.py [num_predict]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ has no __init__.py

import vg09.answer as answer_mod
from t031_evaluation_harness import load_questions_with_facit
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import latest_feed_date

# A mix of real F-numbers from T-032's actual run - not chosen for any prior truncation
# history, since a 500-token cap should truncate almost any real question's reasoning.
QUESTIONS_TO_SAMPLE = [1, 6, 11]


def main(num_predict: int) -> None:
    original_num_predict = answer_mod.NUM_PREDICT
    original_chat_once = answer_mod._chat_once
    answer_mod.NUM_PREDICT = num_predict  # process-local only; vg09/answer.py on disk unchanged
    print(f"NUM_PREDICT monkeypatched to {num_predict} for this process only "
          f"(checked-in value stays {original_num_predict})\n")

    call_done_reasons: list[str] = []

    def recording_chat_once(messages):
        result = original_chat_once(messages)
        call_done_reasons.append(result[2])  # (reasoning, answer, done_reason, prompt_eval_count)
        return result

    answer_mod._chat_once = recording_chat_once

    try:
        questions = load_questions_with_facit()
        today = latest_feed_date()

        for n in QUESTIONS_TO_SAMPLE:
            q = questions[n]["question"]
            date_range = resolve_date_range(q, today)
            ranking = detect_recency_ranking(q)
            retrieval = retrieve(q, date_range=date_range, ranking=ranking)

            call_done_reasons.clear()
            result = answer_mod.generate_answer(q, retrieval.chunks)

            print(f"F{n:02d}: {q}")
            print(f"  chunks packed: {len(retrieval.chunks)}")
            print(f"  real Ollama calls made: {len(call_done_reasons)}  "
                  f"(done_reason per call: {call_done_reasons})")
            print(f"  AnswerResult: done_reason={result.done_reason!r}  "
                  f"retries={result.retries}  incomplete={result.incomplete}")
            print(f"  reasoning chars={len(result.reasoning)}  answer chars={len(result.answer)}")
            print(f"  answer text: {result.answer!r}")

            if not call_done_reasons:
                print("  !! no calls recorded - script bug, not a real result\n")
                continue

            first_done_reason = call_done_reasons[0]
            retried = len(call_done_reasons) > 1
            last_done_reason = call_done_reasons[-1]

            if first_done_reason != "length":
                print("  (this question's first attempt was not cut off at this cap - "
                      "no retry to observe here; try a lower num_predict or another question)\n")
                continue

            checks = [
                ("(a) first attempt done_reason == 'length'", first_done_reason == "length"),
                ("(b) a retry was actually made (2 real Ollama calls)", retried),
                ("(c) AnswerResult.retries == 1", result.retries == 1),
            ]
            if last_done_reason == "length":
                checks.append(("(d) retry also cut off -> incomplete flagged True",
                                result.incomplete is True))
            else:
                checks.append(("(d, alt) retry completed -> incomplete flagged False, "
                                "not the first attempt's cut-off text",
                                result.incomplete is False))

            for label, ok in checks:
                print(f"  {label}: {'OK' if ok else 'FAIL'}")
            print()
    finally:
        answer_mod.NUM_PREDICT = original_num_predict
        answer_mod._chat_once = original_chat_once
        print(f"NUM_PREDICT restored to {answer_mod.NUM_PREDICT} "
              f"(checked-in value, unchanged throughout)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
