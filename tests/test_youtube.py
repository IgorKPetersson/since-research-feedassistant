"""Unit tests for vg09.youtube (T-010).

No live network calls: `YouTubeTranscriptApi` is mocked in every test, per
explicit instruction not to make YouTube calls (transcript or yt-dlp) for this
ticket. Uses stdlib unittest/unittest.mock - no test framework has been chosen
for this project yet, and adding one (e.g. pytest) is a dependency decision
this ticket wasn't asked to make.
"""

from __future__ import annotations

import json
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

        doc.write()
        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        self.assertTrue(final_path.exists())

    def test_blocked_writes_no_final_document_marks_pending_and_raises(self):
        """RequestBlocked/IpBlocked (KB-008) is not a per-video signal - D-006's
        "blocked" case - so no final document is written, and the caller must
        stop rather than silently continuing."""
        with patch("vg09.youtube.YouTubeTranscriptApi") as mock_api_cls:
            mock_api_cls.return_value.fetch.side_effect = IpBlocked(VIDEO["id"])

            with self.assertRaises(youtube.IngestBlocked) as ctx:
                youtube.normalize(VIDEO)

        self.assertEqual(ctx.exception.video_id, VIDEO["id"])
        self.assertEqual(ctx.exception.reason, "IpBlocked")

        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        pending_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.pending.json"
        self.assertFalse(final_path.exists())
        self.assertTrue(pending_path.exists())

        pending_data = json.loads(pending_path.read_text(encoding="utf-8"))
        self.assertEqual(pending_data["id"], VIDEO["id"])
        self.assertEqual(pending_data["reason"], "IpBlocked")
        self.assertEqual(pending_data["feed_date"], "2026-09-10")

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

        doc.write()
        final_path = self.raw_dir / "youtube" / "2026-09-10" / f"{VIDEO['id']}.json"
        self.assertTrue(final_path.exists())


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
