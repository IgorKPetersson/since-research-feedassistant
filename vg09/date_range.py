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
regardless of the real wall-clock date. The app passes the reference date from
`vg09.reference_date` (T-093, D-022: the user's calendar date in the configured time
zone); evaluation runs pass a fixed date.
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


# T-066: phrases the 2026-10-05 probe run showed real questions use and this module
# ignored ("yesterday", "on Friday", "since Monday", "since September") or misread
# ("between September 20 and September 25" became September 20 alone). Same closed
# vocabulary approach as above, both languages.
_EN_MONTH_ABBREVIATIONS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
_ANY_MONTH = {**_MONTH_NAMES, **_EN_MONTH_NAMES, **_EN_MONTH_ABBREVIATIONS}
_ANY_MONTH_RE = "(" + "|".join(sorted(_ANY_MONTH, key=len, reverse=True)) + r")\.?"
_FULL_MONTH_RE = "(" + "|".join(sorted({**_MONTH_NAMES, **_EN_MONTH_NAMES}, key=len, reverse=True)) + ")"
_WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4,
    "saturday": 5, "sunday": 6,
    "måndag": 0, "mandag": 0, "tisdag": 1, "onsdag": 2, "torsdag": 3, "fredag": 4,
    "lördag": 5, "lordag": 5, "söndag": 6, "sondag": 6,
}
_EN_WEEKDAY_RE = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
# "i fredags" - Swedish for the most recent Friday before today.
_SV_PAST_WEEKDAY_RE = r"i\s+(m[aå]ndag|tisdag|onsdag|torsdag|fredag|l[oö]rdag|s[oö]ndag)s"
_DAY = r"(\d{1,2})(?:st|nd|rd|th)?"
_YESTERDAY_RE = r"(yesterday|i\s*g[aå]r)"
_ANY_NUMBER_WORDS = {**_NUMBER_WORDS, **_EN_NUMBER_WORDS}
_ANY_NUM = r"(\d+|" + "|".join(_ANY_NUMBER_WORDS) + r")"


def _day_in_past_year(month: int, day: int, today: date) -> date | None:
    """This year's date, or last year's if this year's is still ahead of `today`."""
    try:
        d = date(today.year, month, day)
        return d if d <= today else date(today.year - 1, month, day)
    except ValueError:
        return None  # not a real calendar date - don't guess


def _month_span(month: int, today: date) -> DateRange:
    """The whole calendar month: this year's, or last year's if it hasn't begun yet."""
    year = today.year if month <= today.month else today.year - 1
    next_first = date(year + (month == 12), month % 12 + 1, 1)
    return date(year, month, 1), next_first - timedelta(days=1)


def _weekday_back(today: date, weekday: int, strictly_before: bool) -> date:
    days = (today.weekday() - weekday) % 7
    if days == 0 and strictly_before:
        days = 7
    return today - timedelta(days=days)


# T-094: dates written with their year. An ISO date ("2026-10-05") or a month and day
# followed by a year ("October 5, 2025", "5 oktober 2025") is taken as written, never
# moved to another year; an impossible one ("2026-02-29") resolves to nothing, which the
# app then asks about instead of searching every date.
_ISO_RE = r"(\d{4})-(\d{1,2})-(\d{1,2})"
_DAY_BEFORE_YESTERDAY_RE = r"(?:the\s+)?day\s+before\s+yesterday|i\s*f[oö]rrg[aå]r"


def _iso(m: re.Match, offset: int = 0) -> date | None:
    return _dated(int(m.group(offset + 1)), int(m.group(offset + 2)), int(m.group(offset + 3)))


