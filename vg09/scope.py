"""T-095: what a question actually searched, said by the app rather than by the model.

A "not found" answer is only as good as its scope: the date range, which sources, how
many documents, how many videos had no transcript, which exact names occur, and where
the YouTube coverage itself has holes (T-091). The app computes these from the index and
the channel records, shows them under the answer, and gives the model a one-line summary
so a negative answer names the scope instead of claiming something was never said.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class SearchScope:
    date_range: tuple[date, date] | None
    source: str | None
    papers: int = 0
    videos: int = 0
    video_text: dict[str, int] = field(default_factory=dict)  # captions/whisper/title_description
    name_counts: dict[str, int] = field(default_factory=dict)
    coverage_notes: list[str] = field(default_factory=list)


def search_scope(date_range: tuple[date, date] | None, source: str | None,
                 name_counts: dict[str, int], channels=None) -> SearchScope:
    """`channels`: the configured channel handles, for the coverage notes; None skips them
    (the frozen evaluation has no channel records)."""
    from vg09.retrieval import scope_where
    from vg09.store import get_collection

    metadatas = get_collection().get(where=scope_where(date_range, source),
                                     include=["metadatas"])["metadatas"]
    docs = {m["doc_id"]: m for m in metadatas}
    scope = SearchScope(date_range, source, name_counts=dict(name_counts))
    for m in docs.values():
        if m["source"] == "hf":
            scope.papers += 1
        else:
            scope.videos += 1
            kind = m.get("text_source") or "captions"
            scope.video_text[kind] = scope.video_text.get(kind, 0) + 1
    if channels is not None and source != "hf":
        scope.coverage_notes = channel_coverage_notes(date_range, list(channels))
    return scope


def channel_coverage_notes(date_range: tuple[date, date] | None, handles: list[str]) -> list[str]:
    """Holes in the YouTube coverage that matter for this date range (T-091, T-103, T-104)."""
    from vg09 import channel_state

    records = channel_state.load()["channels"]
    start = date_range[0].isoformat() if date_range else None
    end = date_range[1].isoformat() if date_range else None
    notes: list[str] = []
    unverified = []
    for handle in handles:
        r = records.get(handle)
        if r is None or r.get("last_attempt") is None:
            notes.append(f"@{handle} has not been checked yet")
            continue
        if r["last_result"] in (channel_state.RESULT_FAILED, channel_state.RESULT_INCOMPLETE) \
                and (end is None or r["pending_from"] <= end):
            notes.append(f"@{handle}: the last check {r['last_result']}, so videos from "
                         f"{r['pending_from']} on may be missing")
        for gap in r.get("gaps", []):
            if start is None or (gap["from"] <= end and gap["through"] >= start):
                notes.append(f"@{handle}: {gap['from']} to {gap['through']} not verified")
        if r.get("unreadable"):
            notes.append(f"@{handle}: {len(r['unreadable'])} listed videos can't be read "
                         "(members-only or private)")
        if r.get("late"):
            notes.append(f"@{handle}: {len(r['late'])} videos that appeared late were not fetched")
        if r.get("unverified_before") and (start is None or start < r["unverified_before"]):
            unverified.append(r["unverified_before"])
    if unverified:
        notes.append(f"Videos before {max(unverified)} were never checked")
    return notes


def _quoted(name: str) -> str:
    return f"“{name}”"


def _period(scope: SearchScope) -> str:
    if scope.date_range is None:
        return "of all dates"
    start, end = scope.date_range
    return f"dated {start.isoformat()}" if start == end else f"dated {start.isoformat()} to {end.isoformat()}"


def _names(scope: SearchScope) -> str:
    parts = [f"{_quoted(n)} in {'no source' if c == 0 else f'{c} source' + ('' if c == 1 else 's')}"
             for n, c in scope.name_counts.items()]
    return "Exact text: " + "; ".join(parts) + "." if parts else ""


def scope_lines(scope: SearchScope) -> list[str]:
    """For the app, under the answer. Plain text; the caller escapes it for markdown."""
    lines = [f"Searched {scope.papers} papers and {scope.videos} videos {_period(scope)}."]
    title_only = scope.video_text.get("title_description", 0)
    whisper = scope.video_text.get("whisper", 0)
    parts = []
    if whisper:
        parts.append(f"{whisper} {'was' if whisper == 1 else 'were'} transcribed by Whisper")
    if title_only:
        parts.append(f"{title_only} {'has' if title_only == 1 else 'have'} only a title and description")
    if parts:
        lines[0] += " Of the videos, " + " and ".join(parts) + "."
    if scope.name_counts:
        lines.append(_names(scope))
    if scope.coverage_notes:
        lines.append("Video coverage: " + "; ".join(scope.coverage_notes) + ".")
    return lines


def scope_prompt(scope: SearchScope) -> str:
    """For the model, after the date line: the scope, and how to phrase "not found"."""
    text = f"The search covered {scope.papers} papers and {scope.videos} videos {_period(scope)}."
    title_only = scope.video_text.get("title_description", 0)
    if title_only:
        text += (f" {title_only} of the videos {'has' if title_only == 1 else 'have'} only a title "
                 "and description, no transcript.")
    if scope.coverage_notes:
        text += " Some YouTube videos for this period could not be checked or read."
    # The exact-name counts are not given to the model: on the frozen set it repeated
    # "'Copding' in no source" for a typo (F04) and "'Palantir' in no source" over the
    # misspelling it had found itself (F12). They are shown to the user instead.
    return (text + " If the sources don't answer the question, say it was not found in these "
            "sources for this period; don't say it was never mentioned anywhere.")
