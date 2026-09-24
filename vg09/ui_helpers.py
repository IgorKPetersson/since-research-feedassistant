"""T-025: small, pure logic pulled out of app.py so it's unit-testable without a
running Streamlit session - app.py itself is a thin rendering layer over this and the
rest of vg09/.

T-042/D-016: UI-facing text is English throughout (this module's included) - see
docs/DECISIONS.md D-016 for why.

T-045: the app's real name and visual identity live here too - APP_NAME, the accent
colour (also set in .streamlit/config.toml - see that file's own comment for why it
can't be a single shared Python constant across both), and the Google Fonts typeface.
"""

from __future__ import annotations

import re
from datetime import date

from vg09.citations import Citation
from vg09.retrieval import Candidate

# T-045: "Since" - what's happened since you last checked. Display-only rename -
# vg09/ (the package/import path) and vg09.store.COLLECTION_NAME stay untouched,
# same out-of-scope boundary T-035 already drew for the project's own earlier rename.
APP_NAME = "Since"

# Matches .streamlit/config.toml's [theme] primaryColor - the two can't share one
# Python constant (config.toml isn't Python), so this comment is the cross-reference.
ACCENT_COLOR = "#C17F1A"

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


_MONTH_ABBR = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def format_date_range_short(date_range: tuple[date, date] | None) -> str:
    """T-044: the pipeline strip's "Date range" tile - the real resolved window,
    compactly ("Sep 11-17" same month, "Sep 28 - Oct 3" across a month boundary,
    "Sep 16" a single day), or "None" when no window was resolved (unfiltered search
    or ranking mode both have no bounded window to show - `describe_retrieval_mode()`,
    shown in full alongside this tile, still tells those two apart).

    Built by hand rather than via `date.strftime()`'s day-of-month formats: `%-d`
    (no leading zero) is a POSIX strftime extension, not supported by Windows' C
    runtime this project actually runs on (`%#d` there instead) - string-building the
    day number directly (`str(d.day)`) sidesteps the platform difference entirely."""
    if date_range is None:
        return "None"
    start, end = date_range
    if start == end:
        return f"{_MONTH_ABBR[start.month]} {start.day}"
    if start.year == end.year and start.month == end.month:
        return f"{_MONTH_ABBR[start.month]} {start.day}-{end.day}"
    return f"{_MONTH_ABBR[start.month]} {start.day} - {_MONTH_ABBR[end.month]} {end.day}"


def format_corpus_summary(stats: dict, latest: date | None) -> str:
    """T-045: the compact header line's right-hand side - real corpus counts and
    freshness on one line next to the "Since" wordmark, replacing T-042's separate
    3-column st.metric status bar (that read as a second big header, not one compact
    line - the opposite of this ticket's "no big centered title, no subtitle line"
    goal). Same real data source (`vg09.store.corpus_stats()`/`latest_feed_date()`),
    only the rendering changed."""
    counts = f"{stats['hf_documents']} papers · {stats['youtube_documents']} videos · {stats['chunks']} chunks"
    if latest is None:
        return counts
    return f"{counts} · Caught up through {latest.isoformat()}"


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
    """T-042/T-045: replaces every resolved `[N]`/`[N, M]`/`[N-M]` citation marker in
    the answer with a small HTML chip, in the UI's one accent colour (`ACCENT_COLOR`
    - T-045 dropped T-042's original per-source-type chip colouring, by my explicit
    decision: source type is still visible via the unchanged PAPER/VIDEO badge on each
    source card, chips themselves now just point there), linking to that source's card
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
    citation-resolution one (unchanged since T-042)."""
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
            chips.append(f'<a class="citation-chip" href="#cite-{card_index}">{n}</a>')
        return "".join(chips) if chips else raw

    return _BRACKET_RE.sub(replace, answer)


