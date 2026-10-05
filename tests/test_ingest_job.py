"""Unit tests for vg09.ingest_job (T-055). Nothing real is started or fetched: the
process launch, both fetchers and the store rebuild are mocked, and every path the
module writes to is redirected to a temporary directory.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from vg09 import ingest_job
from vg09.sources import Sources, save
from vg09.watermark import write_watermark
from vg09.youtube_backfill import BackfillResult


class IngestJobTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        for target, value in (
            ("vg09.ingest_job.STATUS_PATH", self.tmp / "ingest_status.json"),
            ("vg09.ingest_job.LOG_PATH", self.tmp / "ingest_log.txt"),
            ("vg09.ingest_job.RAW_DIR", self.tmp / "raw"),
            ("vg09.sources.SOURCES_PATH", self.tmp / "sources.json"),
            ("vg09.watermark.WATERMARK_DIR", self.tmp),
        ):
            patcher = patch(target, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_status(self, **fields) -> None:
        (self.tmp / "ingest_status.json").write_text(json.dumps(fields), encoding="utf-8")

    def add_video(self, video_id: str, channel: str) -> None:
        day = self.tmp / "raw" / "youtube" / "2026-09-20"
        day.mkdir(parents=True, exist_ok=True)
        (day / f"{video_id}.json").write_text(json.dumps({"id": video_id, "channel": channel}),
                                              encoding="utf-8")


class StartOnOpenTests(IngestJobTestCase):
    """D-018: opening the app starts an update only when nothing was fetched today."""

    TODAY = date(2026, 10, 5)

    def decide(self, job: dict, **config) -> bool:
        return ingest_job.should_start_on_open(Sources(saved=True, **config), job, self.TODAY)

    def test_never_updated_starts(self):
        self.assertTrue(self.decide({"state": "idle"}))

    def test_finished_on_an_earlier_day_starts(self):
        self.assertTrue(self.decide({"state": "done", "finished": "2026-10-04T23:59:00"}))

    def test_interrupted_starts_again(self):
        self.assertTrue(self.decide({"state": "interrupted", "started": "2026-10-05T08:00:00"}))

    def test_finished_today_does_not_start(self):
        self.assertFalse(self.decide({"state": "done", "finished": "2026-10-05T00:01:00"}))

    def test_finished_today_with_errors_is_not_retried(self):
        self.assertFalse(self.decide({"state": "done_with_errors",
                                      "finished": "2026-10-05T09:00:00", "errors": ["x"]}))

    def test_running_does_not_start(self):
        self.assertFalse(self.decide({"state": "running"}))

    def test_setting_off_does_not_start(self):
        self.assertFalse(self.decide({"state": "idle"}, update_on_open=False))

    def test_first_start_with_nothing_saved_is_left_to_the_sources_page(self):
        self.assertFalse(ingest_job.should_start_on_open(Sources(), {"state": "idle"}, self.TODAY))

    def test_start_on_open_launches_one_job_and_a_second_tab_launches_none(self):
        save(Sources())
        with patch("vg09.ingest_job.subprocess.Popen") as mock_popen:
            self.assertTrue(ingest_job.start_on_open(self.TODAY))
            self.assertFalse(ingest_job.start_on_open(self.TODAY))
        self.assertEqual(mock_popen.call_count, 1)


class StatusTests(IngestJobTestCase):
    def test_no_status_file_is_idle(self):
        self.assertEqual(ingest_job.status(), {"state": "idle"})

    def test_running_with_a_fresh_heartbeat_is_running(self):
        self.write_status(state="running", heartbeat=datetime.now().isoformat())
        self.assertEqual(ingest_job.status()["state"], "running")

    def test_running_with_a_stale_heartbeat_is_reported_as_interrupted(self):
        old = datetime.now() - timedelta(seconds=ingest_job.STALE_AFTER_SECONDS + 5)
        self.write_status(state="running", heartbeat=old.isoformat())
        self.assertEqual(ingest_job.status()["state"], "interrupted")

    def test_a_finished_job_stays_finished_however_old_it_is(self):
        old = datetime.now() - timedelta(days=3)
        self.write_status(state="done", heartbeat=old.isoformat())
        self.assertEqual(ingest_job.status()["state"], "done")


class FileCollisionTests(IngestJobTestCase):
    """Found by the first real run: Windows raises PermissionError when the status file
    is replaced while the app has it open. The job must ride it out, not die."""

    def test_a_write_that_collides_with_a_reader_is_retried_until_it_goes_through(self):
        real_replace = ingest_job.os.replace
        attempts = []

        def flaky(src, dst):
            attempts.append(1)
            if len(attempts) < 3:
                raise PermissionError(13, "Access is denied")
            real_replace(src, dst)

        with patch("vg09.ingest_job.os.replace", side_effect=flaky), \
             patch("vg09.ingest_job.time.sleep"):
            ingest_job._write({"state": "done", "heartbeat": datetime.now().isoformat()})

        self.assertEqual(len(attempts), 3)
        self.assertEqual(ingest_job.status()["state"], "done")

    def test_a_collision_that_never_clears_is_raised_not_swallowed(self):
        with patch("vg09.ingest_job.os.replace", side_effect=PermissionError(13, "denied")), \
             patch("vg09.ingest_job.time.sleep"):
            with self.assertRaises(PermissionError):
                ingest_job._write({"state": "done"})


class StartTests(IngestJobTestCase):
    def test_start_is_refused_while_a_job_is_running_and_launches_nothing(self):
        self.write_status(state="running", heartbeat=datetime.now().isoformat())
        with patch("vg09.ingest_job.subprocess.Popen") as mock_popen:
            with self.assertRaises(ingest_job.AlreadyRunning):
                ingest_job.start()
        mock_popen.assert_not_called()

    def test_start_launches_the_module_and_marks_the_job_running_at_once(self):
        with patch("vg09.ingest_job.subprocess.Popen") as mock_popen:
            ingest_job.start()
        command = mock_popen.call_args.args[0]
        self.assertEqual(command[1:], ["-m", "vg09.ingest_job"])
        # running before the process has written anything itself - a second start is refused
        self.assertEqual(ingest_job.status()["state"], "running")
        with patch("vg09.ingest_job.subprocess.Popen") as second:
            with self.assertRaises(ingest_job.AlreadyRunning):
                ingest_job.start()
        second.assert_not_called()

    def test_start_is_allowed_again_after_an_interrupted_job(self):
        old = datetime.now() - timedelta(seconds=ingest_job.STALE_AFTER_SECONDS + 5)
        self.write_status(state="running", heartbeat=old.isoformat())
        with patch("vg09.ingest_job.subprocess.Popen") as mock_popen:
            ingest_job.start()
        mock_popen.assert_called_once()


class RunJobTests(IngestJobTestCase):
    TODAY = date(2026, 10, 2)

    def run_job(self, hf=None, youtube=None, index=None):
        self.calls: list[str] = []
        hf_result = {"total_papers": 7}

        def fake_hf(**kwargs):
            self.calls.append("hf")
            self.hf_kwargs = kwargs
            return hf_result

        def fake_youtube(**kwargs):
            self.calls.append("youtube")
            self.youtube_calls.append(kwargs)
            return BackfillResult(fetched_captions=2)

        def fake_index(**kwargs):
            self.calls.append("index")
            return {}

        self.youtube_calls: list[dict] = []
        with patch("vg09.sync.sync_hf", side_effect=hf or fake_hf), \
             patch("vg09.youtube_backfill.run", side_effect=youtube or fake_youtube), \
             patch("vg09.store.build_store", side_effect=index or fake_index):
            return ingest_job.run_job(today=self.TODAY)

    def test_stages_run_in_order_and_the_job_ends_done(self):
        write_watermark("hf", "2026-09-30")
        write_watermark("youtube", "2026-09-30")
        save(Sources(channels={"alpha": "https://www.youtube.com/@alpha/videos"}))
        self.add_video("v1", "alpha")

        final = self.run_job()

        self.assertEqual(self.calls, ["hf", "youtube", "index"])
        self.assertEqual(final["state"], "done")
        self.assertEqual(final["errors"], [])
        self.assertEqual(ingest_job.status()["state"], "done")
        self.assertEqual(self.hf_kwargs["start"], date(2026, 10, 1))  # the day after the watermark

    def test_hugging_face_switched_off_is_not_fetched(self):
        save(Sources(hf_enabled=False, channels={}))
        self.run_job()
        self.assertEqual(self.calls, ["index"])

    def test_no_watermarks_means_a_backfill_of_the_configured_weeks(self):
        save(Sources(hf_weeks=2, youtube_weeks=1,
                     channels={"alpha": "https://www.youtube.com/@alpha/videos"}))
        self.run_job()
        self.assertEqual(self.hf_kwargs["start"], date(2026, 9, 19))  # 14 days, both ends counted
        self.assertEqual(len(self.youtube_calls), 1)
        self.assertEqual(self.youtube_calls[0]["start"], date(2026, 9, 26))  # 7 days
        self.assertEqual(list(self.youtube_calls[0]["channels"]), ["alpha"])

    def test_a_newly_added_channel_gets_the_backfill_window_the_others_only_catch_up(self):
        write_watermark("youtube", "2026-09-30")
        save(Sources(hf_enabled=False, youtube_weeks=4, channels={
            "alpha": "https://www.youtube.com/@alpha/videos",
            "newone": "https://www.youtube.com/@newone/videos",
        }))
        self.add_video("v1", "alpha")  # alpha has data on disk, newone has none

        self.run_job()

        catch_up, backfill = self.youtube_calls
        self.assertEqual((list(catch_up["channels"]), catch_up["start"]), (["alpha"], date(2026, 10, 1)))
        self.assertEqual((list(backfill["channels"]), backfill["start"]), (["newone"], date(2026, 9, 5)))

    def test_a_failing_stage_is_recorded_and_the_store_is_still_rebuilt(self):
        save(Sources(channels={"alpha": "https://www.youtube.com/@alpha/videos"}))

        def broken(**kwargs):
            self.calls.append("youtube")
            raise RuntimeError("YouTube unreachable")

        final = self.run_job(youtube=broken)

        self.assertEqual(self.calls, ["hf", "youtube", "index"])
        self.assertEqual(final["state"], "done_with_errors")
        self.assertEqual(final["errors"], ["youtube: YouTube unreachable"])

    def test_progress_from_the_fetchers_reaches_the_status_file(self):
        save(Sources(hf_enabled=False, channels={"alpha": "https://www.youtube.com/@alpha/videos"}))

        def youtube(**kwargs):
            kwargs["on_progress"](BackfillResult(fetched_captions=3, channels_reached=["alpha"]))
            self.seen = ingest_job.status()
            return BackfillResult(fetched_captions=3)

        def index(on_progress=None, only_new=False):
            self.only_new = only_new
            on_progress(40, 80)
            self.seen_index = ingest_job.status()
            return {}

        self.run_job(youtube=youtube, index=index)

        self.assertEqual(self.seen["youtube_videos"], 3)
        self.assertIn("@alpha", self.seen["detail"])
        self.assertEqual((self.seen_index["index_done"], self.seen_index["index_total"]), (40, 80))
        self.assertTrue(self.only_new)  # the job only writes what the store lacks
        # seen while the index stage was running: the app must not query the store now
        self.assertEqual(self.seen_index["stage"], "index")


class StoreHandoverTests(IngestJobTestCase):
    """Found by the first real run through the app: Chroma's embedded store can't be
    queried while another process writes it, and the app's cached client stays out of
    step with the files after the job has finished."""

    def setUp(self):
        super().setUp()
        patcher = patch("vg09.ingest_job._last_seen_finish", ingest_job._NOT_LOOKED)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_is_writing_store_only_during_a_running_jobs_index_stage(self):
        now = datetime.now().isoformat()
        self.assertFalse(ingest_job.is_writing_store())  # no job has ever run
        self.write_status(state="running", stage="youtube", heartbeat=now)
        self.assertFalse(ingest_job.is_writing_store())
        self.write_status(state="running", stage="index", heartbeat=now)
        self.assertTrue(ingest_job.is_writing_store())
        self.write_status(state="done", stage="finished", heartbeat=now, finished=now)
        self.assertFalse(ingest_job.is_writing_store())

    def test_the_client_is_reset_once_when_a_job_finishes_while_the_app_is_open(self):
        with patch("vg09.store.reset_client") as mock_reset:
            self.assertFalse(ingest_job.refresh_store_if_updated())  # first look: nothing run yet
            self.write_status(state="done", heartbeat="2026-10-02T17:00:00",
                              finished="2026-10-02T17:00:00")
            self.assertTrue(ingest_job.refresh_store_if_updated())   # the first job ever
            self.assertFalse(ingest_job.refresh_store_if_updated())  # same finish: no repeat
            self.write_status(state="done", heartbeat="2026-10-02T18:00:00",
                              finished="2026-10-02T18:00:00")
            self.assertTrue(ingest_job.refresh_store_if_updated())   # a later job
        self.assertEqual(mock_reset.call_count, 2)

    def test_a_process_that_starts_after_a_job_finished_has_nothing_to_reset(self):
        self.write_status(state="done", heartbeat="2026-10-02T17:00:00",
                          finished="2026-10-02T17:00:00")
        with patch("vg09.store.reset_client") as mock_reset:
            self.assertFalse(ingest_job.refresh_store_if_updated())
        mock_reset.assert_not_called()


if __name__ == "__main__":
    unittest.main()
