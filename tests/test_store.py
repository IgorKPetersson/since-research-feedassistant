"""Unit tests for vg09.store (T-027's latest_feed_date() only).

vg09/store.py's other functions (embed_batch, build_store) remain untested per the
Phase 1 grill-me review's deferred finding (docs/PLAN.md's risk register) - this file
covers only the new function T-027 added, per "test what changed", not a backfill of
the rest of the module.
"""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from vg09.store import latest_feed_date


class LatestFeedDateTests(unittest.TestCase):
    def test_returns_the_max_feed_date_ordinal_across_both_sources(self):
        collection = MagicMock()
        collection.count.return_value = 3
        collection.get.return_value = {
            "metadatas": [
                {"feed_date_ordinal": date(2026, 9, 14).toordinal()},  # hf
                {"feed_date_ordinal": date(2026, 9, 17).toordinal()},  # youtube - latest
                {"feed_date_ordinal": date(2026, 9, 10).toordinal()},
            ]
        }
        with patch("vg09.store.get_collection", return_value=collection):
            result = latest_feed_date()

        self.assertEqual(result, date(2026, 9, 17))

    def test_empty_store_returns_none(self):
        collection = MagicMock()
        collection.count.return_value = 0
        with patch("vg09.store.get_collection", return_value=collection):
            result = latest_feed_date()

        self.assertIsNone(result)
        collection.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
