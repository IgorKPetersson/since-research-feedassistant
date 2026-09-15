"""T-002: YouTube captions feasibility test.

For each chosen channel, fetch metadata for the latest N videos via yt-dlp,
then attempt to fetch a transcript for each via youtube-transcript-api.
Records success/failure, error type, and per-channel latest upload date.

Raw results go to data/t002_youtube_captions.json (gitignored). This script
makes real network calls to YouTube; run it manually, it is not a test.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

CHANNELS = {
    "theAIsearch": "https://www.youtube.com/@theAIsearch/videos",
    "mreflow": "https://www.youtube.com/@mreflow/videos",
    "NateBJones": "https://www.youtube.com/@NateBJones/videos",
    "ColeMedin": "https://www.youtube.com/@ColeMedin/videos",
}

VIDEOS_PER_CHANNEL = 5
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def latest_videos(channel_url: str, count: int) -> list[dict]:
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
    usable = [e for e in entries if e][:count]
    skipped = len(entries) - len(usable)
    if skipped:
        print(f"  ({skipped} entries had no metadata and were skipped)")
    return usable


def try_transcript(video_id: str) -> dict:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id)
        return {
            "success": True,
            "error_type": None,
            "language": fetched.language_code,
            "is_generated": fetched.is_generated,
            "snippet_count": len(fetched),
        }
    except TranscriptsDisabled:
        return {"success": False, "error_type": "transcripts_disabled"}
    except NoTranscriptFound:
        return {"success": False, "error_type": "no_transcript_found"}
    except VideoUnavailable:
        return {"success": False, "error_type": "video_unavailable"}
    except Exception as exc:  # record, don't hide, unexpected error shapes
        return {"success": False, "error_type": f"other:{type(exc).__name__}"}


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    results: dict = {"run_at": datetime.now(timezone.utc).isoformat(), "channels": {}}

    for handle, url in CHANNELS.items():
        print(f"== {handle} ==")
        channel_result = {"videos": [], "latest_upload_date": None}
        try:
            videos = latest_videos(url, VIDEOS_PER_CHANNEL)
        except Exception as exc:
            channel_result["list_error"] = f"{type(exc).__name__}: {exc}"
            results["channels"][handle] = channel_result
            print(f"  FAILED to list videos: {exc}")
            continue

        upload_dates = []
        for v in videos:
            video_id = v.get("id")
            title = v.get("title")
            upload_date = v.get("upload_date")  # YYYYMMDD or None
            if upload_date:
                upload_dates.append(upload_date)
            transcript_result = try_transcript(video_id)
            channel_result["videos"].append(
                {
                    "video_id": video_id,
                    "title": title,
                    "upload_date": upload_date,
                    **transcript_result,
                }
            )
            status = "OK" if transcript_result["success"] else transcript_result["error_type"]
            print(f"  {video_id}  {upload_date}  {status}  {title!r}")

        channel_result["latest_upload_date"] = max(upload_dates) if upload_dates else None
        results["channels"][handle] = channel_result

    out_path = DATA_DIR / "t002_youtube_captions.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
