"""T-053 (D-017): which sources are ingested, read from a user-local file instead of
code. `data/sources.json` is gitignored along with the rest of `data/`, so one user's
choice of channels never reaches another user's clone. With no file yet,
`vg09/channels.py`'s list is the default, so the README's terminal commands keep working
on a fresh clone and on a store built before this file existed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from vg09.channels import CHANNELS as DEFAULT_CHANNELS

SOURCES_PATH = Path(__file__).resolve().parent.parent / "data" / "sources.json"
DEFAULT_HF_WEEKS = 8  # T-015's backfill window
DEFAULT_YOUTUBE_WEEKS = 4  # T-017's backfill window
MAX_CHANNELS = 5  # T-058, my choice: every channel adds minutes to every update
# (videos are fetched 3-8 seconds apart on purpose, and a blocked one is transcribed
# locally). Enforced when a channel is added, not when the file is read, so a list
# someone edited by hand still loads.

# A handle as YouTube allows it: letters, digits, underscore, hyphen, period.
_HANDLE = r"[A-Za-z0-9_.-]{3,30}"
_HANDLE_ONLY = re.compile(rf"^@?({_HANDLE})$")
_HANDLE_URL = re.compile(rf"^(?:https?://)?(?:www\.|m\.)?youtube\.com/@({_HANDLE})(?:/[a-z]*)?/?$")


@dataclass
class Sources:
    hf_enabled: bool = True
    hf_weeks: int = DEFAULT_HF_WEEKS
    youtube_weeks: int = DEFAULT_YOUTUBE_WEEKS
    channels: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_CHANNELS))
    # D-018: start an update when the app is opened and nothing was fetched today.
    update_on_open: bool = True
    # T-093 (D-022): the time zone "today" is measured in, an IANA name.
    timezone: str = "Europe/Stockholm"
    saved: bool = False  # False: no file yet, these are the defaults offered as a start


def load() -> Sources:
    if not SOURCES_PATH.exists():
        return Sources()
    raw = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    return Sources(
        hf_enabled=raw["hf"]["enabled"],
        hf_weeks=raw["hf"]["backfill_weeks"],
        youtube_weeks=raw["youtube"]["backfill_weeks"],
        channels={c["handle"]: c["url"] for c in raw["youtube"]["channels"]},
        # Absent in files written before D-018: those read as on, the default.
        update_on_open=raw.get("update_on_open", True),
        # Absent in files written before T-093: those use the default.
        timezone=raw.get("timezone", Sources.timezone),
        saved=True,
    )


def save(sources: Sources) -> None:
    payload = {
        "update_on_open": sources.update_on_open,
        "timezone": sources.timezone,
        "hf": {"enabled": sources.hf_enabled, "backfill_weeks": sources.hf_weeks},
        "youtube": {
            "backfill_weeks": sources.youtube_weeks,
            "channels": [{"handle": h, "url": u} for h, u in sources.channels.items()],
        },
    }
    SOURCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    sources.saved = True


def parse_channel(text: str) -> tuple[str, str]:
    """`@handle`, a bare handle, or a youtube.com/@handle address (with or without a
    trailing tab such as /videos) -> (handle, the channel's /videos address). Whether
    the channel exists on YouTube is not checked here."""
    cleaned = text.strip()
    match = _HANDLE_ONLY.match(cleaned) or _HANDLE_URL.match(cleaned)
    if match is None:
        raise ValueError(
            "Enter a channel as @handle or as its address, "
            "for example https://www.youtube.com/@handle"
        )
    handle = match.group(1)
    return handle, f"https://www.youtube.com/@{handle}/videos"


def add_channel(sources: Sources, text: str) -> str:
    handle, url = parse_channel(text)
    if handle.lower() in {h.lower() for h in sources.channels}:
        raise ValueError(f"@{handle} is already in the list")
    if len(sources.channels) >= MAX_CHANNELS:
        raise ValueError(f"The list is full at {MAX_CHANNELS} channels. Remove one to add another.")
    sources.channels[handle] = url
    return handle


def remove_channel(sources: Sources, handle: str) -> None:
    if handle not in sources.channels:
        raise ValueError(f"@{handle} is not in the list")
    del sources.channels[handle]
