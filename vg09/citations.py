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

T-040/D-015: a bracket can also hold a numeric *range* ("[1-20]", "[21-22]"), which
T-028's comma-only splitting never covered - a range fell straight into
`unlinked_references` as one unparsed blob, silently dropping any real citation that
happened to be part of it. D-015's real-data finding: a short range is a genuine
multi-source citation (`[21-22]`, T-032's F10-A) and resolves like a comma list; a
long range is the model describing "all N sources", not citing evidence for a claim
(`[1-31]`, T-032's F12-A - the exact shape T-024's own ticket predicted). D-015 draws
the line at `DESCRIPTIVE_BRACKET_THRESHOLD` numbers named in the bracket, counting
every piece together - at or under it, every number resolves individually, exactly
like a comma-separated bracket; over it, the whole bracket is descriptive - not
expanded into per-source citations, and not reported as unlinked either, since it was
never a citation attempt to begin with. It's collected separately
(`CitationResult.descriptive_ranges`) so it stays visible rather than disappearing
silently.

T-041, real finding: the first version of this rule only checked a *single piece's own*
span against the threshold - a range like "1-31" (one piece, span 31) was caught, but a
model spelling the identical "all N sources" claim out as 31 individual comma-separated
numbers ("[1,2,3,...,31]") was not, since each bare number has span 1 on its own. The
rule now sums every piece's span across the whole bracket - a range and a comma-list
enumeration of the same size are classified identically, matching D-015's original
intent ("more than N numbers named in one bracket is descriptive"), not just its first,
incomplete implementation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from vg09.retrieval import Candidate

_BRACKET_RE = re.compile(r"\[([^\]]+)\]")
_RANGE_RE = re.compile(r"^(\d+)-(\d+)$")

# D-015/T-041: a bracket naming this many numbers or fewer (summed across every
# comma-separated piece, range or bare) is a real multi-source citation and resolves
# like a comma list; more than this is treated as a descriptive enumeration ("reviewed
# sources [1] to [31]", or the same claim spelled out as "[1,2,3,...,31]"), not
# evidence for a claim.
DESCRIPTIVE_BRACKET_THRESHOLD = 5


@dataclass
class Citation:
    doc_id: str
    title: str
    feed_date: str
    url: str
    is_fallback: bool  # True iff built from a title_description fallback document (D-006)
    arxiv_published_at: str | None = None  # papers only
    text_source: str | None = None  # T-042: "captions" | "whisper" | "title_description"
    # | None (HF papers) - the real three-tier value is_fallback alone collapses into
    # two (fallback vs not); the chat UI's source-card badge needs the real distinction.
    # Display-only addition - is_fallback's own meaning and every existing caller of it
    # is unchanged


@dataclass
class CitationResult:
    citations: list[Citation]  # deduplicated by doc_id, first-cited order
    unlinked_references: list[str]  # raw bracket text ("[27]", "[Title, 2026-09-09]", ...)
    # that could not be resolved to a real chunk - deduplicated, first-seen order,
    # never silently hidden
    descriptive_ranges: list[str] = field(default_factory=list)  # raw bracket text of a
    # long numeric range ("[1-31]") judged descriptive rather than a citation (D-015) -
    # deduplicated, first-seen order; not in unlinked_references (it was never a failed
    # citation attempt) and not expanded into per-source citations either


def _citation_from_chunk(c: Candidate) -> Citation:
    m = c.metadata
    return Citation(
        doc_id=m["doc_id"],
        title=m["title"],
        feed_date=m["feed_date"],
        url=m["url"],
        is_fallback=(m.get("text_source") == "title_description"),
        arxiv_published_at=m.get("arxiv_published_at"),
        text_source=m.get("text_source"),
    )


def build_citations(answer: str, source_map: dict[int, Candidate]) -> CitationResult:
    """Scans the answer text (not the reasoning - the reasoning is never shown to the
    user, T-011) for bracketed references. A reference resolves only if its content is
    a bare integer (or, T-040/D-015, part of a short numeric range) that's a real key
    in `source_map` - anything else (a non-numeric bracket, a number outside the range
    actually offered, or a long range judged descriptive) is unlinked or descriptive,
    not guessed at. When the same document is cited more than once (the same number
    twice, or two different numbers that happen to be chunks of the same document), only the first
    occurrence becomes a citation - one entry per document, not per chunk or per
    citation mark.

    T-028, real finding: a bracket can hold more than one comma-separated number
    ("[17, 18]") - the model does this for a claim drawing on several sources at once.
    Each number in that bracket is resolved independently, exactly as if it had been
    its own bracket - a bracket where some numbers resolve and others don't reports
    only the failing ones as unlinked, the rest still become real citations. A bracket
    that *isn't* a comma-separated list of bare numbers or numeric ranges (T-024's
    original non-numeric case, e.g. the never-reliably-followed "[Title, YYYY-MM-DD]"
    shape) is still reported as one whole unlinked reference, unchanged - splitting
    only applies once every comma-separated piece is confirmed to be a bare number or a
    valid range, so a citation-shaped bracket that merely happens to contain a comma
    elsewhere isn't torn apart by mistake.

    T-040/D-015, real finding: a comma-separated piece can also be a numeric range
    ("[1-20]", "[21-22]"). A bracket naming at most `DESCRIPTIVE_BRACKET_THRESHOLD`
    numbers in total (summed across every piece, range or bare) is a real multi-source
    citation and expands exactly like a comma list - each number resolved
    independently. A bracket naming more than that is the model describing "all N
    sources" rather than citing evidence, so it is not expanded into one citation per
    number (which would fabricate citations for a sentence that was never citing
    anything) - it is collected whole into `CitationResult.descriptive_ranges` instead,
    still visible, just not treated as either a citation or a failed one.

    T-041, real finding: the threshold is checked against the *sum* of every piece's
    span, not any single piece in isolation - a long range ("[1-31]") and the same claim
    spelled out as 31 individual comma-separated bare numbers ("[1,2,...,31]") are both
    over-threshold and both classified as descriptive, the same way. A bracket mixing a
    short piece with a long range/enumeration is descriptive as a whole too - a bracket
    dominated by a "reviewed all sources" claim isn't meaningfully still a citation for
    its other, smaller piece."""
    citations: list[Citation] = []
    seen_doc_ids: set[str] = set()
    unlinked: list[str] = []
    seen_unlinked: set[str] = set()
    descriptive_ranges: list[str] = []
    seen_descriptive: set[str] = set()

    def add_unlinked(raw: str) -> None:
        if raw not in seen_unlinked:
            seen_unlinked.add(raw)
            unlinked.append(raw)

    def add_descriptive(raw: str) -> None:
        if raw not in seen_descriptive:
            seen_descriptive.add(raw)
            descriptive_ranges.append(raw)

    def part_bounds(part: str) -> tuple[int, int] | None:
        """Returns the inclusive (start, end) integer bounds a bracket piece stands
        for, without ever materializing them into a list. A bare number "n" is
        (n, n); a valid "start-end" range (start <= end) is (start, end); anything
        else - including a reversed range - is not a citation shape at all, and
        returns None so the whole bracket falls back to being reported as one
        unlinked reference.

        Deliberately returns bounds, not numbers: a deep-review finding (2026-09-22)
        caught the previous version calling `list(range(start, end + 1))` before the
        descriptive-bracket size check ran, so a single pathological or hallucinated
        bracket (e.g. "[1-500000000]") in real model output would materialize a huge
        list before being discarded. Each piece's `end - start + 1` is summed across
        the whole bracket and checked against `DESCRIPTIVE_BRACKET_THRESHOLD` in the
        caller *before* any range is ever built - this function's job is only to say
        how big a piece would be, cheaply."""
        if part.isdigit():
            n = int(part)
            return (n, n)
        m = _RANGE_RE.match(part)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            if start <= end:
                return (start, end)
        return None

    for match in _BRACKET_RE.finditer(answer):
        raw = match.group(0)
        parts = [p.strip() for p in match.group(1).split(",")]
        bounds = [part_bounds(p) for p in parts]

        if any(b is None for b in bounds):
            add_unlinked(raw)
            continue

        # T-041: summed across every piece, not just checked per-piece - a range and
        # a comma-list enumeration naming the same count of numbers are treated alike.
        if sum(end - start + 1 for start, end in bounds) > DESCRIPTIVE_BRACKET_THRESHOLD:
            add_descriptive(raw)
            continue

        # Every piece is confirmed valid and the bracket's total is no larger than the
        # threshold (checked above, without materializing anything) - only now is it
        # cheap and safe to actually build each piece's numbers.
        for number in (n for start, end in bounds for n in range(start, end + 1)):
            chunk = source_map.get(number)
            if chunk is None:
                add_unlinked(f"[{number}]")
                continue

            doc_id = chunk.metadata["doc_id"]
            if doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc_id)
            citations.append(_citation_from_chunk(chunk))

    return CitationResult(
        citations=citations,
        unlinked_references=unlinked,
        descriptive_ranges=descriptive_ranges,
    )
