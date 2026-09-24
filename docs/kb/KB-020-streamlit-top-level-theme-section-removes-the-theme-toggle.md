# KB-020 — A top-level `[theme]` section in `.streamlit/config.toml` removes the viewer's Light/Dark toggle; `[theme.light]` + `[theme.dark]` keep it

**Area:** UI (Streamlit) — theming
**Status:** verified
**Date:** 2026-09-24  ·  **From:** T-045 / session 2026-09-24 § 11.2

## Claim
In Streamlit 1.64.0, setting any colour under a bare `[theme]` section (we set only
`primaryColor`) makes the app one fixed custom theme. The main menu's System/Light/Dark
group disappears, and the OS `prefers-color-scheme` is ignored. Setting the same key
under both `[theme.light]` and `[theme.dark]` instead keeps the toggle and Streamlit's
own per-mode defaults for everything not set.

## Evidence
- With `[theme]\nprimaryColor = "#C17F1A"`: opened the main menu in Playwright and there
  was no Theme group. `browser_emulate_media(colorScheme: "dark")` still rendered the
  light background.
- With `[theme.light]` and `[theme.dark]`, each setting only `primaryColor`: the Theme
  group was back, and switching Dark/Light gave `.stApp` background `rgb(14, 17, 23)` /
  `rgb(255, 255, 255)`, with the accent applied in both.
- `theme.light` / `theme.dark` are listed as valid section patterns in Streamlit's own
  `streamlit/config.py` (grepped in `.venv`).

## Consequences
`.streamlit/config.toml` must keep the two per-mode sections. Collapsing them into one
`[theme]` "for simplicity" silently removes dark mode for every viewer.
`tests/test_ui_helpers.py` checks the accent appears in the file, not the section
shape, so a test wouldn't catch this; the comment in the file explains it.

## Confidence and limits
Streamlit 1.64.0, Chromium via Playwright, Windows. Checked twice (both configs). Other
Streamlit versions not checked.
