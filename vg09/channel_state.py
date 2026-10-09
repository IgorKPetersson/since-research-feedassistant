"""T-091 (D-021): how far each YouTube channel has been checked, stored per channel.

Until T-091 one shared watermark said how far YouTube had been checked. It advanced even
when one channel's listing failed, so that channel's missing days were forgotten. Here
each channel has its own record in `data/youtube_channels.json`:

- `checked_through`: the date of the last check that covered the channel completely.
  The next check starts at `catch_up_start(checked_through)` (T-090's recheck).
- `pending_from`: the start of an interval that must still be checked, kept when a check
  fails or is incomplete, so a later run covers it however long the failure lasted.
  Set for a channel that has never been checked completely.
- `last_attempt`, `last_result`, `last_error`, `last_success`: what happened when.
- `newest_content`: the newest feed date among the channel's listed videos on disk.
- `listing`: the video ids of the last complete listing. YouTube lists a channel in
  publication order, so if a new listing still contains one of these, everything
  published since is above it and was seen.
- `dates`: feed dates of listed videos that were looked up but are not on disk (outside
  the window), so they are not looked up again.
- `unreadable`: listed videos YouTube refuses to show (members-only, private).
- `gaps`: intervals that could not be verified and are not retried, each with a reason.
- `unverified_before`: coverage before this date was never checked by this record.

A channel without a record starts unverified: `pending_from` is the start of the backfill
window, and nothing earlier counts as checked. That includes channels that existed under
the shared watermark: the migration does not trust it (T-091), it only notes its value.

The file is written whole to a temporary file and moved into place, so an interrupted
write leaves the previous version.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime

from vg09 import watermark

FILE_NAME = "youtube_channels.json"
VERSION = 1

RESULT_COMPLETE = "complete"
RESULT_COMPLETE_WITH_GAP = "complete_with_gap"
RESULT_INCOMPLETE = "incomplete"
RESULT_FAILED = "failed"


def state_path():
    # Read at call time: tests that redirect the watermark folder redirect this too.
    return watermark.WATERMARK_DIR / FILE_NAME


def load() -> dict:
    path = state_path()
    if not path.exists():
        return {"version": VERSION, "channels": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("version") != VERSION:
        raise ValueError(f"{path} has version {state.get('version')}, expected {VERSION}")
    return state


def save(state: dict) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def new_record(window_start: date) -> dict:
    return {
        "checked_through": None,
        "pending_from": window_start.isoformat(),
        "unverified_before": window_start.isoformat(),
        "last_attempt": None,
        "last_result": None,
        "last_error": None,
        "last_success": None,
        "newest_content": None,
        "listing": [],
        "dates": {},
        "unreadable": {},
        "gaps": [],
    }


def ensure_channels(state: dict, handles, backfill_start: date) -> list[str]:
    """Give every configured channel without a record an unverified one. Returns the
    handles that got a new record. Idempotent: a channel that has a record keeps it.
    The first time the file is created while the old shared watermark exists, its value
    is noted for reference only (`migrated_from`), never used as coverage."""
    if "migrated_from" not in state:
        shared = watermark.read_watermark("youtube")
        state["migrated_from"] = {"shared_watermark": shared, "at": _now(),
                                  "trusted": False} if shared else None
    added = []
    for handle in handles:
        if handle not in state["channels"]:
            state["channels"][handle] = new_record(backfill_start)
            added.append(handle)
    return added


def window_start(record: dict) -> date:
    """Where this channel's next check starts: a kept interval if there is one,
    otherwise the recheck window before the last complete check."""
    from vg09.youtube_backfill import catch_up_start

    if record["pending_from"]:
        return date.fromisoformat(record["pending_from"])
    return catch_up_start(record["checked_through"])


def record_failure(record: dict, start: date, result: str, error: str) -> None:
    """A failed or incomplete check: keep everything from `start` for the next run."""
    record["last_attempt"] = _now()
    record["last_result"] = result
    record["last_error"] = error
    kept = record["pending_from"]
    if kept is None or start.isoformat() < kept:
        record["pending_from"] = start.isoformat()


def record_success(record: dict, today: date, result: str, listing: list[str],
                   gap: dict | None = None, note: str | None = None) -> None:
    now = _now()
    record["last_attempt"] = now
    record["last_success"] = now
    record["last_result"] = result
    record["last_error"] = note
    record["checked_through"] = today.isoformat()
    record["pending_from"] = None
    record["listing"] = list(listing)
    if gap:
        record["gaps"].append(gap)


def remove(handle: str) -> None:
    """A removed channel loses its record with its data, so adding it again starts an
    unverified check instead of trusting coverage whose files are gone."""
    state = load()
    if state["channels"].pop(handle, None) is not None:
        save(state)


def coverage_text(record: dict | None) -> str:
    """One line for the Sources page: how far the channel is verified, and what isn't."""
    if record is None or record["last_attempt"] is None:
        return "Not checked yet"
    parts = []
    if record["checked_through"]:
        parts.append(f"Checked through {record['checked_through']}")
    else:
        parts.append("Not yet checked completely")
    if record["last_result"] in (RESULT_FAILED, RESULT_INCOMPLETE):
        parts.append(f"last check {record['last_result']} ({record['last_error']}); "
                     f"retrying from {record['pending_from']}")
    for gap in record["gaps"]:
        parts.append(f"not verified {gap['from']} to {gap['through']} ({gap['reason']})")
    if record["unreadable"]:
        parts.append(f"{len(record['unreadable'])} listed videos can't be read "
                     "(members-only or private)")
    parts.append(f"nothing before {record['unverified_before']} checked")
    return "; ".join(parts)
