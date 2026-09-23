"""T-025: small, pure logic pulled out of app.py so it's unit-testable without a
running Streamlit session - app.py itself is a thin rendering layer over this and the
rest of vg09/.

T-042/D-016: UI-facing text is English throughout (this module's included) - see
docs/DECISIONS.md D-016 for why.
"""

from __future__ import annotations

import re
from datetime import date

from vg09.citations import Citation
from vg09.retrieval import Candidate

_MARKDOWN_SPECIAL_CHARS = "\\`*_[]"


def escape_markdown_link_text(text: str) -> str:
    """T-029: real HF/YouTube titles are free text pulled straight from a source's own
    API - not authored for this app - and can contain markdown-significant characters
    ("]" closes a `[text](url)` citation link's text portion early; a real example:
    "He Built The Ultimate Spy Tool (Free and Open-Source)"). Escaping keeps the
    rendered link intact regardless of what a real title contains. Backslash is escaped
    first so escaping the rest doesn't double-escape it."""
    result = text.replace("\\", "\\\\")
    for ch in _MARKDOWN_SPECIAL_CHARS[1:]:
        result = result.replace(ch, f"\\{ch}")
    return result


def describe_retrieval_mode(
    date_range: tuple[date, date] | None,
    ranking: bool,
    manual_override: tuple[date, date] | None,
) -> str:
    """Human-readable description of which of T-022's mechanisms actually fired for
    this answer - shown in the UI so the user can always see which one, not just the
    answer text. Priority matches `vg09.date_range.resolve_date_range()`: a manual
    override always wins over whatever was (or wasn't) interpreted. English text per
    D-016 - was Swedish before T-042; the logic (which mode fired, and why) is
    unchanged."""
    if manual_override is not None:
        start, end = manual_override
        return f"Date filter (manually set): {start} – {end}"
    if date_range is not None:
        start, end = date_range
        return f"Date filter (interpreted from the question): {start} – {end}"
    if ranking:
        return "Mode: sorted by most recent (ranking, no date filter)"
    return "No date filter — unbounded search"


# T-042: one example question per docs/GOAL.md question type ("what's new", "did X
# come up", "has Q progressed over the last n weeks") - real topics this project's own
# real corpus actually covers (recursive self-improvement, coding agents both appear
# throughout docs/eval-results/), not placeholders, but deliberately not copied
# verbatim from docs/eval-questions.md's hidden facit set.
EXAMPLE_QUESTIONS: list[tuple[str, str]] = [
    ("What's new", "What's new in AI agent research this week?"),
    ("Did X come up", "Has Anthropic been mentioned in the last two weeks?"),
    ("Has Q progressed", "How has research on coding agents developed over the last month?"),
]


def citation_source_type(url: str) -> str:
    """Infers "paper" vs "video" from a citation's real url. `vg09.citations.Citation`
    doesn't carry the source type explicitly - T-024 never needed it - and this
    project has exactly two sources with a stable, distinctive real url shape (D-001),
    so inferring it here for display is safer than adding another field to `Citation`
    for a UI-only concern. Returns "unknown" rather than guessing if neither shape
    matches - a real, if currently unreachable, defensive case."""
    if "huggingface.co" in url:
        return "paper"
    if "youtube.com" in url:
        return "video"
    return "unknown"


_TEXT_SOURCE_LABELS = {
    "captions": "captions",
    "whisper": "whisper",
    "title_description": "title + description",
}


def text_source_label(text_source: str | None) -> str | None:
    """T-042: the source card's text_source badge label - None for an HF paper
    (text_source is only ever set on a YouTube chunk, D-001/D-009/T-012), otherwise
    the real three-tier value (captions/whisper/title_description), not the coarser
    is_fallback boolean."""
    if text_source is None:
        return None
    return _TEXT_SOURCE_LABELS.get(text_source, text_source)


def short_mode_label(
    date_range: tuple[date, date] | None,
    ranking: bool,
    manual_override: tuple[date, date] | None,
) -> str:
    """T-042: the pipeline strip's compact "Mode" tile - a single short word, not the
    full sentence `describe_retrieval_mode()` renders (still shown in full alongside
    it). Same priority order, same underlying mechanism - a display-only variant.
    Kept to <= 8 characters deliberately - `st.metric`'s value truncates with an
    ellipsis inside a narrow column (found live, T-042's own real verification -
    "Unfiltered" truncated to "Unfilt…" at 5 equal-width columns)."""
    if manual_override is not None:
        return "Manual"
    if date_range is not None:
        return "Filtered"
    if ranking:
        return "Ranking"
    return "None"


def build_retrieval_ranks(chunks: list[Candidate]) -> dict[str, int]:
    """1-based rank of each document's first (best) chunk in the real packed retrieval
    order - `vg09.retrieval.retrieve()`'s own `chunks` list is already in that order
    (relevance- or recency-first, T-022/T-027); this only records first-occurrence
    position per `doc_id` for display, not a new ranking decision."""
    ranks: dict[str, int] = {}
    for i, c in enumerate(chunks, start=1):
        doc_id = c.metadata.get("doc_id")
        if doc_id is not None and doc_id not in ranks:
            ranks[doc_id] = i
    return ranks


