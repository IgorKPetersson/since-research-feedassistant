"""YouTube collector -> normalized Document shape (T-009), with a caption-failure
split added in T-010/D-006.

Captions are the primary transcript source (D-001). A caption fetch can fail two
structurally different ways, and they get different treatment:

- **Missing** (`TranscriptsDisabled`, `NoTranscriptFound`, and anything else under
  `CouldNotRetrieveTranscript` that isn't `RequestBlocked`): a per-video signal
  that this specific video has no captions. Falls back to title+description and
  writes a final `Document` with `text_source="title_description"`.
- **Blocked** (`RequestBlocked`/`IpBlocked` - KB-008): an IP-level block, not a
  per-video signal. Writing a normal fallback document here would silently fill
  an entire run with weak documents while looking like ordinary missing-captions
  cases. Instead: no final document is written, the video is recorded as a
  `Pending` marker for a later retry, and the collector raises `IngestBlocked` so
  the caller stops rather than continuing to the next video.

Video metadata (title/description/upload_date) comes from the same yt-dlp call
T-002 verified (KB-001) - not re-derived here.
"""

from __future__ import annotations

from datetime import datetime

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript, RequestBlocked

from vg09.document import Document, Pending, clear_pending


class IngestBlocked(Exception):
    """Raised when YouTube blocks the caller (RequestBlocked/IpBlocked, KB-008).
    Not a per-video failure - the caller should stop the run and report, not
    continue to the next video."""

    def __init__(self, video_id: str, reason: str):
        self.video_id = video_id
        self.reason = reason
        super().__init__(f"{reason} while fetching captions for {video_id!r} - aborting")


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


def fetch_transcript(video_id: str) -> tuple[str, list[dict]]:
    """The caption transcript as one joined string, plus the real per-snippet
    segments (`{"text", "start", "duration"}`, T-010's verified
    FetchedTranscriptSnippet shape) - preserved so T-012 can chunk by
    timestamp instead of losing timing by only keeping the joined string.
    Raises `CouldNotRetrieveTranscript` (or a subclass - disabled, not found,
    unavailable, IP-blocked, ...) if captions can't be fetched; callers decide
    what to do about it."""
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)
    segments = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
    text = " ".join(s["text"] for s in segments)
    return text, segments


def normalize(video: dict) -> Document | None:
    """Returns a final `Document`, or `None` if the video's own metadata is
    incomplete. Raises `IngestBlocked` if YouTube is blocking the caller - the
    video is written as a `Pending` marker first, so the block is recorded even
    though no final document is."""
    video_id = video.get("id")
    upload_date = video.get("upload_date")
    if not video_id or not upload_date:
        return None
    title = video.get("title", "")
    url = f"https://www.youtube.com/watch?v={video_id}"
    feed_date = _feed_date(upload_date)

    try:
        text, segments = fetch_transcript(video_id)
    except RequestBlocked as exc:
        reason = type(exc).__name__
        Pending(
            id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
            reason=reason,
        ).write()
        raise IngestBlocked(video_id, reason) from exc
    except CouldNotRetrieveTranscript as exc:  # missing, not blocked - D-006
        reason = type(exc).__name__
        print(f"  captions unavailable for {video_id} ({reason}) - using title+description fallback")
        description = video.get("description", "")
        return Document(
            id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
            text=f"{title}\n\n{description}",
            text_source="title_description", fallback_reason=reason,
        )

    return Document(
        id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
        text=text, text_source="captions", fallback_reason=None, segments=segments,
    )


def collect_channel(channel_url: str, count: int) -> list[Document]:
    """List, normalize and persist a channel's latest `count` videos to
    data/raw/youtube/. Returns what was written so far; skips entries missing a
    video id or upload date; propagates `IngestBlocked` uncaught so the caller
    stops the run rather than silently continuing past a block."""
    docs = []
    for video in list_videos(channel_url, count):
        doc = normalize(video)
        if doc is not None:
            doc.write()
            # A final document resolves any earlier pending marker for this id
            # (e.g. a previous run was blocked on this video, this one wasn't).
            clear_pending(doc.source, doc.feed_date, doc.id)
            docs.append(doc)
        else:
            print(f"  skipping entry missing id or upload_date: {video.get('title')!r}")
    return docs
