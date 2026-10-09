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

from vg09 import channel_state, document, sources
from vg09.document import RAW_DIR, Document
from vg09.youtube import YT_DLP_SOCKET_TIMEOUT, list_video_ids, normalize

BACKFILL_WEEKS = 4  # halved from T-017's original 8-week plan to roughly halve
# the number of transcript-fetch requests against a path that was IpBlocked
# two days before this ran (KB-008) - caution over completeness for this pass
LIST_COUNT_PER_CHANNEL = 50  # yt-dlp's channel listing is not the blocked call
# (KB-008 - only the caption fetch itself was affected); generous here is cheap
# and just gets filtered down to the window afterwards
RECHECK_DAYS = 2  # T-090: see catch_up_start()
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
    channel_problems: dict[str, str] = field(default_factory=dict)  # T-091


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


def catch_up_start(watermark: str) -> date:
    """T-090: where a catch-up starts, given the date the last full run covered up to.

    The watermark is that run's own date, so the run saw only the videos uploaded
    before it started; one uploaded later that day was never listed. A catch-up
    therefore looks at the watermark day again, and the day before it as well, since
    yt-dlp dates a video in UTC while the watermark is the local date: just after local
    midnight in Sweden, UTC is still on the previous day. Hugging Face re-checks its
    last two days for a similar reason (T-015, `vg09.sync.REOPEN_DAYS`).

    Rechecking costs little: a video already on disk is listed with its stored date and
    is neither looked up nor fetched again (`_check_channel()`, `document.exists()`).
    A video that appears even later with an older date stays outside the window."""
    return date.fromisoformat(watermark) - timedelta(days=RECHECK_DAYS - 1)


def _known_video_dates() -> dict[str, str]:
    """Every video already fetched, id -> feed date, read from where the files sit
    (`data/raw/youtube/<feed_date>/<id>.json`) without opening them."""
    return {
        path.stem: path.parent.name
        for path in RAW_DIR.glob("youtube/*/*.json")
        if not path.name.endswith(".pending.json")
    }


# T-091: YouTube's own refusals, which retrying won't change. Any other error reading a
# listed video leaves the channel's check incomplete, to be retried.
_UNREADABLE = (("members-only", "members-only"), ("Join this channel", "members-only"),
               ("Private video", "private"))


def _unreadable_reason(exc: Exception) -> str | None:
    text = str(exc)
    return next((reason for marker, reason in _UNREADABLE if marker in text), None)


@dataclass
class ChannelCheck:
    """T-091: what one channel's listing showed for the window [start, today]."""
    listing: list[str]
    to_fetch: list[dict] = field(default_factory=list)  # in the window, not on disk
    already_done: int = 0
    dates: dict[str, str] = field(default_factory=dict)  # looked up, not on disk
    unreadable: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    late: list[list[str]] = field(default_factory=list)  # new since last check, dated before the window
    oldest_listed: str | None = None
    reaches_back: bool = False