def _dated(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _month_day_year(text: str) -> list[date | None]:
    """Every "Month D, YYYY" / "D Month YYYY" / "den D månad YYYY" in `text`, in order;
    None for an impossible one."""
    found = []
    for m in re.finditer(r"\b" + _ANY_MONTH_RE + r"\s+" + _DAY + r",?\s+(\d{4})\b", text):
        found.append((m.start(), _dated(int(m.group(3)), _ANY_MONTH[m.group(1)], int(m.group(2)))))
    for m in re.finditer(r"\b(?:den\s+|the\s+)?" + _DAY + r"\s+(?:of\s+)?" + _ANY_MONTH_RE
                         + r",?\s+(\d{4})\b", text):
        found.append((m.start(), _dated(int(m.group(3)), _ANY_MONTH[m.group(2)], int(m.group(1)))))
    return [d for _, d in sorted(found, key=lambda pair: pair[0])]


_RELATIVE_TO_A_DATE_RE = re.compile(
    r"\b(?:week|weeks|day|days|month|months)\s+(?:after|before(?!\s+yesterday)|following|prior\s+to|leading\s+up\s+to)\b"
    r"|\b(?:veckan|veckorna|dagen|dagarna|m[aå]naden)\s+(?:efter|f[oö]re|innan)\b")


def _iso_week(week: int, year: int | None, today: date) -> DateRange | None:
    """T-094: "week 41" / "vecka 41" - the ISO week, Monday to Sunday. Without a year it
    is this year's week, or last year's if this year's hasn't started yet."""
    try:
        if year is not None:
            monday = date.fromisocalendar(year, week, 1)
        else:
            monday = date.fromisocalendar(today.isocalendar()[0], week, 1)
            if monday > today:
                monday = date.fromisocalendar(today.isocalendar()[0] - 1, week, 1)
    except ValueError:
        return None
    return monday, monday + timedelta(days=6)


def _start_of(text: str, today: date) -> date | None:
    """The date a "since ..." phrase starts from, or None if what follows isn't one."""
    # T-094: an ISO date, a date with its year, or the day before yesterday.
    m = re.match(_ISO_RE + r"\b", text)
    if m:
        return _iso(m)
    if re.match(r"(?:" + _DAY_BEFORE_YESTERDAY_RE + r")\b", text):
        return today - timedelta(days=2)
    with_year = re.match(r"(?:" + _ANY_MONTH_RE + r"\s+" + _DAY + r",?\s+\d{4}"
                         r"|(?:den\s+|the\s+)?" + _DAY + r"\s+(?:of\s+)?" + _ANY_MONTH_RE
                         + r",?\s+\d{4})\b", text)
    if with_year:
        return _month_day_year(with_year.group(0))[0]
    if re.match(_YESTERDAY_RE + r"\b", text):
        return today - timedelta(days=1)
    # T-084: "since 3 days (ago)", "sedan 2 veckor" - N days back, that day included,
    # the same way "since yesterday" includes yesterday.
    m = re.match(_ANY_NUM + r"\s+(days?|weeks?|dagar|dag|veckor|vecka)\b", text)
    if m:
        n = _ANY_NUMBER_WORDS[m.group(1)] if m.group(1) in _ANY_NUMBER_WORDS else int(m.group(1))
        return today - timedelta(days=n * (7 if m.group(2).startswith(("week", "veck")) else 1))
    m = re.match(_SV_PAST_WEEKDAY_RE + r"\b", text)
    if m:
        return _weekday_back(today, _WEEKDAYS[m.group(1)], True)
    m = re.match(r"(?:last\s+)?" + _EN_WEEKDAY_RE + r"\b|(m[aå]ndag|tisdag|onsdag|torsdag|fredag|l[oö]rdag|s[oö]ndag)\b", text)
    if m:
        name = m.group(1) or m.group(2)
        return _weekday_back(today, _WEEKDAYS[name], text.startswith("last"))
    m = re.match(_ANY_MONTH_RE + r"\s+" + _DAY + r"\b", text) or \
        re.match(r"(?:den\s+)?" + _DAY + r"\s+(?:of\s+)?" + _ANY_MONTH_RE + r"\b", text)
    if m:
        a, b = m.group(1), m.group(2)
        month, day = (_ANY_MONTH[a], int(b)) if a in _ANY_MONTH else (_ANY_MONTH[b], int(a))
        return _day_in_past_year(month, day, today)
    m = re.match(_FULL_MONTH_RE + r"\b", text)
    if m:
        return _month_span(_ANY_MONTH[m.group(1)], today)[0]
    return None


def _two_date_range(q: str, today: date) -> DateRange | None:
    """"between September 20 and 25", "September 20-25", "from Sept 20 to Sept 25",
    "mellan den 20 och den 25 september". The year comes from the start date."""
    sep = r"\s*(?:and|to|through|until|och|till|-|–)\s*"
    # T-094: "between 2026-10-01 and 2026-10-05", "2026-10-01 to 2026-10-05". A plain
    # hyphen without spaces isn't a separator here: it reads as part of a date.
    m = re.search(r"\b(?:(?:between|from|mellan)\s+)?" + _ISO_RE
                  + r"\s+(?:and|to|through|until|och|till|-|–)\s+" + _ISO_RE + r"\b", q)
    if m:
        start, end = _iso(m), _iso(m, 3)
        return (start, end) if start and end and start <= end else ()
    m = re.search(r"\b(?:between|from)\s+" + _ANY_MONTH_RE + r"\s+" + _DAY + sep
                  + r"(?:" + _ANY_MONTH_RE + r"\s+)?" + _DAY + r"\b", q) or \
        re.search(r"\b" + _ANY_MONTH_RE + r"\s+" + _DAY + r"\s*(?:-|–|to|through|until)\s*"
                  + r"(?:" + _ANY_MONTH_RE + r"\s+)?" + _DAY + r"\b", q)
    if m:
        first_month, first_day, second_month, second_day = m.groups()
        start_month = _ANY_MONTH[first_month]
        end_month = _ANY_MONTH[second_month] if second_month else start_month
    else:
        m = re.search(r"\b(?:mellan|between|from)\s+(?:den\s+)?" + _DAY + r"(?:\s+" + _ANY_MONTH_RE
                      + r")?" + sep + r"(?:den\s+)?" + _DAY + r"\s+" + _ANY_MONTH_RE + r"\b", q)
        if not m:
            return None
        first_day, first_month, second_day, second_month = m.groups()
        end_month = _ANY_MONTH[second_month]
        start_month = _ANY_MONTH[first_month] if first_month else end_month
    # T-094: a range was written; if it isn't a real one, say so with () so that no
    # single-date pattern later reads its first date as the whole question.
    start = _day_in_past_year(start_month, int(first_day), today)
    if start is None:
        return ()
    try:
        end = date(start.year + (end_month < start_month), end_month, int(second_day))
    except ValueError:
        return ()
    return (start, end) if start <= end else ()


def _phrases_checked_first(q: str, today: date) -> DateRange | None:
    """Two-date ranges and "since ..." - checked before the single-date patterns
    below, which would otherwise take the first date of a range as the whole range."""
    span = _two_date_range(q, today)
    if span is not None:
        return span
    m = re.search(r"\b(?:since|sedan|sen)\s+(.*)", q)
    if m:
        start = _start_of(m.group(1), today)
        if start is not None:
            return start, today
    return None


def _phrases_checked_last(q: str, today: date) -> DateRange | None:
    """Single days and whole months that the patterns above don't cover."""
    if re.search(r"\b" + _YESTERDAY_RE + r"\b", q):
        d = today - timedelta(days=1)
        return d, d
    m = re.search(r"\b" + _SV_PAST_WEEKDAY_RE + r"\b", q)
    if m:
        d = _weekday_back(today, _WEEKDAYS[m.group(1)], True)
        return d, d
    m = re.search(r"\b(last\s+)?" + _EN_WEEKDAY_RE + r"\b", q)
    if m:
        d = _weekday_back(today, _WEEKDAYS[m.group(2)], bool(m.group(1)))
        return d, d
    if re.search(r"\bthis\s+month\b|\bdenna\s+m[aå]nad\b", q):
        return today.replace(day=1), today
    m = re.search(r"\b(?:in|during|i|under)\s+" + _FULL_MONTH_RE + r"\b(?!\s+\d)", q)
    if m:
        return _month_span(_ANY_MONTH[m.group(1)], today)
    return None


def _t094_phrases(q: str, today: date) -> DateRange | tuple[()] | None:
    """T-094 additions, checked after ranges and "since", before the older single-date
    patterns (which would read "October 5, 2025" as this year's October 5).

    Returns a range, `()` when the question names a date that doesn't exist (so nothing
    older may guess at it), or None when none of these phrases is present."""
    # A period relative to a named date ("the week after October 1") is not supported;
    # without this, the date alone would be read as the whole question.
    if _RELATIVE_TO_A_DATE_RE.search(q):
        return ()
    # Single days.
    m = re.search(_ISO_RE, q)
    if m and not re.search(_ISO_RE + r".*" + _ISO_RE, q):
        d = _iso(m)
        return (d, d) if d else ()
    with_year = _month_day_year(q)
    if len(with_year) == 1:
        d = with_year[0]
        return (d, d) if d else ()
    if len(with_year) > 1:
        return ()  # several dates but no range the range patterns could read: ask
    if re.search(r"\b(?:" + _DAY_BEFORE_YESTERDAY_RE + r")\b", q):
        d = today - timedelta(days=2)
        return d, d
    m = (re.search(r"\b" + _ANY_NUM + r"\s+days?\s+ago\b", q)
         or re.search(r"\bf[oö]r\s+" + _ANY_NUM + r"\s+dag(?:ar)?\s+sedan\b", q))
    if m:
        d = today - timedelta(days=_ANY_NUMBER_WORDS.get(m.group(1)) or int(m.group(1)))
        return d, d
    if re.search(r"\b(?:idag|i\s+dag)\b", q):
        return today, today

    # Calendar periods: an ISO week, a month of a given year, this year.
    m = re.search(r"\b(?:week|vecka|v\.)\s*(\d{1,2})(?:\s*,?\s*(\d{4}))?\b", q)
    if m:
        return _iso_week(int(m.group(1)), int(m.group(2)) if m.group(2) else None, today) or ()
    m = re.search(r"\b(?:in|during|i|under)\s+" + _FULL_MONTH_RE + r"\s+(\d{4})\b", q)
    if m:
        year, month = int(m.group(2)), _ANY_MONTH[m.group(1)]
        return date(year, month, 1), date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1)
    if re.search(r"\b(?:this\s+year|i\s+år)\b", q):
        return today.replace(month=1, day=1), today
    if re.search(r"\b(?:den\s+h[aä]r\s+m[aå]naden|denna\s+m[aå]nad(?:en)?)\b", q):
        return today.replace(day=1), today

    # Rolling periods ending today, same convention as "last month" / "senaste veckan".
    if re.search(r"\bf[oö]rra\s+m[aå]naden\b", q):
        return _subtract_months(today, 1), today
    if re.search(r"\b(?:the\s+past\s+year|past\s+year|(?:det\s+)?senaste\s+[aå]ret)\b", q):
        return _subtract_months(today, 12), today
    return None


