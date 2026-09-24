"""T-021/T-043: extract a feed-date range from a free-text question, in Swedish or
English.

Rule-based, stdlib-only - no new dependency, no LLM call. The vocabulary is small and
fixed (a handful of relative-time phrases per language) because that's what T-014's
real 15-question eval set actually uses (docs/eval-questions.md, Swedish) plus its real
English translations (T-043, docs/eval-results/2026-09-24-t043-english-date-
extraction.md); this is not a general natural-language date parser and isn't meant to
become one.

T-043: the UI is English by default now (D-016), and D-016 itself flagged this as a
real bug, not a risk to accept - the project's core relative-time feature was silently
off for every non-Swedish question. English gets its own real vocabulary, not a 1:1
translation of the Swedish regexes - "senaste" is one Swedish word doing two jobs
(window and ranking, disambiguated by what follows it); natural English already has two
different words for those two jobs ("last"/"past" for a window, "latest"/"most recent"
for ranking), so the English patterns use those instead of overloading one word. Same
underlying rules either way: a calendar month for "month" (`_subtract_months()`, not a
fixed 30 days), and a bare plural with no number ("recent weeks") stays unresolvable
rather than guessed - `None` is a real, valid result in both languages.

Returns `None`, deliberately, whenever the question doesn't name a range with enough
confidence to act on - a bare plural with no number ("de senaste veckorna" / "recent
weeks") is exactly this case: ambiguous by construction, not a number this module
should guess at. `None` is a real, valid result: the caller falls back to the full
(unbounded) window plus whatever the UI's manual date picker sets (T-021's other half,
wired in by T-025).

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


# T-043: English number words and month names, same closed vocabulary approach as the
# Swedish side above - digits work too ("2 weeks"), but the real English translations
# of docs/eval-questions.md's questions (T-043's own verification) write them out
# ("the last two weeks"), so word forms are supported the same way _NUMBER_WORDS
# already does for Swedish.
_EN_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_EN_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

_EN_NUM = r"(\d+|" + "|".join(_EN_NUMBER_WORDS) + r")"


def _parse_number_en(token: str) -> int:
    if token.isdigit():
        return int(token)
    return _EN_NUMBER_WORDS[token]


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

    # T-043: English. Checked after every Swedish pattern above, never instead of them -
    # a Swedish question is fully unaffected by anything below.

    # Absolute date: "September 16"/"September 16th" (month-then-day, the common
    # English order) or "the 16th of September" (day-then-month) - same "still in the
    # future -> must mean last year" rule as the Swedish "den D <manad>" case.
    month = day = None
    m = re.search(r"\b(" + "|".join(_EN_MONTH_NAMES) + r")\s+(\d{1,2})(?:st|nd|rd|th)?\b", q)
    if m:
        month, day = _EN_MONTH_NAMES[m.group(1)], int(m.group(2))
    else:
        m = re.search(
            r"\bthe\s+(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(" + "|".join(_EN_MONTH_NAMES) + r")\b", q
        )
        if m:
            day, month = int(m.group(1)), _EN_MONTH_NAMES[m.group(2)]
    if month is not None:
        year = today.year
        try:
            d = date(year, month, day)
        except ValueError:
            return None  # not a real calendar date - don't guess
        if d > today:
            d = date(year - 1, month, day)
        return d, d

    # "the last/past N weeks/days/months" - a number is required here; a bare plural
    # with no number ("recent weeks") does NOT match and falls through, deliberately -
    # the same ambiguous-by-design case as Swedish's "senaste veckorna".
    m = re.search(r"\b(?:last|past)\s+" + _EN_NUM + r"\s+weeks\b", q)
    if m:
        return _last_n_days(today, _parse_number_en(m.group(1)) * 7)

    m = re.search(r"\b(?:last|past)\s+" + _EN_NUM + r"\s+days\b", q)
    if m:
        return _last_n_days(today, _parse_number_en(m.group(1)))

    m = re.search(r"\b(?:last|past)\s+" + _EN_NUM + r"\s+months\b", q)
    if m:
        return _subtract_months(today, _parse_number_en(m.group(1))), today

    # "last week"/"past week"/"this week"/"this past week" (singular, no number) - all
    # the same rolling 7-day window as Swedish "senaste veckan"/"forra veckan", not a
    # calendar-week-aligned window (this project's own established convention, kept
    # consistent across both languages).
    if re.search(r"\b(this\s+past\s+week|the\s+past\s+week|last\s+week|past\s+week|this\s+week)\b", q):
        return _last_n_days(today, 7)

    # "last month"/"past month"/"this past month" (singular) - one calendar month back,
    # same as Swedish "senaste manaden".
    if re.search(r"\b(this\s+past\s+month|the\s+past\s+month|last\s+month|past\s+month)\b", q):
        return _subtract_months(today, 1), today

    if re.search(r"\btoday\b", q):
        return today, today

    return None


_TIME_UNIT_AFTER_SENASTE = r"(veckan|veckorna|dagarna|m[aå]naden|m[aå]naderna)"
_EN_TIME_UNIT_WORDS = r"(week|weeks|day|days|month|months)"


def detect_recency_ranking(question: str) -> bool:
    """T-022/T-043: "det/den/de [absolut] senaste [N]" (Swedish, F01/F03/F06) or
    "the latest"/"the most recent" (English) asks for a *ranking* - the most recent
    matching items, with no boundary at all - not a bounded window like "senaste
    veckan"/"last week" (already handled by `extract_date_range()`).

    Swedish uses one word ("senaste") for both jobs, disambiguated by what follows it:
    a time-unit word means it's a window question (this returns False,
    `extract_date_range` handles it); anything else (a topic noun, or nothing) means
    it's a ranking question (this returns True). English already has two different
    words for the two jobs in natural use ("last"/"past" for a window, "latest"/"most
    recent" for ranking) - T-043 uses that distinction directly rather than overloading
    one word the way Swedish does, but applies the same "what follows it" check
    defensively, in case a time-unit word ever follows "latest" anyway (e.g. a
    hypothetical "the latest week").

    See docs/DESIGN.md's "Filtering by date and sorting by date are two different
    mechanisms" note - retrieval (T-022) sorts by feed date descending instead of by
    similarity score when this is True, instead of filtering to a window."""
    q = question.lower()
    if re.search(r"\bsenaste\b", q):
        if re.search(r"senaste\s+(" + _NUM + r"\s+)?" + _TIME_UNIT_AFTER_SENASTE + r"\b", q):
            return False
        return True
    if re.search(r"\b(latest|most\s+recent)\b", q):
        if re.search(
            r"(latest|most\s+recent)\s+(?:" + _EN_NUM + r"\s+)?" + _EN_TIME_UNIT_WORDS + r"\b", q
        ):
            return False
        return True
    return False


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
