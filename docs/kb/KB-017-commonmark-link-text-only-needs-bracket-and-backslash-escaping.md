# KB-017 — Under CommonMark, a markdown `[text](url)` link's text portion only needs `[`, `]` and backslash escaped — parentheses inside it are safe unescaped

**Area:** UI (Streamlit / markdown rendering)
**Status:** verified
**Date:** 2026-09-20  ·  **From:** T-029, Phase 2 adversarial review review

## Claim
A real, free-text title interpolated into a markdown link's `[text]` portion (e.g. a
citation: `f"[{title}]({url})"`) only risks breaking the link syntax from an unescaped
`[`, `]`, or backslash. Parentheses — `(` and `)` — inside the `[text]` portion do **not**
need escaping under CommonMark (the spec Streamlit's `st.markdown()` follows); they are
only special inside the separate `(url)` destination portion, not inside `[text]`.

## Evidence
Real title pulled from `data/raw/youtube/2026-09-16/S2VJU5DQqlU.json`: "He Built The
Ultimate Spy Tool (Free and Open-Source)" — contains unescaped parens, was flagged in
the adversarial review's initial review as a plausible risk to a rendered citation link. Investigated
against the CommonMark spec while implementing the fix (`vg09.ui_helpers.
escape_markdown_link_text()`, T-029): `[text]`'s content is delimited purely by the outer
`[`/`]` pair; parens inside it are ordinary characters with no special meaning there. Only
an unescaped `]` (closes the text portion early) or `[` (nesting ambiguity) is a real risk
in that position. Confirmed via `tests/test_ui_helpers.py::EscapeMarkdownLinkTextTests` —
the real parenthetical title round-trips through `escape_markdown_link_text()` with its
parens intact and unescaped, while a synthetic `"New Model [SOTA]"` title has both
brackets escaped.

## Consequences
`escape_markdown_link_text()` escapes `\`, `` ` ``, `*`, `_`, `[`, `]` (backslash first, so
the rest of the escaping isn't itself double-escaped) — not parens. A future reviewer
re-examining this code should not add paren-escaping expecting it to fix a real rendering
bug; it wouldn't be fixing anything, since parens in this position were never actually
broken.

## Confidence and limits
Confirmed against CommonMark's own spec reasoning and Streamlit's markdown renderer
behavior (which follows CommonMark/GFM), not against every markdown renderer that has ever
existed — some older/non-standard renderers do treat parens more aggressively inside link
text. Not a concern for this project (one renderer, Streamlit, in one deployment shape).