def extract_date_range(question: str, today: date) -> DateRange | None:
    q = question.lower()

    first = _phrases_checked_first(q, today)
    if first is not None:
        return first or None  # () means a range was written but isn't a real one

    added = _t094_phrases(q, today)
    if added is not None:
        return added or None  # () means "a date was named, but it isn't a real one"

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
    # T-079: the number may also come first, "de 5 senaste dagarna".
    m = (re.search(r"senaste\s+" + _NUM + r"\s+veckorna", q)
         or re.search(r"\b" + _NUM + r"\s+senaste\s+veckorna", q))
    if m:
        return _last_n_days(today, _parse_number(m.group(1)) * 7)

    m = (re.search(r"senaste\s+" + _NUM + r"\s+dagarna", q)
         or re.search(r"\b" + _NUM + r"\s+senaste\s+dagarna", q))
    if m:
        return _last_n_days(today, _parse_number(m.group(1)))

    m = (re.search(r"senaste\s+" + _NUM + r"\s+m[aå]naderna", q)
         or re.search(r"\b" + _NUM + r"\s+senaste\s+m[aå]naderna", q))
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
    # T-079: "previous" too, and "over/during/in/within the N days" without "last" (my
    # "developed over the 5 days"), but not "the 5 days before/after X".
    lead = (r"\b(?:(?:last|past|previous)\s+"
            r"|(?:over|during|in|within|for)\s+the\s+)")
    not_anchored = r"(?!\s+(?:before|after|leading|following|of)\b)"

    m = re.search(lead + _EN_NUM + r"\s+weeks\b" + not_anchored, q)
    if m:
        return _last_n_days(today, _parse_number_en(m.group(1)) * 7)

    m = re.search(lead + _EN_NUM + r"\s+days\b" + not_anchored, q)
    if m:
        return _last_n_days(today, _parse_number_en(m.group(1)))

    m = re.search(lead + _EN_NUM + r"\s+months\b" + not_anchored, q)
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

    return _phrases_checked_last(q, today)


