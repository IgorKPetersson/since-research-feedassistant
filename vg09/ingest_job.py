"""T-055 (D-017): the whole ingest - fetch Hugging Face, fetch YouTube, rebuild the
store - as one background job the app can start and watch.

A separate process, not a thread: Streamlit reruns its script on every interaction and
would lose a thread's handle, and the job has to keep going when the browser tab closes.
The job and the app share nothing but `data/ingest_status.json`, which the job rewrites
as it goes and the app reads.

Whether a job is still alive is judged from its heartbeat, not its process id: a
heartbeat thread rewrites the time every few seconds for as long as the process lives,
including through a long Whisper transcription or a paced pause. (`os.kill(pid, 0)` is
not a liveness check on Windows - there it terminates the process.)

Run directly with `python -m vg09.ingest_job`; the app does the same through `start()`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from vg09 import sources as sources_config
from vg09.document import RAW_DIR
from vg09.watermark import read_watermark

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATUS_PATH = PROJECT_ROOT / "data" / "ingest_status.json"
LOG_PATH = PROJECT_ROOT / "data" / "ingest_log.txt"
HEARTBEAT_SECONDS = 5
STALE_AFTER_SECONDS = 60  # twelve missed heartbeats: the process is gone
FILE_RETRIES = 40
FILE_RETRY_SECONDS = 0.05  # up to two seconds in all


class AlreadyRunning(Exception):
    pass


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _retrying(action):
    """Windows refuses to replace or open a file that another process has open at that
    instant (PermissionError), and the app reads the status file every two seconds while
    the job rewrites it. Found for real: the first real run died on exactly this, 980
    passages into rebuilding the store. The collision lasts milliseconds, so try again."""
    for attempt in range(FILE_RETRIES):
        try:
            return action()
        except PermissionError:
            if attempt == FILE_RETRIES - 1:
                raise
            time.sleep(FILE_RETRY_SECONDS)


def _write(status: dict) -> None:
    # Written to a temporary file and moved into place, so the app never reads half a file.
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(status, indent=2), encoding="utf-8")
    _retrying(lambda: os.replace(tmp, STATUS_PATH))


def status() -> dict:
    """`{"state": "idle"}` when no job has ever run; otherwise the job's last written
    status. A job that says it is running but whose heartbeat has gone quiet is reported
    as `interrupted`, never as running."""
    if not STATUS_PATH.exists():
        return {"state": "idle"}
    current = json.loads(_retrying(lambda: STATUS_PATH.read_text(encoding="utf-8")))
    if current["state"] == "running":
        age = (datetime.now() - datetime.fromisoformat(current["heartbeat"])).total_seconds()
        if age > STALE_AFTER_SECONDS:
            current["state"] = "interrupted"
    return current


def start() -> None:
    """Launch the job and return at once. Refused while one is running."""
    if status()["state"] == "running":
        raise AlreadyRunning("An update is already running.")
    # Marked as running here, before the process exists, so a second click in the
    # moment before the job writes its own first status is refused too.
    _write({"state": "running", "stage": "starting", "started": _now(), "heartbeat": _now(),
            "detail": "Starting", "errors": []})
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        subprocess.Popen(
            [sys.executable, "-m", "vg09.ingest_job"],
            cwd=str(PROJECT_ROOT), stdout=log, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, creationflags=flags,
        )


def should_start_on_open(config: sources_config.Sources, job: dict, today: date) -> bool:
    """D-018: whether opening the app should start an update. Judged by when the last
    update finished, not by the newest item's date: Hugging Face posts nothing at
    weekends, so a Monday would otherwise start an update on every opening.

    A first start (nothing saved yet) is left to the Sources page, where the user
    chooses the sources before anything is fetched. An update that finished today with
    errors is not retried here; Update now does that once the cause is fixed."""
    if not config.update_on_open or not config.saved:
        return False
    if job["state"] == "running":
        return False
    finished = job.get("finished")
    return not (finished and finished[:10] == today.isoformat())


def start_on_open(today: date | None = None) -> bool:
    """Start an update if `should_start_on_open()` says so. True when one was started."""
    if not should_start_on_open(sources_config.load(), status(), today or date.today()):
        return False
    try:
        start()
    except AlreadyRunning:  # another tab got there a moment earlier
        return False
    return True


def is_writing_store() -> bool:
    """True while a running job is in the stage that writes to the store. Chroma's
    embedded store can't be queried from the app while another process writes to it
    (found for real in T-056: "Error finding id"), so the app asks this before a
    question and says so instead of failing."""
    current = status()
    return current["state"] == "running" and current.get("stage") == "index"


_NOT_LOOKED = "not looked yet"
_last_seen_finish: str | None = _NOT_LOOKED


def refresh_store_if_updated() -> bool:
    """Called by the app on every rerun. When a job has finished since this process
    last looked, drop the app's cached Chroma client so it sees what the job wrote.
    The first look in a process only records the time: a fresh process has no stale
    client to drop. (A sentinel rather than None for "not looked yet": None is also
    the real value when no job has ever finished, and the first job ever to finish
    while the app is open must still trigger the refresh.)"""
    global _last_seen_finish
    finished = status().get("finished")
    if finished == _last_seen_finish:
        return False
    first_look = _last_seen_finish == _NOT_LOOKED
    _last_seen_finish = finished
    if first_look or finished is None:
        return False
    from vg09.store import reset_client

    reset_client()
    return True


def channels_with_documents() -> set[str]:
    """Handles that already have at least one fetched video on disk."""
    found: set[str] = set()
    for path in (RAW_DIR / "youtube").rglob("*.json"):
        if path.name.endswith(".pending.json"):
            continue
        handle = json.loads(path.read_text(encoding="utf-8")).get("channel")
        if handle:
            found.add(handle)
    return found


class _Job:
    def __init__(self, today: date) -> None:
        self.today = today
        self.state = {"state": "running", "stage": "starting", "detail": "Starting",
                      "started": _now(), "heartbeat": _now(), "pid": os.getpid(), "errors": []}
        self._lock = threading.Lock()
        self._stop = threading.Event()

    def update(self, **fields) -> None:
        with self._lock:
            self.state.update(fields)
            self.state["heartbeat"] = _now()
            _write(self.state)

    def _beat(self) -> None:
        while not self._stop.wait(HEARTBEAT_SECONDS):
            self.update()

    def _stage(self, name: str, detail: str, work) -> None:
        """One stage; a failure is recorded and the job goes on, so that whatever was
        fetched before it still reaches the store."""
        self.update(stage=name, detail=detail)
        try:
            work()
        except Exception as exc:  # noqa: BLE001 - recorded in the status, shown to the user
            print(f"stage {name} failed: {exc!r}")
            self.update(errors=self.state["errors"] + [f"{name}: {exc}"])

    def _hf(self, config) -> None:
        from vg09.sync import sync_hf

        watermark = read_watermark("hf")
        if watermark is None:
            start = self.today - timedelta(days=config.hf_weeks * 7 - 1)
        else:
            start = date.fromisoformat(watermark) + timedelta(days=1)
        result = sync_hf(start=start, today=self.today)
        self.update(hf_papers=result["total_papers"])

    def _youtube(self, config) -> None:
        from vg09.youtube_backfill import run as run_youtube

        def progress(result) -> None:
            fetched = result.fetched_captions + result.fetched_whisper + result.fetched_fallback
            channel = result.channels_reached[-1] if result.channels_reached else ""
            total = self.videos_before + fetched
            self.update(youtube_videos=total,
                        detail=f"YouTube: checking @{channel} "
                               f"({total} new video{'' if total == 1 else 's'} so far)")

        self.videos_before = 0
        backfill_start = self.today - timedelta(days=config.youtube_weeks * 7 - 1)
        watermark = read_watermark("youtube")
        known = channels_with_documents()
        new = {h: u for h, u in config.channels.items() if h not in known}
        old = {h: u for h, u in config.channels.items() if h in known}

        if watermark is None:
            # Nothing has ever completed: every channel gets the full window.
            new, old = dict(config.channels), {}
        if old:
            start = date.fromisoformat(watermark) + timedelta(days=1)
            result = run_youtube(start=start, today=self.today, channels=old, on_progress=progress)
            self.videos_before = (result.fetched_captions + result.fetched_whisper
                                  + result.fetched_fallback)
        if new:
            # A channel with nothing on disk yet gets the whole backfill window, not
            # only the days since the last run.
            run_youtube(start=backfill_start, today=self.today, channels=new, on_progress=progress)

    def _index(self) -> None:
        from vg09.store import build_store

        def progress(done: int, total: int) -> None:
            self.update(index_done=done, index_total=total,
                        detail=f"Making it searchable: {done} of {total} new passages")

        # Only what is new: the app can't answer questions while the store is being
        # written (see is_writing_store()), so this stage has to be short.
        build_store(on_progress=progress, only_new=True)

    def run(self) -> dict:
        config = sources_config.load()
        beat = threading.Thread(target=self._beat, daemon=True)
        beat.start()
        try:
            if config.hf_enabled:
                self._stage("hf", "Hugging Face Daily Papers", lambda: self._hf(config))
            if config.channels:
                self._stage("youtube", "YouTube", lambda: self._youtube(config))
            self._stage("index", "Making it searchable", self._index)
        finally:
            self._stop.set()
            beat.join()
        final = "done_with_errors" if self.state["errors"] else "done"
        self.update(state=final, stage="finished", finished=_now(),
                    detail="Finished" if final == "done" else "Finished, with errors")
        return self.state


def run_job(today: date | None = None) -> dict:
    return _Job(today or date.today()).run()


if __name__ == "__main__":
    run_job()
