"""YouTube collector -> normalized Document shape (T-009), with a caption-failure
split added in T-010/D-006, and Whisper as a second transcript path (T-019/D-009).

Captions are the primary transcript source (D-001). A caption fetch can fail two
structurally different ways, and they get different treatment:

- **Missing** (`TranscriptsDisabled`, `NoTranscriptFound`, and anything else under
  `CouldNotRetrieveTranscript` that isn't `RequestBlocked`): a per-video signal
  that this specific video has no captions. Falls back to title+description and
  writes a final `Document` with `text_source="title_description"`.
- **Blocked** (`RequestBlocked`/`IpBlocked` - KB-008): an IP-level block on the
  transcript-fetch call specifically, not on `yt-dlp` (KB-008, T-018). Rather
  than aborting the run (D-006's original behavior), `yt-dlp` audio download +
  local `faster-whisper` transcription is tried as a second path (D-009, real
  feasibility confirmed by T-018/KB-012/KB-013/KB-015). Only if *that* also
  fails does the video fall back to title+description -
  `text_source="title_description"` is now the **third** resort, not the
  second. No video causes the whole run to stop any more; every video
  resolves to some final `Document`.

Video metadata (title/description/upload_date) comes from the same yt-dlp call
T-002 verified (KB-001) - not re-derived here.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript, RequestBlocked

from vg09.document import Document, clear_pending

WHISPER_AUDIO_DIR = Path(__file__).resolve().parent.parent / "data" / "whisper_audio"
WHISPER_MODEL_SIZE = "small"  # T-018/KB-013's feasibility measurement used this size

_whisper_model = None  # lazy singleton - loaded once, reused across videos in a
# run (KB-015: fits alongside qwen3:30b-a3b + bge-m3 with real headroom to
# spare, no need to load/unload per video on this machine)


def _add_whisper_cuda_dll_dirs() -> None:
    """ctranslate2 (faster-whisper's backend) needs cuBLAS/cuDNN on PATH -
    `os.add_dll_directory()` does not work for it on Windows (KB-012)."""
    site_packages = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
    dirs = [str(site_packages / "nvidia" / pkg / "bin") for pkg in ("cublas", "cudnn", "cuda_nvrtc")]
    dirs = [d for d in dirs if os.path.isdir(d)]
    if dirs:
        os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ.get("PATH", "")


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _add_whisper_cuda_dll_dirs()
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cuda", compute_type="float16")
    return _whisper_model


YT_DLP_SOCKET_TIMEOUT = 30  # seconds - matches the requests.get/post timeout pattern
# used elsewhere in the codebase (hf_papers.py, store.py); yt-dlp has no default, so a
# stalled connection would otherwise hang indefinitely (found in Phase 1's grill-me
# review, T-020).


def list_videos(channel_url: str, count: int) -> list[dict]:
    opts = {
        "skip_download": True,
        "extract_flat": False,
        "playlistend": count,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": YT_DLP_SOCKET_TIMEOUT,
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


def fetch_whisper_transcript(video_id: str) -> tuple[str, list[dict]]:
    """Second transcript path (D-009/T-019), tried when captions are blocked.
    Downloads audio via `yt-dlp` (no caption/transcript API call at all) and
    transcribes it locally with `faster-whisper`. The audio file is always
    deleted afterwards, success or failure (disk space and copyright - T-019's
    explicit instruction, not just tidiness). Segments come back already
    converted from `faster-whisper`'s real `{text, start, end}` shape (T-018)
    to the `{text, start, duration}` shape `vg09/document.py` expects.
    Raises on any download or transcription failure; the caller decides what
    to do about it (T-019: fall back to title+description)."""
    WHISPER_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    outtmpl = str(WHISPER_AUDIO_DIR / f"{video_id}.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": YT_DLP_SOCKET_TIMEOUT,
    }
    audio_path: Path | None = None
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            audio_path = Path(ydl.prepare_filename(info))

        model = _get_whisper_model()
        raw_segments, _ = model.transcribe(str(audio_path), beam_size=5)
        segments = [
            {"text": s.text.strip(), "start": s.start, "duration": s.end - s.start}
            for s in raw_segments
        ]
        text = " ".join(s["text"] for s in segments)
        return text, segments
    finally:
        if audio_path is not None and audio_path.exists():
            audio_path.unlink()


def normalize(video: dict) -> Document | None:
    """Returns a final `Document`, or `None` if the video's own metadata is
    incomplete. Three-tier fallback (T-019/D-009): captions, then Whisper if
    captions are blocked, then title+description if both fail. No video
    causes the caller to stop early any more - every video resolves to a
    final `Document`."""
    video_id = video.get("id")
    upload_date = video.get("upload_date")
    if not video_id or not upload_date:
        return None
    title = video.get("title", "")
    url = f"https://www.youtube.com/watch?v={video_id}"
    feed_date = _feed_date(upload_date)
    description = video.get("description", "")

    try:
        text, segments = fetch_transcript(video_id)
        return Document(
            id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
            text=text, text_source="captions", fallback_reason=None, segments=segments,
        )
    except RequestBlocked as exc:
        captions_reason = type(exc).__name__
        print(f"  captions blocked for {video_id} ({captions_reason}) - trying yt-dlp audio + "
              f"Whisper (D-009)")
        try:
            text, segments = fetch_whisper_transcript(video_id)
            print(f"  Whisper transcription succeeded for {video_id}")
            return Document(
                id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
                text=text, text_source="whisper", fallback_reason=captions_reason,
                segments=segments,
            )
        except Exception as whisper_exc:  # noqa: BLE001 - any Whisper failure falls through
            print(f"  Whisper also failed for {video_id} ({type(whisper_exc).__name__}) - "
                  f"falling back to title+description")
            return Document(
                id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
                text=f"{title}\n\n{description}", text_source="title_description",
                fallback_reason=f"{captions_reason};whisper:{type(whisper_exc).__name__}",
            )
    except CouldNotRetrieveTranscript as exc:  # missing, not blocked - D-006
        reason = type(exc).__name__
        print(f"  captions unavailable for {video_id} ({reason}) - using title+description fallback")
        return Document(
            id=video_id, source="youtube", url=url, title=title, feed_date=feed_date,
            text=f"{title}\n\n{description}",
            text_source="title_description", fallback_reason=reason,
        )


def collect_channel(channel_url: str, count: int) -> list[Document]:
    """List, normalize and persist a channel's latest `count` videos to
    data/raw/youtube/. Returns what was written so far; skips entries missing
    a video id or upload date. Every video resolves to a final `Document`
    (captions -> Whisper -> title+description, T-019/D-009) - nothing here
    stops the loop early any more."""
    docs = []
    for video in list_videos(channel_url, count):
        doc = normalize(video)
        if doc is not None:
            doc.write()
            # A final document resolves any earlier pending marker for this id
            # (e.g. an older run left one before T-019's Whisper path existed).
            clear_pending(doc.source, doc.feed_date, doc.id)
            docs.append(doc)
        else:
            print(f"  skipping entry missing id or upload_date: {video.get('title')!r}")
    return docs
