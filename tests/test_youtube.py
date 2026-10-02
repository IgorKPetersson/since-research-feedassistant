"""Unit tests for vg09.youtube (T-010).

No live network calls: `YouTubeTranscriptApi` is mocked in every test, per
explicit instruction not to make YouTube calls (transcript or yt-dlp) for this
ticket. Uses stdlib unittest/unittest.mock - no test framework has been chosen
for this project yet, and adding one (e.g. pytest) is a dependency decision
this ticket wasn't asked to make.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from youtube_transcript_api._errors import IpBlocked, NoTranscriptFound
from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet

from vg09 import youtube

VIDEO = {
    "id": "abc123XYZ90",
    "title": "Some Video Title",
    "upload_date": "20260910",
    "description": "A description of the video.",
}


class YoutubeNormalizeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raw_dir = Path(tmp.name)
        patcher = patch("vg09.document.RAW_DIR", self.raw_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_missing_captions_falls_back_to_title_description(self):
        """TranscriptsDisabled/NoTranscriptFound (and similar) are per-video -
        D-006's "missing" case - and still produce a final document (D-001)."""
        with patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls:
            mock_api_cls.return_value.fetch.side_effect = NoTranscriptFound(
                VIDEO["id"], ["en"], {}
            )
            doc = youtube.normalize(VIDEO)

        self.assertIsNotNone(doc)
        self.assertEqual(doc.text_source, "title_description")
        self.assertEqual(doc.fallback_reason, "NoTranscriptFound")
        self.assertTrue(doc.text.startswith(VIDEO["title"]))
        self.assertIn(VIDEO["description"], doc.text)
        self.assertIsNone(doc.segments)  # nothing was ever fetched to segment

        doc.write()
        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        self.assertTrue(final_path.exists())

    def test_blocked_falls_back_to_whisper(self):
        """RequestBlocked/IpBlocked (KB-008) triggers the Whisper path
        (D-009/T-019) instead of aborting - a caption block no longer means
        no transcript, or stopping the run."""
        fake_segments = [{"text": "Hello", "start": 0.0, "duration": 1.0}]
        with (
            patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls,
            patch("vg09.youtube.fetch_whisper_transcript",
                  return_value=("Hello", fake_segments)) as mock_whisper,
        ):
            mock_api_cls.return_value.fetch.side_effect = IpBlocked(VIDEO["id"])
            doc = youtube.normalize(VIDEO)

        mock_whisper.assert_called_once_with(VIDEO["id"])
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text_source, "whisper")
        self.assertEqual(doc.fallback_reason, "IpBlocked")
        self.assertEqual(doc.text, "Hello")
        self.assertEqual(doc.segments, fake_segments)

        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        pending_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.pending.json"
        doc.write()
        self.assertTrue(final_path.exists())
        self.assertFalse(pending_path.exists())  # normalize() no longer writes one

    def test_blocked_and_whisper_fails_falls_back_to_title_description(self):
        """When both captions and Whisper fail, title+description is the
        third resort (T-019) - still a final document, never an abort."""
        with (
            patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls,
            patch("vg09.youtube.fetch_whisper_transcript",
                  side_effect=RuntimeError("no GPU")),
        ):
            mock_api_cls.return_value.fetch.side_effect = IpBlocked(VIDEO["id"])
            doc = youtube.normalize(VIDEO)

        self.assertIsNotNone(doc)
        self.assertEqual(doc.text_source, "title_description")
        self.assertEqual(doc.fallback_reason, "IpBlocked;whisper:RuntimeError")
        self.assertTrue(doc.text.startswith(VIDEO["title"]))
        self.assertIn(VIDEO["description"], doc.text)
        self.assertIsNone(doc.segments)

    def test_captions_available_uses_the_real_transcript_shape(self):
        """The success path (never actually run in T-009 - every attempt hit
        IpBlocked, KB-008) against the library's real FetchedTranscript/
        FetchedTranscriptSnippet dataclasses, not an invented mock shape."""
        fake_transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(text="Hello", start=0.0, duration=1.0),
                FetchedTranscriptSnippet(text="world", start=1.0, duration=1.0),
            ],
            video_id=VIDEO["id"],
            language="English",
            language_code="en",
            is_generated=True,
        )
        with patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls:
            mock_api_cls.return_value.fetch.return_value = fake_transcript
            doc = youtube.normalize(VIDEO)

        self.assertIsNotNone(doc)
        self.assertEqual(doc.text_source, "captions")
        self.assertIsNone(doc.fallback_reason)
        self.assertEqual(doc.text, "Hello world")
        self.assertEqual(
            doc.segments,
            [
                {"text": "Hello", "start": 0.0, "duration": 1.0},
                {"text": "world", "start": 1.0, "duration": 1.0},
            ],
        )

        doc.write()
        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        self.assertTrue(final_path.exists())


