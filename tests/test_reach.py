"""Unit tests for T-074 (D-020): ids and dates from fetched data cannot point outside
`data/`, and only well-formed arXiv and YouTube ids become file names or addresses."""

from __future__ import annotations

import unittest

from vg09 import hf_papers, youtube
from vg09.document import RAW_DIR, pending_path, raw_path

BAD_DATES = ("../2026-10-05", "2026-10-05/../..", "..", "C:\\Windows", "2026-10-5", "")
BAD_VIDEO_IDS = ("../evil", "a" * 12, "short", "abc/def_ghi", "", "..\\..\\x12345")
BAD_ARXIV_IDS = ("../../etc", "abc", "2609.10297/../x", "", "2609.10297; rm")


class RawPathTests(unittest.TestCase):
    def test_a_real_date_stays_inside_data_raw(self):
        for fn in (raw_path, pending_path):
            path = fn("hf", "2026-10-05", "2609.10297")
            self.assertEqual(path.parent.parent.parent, RAW_DIR)

    def test_a_date_that_is_not_yyyy_mm_dd_is_refused(self):
        for d in BAD_DATES:
            for fn in (raw_path, pending_path):
                with self.assertRaises(ValueError, msg=d):
                    fn("hf", d, "2609.10297")


class HfNormalizeTests(unittest.TestCase):
    def entry(self, arxiv_id="2609.10297", day="2026-10-05T00:00:00.000Z"):
        return {"paper": {"id": arxiv_id, "submittedOnDailyAt": day}, "title": "T", "summary": "S"}

    def test_a_real_paper_is_kept(self):
        doc = hf_papers.normalize(self.entry())
        self.assertEqual((doc.id, doc.feed_date), ("2609.10297", "2026-10-05"))

    def test_a_malformed_id_or_date_is_dropped(self):
        for bad in BAD_ARXIV_IDS:
            self.assertIsNone(hf_papers.normalize(self.entry(arxiv_id=bad)), bad)
        for bad in ("../2026-10-05T00:00:00Z", "yesterday"):
            self.assertIsNone(hf_papers.normalize(self.entry(day=bad)), bad)


class YoutubeIdTests(unittest.TestCase):
    def test_a_malformed_video_id_is_dropped_before_anything_is_fetched(self):
        for bad in BAD_VIDEO_IDS:
            self.assertIsNone(youtube.normalize({"id": bad, "upload_date": "20261005"}), bad)

    def test_whisper_refuses_a_malformed_id_before_it_becomes_a_file_name(self):
        for bad in BAD_VIDEO_IDS:
            with self.assertRaises(ValueError, msg=bad):
                youtube.fetch_whisper_transcript(bad)


if __name__ == "__main__":
    unittest.main()
