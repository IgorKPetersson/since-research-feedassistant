# KB-035 — Numbered markers like `<<<SOURCE 22 BEGIN>>>` make qwen3 cite "Source 22" instead of [22]

**Area:** Local model behaviour — citation format
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-073

## Claim
`qwen3:30b-a3b` copies the wording of whatever labels a source in the prompt. With each
source wrapped in `<<<SOURCE N BEGIN>>>`/`<<<SOURCE N END>>>`, it wrote "Source 22" instead
of the `[22]` format the system prompt asks for, often enough that answers lost their
clickable chips; one answer had no `[N]` at all.

## Evidence
Same 42 answers per version (12 citation runs + 30 injection runs):
- no markers: 0 "Source N" citations without brackets, 0 answers without `[N]`
- numbered markers (two prompt wordings): 93 and 103 "Source N", 1 answer without `[N]` each
- `<<<BEGIN>>>`/`<<<END>>>` with no word or number, plus "never write "Source N" instead of
  [N]": 0 and 0
All 340 unit tests passed with the numbered markers; only the measurement showed it.

## Consequences
`format_source()` uses unnumbered markers; the number stays on the `[N]` line inside.
Any future prompt change is measured with `scripts/t073_citation_placement.py` and
`scripts/t073_injection_check.py`, counting "Source N" as well as `[N]`.

## Confidence and limits
One model, one day's data, 42 answers per version. A different label wording may behave
differently; the rule is to measure, not to trust the wording.
