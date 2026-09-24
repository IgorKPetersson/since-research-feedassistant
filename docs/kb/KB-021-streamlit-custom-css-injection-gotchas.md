# KB-021 — Custom CSS in Streamlit 1.64 loses to its own markdown styles unless scoped under `[data-testid]` with `!important`; `st.html()` strips `<link>`, so load fonts via `@import`

**Area:** UI (Streamlit) — custom CSS injection
**Status:** verified
**Date:** 2026-09-24  ·  **From:** T-045, T-046 / session 2026-09-24 §§ 11.2, 12.1

## Claim
Six behaviours of Streamlit 1.64.0, each found live and each silent, with no error:
1. `st.markdown(css, unsafe_allow_html=True)` where a `<link>` tag precedes `<style>`
   renders the CSS rules as visible page text.
2. `st.html()` injects `<style>` correctly but **strips `<link>` tags**, so a Google Font
   `<link>` never loads. `@import url(...)` as the first rule inside `<style>` works.
3. `html, body, .stApp { font-family: X !important }` does not win: Streamlit's
   `[data-testid="stMarkdownContainer"]` rule re-applies its own font with equal
   specificity and its own `!important`, and wins the tie. `[data-testid],
   [data-testid] *` does win.
4. That broad selector also overrides the Material icon font. Icons then render as their
   ligature names, e.g. the expander arrow shows as the text "keyboard_arrow_right".
   Fix: a later `[data-testid="stIconMaterial"] { font-family: 'Material Symbols
   Rounded' !important }`. The icon element does carry that testid.
5. `a.my-class { color: ...; text-decoration: none }` inside markdown loses to
   Streamlit's link rule (blue, underlined). It needs
   `[data-testid="stMarkdownContainer"] a.my-class` plus `!important` on colour and
   decoration.
6. `st.set_page_config(page_icon="path/to/file.svg")` works: Streamlit reads the file
   and serves it as a `data:image/svg+xml;base64,...` favicon
   (`streamlit/elements/lib/image_utils.py`).

## Evidence
All checked in the running app via Playwright `getComputedStyle` / DOM queries:
- (2) `document.querySelectorAll('link[href*="fonts.google"]')` was empty and
  `document.fonts` had no Instrument Sans; after `@import`, `document.fonts` listed it
  as loaded.
- (3) Walking `.app-name`'s ancestors showed `"Source Sans", sans-serif` coming from
  the `stMarkdownContainer` rule.
- (4) Screenshot showed overlapping ligature text; the element containing
  `keyboard_arrow_right` had `data-testid="stIconMaterial"`.
- (5) Chip computed `color: rgb(0, 84, 163)`, `text-decoration-line: underline` before;
  `rgb(26, 26, 26)` / `none` after.
- (6) The favicon `<link>` href decoded byte-identical to the header `<img>` built from
  the same file.

## Consequences
`vg09/ui_helpers.py`'s `CUSTOM_CSS` is injected with `st.html()`, loads the font with
`@import`, uses the `[data-testid]` selectors, and restores the icon font. Any new
styled element inside markdown needs the same `stMarkdownContainer` scoping.
`tests/test_ui_helpers.py` pins (2), (4) and (5) as regressions.

## Confidence and limits
Streamlit 1.64.0 only. Streamlit's `data-testid` names and internal rules are not a
public API and may change between versions. Re-check computed styles after any
Streamlit upgrade.
