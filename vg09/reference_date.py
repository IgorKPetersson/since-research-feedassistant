"""T-093 (D-022): the one date relative questions are measured from.

"Today", "yesterday" and "the last 7 days" mean the user's own calendar date, in the time
zone set in `data/sources.json` (`timezone`, an IANA name; Europe/Stockholm by default).
Until T-093 the app measured them from the newest date in the index instead, while the
answer prompt used the computer's date, so with stale data the two disagreed (D-012,
superseded for the app by D-022). The newest indexed date is shown separately and never
moves a requested period.

The app resolves the date once per question and passes it on; nothing below the app asks
the clock itself. Tests pass `now`, a fixed instant, so midnight and daylight-saving
changes can be checked without waiting for them.

Feed dates are not converted: a paper's date is its Daily Papers day and a video's is
yt-dlp's UTC upload date (KB-040). They are compared with this local date as calendar
dates, so near midnight a video can count for the neighbouring day.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Europe/Stockholm"


class TimezoneError(ValueError):
    pass


def zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise TimezoneError(
            f'"{name}" is not a known time zone. Set "timezone" in data/sources.json to an '
            f'IANA name such as "{DEFAULT_TIMEZONE}".') from exc


def configured_timezone() -> str:
    from vg09 import sources  # here, not at import: vg09.sources is read per call

    return sources.load().timezone


def today(tz_name: str | None = None, now: datetime | None = None) -> date:
    """The calendar date in the configured (or given) time zone at `now` (default: the
    real current instant). `now` must carry its own time zone."""
    instant = now if now is not None else datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return instant.astimezone(zone(tz_name or configured_timezone())).date()
