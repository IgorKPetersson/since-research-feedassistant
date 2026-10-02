"""Unit tests for vg09.sources (T-053). The file path is patched to a temporary
directory in every test - the user's real data/sources.json is never read or written.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg09.channels import CHANNELS
from vg09.sources import Sources, add_channel, load, parse_channel, remove_channel, save


class SourcesFileTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "data" / "sources.json"
        patcher = patch("vg09.sources.SOURCES_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_no_file_gives_the_default_channels_marked_as_not_saved(self):
        sources = load()
        self.assertEqual(sources.channels, CHANNELS)
        self.assertTrue(sources.hf_enabled)
        self.assertFalse(sources.saved)

    def test_defaults_are_a_copy_so_editing_them_does_not_change_the_module_list(self):
        sources = load()
        sources.channels.clear()
        self.assertEqual(len(load().channels), len(CHANNELS))

    def test_save_then_load_round_trips_every_field(self):
        save(Sources(hf_enabled=False, hf_weeks=2, youtube_weeks=6,
                     channels={"somechannel": "https://www.youtube.com/@somechannel/videos"}))
        loaded = load()
        self.assertFalse(loaded.hf_enabled)
        self.assertEqual((loaded.hf_weeks, loaded.youtube_weeks), (2, 6))
        self.assertEqual(loaded.channels, {"somechannel": "https://www.youtube.com/@somechannel/videos"})
        self.assertTrue(loaded.saved)

    def test_an_empty_saved_channel_list_stays_empty_and_is_not_replaced_by_defaults(self):
        save(Sources(channels={}))
        self.assertEqual(load().channels, {})


class ParseChannelTests(unittest.TestCase):
    def test_accepted_forms_all_give_the_same_handle_and_videos_address(self):
        expected = ("theAIsearch", "https://www.youtube.com/@theAIsearch/videos")
        for text in (
            "@theAIsearch",
            "theAIsearch",
            "  @theAIsearch  ",
            "https://www.youtube.com/@theAIsearch",
            "https://www.youtube.com/@theAIsearch/",
            "https://www.youtube.com/@theAIsearch/videos",
            "youtube.com/@theAIsearch/featured",
            "https://m.youtube.com/@theAIsearch",
        ):
            self.assertEqual(parse_channel(text), expected, text)

    def test_other_text_is_rejected_with_a_message(self):
        for text in (
            "",
            "https://www.youtube.com/watch?v=YTG0rdHPTDE",
            "https://example.com/@theAIsearch",
            "https://www.youtube.com/channel/UC123",
            "two words",
        ):
            with self.assertRaises(ValueError, msg=text):
                parse_channel(text)


class AddRemoveTests(unittest.TestCase):
    def test_add_puts_the_channel_in_the_list(self):
        sources = Sources(channels={})
        self.assertEqual(add_channel(sources, "https://www.youtube.com/@mreflow"), "mreflow")
        self.assertEqual(sources.channels, {"mreflow": "https://www.youtube.com/@mreflow/videos"})

    def test_adding_an_existing_channel_is_rejected_whatever_its_letter_case(self):
        sources = Sources(channels={"mreflow": "https://www.youtube.com/@mreflow/videos"})
        with self.assertRaises(ValueError):
            add_channel(sources, "@MrEflow")

    def test_remove_takes_it_out_and_an_unknown_one_is_rejected(self):
        sources = Sources(channels={"mreflow": "https://www.youtube.com/@mreflow/videos"})
        remove_channel(sources, "mreflow")
        self.assertEqual(sources.channels, {})
        with self.assertRaises(ValueError):
            remove_channel(sources, "mreflow")


if __name__ == "__main__":
    unittest.main()
