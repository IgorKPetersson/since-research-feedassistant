"""T-093 (D-022): how far each source has been checked, kept apart from the newest
content in the index and from the period a question asks about.

- Papers: the date of the last completed Hugging Face sync. The sync stores its
  watermark `REOPEN_DAYS` before the day it ran (`vg09.sync`), so the day it checked
  through is the watermark plus `REOPEN_DAYS`.
- Videos: the earliest `checked_through` among the configured channels (T-091). One
  channel never checked completely makes the whole answer None: the videos are only
  checked as far as the least-checked channel.

Checked is not the same as stored (T-092): members-only videos and late discoveries are
checked but not in the index.
"""

from __future__ import annotations

from datetime import date, timedelta


def papers_checked_through() -> date | None:
    from vg09.sync import REOPEN_DAYS
    from vg09.watermark import read_watermark

    watermark = read_watermark("hf")
    if watermark is None:
        return None
    return date.fromisoformat(watermark) + timedelta(days=REOPEN_DAYS)


def videos_checked_through(handles) -> date | None:
    from vg09 import channel_state

    handles = list(handles)
    if not handles:
        return None
    records = channel_state.load()["channels"]
    dates = [records.get(h, {}).get("checked_through") for h in handles]
    if any(d is None for d in dates):
        return None
    return date.fromisoformat(min(dates))
