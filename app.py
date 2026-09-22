"""T-025: the chat UI. One question, one answer, its sources - no conversation
history (`docs/GOAL.md`'s explicit non-goal), no accounts.

A thin rendering layer: every real decision (date-range extraction, retrieval,
answer generation, citation resolution) already lives in `vg09/` and is unit- and
real-data-tested there (T-021-T-024). Run with `streamlit run app.py`.
"""

from __future__ import annotations

from datetime import date, timedelta

import requests
import streamlit as st

from vg09.answer import generate_answer
from vg09.citations import build_citations
from vg09.date_range import detect_recency_ranking, resolve_date_range
from vg09.retrieval import retrieve
from vg09.store import is_empty, latest_feed_date
from vg09.ui_helpers import describe_retrieval_mode, escape_markdown_link_text

st.set_page_config(page_title="VG-09", page_icon=":material/search:")
st.title("VG-09 — forskningsflödesassistent")

if is_empty():
    st.info("Ingen data ännu, kör ingest.")
    st.stop()

with st.sidebar:
    st.header("Datumfilter")
    st.caption(
        "Frågan tolkas automatiskt (t.ex. \"senaste veckan\"). Ange ett eget "
        "intervall nedan för att alltid override:a tolkningen."
    )
    use_manual_range = st.checkbox("Ange eget datumintervall")
    manual_range: tuple[date, date] | None = None
    if use_manual_range:
        today = latest_feed_date() or date.today()
        start = st.date_input("Från", value=today - timedelta(days=7))
        end = st.date_input("Till", value=today)
        if start and end:
            manual_range = (start, end)

question = st.text_input("Fråga:", placeholder="Vad har hänt med AI-agenter den senaste veckan?")
ask = st.button("Fråga", type="primary")

if ask and question.strip():
    today = latest_feed_date()
    # T-029: the manual-override-always-wins precedence lives in resolve_date_range()
    # itself (T-021's own contract) - called once here for the value actually used,
    # and separately (override=None) only so describe_retrieval_mode() can show what
    # the question alone would have resolved to, for the user's own inspection.
    interpreted_range = resolve_date_range(question, today, manual_override=None)
    date_range = resolve_date_range(question, today, manual_override=manual_range)
    ranking = detect_recency_ranking(question)

    st.caption(describe_retrieval_mode(interpreted_range, ranking, manual_range))

    try:
        with st.spinner("Söker och genererar svar..."):
            retrieval = retrieve(question, date_range=date_range, ranking=ranking)
            result = generate_answer(question, retrieval.chunks)
            citations = build_citations(result.answer, result.source_map)
    except requests.exceptions.RequestException:
        st.error("Ollama svarar inte – är den igång och är modellen nedladdad?")
        st.stop()

    # T-039: shown whenever a second attempt was made, whether or not it succeeded -
    # the user should know the answer took a second try, and (below) whether even that
    # one was cut off.
    if result.retries:
        st.info("Första försöket avbröts av längdgränsen, så frågan kördes om en gång.")

    if result.incomplete:
        st.warning("Svaret är ofullständigt — avbröts av längdgränsen innan det var klart.")

    st.markdown(result.answer)

    with st.expander("Visa modellens resonemang"):
        st.text(result.reasoning)

    st.subheader("Källor")
    if not citations.citations:
        st.caption("Inga källor kunde kopplas till svaret.")
    for c in citations.citations:
        note = " _(endast titel/beskrivning — ingen transkription/abstract)_" if c.is_fallback else ""
        arxiv_note = f", arXiv {c.arxiv_published_at[:10]}" if c.arxiv_published_at else ""
        title = escape_markdown_link_text(c.title)
        st.markdown(f"- [{title}]({c.url}) — {c.feed_date}{arxiv_note}{note}")

    if citations.unlinked_references:
        st.caption(
            "Hänvisningar i svaret som inte gick att koppla till en källa: "
            + ", ".join(citations.unlinked_references)
        )
    if citations.descriptive_ranges:
        st.caption(
            "Beskrivande intervall (t.ex. \"alla N källor\") - inte källhänvisningar: "
            + ", ".join(citations.descriptive_ranges)
        )
elif ask:
    st.warning("Skriv en fråga först.")
