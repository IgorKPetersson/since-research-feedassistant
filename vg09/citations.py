"""T-024: turn the model's own positional citations into structured, verifiable
citation data - title, feed date, link (a YouTube chunk's `&t=SECONDS` is already
baked into its `url` by T-012's chunking, nothing to add here), and arXiv
`published_at` for papers.

T-023's real finding: the model doesn't reliably follow a "[Title, YYYY-MM-DD]"
citation instruction - it cites the bracketed *source number* shown in the prompt
instead ("source [27]"), matching `vg09.answer.number_sources()`'s own numbering.
Rather than fighting that, `vg09.answer.SYSTEM_PROMPT` now asks for exactly that, and
this module resolves those numbers back to real chunks via the same mapping the
prompt was built from (`AnswerResult.source_map`). A bracketed reference that can't be
resolved this way - an out-of-range number, or any other bracket format the model
might still produce - is reported, never silently dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from vg09.retrieval import Candidate

_BRACKET_RE = re.compile(r"\[([^\]]+)\]")


@dataclass
class Citation:
    doc_id: str
    title: str
    feed_date: str
    url: str
    is_fallback: bool  # True iff built from a title_description fallback document (D-006)
    arxiv_published_at: str | None = None  # papers only


@dataclass
class CitationResult:
    citations: list[Citation]  # deduplicated by doc_id, first-cited order
    unlinked_references: list[str]  # raw bracket text ("[27]", "[Title, 2026-09-09]", ...)
    # that could not be resolved to a real chunk - deduplicated, first-seen order,
    # never silently hidden


def _citation_from_chunk(c: Candidate) -> Citation:
    m = c.metadata
    return Citation(
        doc_id=m["doc_id"],
        title=m["title"],
        feed_date=m["feed_date"],
        url=m["url"],
        is_fallback=(m.get("text_source") == "title_description"),
        arxiv_published_at=m.get("arxiv_published_at"),
    )


def build_citations(answer: str, source_map: dict[int, Candidate]) -> CitationResult:
    """Scans the answer text (not the reasoning - the reasoning is never shown to the
    user, T-011) for bracketed references. A reference resolves only if its content is
    a bare integer that's a real key in `source_map` - anything else (a non-numeric
    bracket, or a number outside the range actually offered) is unlinked, not guessed
    at. When the same document is cited more than once (the same number twice, or two
    different numbers that happen to be chunks of the same document), only the first
    occurrence becomes a citation - one entry per document, not per chunk or per
    citation mark.

    T-028, real finding: a bracket can hold more than one comma-separated number
    ("[17, 18]") - the model does this for a claim drawing on several sources at once.
    Each number in that bracket is resolved independently, exactly as if it had been
    its own bracket - a bracket where some numbers resolve and others don't reports
    only the failing ones as unlinked, the rest still become real citations. A bracket
    that *isn't* a comma-separated list of bare numbers (T-024's original non-numeric
    case, e.g. the never-reliably-followed "[Title, YYYY-MM-DD]" shape) is still
    reported as one whole unlinked reference, unchanged - comma-splitting only applies
    once every piece is confirmed to be a bare number, so a citation-shaped bracket
    that merely happens to contain a comma elsewhere isn't torn apart by mistake."""
    citations: list[Citation] = []
    seen_doc_ids: set[str] = set()
    unlinked: list[str] = []
    seen_unlinked: set[str] = set()

    def add_unlinked(raw: str) -> None:
        if raw not in seen_unlinked:
            seen_unlinked.add(raw)
            unlinked.append(raw)

    for match in _BRACKET_RE.finditer(answer):
        raw = match.group(0)
        parts = [p.strip() for p in match.group(1).split(",")]

        if not all(p.isdigit() for p in parts):
            add_unlinked(raw)
            continue

        for part in parts:
            chunk = source_map.get(int(part))
            if chunk is None:
                add_unlinked(f"[{part}]")
                continue

            doc_id = chunk.metadata["doc_id"]
            if doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc_id)
            citations.append(_citation_from_chunk(chunk))

    return CitationResult(citations=citations, unlinked_references=unlinked)
