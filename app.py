"""T-025: the chat UI. One question, one answer, its sources - no conversation
history (`docs/GOAL.md`'s explicit non-goal), no accounts.

T-042: redesigned layout (status bar, a live pipeline strip, citation chips, source
cards) - presentation only, every number shown comes from data the pipeline already
produces (`vg09.date_range`/`vg09.retrieval`/`vg09.answer`/`vg09.citations`'s actual
behavior is unchanged). UI text is English throughout, D-016.

A thin rendering layer: every real decision (date-range extraction, retrieval,
answer generation, citation resolution) already lives in `vg09/` and is unit- and
real-data-tested there (T-021-T-024). Run with `streamlit run app.py`.
"""

from __future__ import annotations

import time
from datetime import date, timedelta

import requests
import streamlit as st

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import NUM_CTX, retrieve
from vg09.store import corpus_stats, is_empty, latest_feed_date
from vg09.ui_helpers import (
    CUSTOM_CSS,
    EXAMPLE_QUESTIONS,
    build_retrieval_ranks,
    citation_source_type,
    describe_retrieval_mode,
    escape_markdown_link_text,
    render_citation_chips,
    short_mode_label,
    text_source_label,
)

_SOURCE_TYPE_LABEL = {"paper": "PAPER", "video": "VIDEO", "unknown": "SOURCE"}

st.set_page_config(page_title="research-feed-assistant", page_icon=":material/search:")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("research-feed-assistant")
st.caption("Ask what's new, whether a topic came up, or how it has developed over time.")

if is_empty():
    st.info("No data yet — run ingest.")
    st.stop()

# --- Status bar (T-042): real corpus size and freshness, never hardcoded ---
stats = corpus_stats()
latest = latest_feed_date()

status_cols = st.columns(3)
status_cols[0].metric("Papers", stats["hf_documents"])
status_cols[1].metric("Videos", stats["youtube_documents"])
status_cols[2].metric("Chunks", stats["chunks"])
# A 4th st.metric column here truncated the date with an ellipsis at this width
# (found live, T-042's own real verification) - a plain caption has room to render
# the full date instead.
st.caption(f"Caught up through **{latest.isoformat()}**" if latest else "No content ingested yet")


def _fill_question(text: str) -> None:
    st.session_state["question_input"] = text


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

question = st.text_input(
    "Question:", key="question_input",
    placeholder="What's happened with AI agents this week?",
)
ask = st.button("Ask", type="primary")

if ask and question.strip():
    today = latest_feed_date()
    # T-029: the manual-override-always-wins precedence lives in resolve_date_range()
    # itself (T-021's own contract) - called once here for the value actually used,
    # and separately (override=None) only so describe_retrieval_mode() can show what
    # the question alone would have resolved to, for the user's own inspection.
    interpreted_range = resolve_date_range(question, today, manual_override=None)
    date_range = resolve_date_range(question, today, manual_override=manual_range)
    ranking = detect_recency_ranking(question)

    # --- Pipeline strip (T-042): filled in progressively, real data per stage, as
    # each stage actually completes - not one spinner wrapping the whole call. ---
    stage_cols = st.columns(5)
    mode_slot = stage_cols[0].empty()
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

    mode_slot.metric("Mode", short_mode_label(interpreted_range, ranking, manual_range))
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
        st.stop()

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
    for i, c in enumerate(citations.citations, start=1):
        source_type = citation_source_type(c.url)
        title = escape_markdown_link_text(c.title)
        badges_html = (
            f'<div id="cite-{i}"></div>'
            f'<span class="source-badge badge-{source_type}">{_SOURCE_TYPE_LABEL[source_type]}</span>'
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
elif ask:
    st.warning("Write a question first.")
