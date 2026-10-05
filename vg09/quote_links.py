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


def _quote_pieces(answer: str):
    """(piece, start, end) for every quoted passage piece of at least `MIN_QUOTE_WORDS`
    words; start/end are the whole quoted passage's span, quote marks included."""
    for match in _QUOTED.finditer(answer):
        for piece in _ELLIPSIS.split(match.group(1)):
            piece = piece.strip()
            if len(piece.split()) >= MIN_QUOTE_WORDS:
                yield piece, match.start(), match.end()


def quotes_in(answer: str) -> list[str]:
    """Every quoted passage of at least `MIN_QUOTE_WORDS` words; a passage the model
    shortened with an ellipsis counts as its separate pieces."""
    return [piece for piece, _, _ in _quote_pieces(answer)]


# T-064: how an answer names a source - "[23]", "[3, 4]", "source 23", "Source [23]". A
# range ("[1-20]") is a descriptive enumeration, not a citation (D-015), and is skipped.
_BRACKET_REF = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
_WORD_REF = re.compile(r"\bsources?\s+(\d+)\b", re.IGNORECASE)
_SENTENCE_END = re.compile(r"[.!?]\s|\n")
IMMEDIATE_CHARS = 3  # `"…" [7]`, `"…," [7]` and `"…". [7]` all count as right after


def _references(answer: str) -> list[tuple[int, int, list[int]]]:
    refs = [(m.start(), m.end(), [int(n) for n in m.group(1).split(",")])
            for m in _BRACKET_REF.finditer(answer)]
    refs += [(m.start(), m.end(), [int(m.group(1))]) for m in _WORD_REF.finditer(answer)]
    return sorted(refs)


def credited_sources(answer: str) -> list[tuple[str, list[int]]]:
    """Each quote with the source numbers the answer credits it to: a citation right
    after the quote; else the last source named before it in the same sentence; else
    the first named after it in that sentence. A quote credited to nothing is left out.
    Found for real (T-063): 'source [23] with the statement "…" and in source [25] with
    the identical statement' credits the quote to 23, where it is not."""
    refs = _references(answer)
    credited = []
    for piece, start, end in _quote_pieces(answer):
        before_quote = answer[:start]
        sentence_start = max((m.end() for m in _SENTENCE_END.finditer(before_quote)), default=0)
        after = _SENTENCE_END.search(answer, end)
        sentence_end = after.start() + 1 if after else len(answer)
        immediate = [r for r in refs if end <= r[0] <= end + IMMEDIATE_CHARS
                     and answer[r[0]] == "["]
        before = [r for r in refs if sentence_start <= r[0] and r[1] <= start]
        following = [r for r in refs if end <= r[0] < sentence_end]
        chosen = immediate[:1] or before[-1:] or following[:1]
        if chosen:
            credited.append((piece, chosen[0][2]))
    return credited


# T-064: share of a quote's three-word sequences that must occur in the source. The model
# quotes loosely ("a personal agent" for "the personal agent", a dropped "a lot of"), so
# an exact match flagged 4 of 12 real quotes whose source was right. Measured 2026-10-05
# on real transcripts: right source with loose wording 0.67-0.86, the real false claim
# 0.00, the best-scoring unrelated video for any of those quotes 0.46.
QUOTE_MATCH_THRESHOLD = 0.6


def _trigrams(words: list[str]) -> list[tuple[str, ...]]:
    return [tuple(words[i:i + 3]) for i in range(len(words) - 2)]


def quote_in_text(quote: str, text: str) -> bool:
    wanted = _trigrams(_normalise(quote).split())
    if not wanted:
        return False
    present = set(_trigrams(_normalise(text).split()))
    return sum(g in present for g in wanted) / len(wanted) >= QUOTE_MATCH_THRESHOLD


def _document_text(candidate: Candidate) -> str:
    """The whole document - full transcript or abstract - not just the excerpt: the
    model can credit a quote to the wrong excerpt of the right video (T-063), and that
    is not the false claim this check is for."""
    m = candidate.metadata
    path = raw_path(m.get("source", ""), m.get("feed_date", ""), m.get("doc_id", ""))
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("text") or candidate.text
    return candidate.text


def misattributed_quotes(answer: str, source_map: dict[int, Candidate]
                         ) -> list[tuple[str, list[int], int | None]]:
    """T-064: (quote, the sources it is credited to, the source it is really in or None)
    for every quote none of its credited sources contains. Measured on a real answer:
    4 of 5 quotes were word for word from a different video than the one credited, so
    where it really is, when that is one of the answer's sources, is worth saying.
    Numbers that aren't sources in the prompt are ignored; the citation notices already
    report those."""
    texts: dict[str, str] = {}

    def text_of(candidate: Candidate) -> str:
        key = candidate.metadata.get("doc_id", candidate.id)
        if key not in texts:
            texts[key] = _document_text(candidate)
        return texts[key]

    found = []
    for quote, numbers in credited_sources(answer):
        known = [n for n in numbers if n in source_map]
        if not known or any(quote_in_text(quote, text_of(source_map[n])) for n in known):
            continue
        actual = next((n for n, c in sorted(source_map.items())
                       if n not in known and quote_in_text(quote, text_of(c))), None)
        found.append((quote, known, actual))
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