def _check_channel(channel_url: str, record: dict, start: date, today: date,
                   known: dict[str, str]) -> ChannelCheck:
    """T-091: walk the channel's whole listing and decide what to fetch and whether
    the listing covers the window.

    No date order is assumed. Until T-091 the walk stopped at the first new video dated
    before the window, so a video listed above others with an older date (a scheduled
    upload, for instance) hid every in-window video below it (KB-040). Now every listed
    id is classified: on disk (its stored date, no request), looked up before (its
    cached date, no request), or new (one request for its details, once).

    The listing covers the window when it has fewer ids than asked for (the whole
    channel; `list_video_ids()` raises on a broken page instead of returning a short
    list), or it still contains an id from the last complete listing (YouTube lists in
    publication order, so everything published since is above it), or, on a first
    check, its oldest listed video is dated before the window. Otherwise older videos
    may have scrolled out of the newest `LIST_COUNT_PER_CHANNEL`."""
    ids = list_video_ids(channel_url, LIST_COUNT_PER_CHANNEL)
    check = ChannelCheck(listing=ids)
    window = (start.isoformat(), today.isoformat())
    previous = set(record["listing"])
    first_anchor = next((i for i, video_id in enumerate(ids) if video_id in previous), None)

    for position, video_id in enumerate(ids):
        if video_id in known:
            feed_date = known[video_id]
            if window[0] <= feed_date <= window[1]:
                check.already_done += 1
        elif (video_id in record["dates"]
              and not window[0] <= record["dates"][video_id] <= window[1]):
            feed_date = check.dates[video_id] = record["dates"][video_id]
        else:
            # New, or looked up before while outside the window and now inside it (a
            # video dated ahead of the local date, say): its details are needed to fetch.
            try:
                video = _fetch_single_video_metadata(video_id)
            except Exception as exc:  # noqa: BLE001 - sorted into unreadable or retry below
                reason = _unreadable_reason(exc)
                if reason:
                    check.unreadable[video_id] = reason
                else:
                    check.errors.append(f"{video_id}: {exc}")
                print(f"  could not read {video_id}: {reason or repr(exc)}")
                continue
            if not video.get("upload_date"):
                check.errors.append(f"{video_id}: no upload date")
                continue
            feed_date = _feed_date_from_upload_date(video["upload_date"])
            if window[0] <= feed_date <= window[1]:
                if not document.pending_path("youtube", feed_date, video_id).exists():
                    check.to_fetch.append(video)
            else:
                check.dates[video_id] = feed_date
                newly_published = previous and (first_anchor is None or position < first_anchor)
                if feed_date < window[0] and newly_published:
                    check.late.append([video_id, feed_date])  # T-103
        check.oldest_listed = feed_date

    check.reaches_back = (
        len(ids) < LIST_COUNT_PER_CHANNEL
        or first_anchor is not None
        or (not previous and check.oldest_listed is not None and check.oldest_listed < window[0])
    )
    return check


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
    """Fetch every channel's videos that its own record says are still unchecked.

    T-091 (D-021): each channel has its own window from `vg09.channel_state`. `start`
    (default: `weeks_back` weeks before `today`) only applies to a channel that has no
    record yet, as the start of its first, unverified check. A channel whose listing
    fails or is incomplete keeps its window for the next run; the others move on.
    `on_progress` is called after every video, for the background job's status file."""
    today = today or date.today()
    if start is None:
        start = today - timedelta(days=weeks_back * 7 - 1)
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
    state = channel_state.load()
    added = channel_state.ensure_channels(state, channels, start)
    channel_state.save(state)  # before any fetch, so new records survive a crash
    if added:
        print(f"New, unverified channel records from {start.isoformat()}: {added}")

    for handle, url in channels.items():
        record = state["channels"][handle]
        window_start = channel_state.window_start(record)
        print(f"\n== {handle} == window {window_start.isoformat()} .. {today.isoformat()}")
        result.channels_reached.append(handle)
        if on_progress is not None:
            on_progress(result)  # listing a channel can take a minute: say which one
        try:
            check = _check_channel(url, record, window_start, today, _known_video_dates())
        except Exception as exc:  # noqa: BLE001 - this channel waits, the others go on
            print(f"  could not list videos for {handle}: {exc!r} - kept for the next run")
            channel_state.record_failure(record, window_start, channel_state.RESULT_FAILED,
                                         f"listing failed: {exc}")
            channel_state.save(state)
            result.channel_problems[handle] = record["last_error"]
            continue

        result.already_done += check.already_done
        for video in check.to_fetch:
            print(f"  {video['id']} ({_feed_date_from_upload_date(video['upload_date'])}) "
                  f"{video.get('title')!r}")
            _process_video(video, result, channel=handle, on_progress=on_progress)

        on_disk = _known_video_dates()
        listed_dates = [on_disk[v] for v in check.listing if v in on_disk]
        record["newest_content"] = max(listed_dates) if listed_dates else None
        record["dates"] = check.dates
        record["unreadable"] = check.unreadable
        record["late"] = check.late
        if check.late:
            print(f"  appeared after the window had passed, not fetched (T-103): {check.late}")
        if check.errors:
            channel_state.record_failure(
                record, window_start, channel_state.RESULT_INCOMPLETE,
                f"{len(check.errors)} listed video(s) could not be read, first: {check.errors[0]}")
            result.channel_problems[handle] = record["last_error"]
        elif not check.reaches_back:
            gap = {"from": window_start.isoformat(),
                   "through": check.oldest_listed or today.isoformat(),
                   "reason": f"older than the newest {LIST_COUNT_PER_CHANNEL} videos YouTube lists"}
            channel_state.record_success(record, today, channel_state.RESULT_COMPLETE_WITH_GAP,
                                         check.listing, gap=gap)
            result.channel_problems[handle] = f"not verified {gap['from']} to {gap['through']}"
        else:
            channel_state.record_success(record, today, channel_state.RESULT_COMPLETE, check.listing)
        channel_state.save(state)
        print(f"  {record['last_result']}; checked through {record['checked_through']}, "
              f"retry from {record['pending_from']}")

    if result.fetched_whisper:
        print(f"({result.fetched_whisper} video(s) needed the Whisper fallback - "
              f"captions were blocked for them, D-009)")
    _report(result)
    return result


if __name__ == "__main__":
    run()
