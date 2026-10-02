"""T-056 (D-017): the Sources page - which sources are watched, and fetching them.

A rendering layer over `vg09.sources` (the saved choice), `vg09.store` (what is actually
stored per channel) and `vg09.ingest_job` (the background update). UI text in English
(D-016).
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from vg09 import ingest_job, sources
from vg09.store import channel_stats, corpus_stats, latest_feed_date, remove_channel_data
from vg09.ui_helpers import staleness_note

UPDATE_WARNING = (
    "An update takes roughly 10–20 minutes, longer the first time. Most of that is "
    "YouTube, which is fetched slowly on purpose and sometimes has to be transcribed "
    "on this machine. You can keep asking questions while it runs. New content becomes "
    "searchable when the update has finished."
)


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _flash(kind: str, message: str) -> None:
    """A message that survives the rerun an action triggers."""
    st.session_state["sources_flash"] = (kind, message)


def _show_flash() -> None:
    flash = st.session_state.pop("sources_flash", None)
    if flash:
        getattr(st, flash[0])(flash[1])


@st.dialog("Remove channel")
def _confirm_remove(handle: str, documents: int) -> None:
    if documents:
        st.write(f"@{handle} and its {_count(documents, 'stored video')} will be removed. "
                 "Answers will no longer use them. This cannot be undone, but adding the "
                 "channel again fetches its recent videos anew.")
    else:
        st.write(f"@{handle} will be removed from the list. Nothing has been fetched from it yet.")
    left, right = st.columns(2)
    if left.button("Remove", type="primary", use_container_width=True):
        config = sources.load()
        sources.remove_channel(config, handle)
        sources.save(config)
        removed = remove_channel_data(handle)
        _flash("success", f"Removed @{handle}: {_count(removed['documents'], 'video')} deleted.")
        st.rerun()
    if right.button("Cancel", use_container_width=True):
        st.rerun()


def _add_channel(text: str) -> None:
    config = sources.load()
    try:
        handle, url = sources.parse_channel(text)
        if handle.lower() in {h.lower() for h in config.channels}:
            raise ValueError(f"@{handle} is already in the list")
    except ValueError as exc:
        _flash("error", str(exc))
        return
    try:
        from vg09.youtube import list_video_ids

        found = list_video_ids(url, 1)
    except Exception:  # noqa: BLE001 - yt-dlp raises its own types for a missing channel
        found = []
    if not found:
        _flash("error", f"Couldn't find a YouTube channel at @{handle}. Check the spelling.")
        return
    config.channels[handle] = url
    sources.save(config)
    _flash("success", f"Added @{handle}. Its videos become searchable after the next update.")


@st.fragment(run_every=2)
def _job_status() -> None:
    """Re-read every two seconds on its own, without rerunning the whole page."""
    job = ingest_job.status()
    state = job["state"]
    was_running = st.session_state.get("sources_job_was_running", False)
    st.session_state["sources_job_was_running"] = state == "running"
    if was_running and state != "running":
        st.rerun()  # the whole page: counts and the Update button change when a job ends

    if state == "running":
        st.info(f"Updating — {job.get('detail', 'Starting')}")
        if job.get("index_total"):
            st.progress(job["index_done"] / job["index_total"])
        st.caption(f"Started {job['started'][11:16]}. You can leave this page; the update keeps going.")
    elif state == "interrupted":
        st.warning("The last update stopped before it finished. Start it again; it "
                   "continues from where it stopped.")
    elif state == "done":
        st.success(f"Last update finished {job['finished'][:10]} at {job['finished'][11:16]}: "
                   f"{_count(job.get('hf_papers', 0), 'paper')} checked, "
                   f"{_count(job.get('youtube_videos', 0), 'new video')}.")
    elif state == "done_with_errors":
        st.warning(f"Last update finished {job['finished'][:10]} at {job['finished'][11:16]} "
                   "with problems: " + "; ".join(job["errors"]))


def render() -> None:
    st.header("Sources")
    _show_flash()
    config = sources.load()
    running = ingest_job.status()["state"] == "running"

    # --- Hugging Face ---
    stats = corpus_stats()
    if not config.saved and stats["chunks"] == 0:
        # Only on a first start. Someone who already has data fetched from the default
        # channels has, in effect, chosen them - to them these are not suggestions.
        st.info("These are suggested starting sources. Remove what you don't want, add "
                "your own channels, then press Update now.")
    st.subheader("Hugging Face Daily Papers")
    hf_enabled = st.toggle("Fetch the daily paper selection", value=config.hf_enabled,
                           disabled=running)
    hf_weeks = st.number_input("Weeks of history to fetch the first time", min_value=1,
                               max_value=26, value=config.hf_weeks, disabled=running)
    st.caption(f"{stats['hf_documents']} papers stored.")

    # --- YouTube ---
    st.subheader("YouTube channels")
    per_channel = channel_stats()
    if not config.channels:
        st.caption("No channels yet.")
    for handle in config.channels:
        info = per_channel.get(handle)
        left, right = st.columns([5, 1])
        if info:
            left.markdown(f"**@{handle}**  \n{_count(info['documents'], 'video')} · "
                          f"latest {info['latest']}")
        else:
            left.markdown(f"**@{handle}**  \nNot fetched yet — searchable after the next update")
        if right.button("Remove", key=f"remove_{handle}", disabled=running):
            _confirm_remove(handle, info["documents"] if info else 0)

    with st.form("add_channel", clear_on_submit=True, border=False):
        new_channel = st.text_input("Add a channel", placeholder="https://www.youtube.com/@handle",
                                    disabled=running)
        add = st.form_submit_button("Add", disabled=running)
    youtube_weeks = st.number_input("Weeks of history to fetch for a new channel", min_value=1,
                                    max_value=12, value=config.youtube_weeks, disabled=running)
    st.caption("YouTube only lists a channel's most recent videos, so older history may "
               "not be available however many weeks are chosen.")

    settings_changed = (hf_enabled, hf_weeks, youtube_weeks) != (
        config.hf_enabled, config.hf_weeks, config.youtube_weeks)
    if settings_changed and not running:
        config.hf_enabled, config.hf_weeks, config.youtube_weeks = hf_enabled, hf_weeks, youtube_weeks
        sources.save(config)
    if add and new_channel.strip():
        with st.spinner("Checking the channel on YouTube…"):
            _add_channel(new_channel)
        st.rerun()

    # --- Update ---
    st.divider()
    latest = latest_feed_date()
    stale = staleness_note(latest, date.today())
    if latest is None:
        st.markdown("**Nothing has been fetched yet.**")
    elif stale:
        st.markdown(f"**The data is {stale}** (latest: {latest}).")
    else:
        st.markdown(f"The data is up to date through {latest}.")
    st.caption(UPDATE_WARNING)
    if st.button("Update now", type="primary", disabled=running):
        sources.save(config)  # from here on the list is the user's own, not a suggestion
        try:
            ingest_job.start()
        except ingest_job.AlreadyRunning:
            pass
        st.session_state["sources_job_was_running"] = True
        st.rerun()
    _job_status()
