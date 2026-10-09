"""T-025: the chat UI. One question, one answer, its sources - no conversation
history (`docs/GOAL.md`'s explicit non-goal), no accounts.

T-042: redesigned layout (status bar, a live pipeline strip, citation chips, source
cards) - presentation only, every number shown comes from data the pipeline already
produces (`vg09.date_range`/`vg09.retrieval`/`vg09.answer`/`vg09.citations`'s actual
behavior is unchanged). UI text is English throughout, D-016.

T-045: real visual identity - the app is named "Since" (display strings only, `vg09`/
`COLLECTION_NAME` untouched, same boundary T-035 drew), a compact single-line header
replaces the old big centered title, a Google Fonts typeface and one accent colour
(`.streamlit/config.toml`) replace Streamlit's stock look.

T-056 (D-017): two pages - asking (this file's `ask_page()`) and Sources
(`vg09/sources_page.py`), where the watched sources are chosen and fetched.

A thin rendering layer: every real decision (date-range extraction, retrieval,
answer generation, citation resolution) already lives in `vg09/` and is unit- and
real-data-tested there (T-021-T-024). Run with `streamlit run app.py`.
"""

from __future__ import annotations

import time
from datetime import date, timedelta
from html import escape as escape_html

import requests
import streamlit as st

import chromadb.errors

from vg09 import coverage, ingest_job, reference_date, sources, sources_page
from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import (
    detect_recency_ranking,
    manual_range_error,
    resolve_date_range,
    unresolved_time_phrase,
)
from vg09.quote_links import misattributed_quotes, quote_times
from vg09.source_filter import detect_source
from vg09.retrieval import NUM_CTX, retrieve
from vg09.store import corpus_stats, is_empty, latest_feed_date
from vg09.ui_helpers import (
    APP_NAME,
    CUSTOM_CSS,
    EXAMPLE_QUESTIONS,
    LOGO_MARK_PATH,
    build_retrieval_ranks,
    citation_source_type,
    clarify_choices,
    clarify_message,
    dates_note,
    describe_retrieval_mode,
    escape_markdown_link_text,
    format_corpus_summary,
    format_date_range_short,
    logo_mark_html,
    misattribution_note,
    past_newest_note,
    reference_note,
    render_citation_chips,
    staleness_note,
    text_source_label,
    update_note,
    video_date_note,
)

_SOURCE_TYPE_LABEL = {"paper": "PAPER", "video": "VIDEO", "unknown": "SOURCE"}


def _reference_today() -> date | None:
    """T-093 (D-022): the user's calendar date in the configured time zone, or None
    after saying why when the configured zone is not a real one."""
    try:
        return reference_date.today()
    except reference_date.TimezoneError as exc:
        st.error(str(exc))
        return None

st.set_page_config(page_title=APP_NAME, page_icon=str(LOGO_MARK_PATH))
st.html(CUSTOM_CSS)

# --- Header (T-045): "Since" small and left, real corpus counts/freshness on the
# same line to its right - no big centered title, no subtitle line. Rendered before
# the empty-data check, not after: an empty store's real 0/0/0 counts are still real,
# honest data, not hidden - the empty-state message below is additional, not instead.
# T-056: when the data has fallen behind, the same line says by how many days.
# D-018: the first run of each browser session starts an update if none finished
# today, and the header follows it. ---
if "update_on_open_checked" not in st.session_state:
    st.session_state["update_on_open_checked"] = True
    ingest_job.start_on_open()
ingest_job.refresh_store_if_updated()  # before anything reads the store (T-056)
stats = corpus_stats()
st.session_state["header_counts"] = (stats, latest_feed_date())
st.session_state["header_seen_finish"] = ingest_job.status().get("finished")


@st.fragment(run_every=3)
def _header() -> None:
    """Reruns on its own every few seconds, so "Updating…" and the new counts appear
    without a page reload - a full rerun would wipe an answer on screen. Between full
    reruns the counts are read again only when an update has finished: they are a
    scan of every chunk's metadata."""
    job = ingest_job.status()
    ingest_job.refresh_store_if_updated()
    if st.session_state["header_seen_finish"] != job.get("finished"):
        st.session_state["header_seen_finish"] = job.get("finished")
        st.session_state["header_counts"] = (corpus_stats(), latest_feed_date())
    counts, latest = st.session_state["header_counts"]
    today = _reference_today()  # T-093: the same calendar date the questions use
    stale = staleness_note(latest, today) if today else None
    notes = [n for n in (stale, update_note(job)) if n]
    # T-089 (D-020): a note can carry the job's detail, read back from the status file.
    notes_html = "".join(f' · <span class="app-stale">{escape_html(n)}</span>' for n in notes)
    st.markdown(
        f'<div class="app-header"><span class="app-brand">{logo_mark_html()}'
        f'<span class="app-name">{APP_NAME}</span></span>'
        f'<span class="app-stats">{format_corpus_summary(counts, latest)}{notes_html}</span></div>',
        unsafe_allow_html=True,
    )


_header()


