"""T-017/T-019: paced YouTube backfill.

Window cut from the originally-planned 8 weeks to 4 (BACKFILL_WEEKS) and pacing
tightened to a randomized per-video pause plus a longer pause every 20th video
- my explicit direction for T-017's first pass, kept unchanged here.
Caution over completeness: still worth pacing requests even though a caption
block is no longer fatal to the run (T-019/D-009 - see below).

Order: any videos already recorded as `.pending.json` (from a run before
T-019's Whisper path existed) are retried first, then each chosen channel's
remaining videos inside the window - skipping anything already fetched, so an
interrupted run resumes without redoing settled work (same resumability shape
as T-015's HF backfill, via `document.exists()` instead of `hf_papers`'s day
markers).

No longer stops on a caption block (T-019/D-009 supersedes D-006's "abort the
run" consequence for this specific case): `vg09.youtube.normalize()` now
tries Whisper, then title+description, before giving up on a video, so every
video resolves to a final document and the run only stops on a genuinely
uncaught exception. Running totals (captions/whisper/fallback/already-done)
are still reported as the run progresses, not only at the end.
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import yt_dlp

from vg09 import document, sources
from vg09.document import RAW_DIR, Document
from vg09.watermark import write_watermark
from vg09.youtube import YT_DLP_SOCKET_TIMEOUT, list_video_ids, normalize

BACKFILL_WEEKS = 4  # halved from T-017's original 8-week plan to roughly halve
# the number of transcript-fetch requests against a path that was IpBlocked
# two days before this ran (KB-008) - caution over completeness for this pass
LIST_COUNT_PER_CHANNEL = 50  # yt-dlp's channel listing is not the blocked call
# (KB-008 - only the caption fetch itself was affected); generous here is cheap
# and just gets filtered down to the window afterwards
SHORT_PAUSE_SECONDS = (3.0, 8.0)  # randomized pause between every video
LONG_PAUSE_EVERY = 20  # every Nth video (by attempt count, across pending +
# channel videos combined), pause longer instead of the short pause
LONG_PAUSE_SECONDS = (60.0, 120.0)


@dataclass
class BackfillResult:
    fetched_captions: int = 0
    fetched_whisper: int = 0
    fetched_fallback: int = 0
    already_done: int = 0
    attempts: int = 0
    channels_reached: list[str] = field(default_factory=list)


def _feed_date_from_upload_date(upload_date: str) -> str:
    # yt-dlp gives upload_date as YYYYMMDD; kept local rather than importing
    # vg09.youtube's private helper of the same shape.
    return datetime.strptime(upload_date, "%Y%m%d").date().isoformat()


def _pending_videos() -> list[dict]:
    """Every `*.pending.json` marker currently under data/raw/youtube/, oldest
    feed_date first, so the two videos blocked on 2026-09-16 are retried in
    the order they were originally attempted."""
    paths = sorted(RAW_DIR.glob("youtube/**/*.pending.json"))
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def _fetch_single_video_metadata(video_id: str) -> dict:
    """Re-fetch one video's full yt-dlp info dict by id - used for retrying a
    pending video, whose marker only recorded id/title/feed_date/reason, not
    the description normalize() needs for a possible fallback."""
    opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": YT_DLP_SOCKET_TIMEOUT,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)


def _known_video_dates() -> dict[str, str]:
    """Every video already fetched, id -> feed date, read from where the files sit
    (`data/raw/youtube/<feed_date>/<id>.json`) without opening them."""
    return {
        path.stem: path.parent.name
        for path in RAW_DIR.glob("youtube/*/*.json")
        if not path.name.endswith(".pending.json")
    }


def _list_channel(channel_url: str, start: date) -> list[dict]:
    """The channel's latest videos, newest first, asking YouTube for a video's details
    only when it is not on disk yet (T-055). `list_videos()` asks for the details of all
    50, one request each, which made an update with nothing new take over five minutes
    for four channels. Here the ids come from one request for the whole channel; a known
    video is returned with the date it was stored under; and the walk stops at the first
    new video older than the window, since everything after it is older still."""
    known = _known_video_dates()
    videos: list[dict] = []
    for video_id in list_video_ids(channel_url, LIST_COUNT_PER_CHANNEL):
        if video_id in known:
            videos.append({"id": video_id, "upload_date": known[video_id].replace("-", ""),
                           "title": None})
            continue
        try:
            video = _fetch_single_video_metadata(video_id)
        except Exception as exc:  # noqa: BLE001 - one unavailable video isn't the channel
            print(f"  could not read {video_id}: {exc!r} - skipping this video")
            continue
        videos.append(video)
        upload_date = video.get("upload_date")
        if upload_date and _feed_date_from_upload_date(upload_date) < start.isoformat():
            break
    return videos


def _report(result: BackfillResult) -> None:
    print(
        f"  [progress] captions={result.fetched_captions} "
        f"whisper={result.fetched_whisper} fallback={result.fetched_fallback} "
        f"already_done={result.already_done} attempts={result.attempts} "
        f"pending_now={len(_pending_videos())}"
    )


def _pause(result: BackfillResult) -> None:
    if result.attempts > 0 and result.attempts % LONG_PAUSE_EVERY == 0:
        secs = random.uniform(*LONG_PAUSE_SECONDS)
        print(f"  ...longer pause after {result.attempts} videos: {secs:.1f}s")
    else:
        secs = random.uniform(*SHORT_PAUSE_SECONDS)
    time.sleep(secs)


def _process_video(
    video: dict,
    result: BackfillResult,
    channel: str | None = None,
    on_progress: Callable[[BackfillResult], None] | None = None,
) -> None:
    """Normalizes and writes one video's document. Always resolves to a final
    document (T-019/D-009: captions -> Whisper -> title+description) - there
    is no block-and-abort case left for the caller to react to. `channel` is the
    handle the video was listed under (T-054); a retried pending video has none."""
    doc: Document | None = normalize(video)

    if doc is not None:
        doc.channel = channel
        doc.write()
        document.clear_pending(doc.source, doc.feed_date, doc.id)
        if doc.text_source == "captions":
            result.fetched_captions += 1
        elif doc.text_source == "whisper":
            result.fetched_whisper += 1
        elif doc.text_source == "title_description":
            result.fetched_fallback += 1

    result.attempts += 1
    _report(result)
    if on_progress is not None:
        on_progress(result)
    _pause(result)


def run(
    weeks_back: int = BACKFILL_WEEKS,
    start: date | None = None,
    today: date | None = None,
    channels: dict[str, str] | None = None,
    on_progress: Callable[[BackfillResult], None] | None = None,
) -> BackfillResult:
    """`start`/`today` let a caller (T-013's `catch_up_youtube()`) reuse this
    same paced/three-tier-fallback logic for a narrow catch-up window instead
    of the full `weeks_back` backfill window - same idea as `vg09.sync.sync_hf`
    serving both T-015's backfill and T-013's HF catch-up from one
    implementation. `channels` restricts the run to those channels (T-055: a newly
    added channel gets a backfill window of its own while the others only catch up);
    `on_progress` is called after every video, for the background job's status file."""
    today = today or date.today()
    if start is None:
        start = today - timedelta(days=weeks_back * 7 - 1)
        print(f"YouTube backfill window: {start.isoformat()} .. {today.isoformat()} ({weeks_back} weeks)")
    else:
        print(f"YouTube catch-up window: {start.isoformat()} .. {today.isoformat()}")

    result = BackfillResult()

    pending = _pending_videos()
    print(f"\n{len(pending)} pending video(s) to retry first: {[p['id'] for p in pending]}")
    for p in pending:
        video_id = p["id"]
        print(f"\n[pending] {video_id} ({p['title']!r}, blocked reason was {p['reason']})")
        try:
            meta = _fetch_single_video_metadata(video_id)
        except Exception as exc:  # noqa: BLE001 - a metadata-refetch failure isn't a block
            print(f"  could not re-fetch metadata for {video_id}: {exc!r} - skipping this pending video")
            continue
        _process_video(meta, result, on_progress=on_progress)

    # T-053/D-017: the user's own list (data/sources.json), read when the run starts -
    # vg09/channels.py's four are only the default when nothing has been saved.
    if channels is None:
        channels = sources.load().channels
    for handle, url in channels.items():
        print(f"\n== {handle} ==")
        result.channels_reached.append(handle)
        if on_progress is not None:
            on_progress(result)  # listing a channel can take a minute: say which one
        try:
            videos = _list_channel(url, start)
        except Exception as exc:  # noqa: BLE001 - a listing failure isn't a transcript block
            print(f"  could not list videos for {handle}: {exc!r} - skipping channel")
            continue

        for video in videos:
            video_id = video.get("id")
            upload_date = video.get("upload_date")
            if not video_id or not upload_date:
                continue
            feed_date = _feed_date_from_upload_date(upload_date)
            if feed_date < start.isoformat() or feed_date > today.isoformat():
                continue
            if document.exists("youtube", feed_date, video_id):
                result.already_done += 1
                continue
            if document.pending_path("youtube", feed_date, video_id).exists():
                continue  # already retried in the pending pass above

            print(f"  {video_id} ({feed_date}) {video.get('title')!r}")
            _process_video(video, result, channel=handle, on_progress=on_progress)

    write_watermark("youtube", today.isoformat())
    print(f"\nDone - full window covered. YouTube watermark set to {today.isoformat()}.")
    if result.fetched_whisper:
        print(f"({result.fetched_whisper} video(s) needed the Whisper fallback - "
              f"captions were blocked for them, D-009)")
    _report(result)
    return result


if __name__ == "__main__":
    run()
