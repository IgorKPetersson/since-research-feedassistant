# KB-022 — Instrument Sans on Google Fonts tops out at weight 700; `wght@800` returns HTTP 400

**Area:** UI — typeface (Google Fonts)
**Status:** verified
**Date:** 2026-09-24  ·  **From:** T-046 / session 2026-09-24 § 12.2

## Claim
Instrument Sans's weight axis ends at 700. Requesting 800 (or a range above 700) from
the Google Fonts CSS API fails outright, so "heavier than bold" isn't available for the
wordmark. CSS `font-weight: 800` would only get a browser-synthesised faux bold.

## Evidence
`fetch()` against `https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@<w>`:
`700` → 200 with `font-weight: 700`; `800` → 400; `400..900` → 400.

## Consequences
The "Since" wordmark stays at 700 (`vg09/ui_helpers.py`, `.app-name`). For more visual
weight the options are a larger size or a different face for the wordmark only.

## Confidence and limits
Checked once, 2026-09-24. Google could add weights to the family later.
