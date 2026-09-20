"""T-025: small, pure logic pulled out of app.py so it's unit-testable without a
running Streamlit session - app.py itself is a thin rendering layer over this and the
rest of vg09/.
"""

from __future__ import annotations

from datetime import date


_MARKDOWN_SPECIAL_CHARS = "\\`*_[]"


def escape_markdown_link_text(text: str) -> str:
    """T-029: real HF/YouTube titles are free text pulled straight from a source's own
    API - not authored for this app - and can contain markdown-significant characters
    ("]" closes a `[text](url)` citation link's text portion early; a real example:
    "He Built The Ultimate Spy Tool (Free and Open-Source)"). Escaping keeps the
    rendered link intact regardless of what a real title contains. Backslash is escaped
    first so escaping the rest doesn't double-escape it."""
    result = text.replace("\\", "\\\\")
    for ch in _MARKDOWN_SPECIAL_CHARS[1:]:
        result = result.replace(ch, f"\\{ch}")
    return result


def describe_retrieval_mode(
    date_range: tuple[date, date] | None,
    ranking: bool,
    manual_override: tuple[date, date] | None,
) -> str:
    """Swedish, human-readable description of which of T-022's mechanisms actually
    fired for this answer - shown in the UI so the user can always see which one,
    not just the answer text. Priority matches `vg09.date_range.resolve_date_range()`:
    a manual override always wins over whatever was (or wasn't) interpreted."""
    if manual_override is not None:
        start, end = manual_override
        return f"Datumfilter (manuellt angivet): {start} – {end}"
    if date_range is not None:
        start, end = date_range
        return f"Datumfilter (tolkat från frågan): {start} – {end}"
    if ranking:
        return "Läge: sortering efter senaste (rankning, inget datumfilter)"
    return "Inget datumfilter — obegränsad sökning"