_BRACKET_RE = re.compile(r"\[([^\]]+)\]")
_RANGE_PIECE_RE = re.compile(r"^(\d+)-(\d+)$")


def _numbers_in_resolved_bracket(raw_inner: str) -> list[int]:
    """`raw_inner` is a bracket's content already confirmed, by the caller, to be
    neither unlinked nor a D-015 descriptive range - i.e.
    `vg09.citations.build_citations()` resolved every number in it that it could.
    Splits it back into individual numbers purely for building one chip per number -
    does not re-decide whether any of them resolve; that decision already happened in
    `vg09.citations`, and this function trusts it rather than repeating it."""
    numbers: list[int] = []
    for piece in raw_inner.split(","):
        piece = piece.strip()
        if piece.isdigit():
            numbers.append(int(piece))
            continue
        m = _RANGE_PIECE_RE.match(piece)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            numbers.extend(range(start, end + 1))
    return numbers


def render_citation_chips(
    answer: str,
    source_map: dict[int, Candidate],
    citations: list[Citation],
    unlinked_references: list[str],
    descriptive_ranges: list[str],
) -> str:
    """T-042: replaces every resolved `[N]`/`[N, M]`/`[N-M]` citation marker in the
    answer with a small, source-type-colored HTML chip linking to that source's card
    anchor (`#cite-<card index>`, 1-based, matching the order source cards are
    rendered in below). A bracket already reported as unlinked or a descriptive range
    is left exactly as written - those are explained by their own notices already,
    not citations to chip-ify. A number inside an otherwise-resolved bracket that
    still can't be mapped to a real citation (shouldn't happen, but not assumed) is
    silently dropped from the inline chip run rather than guessed at - a defensive
    case, not the common path.

    Reuses `build_citations()`'s own classification via the `unlinked_references`/
    `descriptive_ranges` lists it already returned, rather than re-deciding it - only
    extracts which individual numbers to link, a rendering concern, not a
    citation-resolution one (unchanged by this ticket)."""
    doc_id_to_card_index: dict[str, int] = {}
    for i, c in enumerate(citations, start=1):
        doc_id_to_card_index.setdefault(c.doc_id, i)

    unlinked_set = set(unlinked_references)
    descriptive_set = set(descriptive_ranges)

    def replace(match: re.Match) -> str:
        raw = match.group(0)
        if raw in unlinked_set or raw in descriptive_set:
            return raw

        chips = []
        for n in _numbers_in_resolved_bracket(match.group(1)):
            candidate = source_map.get(n)
            if candidate is None:
                continue
            doc_id = candidate.metadata.get("doc_id")
            card_index = doc_id_to_card_index.get(doc_id)
            if card_index is None:
                continue
            css_class = f"citation-chip chip-{citation_source_type(candidate.metadata.get('url', ''))}"
            chips.append(f'<a class="{css_class}" href="#cite-{card_index}">{n}</a>')
        return "".join(chips) if chips else raw

    return _BRACKET_RE.sub(replace, answer)


# T-042: flat, theme-adaptive (no hardcoded page background/text color - only the two
# chip/badge swatches are fixed, deliberately, so they read the same regardless of
# which Streamlit theme is active, light or dark). No gradients, no box-shadow, no
# emoji. Streamlit's own components (st.container(border=True), st.metric,
# st.progress, st.columns) cover everything else - this covers only what they can't:
# inline clickable, colored citation markers.
CUSTOM_CSS = """
<style>
.citation-chip {
    display: inline-block;
    padding: 0 0.35em;
    margin: 0 0.1em;
    border-radius: 0.25em;
    font-size: 0.8em;
    font-weight: 600;
    text-decoration: none;
    color: #ffffff;
    line-height: 1.6;
}
.citation-chip.chip-paper { background-color: #3b6ea5; }
.citation-chip.chip-video { background-color: #a5573b; }
.citation-chip.chip-unknown { background-color: #6b6b6b; }
.citation-chip:hover { opacity: 0.85; }

.source-badge {
    display: inline-block;
    padding: 0.1em 0.5em;
    margin-right: 0.4em;
    border-radius: 0.25em;
    font-size: 0.75em;
    font-weight: 700;
    letter-spacing: 0.03em;
    color: #ffffff;
}
.source-badge.badge-paper { background-color: #3b6ea5; }
.source-badge.badge-video { background-color: #a5573b; }
.source-badge.badge-unknown { background-color: #6b6b6b; }

.text-source-badge {
    display: inline-block;
    padding: 0.1em 0.5em;
    margin-right: 0.4em;
    border-radius: 0.25em;
    font-size: 0.75em;
    border: 1px solid currentColor;
    opacity: 0.75;
}

.retrieval-rank {
    font-size: 0.75em;
    opacity: 0.65;
}
</style>
"""