class FetchWhisperTranscriptTests(unittest.TestCase):
    """T-019: no real yt-dlp download or GPU call - `yt_dlp.YoutubeDL` and
    `_get_whisper_model()` are both mocked at the boundary, same style as the
    caption tests above."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.audio_dir = Path(tmp.name)
        patcher = patch("vg09.youtube.WHISPER_AUDIO_DIR", self.audio_dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        # T-057: a failed transcription is remembered for the rest of the process;
        # each test starts without one, and whatever it sets is undone afterwards.
        failed_patcher = patch("vg09.youtube._whisper_failed", None)
        failed_patcher.start()
        self.addCleanup(failed_patcher.stop)

    def test_after_one_runtime_error_whisper_is_not_tried_again_in_this_run(self):
        """Found for real: after one RuntimeError from a broken GPU setup the next
        transcription hung forever. The second video must fail at once, before any
        audio is downloaded."""
        audio_path = self.audio_dir / "vid1.webm"

        class FakeYDL:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *exc):
                return False

            def extract_info(self_inner, url, download=True):
                audio_path.write_bytes(b"fake audio")
                return {"id": "vid1"}

            def prepare_filename(self_inner, info):
                return str(audio_path)

        class BrokenModel:
            def transcribe(self_inner, path, beam_size=5):
                raise RuntimeError("Library cublas64_12.dll is not found")

        with patch("vg09.youtube.yt_dlp.YoutubeDL", return_value=FakeYDL()) as mock_ydl, \
             patch("vg09.youtube._get_whisper_model", return_value=BrokenModel()):
            with self.assertRaises(RuntimeError):
                youtube.fetch_whisper_transcript("vid1")
            self.assertEqual(mock_ydl.call_count, 1)
            with self.assertRaises(RuntimeError) as second:
                youtube.fetch_whisper_transcript("vid2")
            self.assertEqual(mock_ydl.call_count, 1)  # no second download
        self.assertIn("unavailable in this run", str(second.exception))

    def test_cuda_dll_dirs_are_found_in_the_running_interpreters_site_packages(self):
        """The wheels' bin directories are looked up where this interpreter keeps its
        packages, not in a `.venv` folder assumed to sit inside the repository."""
        import os

        site_packages = self.audio_dir / "site-packages"
        for pkg in ("cublas", "cudnn"):
            (site_packages / "nvidia" / pkg / "bin").mkdir(parents=True)
        paths = {"purelib": str(site_packages), "platlib": str(site_packages)}
        with patch("vg09.youtube.sysconfig.get_paths", return_value=paths), \
             patch.dict(os.environ, {"PATH": "original"}):
            youtube._add_whisper_cuda_dll_dirs()
            parts = os.environ["PATH"].split(os.pathsep)
        self.assertEqual(parts[-1], "original")
        self.assertEqual(sorted(Path(p).parent.name for p in parts[:-1]), ["cublas", "cudnn"])

    def test_converts_segments_and_deletes_audio_after(self):
        audio_path = self.audio_dir / "vid123.webm"

        class FakeYDL:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *exc):
                return False

            def extract_info(self_inner, url, download=True):
                self.audio_dir.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"fake audio")
                return {"id": "vid123"}

            def prepare_filename(self_inner, info):
                return str(audio_path)

        class FakeSegment:
            def __init__(self, text, start, end):
                self.text = text
                self.start = start
                self.end = end

        fake_segments = [FakeSegment(" Hello ", 0.0, 1.5), FakeSegment("world", 1.5, 3.0)]

        class FakeModel:
            def transcribe(self_inner, path, beam_size=5):
                assert path == str(audio_path)
                return fake_segments, object()

        with (
            patch("vg09.youtube.yt_dlp.YoutubeDL", return_value=FakeYDL()),
            patch("vg09.youtube._get_whisper_model", return_value=FakeModel()),
        ):
            text, segments = youtube.fetch_whisper_transcript("vid123")

        self.assertEqual(text, "Hello world")
        self.assertEqual(
            segments,
            [
                {"text": "Hello", "start": 0.0, "duration": 1.5},
                {"text": "world", "start": 1.5, "duration": 1.5},
            ],
        )
        self.assertFalse(audio_path.exists())  # deleted after transcription (T-019)

    def test_deletes_audio_even_when_transcription_fails(self):
        audio_path = self.audio_dir / "vid123.webm"

        class FakeYDL:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *exc):
                return False

            def extract_info(self_inner, url, download=True):
                self.audio_dir.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"fake audio")
                return {"id": "vid123"}

            def prepare_filename(self_inner, info):
                return str(audio_path)

        class FakeModel:
            def transcribe(self_inner, path, beam_size=5):
                raise RuntimeError("simulated transcription failure")

        with (
            patch("vg09.youtube.yt_dlp.YoutubeDL", return_value=FakeYDL()),
            patch("vg09.youtube._get_whisper_model", return_value=FakeModel()),
        ):
            with self.assertRaises(RuntimeError):
                youtube.fetch_whisper_transcript("vid123")

        self.assertFalse(audio_path.exists())  # deleted even on failure (T-019)


class CollectChannelTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raw_dir = Path(tmp.name)
        patcher = patch("vg09.document.RAW_DIR", self.raw_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_later_success_clears_an_earlier_pending_marker(self):
        """A video blocked in one run and successfully fetched in a later one
        should not still look pending to a reader that only checks
        `*.pending.json` (T-015's retry logic)."""
        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        pending_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.pending.json"
        pending_path.parent.mkdir(parents=True)
        pending_path.write_text("{}", encoding="utf-8")

        with (
            patch("vg09.youtube.list_videos", return_value=[VIDEO]),
            patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls,
        ):
            mock_api_cls.return_value.fetch.side_effect = NoTranscriptFound(
                VIDEO["id"], ["en"], {}
            )
            docs = youtube.collect_channel("https://www.youtube.com/@irrelevant/videos", count=1)

        self.assertEqual(len(docs), 1)
        self.assertTrue(final_path.exists())
        self.assertFalse(pending_path.exists())


if __name__ == "__main__":
    unittest.main()