# T-042/T-045: flat, theme-adaptive (no hardcoded page background/text color - the
# accent colour and the source-badge swatches are fixed, deliberately, so they read
# the same regardless of which Streamlit theme is active, light or dark). No
# gradients, no box-shadow, no emoji. Streamlit's own components
# (st.container(border=True), st.metric, st.progress, st.columns) cover everything
# else - this covers only what they can't: the Google Fonts typeface, and inline
# clickable citation markers.
#
# Font-family is set on html/body/.stApp AND every `[data-testid]` element (plus
# their descendants), not a blanket "*" selector - a "*" rule would also override
# Streamlit's own higher-specificity icon-font rules (e.g. the reasoning expander's
# arrow glyph), turning icons into literal text; icon elements carry no data-testid,
# so `[data-testid]` stays safe without needing to enumerate every icon selector
# defensively. `html, body, .stApp` alone lost in real testing (T-045's own live
# verification, not assumed): Streamlit re-applies its own font via `!important` on
# `[data-testid="stMarkdownContainer"]` - confirmed via real computed-style
# inspection - equal specificity to a plain class selector, so Streamlit's own rule
# won the cascade tie. `[data-testid]` (attribute-exists) matches every one of
# Streamlit's own stable customization hooks at once, including that one, with its
# own `!important` so the tie resolves the other way.
#
# Plain template + str.replace() rather than an f-string/`.format()` call - the CSS
# below is full of its own literal "{"/"}" braces, which an f-string would try to
# parse as expressions. A placeholder token sidesteps that entirely.
#
# The font is loaded via a CSS @import inside <style>, not a <link rel="stylesheet">
# element - found live (T-045's own real verification): st.html() silently strips
# <link> tags entirely (confirmed - zero survived in the rendered DOM), while a
# <style> block's own content, including an @import inside it, passes through
# untouched. @import must be the very first rule in the stylesheet (a real CSS
# constraint, not a style choice) - kept on its own line before anything else.
_CUSTOM_CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');

html, body, .stApp, [data-testid], [data-testid] * {
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* The broad rule above's own comment claimed "icon elements carry no data-testid" -
   found live (T-045's own real verification) that this was simply wrong: Streamlit's
   Material icon wrapper (the reasoning expander's arrow, among others) IS itself a
   [data-testid="stIconMaterial"] element, so the broad rule above broke it - real
   rendering, not a hypothetical: "keyboard_arrow_right" showed as literal overlapping
   text instead of an arrow glyph. Restored explicitly, after the broad rule so this
   one wins the tie (equal specificity, equal !important, declared later). */
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}

/* Scoped under stMarkdownContainer and !important: Streamlit's own markdown link rule
   otherwise wins and renders chip numbers as blue underlined link text. Dark text,
   not white: 5.24:1 on the accent vs white's 3.32:1 (below WCAG AA for small text). */
[data-testid="stMarkdownContainer"] a.citation-chip,
a.citation-chip {
    display: inline-block;
    padding: 0 0.35em;
    margin: 0 0.1em;
    border-radius: 0.25em;
    font-size: 0.8em;
    font-weight: 600;
    text-decoration: none !important;
    color: #1a1a1a !important;
    background-color: __ACCENT_COLOR__;
    line-height: 1.6;
}
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

/* T-044: the pipeline strip's five metrics, scoped to that one keyed container
   (st.container(key="pipeline_strip") in app.py - Streamlit's own supported way to
   target a specific region with custom CSS) so the status bar's corpus-count tiles
   (Papers/Videos/Chunks) are untouched - I asked about the pipeline metrics
   specifically, not those. st.metric's default value size is a large "hero number"
   style meant to be the dominant element on a KPI dashboard - backwards here, where
   the answer paragraph these numbers describe is what actually matters most on the
   page. Sized below normal body text (Streamlit's own default is ~1rem), not just
   "smaller than before".
*/
.st-key-pipeline_strip [data-testid="stMetricValue"] {
    font-size: 0.95rem;
    font-weight: 600;
}
.st-key-pipeline_strip [data-testid="stMetricLabel"] {
    font-size: 0.7rem;
}

/* T-045: the compact header - "Since" small and left, corpus counts/freshness on the
   same line to its right. Replaces T-042's big centered st.title() + subtitle
   caption + separate 3-column metric status bar entirely. */
.app-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    column-gap: 1.5rem;
    row-gap: 0.25rem;
    padding-bottom: 0.6rem;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
}
.app-name {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}
.app-stats {
    font-size: 0.85rem;
    opacity: 0.7;
}
</style>
"""

CUSTOM_CSS = _CUSTOM_CSS_TEMPLATE.replace("__ACCENT_COLOR__", ACCENT_COLOR)
