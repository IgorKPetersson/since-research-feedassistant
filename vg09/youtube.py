"""YouTube collector -> normalized Document shape (T-009).

Captions are the primary transcript source; falls back to title + description
when captions are unavailable (D-001). Both title/description and the caption
availability check come from the same yt-dlp + youtube-transcript-api calls T-002
verified (KB-001) - not re-derived here.
"""

from __future__ import annotations

from datetime import datetime

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

from vg09.document import Document


def list_videos(channel_url: str, count: int) -> list[dict]:
    opts = {
        "skip_download": True,
        "extract_flat": False,
        "playlistend": count,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
    entries = info.get("entries") or []
    return [e for e in entries if e][:count]


def _feed_date(upload_date: str) -> str:
    # yt-dlp gives upload_date as YYYYMMDD
    return datetime.strptime(upload_date, "%Y%m%d").date().isoformat()


def fetch_transcript_text(video_id: str) -> str:
    """The caption transcript as one string. Raises `CouldNotRetrieveTranscript`
    (or a subclass - disabled, not found, unavailable, IP-blocked, ...) if
    captions can't be fetched; callers decide what to do about it."""
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)
    return " ".join(snippet.text for snippet in fetched)


def normalize(video: dict) -> Document | None:
    video_id = video.get("id")
    upload_date = video.get("upload_date")
    if not video_id or not upload_date:
        return None
    title = video.get("title", "")
    try:
        text = fetch_transcript_text(video_id)
    except CouldNotRetrieveTranscript as exc:  # D-001 fallback
        print(f"  captions unavailable for {video_id} ({type(exc).__name__}) - using title+description fallback")
        description = video.get("description", "")
        text = f"{title}\n\n{description}"
    return Document(
        id=video_id,
        source="youtube",
        url=f"https://www.youtube.com/watch?v={video_id}",
        title=title,
        feed_date=_feed_date(upload_date),
        text=text,
    )


def collect_channel(channel_url: str, count: int) -> list[Document]:
    """List, normalize and persist a channel's latest `count` videos to
    data/raw/youtube/. Returns what was written; skips entries missing a video id
    or upload date rather than writing an incomplete document, and reports the
    skip rather than swallowing it."""
    docs = []
    for video in list_videos(channel_url, count):
        doc = normalize(video)
        if doc is not None:
            doc.write()
            docs.append(doc)
        else:
            print(f"  skipping entry missing id or upload_date: {video.get('title')!r}")
    return docs