_TIME_UNIT_AFTER_SENASTE = r"(veckan|veckorna|dagarna|m[aå]naden|m[aå]naderna|[aå]ret|[aå]ren)"
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


# T-094: words that ask about time without saying which dates. A question with one of
# these and no resolved range is asked about, never searched across every date.
_VAGUE_TIME_RE = re.compile(
    r"\b(?:recent|recently|lately|nowadays|these\s+days|nyligen|p[aå]\s+sistone"
    r"|(?:de\s+)?senaste\s+(?:veckorna|dagarna|m[aå]naderna|[aå]ren)"
    r"|recent\s+(?:weeks|days|months)|earlier\s+this\s+(?:week|month|year)"
    r"|tidigare\s+(?:i\s+veckan|i\s+m[aå]naden|i\s+[aå]r)"
    r"|last\s+year|f[oö]rra\s+[aå]ret|i\s+fjol"
    r"|(?:this|last|the)\s+weekend|i\s+helgen|f[oö]rra\s+helgen"
    r"|q[1-4]|quarter|kvartal(?:et)?|i\s+(?:h[oö]stas|v[aå]ras|somras|vintras)"
    r"|(?:week|weeks|day|days|month|months)\s+(?:after|before(?!\s+yesterday)|following|prior\s+to|leading\s+up\s+to)"
    r"|(?:veckan|veckorna|dagen|dagarna|m[aå]naden)\s+(?:efter|f[oö]re|innan)"
    r"|(?:a|an|one|\d+|" + "|".join(_ANY_NUMBER_WORDS) + r")\s+(?:weeks?|months?|years?)\s+ago"
    r"|f[oö]r\s+(?:en|ett|\d+|" + "|".join(_NUMBER_WORDS) + r")\s+"
    r"(?:vecka|veckor|m[aå]nad|m[aå]nader|[aå]r)\s+sedan)\b")
