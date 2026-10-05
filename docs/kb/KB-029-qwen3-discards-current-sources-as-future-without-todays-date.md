# KB-029 — Without today's date in the prompt, qwen3 assumes a training-era date and discards current sources as "from the future"

**Area:** Local model behaviour — date awareness
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-061 / session 2026-10-05 § 3.1

## Claim
`qwen3:30b-a3b` has no idea what today is. Given correctly retrieved sources dated today
and no date in the prompt, it reasons that today is "a date in 2023 or 2024", calls the
sources "a future date", and answers without citing them.

## Evidence
"What has happebned with Ai today?" (me, in the app, 2026-10-05): retrieval
returned 34 excerpts, all with feed date 2026-10-05. The answer rejected them as future
and cited nothing. After adding one line to the user message (today's date, and that the
sources were selected for the applied range and must not be discarded for their date),
two re-runs through the pipeline cited 10 and 4 sources, both summarising that day's
papers. The line costs 63 tokens (`prompt_eval_count` 191 → 254).

## Consequences
- `generate_answer()` always tells the model today's date and the applied range (T-061);
  the evaluation passes the frozen anchor (2026-09-17) as `today` (T-069), so eval answers
  are told the same thing the app's are.
- A date alone is not enough for weekday phrases: the model named 2026-10-04 a Tuesday in
  one answer and a Friday in another (it was a Sunday). The weekday is now given too (T-066).
- Related, not fixed: an old video's "next week is OpenAI DevDay" was presented as still
  upcoming. The model reads relative time in a source against "now", not the source's date.

## Confidence and limits
One model (`qwen3:30b-a3b`), one question, reproduced before the fix in my run and
fixed in two runs after. Not tested on `qwen3:8b`. No unit test could have caught it:
retrieval was correct, only the answer was wrong.