def _fill_question(text: str) -> None:
    st.session_state["question_input"] = text


def _choose_period(question: str, period) -> None:
    """T-094: remember the period chosen for this question; the rerun answers it."""
    st.session_state["time_choice"] = {"question": question, "range": period}


def ask_page() -> None:
    if is_empty():
        st.info("No data yet. Choose your sources and fetch them on the Sources page.")
        st.page_link(SOURCES_PAGE, label="Go to Sources")
        return

    st.caption("Try an example:")
    example_cols = st.columns(3)
    for col, (label, example_q) in zip(example_cols, EXAMPLE_QUESTIONS):
        col.button(label, on_click=_fill_question, args=(example_q,),
                   use_container_width=True, key=f"example_{label}")

    with st.sidebar:
        st.header("Date filter")
        st.caption(
            "The question is interpreted automatically (e.g. \"last week\"). Set your "
            "own range below to always override the interpretation."
        )
        use_manual_range = st.checkbox("Set a custom date range")
        manual_range: tuple[date, date] | None = None
        manual_error: str | None = None
        if use_manual_range:
            # T-093: the picker starts from the user's date, not the newest source.
            picker_today = _reference_today() or date.today()
            start = st.date_input("From", value=picker_today - timedelta(days=7))
            end = st.date_input("To", value=picker_today)
            manual_error = manual_range_error(start, end)
            if manual_error:
                st.error(manual_error)
            else:
                manual_range = (start, end)

    # T-051: a form, so that Enter in the field or one click on Ask each submit on their
    # own. As a bare text_input plus button, the typed text was only committed on Enter
    # or blur, and that commit's rerun swallowed the click - Enter and then Ask were both
    # needed.
    with st.form("ask_form", border=False):
        question = st.text_input(
            "Question:", key="question_input",
            placeholder="What's happened since…",
        )
        ask = st.form_submit_button("Ask", type="primary")

    # T-094: a period chosen for this question after it was asked about runs the question
    # again on its own, without another click on Ask.
    choice = st.session_state.get("time_choice")
    chosen = choice is not None and choice["question"] == question.strip()
    if choice is not None:
        del st.session_state["time_choice"]
    ask = ask or chosen

    if ask and not question.strip():
        st.warning("Write a question first.")
        return
    if not ask:
        return
    if ingest_job.is_writing_store():
        # T-056: the embedded store can't be searched while the update writes to it.
        # That stage takes seconds; the minutes of fetching before it don't block.
        st.info("New content is being made searchable right now. Ask again in a moment.")
        return

    if manual_error:
        st.error(f"The custom date range can't be used: {manual_error} Fix it or switch it off.")
        return
    # T-093 (D-022): one reference date for this question, passed to parsing, the date
    # filter and the answer prompt. The newest source date is shown apart from it.
    today = _reference_today()
    if today is None:
        return
    newest = latest_feed_date()
    # T-029: the manual-override-always-wins precedence lives in resolve_date_range()
    # itself (T-021's own contract) - called once here for the value actually used,
    # and separately (override=None) only so describe_retrieval_mode() can show what
    # the question alone would have resolved to, for the user's own inspection.
    interpreted_range = resolve_date_range(question, today, manual_override=None)
    date_range = resolve_date_range(question, today, manual_override=manual_range)
    ranking = detect_recency_ranking(question)
    source = detect_source(question)  # T-068: "papers" or "videos" narrows the search

    # T-094: time words without dates ("recently", "two weeks ago", an impossible date)
    # are asked about, not searched across every date. A custom range answers it already.
    if chosen:
        date_range = choice["range"]
    elif date_range is None and not ranking:
        phrase = unresolved_time_phrase(question, today)
        if phrase:
            st.warning(clarify_message(phrase))
            for col, (label, period) in zip(st.columns(3), clarify_choices(today)):
                col.button(label, key=f"period_{label}", use_container_width=True,
                           on_click=_choose_period, args=(question.strip(), period))
            return

    # --- Pipeline strip (T-042/T-044): filled in progressively, real data per stage,
    # as each stage actually completes - not one spinner wrapping the whole call.
    # Wrapped in a keyed container so CUSTOM_CSS can size these five metrics down
    # below the answer text without touching the status bar's corpus-count tiles. ---
    with st.container(key="pipeline_strip"):
        stage_cols = st.columns(5)
        date_range_slot = stage_cols[0].empty()
        candidates_slot = stage_cols[1].empty()
        dedup_slot = stage_cols[2].empty()
        packed_slot = stage_cols[3].empty()
        time_slot = stage_cols[4].empty()
        budget_slot = st.empty()

        for slot, label in (
            (candidates_slot, "Candidates"), (dedup_slot, "After dedup"),
            (packed_slot, "Packed"), (time_slot, "Time"),
        ):
            slot.metric(label, "…")

        # The real resolved window actually used for retrieval (post manual-override),
        # not the merely-interpreted one - matching every other tile's "what actually
        # happened" contract. "None" here covers both unfiltered search and ranking
        # mode (neither has a bounded window) - describe_retrieval_mode() right below
        # still tells those two apart in full.
        date_range_slot.metric("Date range", format_date_range_short(date_range))
    st.caption(describe_retrieval_mode(date_range if chosen else interpreted_range, ranking,
                                       manual_range, source=source, chosen=chosen))
    video_note = video_date_note(date_range, source)  # T-094
    if video_note:
        st.caption(video_note)
    config = sources.load()
    st.caption(dates_note(today, config.timezone, newest, coverage.papers_checked_through(),
                          coverage.videos_checked_through(config.channels)))
    beyond = past_newest_note(date_range, newest)
    if beyond:
        st.warning(beyond)

    try:
        retrieval = retrieve(question, date_range=date_range, ranking=ranking, source=source)
        candidates_slot.metric("Candidates", retrieval.candidates_considered)
        dedup_slot.metric("After dedup", retrieval.candidates_after_dedup)
        packed_slot.metric("Packed", len(retrieval.chunks))

        start_t = time.monotonic()
        result = generate_answer(question, retrieval.chunks, date_range=date_range, today=today)
        elapsed = time.monotonic() - start_t
        time_slot.metric("Time", f"{elapsed:.1f}s")

        pct = 100 * result.prompt_eval_count / NUM_CTX
        budget_slot.progress(
            min(result.prompt_eval_count / NUM_CTX, 1.0),
            text=f"Context budget: {result.prompt_eval_count} / {NUM_CTX} tokens ({pct:.0f}%)",
        )

        citations = build_citations(result.answer, result.source_map)
    except requests.exceptions.RequestException:
        st.error("Ollama isn't responding — is it running, and is the model pulled?")
        return
    except chromadb.errors.ChromaError:
        # The update began writing between the check above and the search itself.
        st.info("New content is being made searchable right now. Ask again in a moment.")
        return

    # T-039: shown whenever a second attempt was made, whether or not it succeeded -
    # the user should know the answer took a second try, and (below) whether even that
    # one was cut off.
    if result.retries:
        st.info("The first attempt was cut off by the length limit, so the question was run again.")

    if result.incomplete:
        st.warning("The answer is incomplete — it was cut off by the length limit before finishing.")

    # --- Answer with citation chips (T-042) ---
    chip_answer = render_citation_chips(
        result.answer, result.source_map, citations.citations,
        citations.unlinked_references, citations.descriptive_ranges,
        quote_seconds=quote_times(result.answer, result.source_map),  # T-063
    )
    st.markdown(chip_answer, unsafe_allow_html=True)

    # T-064: a quote credited to a source that doesn't contain it is the answer's own
    # error, so it is said right under the answer, not tucked away with the sources.
    misattributed = misattribution_note(misattributed_quotes(result.answer, result.source_map))
    if misattributed:
        st.warning(misattributed)

    with st.expander("Show the model's reasoning"):
        st.text(result.reasoning)

    # --- Source cards (T-042), replacing the bullet list ---
    ranks = build_retrieval_ranks(retrieval.chunks)

    st.subheader("Sources")
    if not citations.citations:
        st.caption("No sources could be linked to the answer.")
    with st.container(key="source_cards"):
        for i, c in enumerate(citations.citations, start=1):
            source_type = citation_source_type(c.url)
            title = escape_markdown_link_text(c.title)
            badges_html = (
                f'<div id="cite-{i}"></div>'
                f'<span class="source-badge">{_SOURCE_TYPE_LABEL[source_type]}</span>'
            )
            ts_label = text_source_label(c.text_source)
            if ts_label:
                # T-089 (D-020): an unknown stored value is shown as it is, so escape it.
                badges_html += f'<span class="text-source-badge">{escape_html(ts_label)}</span>'
            rank = ranks.get(c.doc_id)
            if rank:
                badges_html += f'<span class="retrieval-rank">retrieval rank #{rank}</span>'

            with st.container(border=True):
                st.markdown(badges_html, unsafe_allow_html=True)
                arxiv_note = f" · arXiv {c.arxiv_published_at[:10]}" if c.arxiv_published_at else ""
                st.markdown(f"**[{title}]({c.url})**  \n{c.feed_date}{arxiv_note}")

    for note in (
        reference_note("References in the answer that couldn't be linked to a source: ",
                       citations.unlinked_references),
        reference_note("Descriptive ranges (e.g. \"all N sources\") — not source citations: ",
                       citations.descriptive_ranges),
    ):
        if note:
            st.caption(note)


# T-056: a first start - nothing stored and no saved choice of sources - opens on
# Sources, where the choice is made, rather than on a question field with nothing behind it.
first_start = stats["chunks"] == 0 and not sources.load().saved
ASK_PAGE = st.Page(ask_page, title="Ask", icon=":material/search:", url_path="ask",
                   default=not first_start)
SOURCES_PAGE = st.Page(sources_page.render, title="Sources", icon=":material/rss_feed:",
                       url_path="sources", default=first_start)
st.navigation([ASK_PAGE, SOURCES_PAGE]).run()