# Something shaped like a date that the parser could not turn into one: an impossible
# ISO date or day of a month, a week number out of range, or a range written backwards.
_DATE_SHAPED_RE = re.compile(
    r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b(?:week|vecka|v\.)\s*\d{1,2}\b"
    r"|\b" + _ANY_MONTH_RE + r"\s+\d{1,2}(?:st|nd|rd|th)?\b"
    r"|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?" + _FULL_MONTH_RE + r"\b")


def unresolved_time_phrase(question: str, today: date) -> str | None:
    """T-094: the words in `question` that ask about a time this module can't turn into
    dates, or None. None as well when a range or a "latest" ranking was found, or when
    the question doesn't ask about time at all (an ordinary question searches every date,
    as before). The app shows the words and asks for a period instead of searching."""
    if extract_date_range(question, today) is not None or detect_recency_ranking(question):
        return None
    q = question.lower()
    m = _VAGUE_TIME_RE.search(q) or _DATE_SHAPED_RE.search(q)
    return question[m.start():m.end()] if m else None


def manual_range_error(start: date | None, end: date | None) -> str | None:
    """T-093: why a range from the date picker can't be used, or None when it can. A
    future end is allowed; the app says separately when a period runs past the newest
    source (D-022)."""
    if start is None or end is None:
        return "Choose both a start and an end date."
    if start > end:
        return f"The start date ({start}) is after the end date ({end})."
    return None


def resolve_date_range(
    question: str, today: date, manual_override: DateRange | None = None
) -> DateRange | None:
    """The one function T-022 (retrieval) and T-025 (the chat UI) both call - the
    manual override, whenever the UI's date picker sets one, always wins over
    whatever (if anything) was extracted from the question text, including a date the
    question names. `None` either way means "no range" - retrieval runs unfiltered by
    date, per T-021's acceptance criteria (no range is ever invented).

    `today` is the reference date (T-093, D-022): the user's calendar date in the
    configured time zone, resolved once per question by the caller."""
    if manual_override is not None:
        error = manual_range_error(*manual_override)
        if error:
            raise ValueError(error)
        return manual_override
    return extract_date_range(question, today)
