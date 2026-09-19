"""T-021: extract a feed-date range from a free-text question, in Swedish.

Rule-based, stdlib-only - no new dependency, no LLM call. The vocabulary is small and
fixed (a handful of relative-time phrases: "senaste N veckorna/dagarna", "senaste
veckan"/"manaden", "forra veckan", "den D <manad>") because that's what T-014's real
15-question eval set actually uses (docs/eval-questions.md); this is not a general
natural-language date parser and isn't meant to become one.

Returns `None`, deliberately, whenever the question doesn't name a range with enough
confidence to act on - a bare plural with no number ("de senaste veckorna") is exactly
this case: ambiguous by construction, not a number this module should guess at. `None`
is a real, valid result: the caller falls back to the full (unbounded) window plus
whatever the UI's manual date picker sets (T-021's other half, wired in by T-025).

`today` is always an explicit parameter, never `date.today()` internally - so relative
phrases resolve the same way on every run against the frozen eval dataset (T-020),
regardless of the real wall-clock date. Callers building the real UI pass the real
`date.today()` explicitly; tests and eval runs pass a fixed date.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

DateRange = tuple[date, date]

_NUMBER_WORDS = {
    "en": 1, "ett": 1,
    "två": 2, "tva": 2,
    "tre": 3,
    "fyra": 4,
    "fem": 5,
    "sex": 6,
    "sju": 7,
    "åtta": 8, "atta": 8,
    "nio": 9,
    "tio": 10,
}

_MONTH_NAMES = {
    "januari": 1, "februari": 2, "mars": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "augusti": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}

_NUM = r"(\d+|" + "|".join(_NUMBER_WORDS) + r")"


def _parse_number(token: str) -> int:
    if token.isdigit():
        return int(token)
    return _NUMBER_WORDS[token]


def _subtract_months(d: date, months: int) -> date:
    """One or more calendar months back, day-clamped for a shorter target month
    (e.g. Mar 31 - 1 month -> Feb 28/29, not an error and not Mar 3)."""
    month_index = d.month - 1 - months  # 0-based, can go negative
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = d.day
    while True:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1  # walk back to the last valid day of that month


def _last_n_days(today: date, n: int) -> DateRange:
    """An n-day window ending today, inclusive - e.g. n=7 gives today and the 6 days
    before it, matching docs/eval-questions.md's "senaste veckan" convention exactly."""
    return today - timedelta(days=n - 1), today


def extract_date_range(question: str, today: date) -> DateRange | None:
    q = question.lower()

    # Absolute date: "den 16 september" - resolves to this year unless that's still in
    # the future relative to `today`, in which case it must mean last year.
    m = re.search(r"\bden\s+(\d{1,2})\s+(" + "|".join(_MONTH_NAMES) + r")\b", q)
    if m:
        day = int(m.group(1))
        month = _MONTH_NAMES[m.group(2)]
        year = today.year
        try:
            d = date(year, month, day)
        except ValueError:
            return None  # not a real calendar date - don't guess
        if d > today:
            d = date(year - 1, month, day)
        return d, d

    # "senaste/de senaste <N> veckorna/dagarna/manaderna" - a number is required here;
    # a bare plural with no number ("senaste veckorna") does NOT match this pattern and
    # falls through to the "no discernible range" case at the end, deliberately.
    m = re.search(r"senaste\s+" + _NUM + r"\s+veckorna", q)
    if m:
        return _last_n_days(today, _parse_number(m.group(1)) * 7)

    m = re.search(r"senaste\s+" + _NUM + r"\s+dagarna", q)
    if m:
        return _last_n_days(today, _parse_number(m.group(1)))

    m = re.search(r"senaste\s+" + _NUM + r"\s+m[aå]naderna", q)
    if m:
        n = _parse_number(m.group(1))
        return _subtract_months(today, n), today

    # "senaste veckan" (singular) / "forra veckan" - both mean the same 7-day window.
    if re.search(r"\b(senaste\s+veckan|f[oö]rra\s+veckan)\b", q):
        return _last_n_days(today, 7)

    # "senaste manaden" (singular) - one calendar month back, not a fixed 30 days
    # (matches docs/eval-questions.md's already-written convention: 2026-08-16 for a
    # 2026-09-16 "today", which is a calendar month, not 30 raw days).
    if re.search(r"\bsenaste\s+m[aå]naden\b", q):
        return _subtract_months(today, 1), today

    return None


def resolve_date_range(
    question: str, today: date, manual_override: DateRange | None = None
) -> DateRange | None:
    """The one function T-022 (retrieval) and T-025 (the chat UI) both call - the
    manual override, whenever the UI's date picker sets one, always wins over
    whatever (if anything) was extracted from the question text. `None` either way
    means "no range" - retrieval runs unfiltered by date, per T-021's acceptance
    criteria (no range is ever invented)."""
    if manual_override is not None:
        return manual_override
    return extract_date_range(question, today)
