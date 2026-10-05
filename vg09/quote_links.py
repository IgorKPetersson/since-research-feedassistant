"""T-063: link a video citation to the second where the quoted words are spoken.

A video excerpt is about a minute and a half of speech and carries only its start time
(`&t=` in its url, T-012), so a link to it can land well before the sentence the answer
cites: my first report was a quote spoken at 9:50 behind a link to 9:32. When
the answer quotes the video word for word, those words are looked up in the excerpt's
own transcript lines, which keep their real start times on disk, and the link goes to
the line where the quote begins. A paraphrase cannot be located this way and keeps the
excerpt's start.
"""

from __future__ import annotations

import bisect
import json
import re

from vg09.document import raw_path
from vg09.retrieval import Candidate

LEAD_SECONDS = 2  # my choice: start a little early, so the sentence is heard from its start
MIN_QUOTE_WORDS = 4  # shorter quotes ("Claude Code") occur all over a transcript

_QUOTED = re.compile(r'["“]([^"“”]+)["”]')
_ELLIPSIS = re.compile(r"\.\.\.|…")
_NOT_WORD = re.compile(r"[^\w']+")
_TIME_PARAM = re.compile(r"&t=\d+")


def _normalise(text: str) -> str:
    return " ".join(_NOT_WORD.sub(" ", text.lower()).split())


def quotes_in(answer: str) -> list[str]:
    """Every quoted passage of at least `MIN_QUOTE_WORDS` words; a passage the model
    shortened with an ellipsis counts as its separate pieces."""
    found = []
    for match in _QUOTED.finditer(answer):
        for piece in _ELLIPSIS.split(match.group(1)):
            piece = piece.strip()
            if len(piece.split()) >= MIN_QUOTE_WORDS:
                found.append(piece)
    return found


def find_quote_start(quotes: list[str], segments: list[dict], excerpt_start: float,
                     excerpt_text: str) -> float | None:
    """Start time of the transcript line where a quote begins, or None.

    A quote in this excerpt's own text is looked up from the excerpt's start. A quote
    that is not, is looked up in the whole video: found for real in T-063's browser run,
    the model put a verbatim quote spoken at 9:50 under the number of the same video's
    excerpt from 14:56. The quoted words are exact where the number is not, so the words
    decide. A quote found nowhere in this video gives None."""
    excerpt = _normalise(excerpt_text)
    joined, offsets = "", []
    for line in segments:
        offsets.append(len(joined))
        joined += _normalise(line["text"]) + " "
    excerpt_offset = next((offsets[i] for i, line in enumerate(segments)
                           if line["start"] >= excerpt_start - 0.01), len(joined))
    normalised = [q for q in (_normalise(q) for q in quotes) if q]
    in_excerpt = [q for q in normalised if q in excerpt]
    for wanted, search_from in ([(q, excerpt_offset) for q in in_excerpt]
                                + [(q, 0) for q in normalised if q not in in_excerpt]):
        at = joined.find(wanted, search_from)
        if at >= 0:
            return segments[bisect.bisect_right(offsets, at) - 1]["start"]
    return None


def with_timestamp(url: str, seconds: float) -> str:
    return f"{_TIME_PARAM.sub('', url)}&t={max(0, int(seconds) - LEAD_SECONDS)}"


def _segments(candidate: Candidate) -> list[dict]:
    m = candidate.metadata
    path = raw_path("youtube", m["feed_date"], m["doc_id"])
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("segments") or []


def quote_times(answer: str, source_map: dict[int, Candidate]) -> dict[int, float]:
    """Source number -> the second its quote starts, for every video source the answer
    quotes word for word. Sources it doesn't quote are left out."""
    quotes = quotes_in(answer)
    if not quotes:
        return {}
    times = {}
    for n, candidate in source_map.items():
        m = candidate.metadata
        if m.get("source") != "youtube" or m.get("start_seconds") is None:
            continue
        start = find_quote_start(quotes, _segments(candidate), m["start_seconds"], candidate.text)
        if start is not None:
            times[n] = start
    return times
