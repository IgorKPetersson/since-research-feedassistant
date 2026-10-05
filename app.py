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

import requests
import streamlit as st

import chromadb.errors

from vg09 import ingest_job, sources, sources_page
from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import NUM_CTX, retrieve
from vg09.store import corpus_stats, is_empty, latest_feed_date
from vg09.ui_helpers import (
    APP_NAME,
    CUSTOM_CSS,
    EXAMPLE_QUESTIONS,
    LOGO_MARK_PATH,
    build_retrieval_ranks,
    citation_source_type,
    describe_retrieval_mode,
    escape_markdown_link_text,
    format_corpus_summary,
    format_date_range_short,
    logo_mark_html,
    render_citation_chips,
    staleness_note,
    text_source_label,
    update_note,
)

_SOURCE_TYPE_LABEL = {"paper": "PAPER", "video": "VIDEO", "unknown": "SOURCE"}

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
    notes = [n for n in (staleness_note(latest, date.today()), update_note(job)) if n]
    notes_html = "".join(f' · <span class="app-stale">{n}</span>' for n in notes)
    st.markdown(
        f'<div class="app-header"><span class="app-brand">{logo_mark_html()}'
        f'<span class="app-name">{APP_NAME}</span></span>'
        f'<span class="app-stats">{format_corpus_summary(counts, latest)}{notes_html}</span></div>',
        unsafe_allow_html=True,
    )


_header()


def _fill_question(text: str) -> None:
    st.session_state["question_input"] = text


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
        if use_manual_range:
            today = latest_feed_date() or date.today()
            start = st.date_input("From", value=today - timedelta(days=7))
            end = st.date_input("To", value=today)
            if start and end:
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

    today = latest_feed_date()
    # T-029: the manual-override-always-wins precedence lives in resolve_date_range()
    # itself (T-021's own contract) - called once here for the value actually used,
    # and separately (override=None) only so describe_retrieval_mode() can show what
    # the question alone would have resolved to, for the user's own inspection.
    interpreted_range = resolve_date_range(question, today, manual_override=None)
    date_range = resolve_date_range(question, today, manual_override=manual_range)
    ranking = detect_recency_ranking(question)

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
    st.caption(describe_retrieval_mode(interpreted_range, ranking, manual_range))

    try:
        retrieval = retrieve(question, date_range=date_range, ranking=ranking)
        candidates_slot.metric("Candidates", retrieval.candidates_considered)
        dedup_slot.metric("After dedup", retrieval.candidates_after_dedup)
        packed_slot.metric("Packed", len(retrieval.chunks))

        start_t = time.monotonic()
        result = generate_answer(question, retrieval.chunks)
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
    )
    st.markdown(chip_answer, unsafe_allow_html=True)

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
                badges_html += f'<span class="text-source-badge">{ts_label}</span>'
            rank = ranks.get(c.doc_id)
            if rank:
                badges_html += f'<span class="retrieval-rank">retrieval rank #{rank}</span>'

            with st.container(border=True):
                st.markdown(badges_html, unsafe_allow_html=True)
                arxiv_note = f" · arXiv {c.arxiv_published_at[:10]}" if c.arxiv_published_at else ""
                st.markdown(f"**[{title}]({c.url})**  \n{c.feed_date}{arxiv_note}")

    if citations.unlinked_references:
        st.caption(
            "References in the answer that couldn't be linked to a source: "
            + ", ".join(citations.unlinked_references)
        )
    if citations.descriptive_ranges:
        st.caption(
            "Descriptive ranges (e.g. \"all N sources\") — not source citations: "
            + ", ".join(citations.descriptive_ranges)
        )


# T-056: a first start - nothing stored and no saved choice of sources - opens on
# Sources, where the choice is made, rather than on a question field with nothing behind it.
first_start = stats["chunks"] == 0 and not sources.load().saved
ASK_PAGE = st.Page(ask_page, title="Ask", icon=":material/search:", url_path="ask",
                   default=not first_start)
SOURCES_PAGE = st.Page(sources_page.render, title="Sources", icon=":material/rss_feed:",
                       url_path="sources", default=first_start)
st.navigation([ASK_PAGE, SOURCES_PAGE]).run()
