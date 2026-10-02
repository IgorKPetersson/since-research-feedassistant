"""Unit tests for vg09.chunking (T-012).

No network calls. YouTube chunking is tested against a synthetic segment list
(no real caption data exists yet - still IpBlocked, KB-008) built directly as
plain dicts, matching the real `{"text", "start", "duration"}` shape T-010
confirmed for FetchedTranscriptSnippet.
"""

import unittest

from vg09.chunking import TARGET_CHUNK_CHARS, chunk_document, chunk_hf_document, chunk_youtube_document

HF_DOC = {
    "id": "2609.06986",
    "source": "hf",
    "url": "https://huggingface.co/papers/2609.06986",
    "title": "Continual Learning Mechanisms Compose for Long-Horizon Memorization",
    "feed_date": "2026-09-16",
    "text": "Language models may need to internalize information that arrives over time.",
    "arxiv_published_at": "2026-09-07T00:00:00.000Z",
    "text_source": None,
    "fallback_reason": None,
}


def make_segments(n: int, words_per_segment: int = 8, seconds_per_segment: float = 3.0) -> list[dict]:
    """A synthetic but realistically-shaped transcript: no punctuation, no
    capitalization (KB-001), evenly spaced in time - not real caption text,
    just enough to exercise the windowing logic."""
    segments = []
    for i in range(n):
        words = " ".join(f"word{i}_{j}" for j in range(words_per_segment))
        segments.append({"text": words, "start": i * seconds_per_segment, "duration": seconds_per_segment})
    return segments


class ChunkHfTests(unittest.TestCase):
    def test_one_chunk_per_paper(self):
        chunks = chunk_hf_document(HF_DOC)
        self.assertEqual(len(chunks), 1)
        c = chunks[0]
        self.assertEqual(c.id, "hf:2609.06986:0")
        self.assertEqual(c.source, "hf")
        self.assertEqual(c.text, HF_DOC["text"])
        self.assertEqual(c.url, HF_DOC["url"])
        self.assertEqual(c.arxiv_published_at, HF_DOC["arxiv_published_at"])
        self.assertIsNone(c.start_seconds)


class ChunkYoutubeTests(unittest.TestCase):
    def test_fallback_document_with_no_segments_is_one_chunk_no_timestamp(self):
        doc = {
            "id": "abc123",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=abc123",
            "title": "Some Video",
            "feed_date": "2026-09-10",
            "text": "Some Video\n\nA description.",
            "text_source": "title_description",
            "fallback_reason": "NoTranscriptFound",
            "segments": None,
        }
        chunks = chunk_youtube_document(doc)
        self.assertEqual(len(chunks), 1)
        c = chunks[0]
        self.assertIsNone(c.start_seconds)
        self.assertEqual(c.url, doc["url"])  # no &t= appended - no real timestamp exists
        self.assertEqual(c.text_source, "title_description")

    def test_segments_are_windowed_by_char_budget_not_all_in_one_chunk(self):
        # Each segment ~50 chars; enough segments to comfortably exceed
        # TARGET_CHUNK_CHARS and force at least 2 windows.
        n = (TARGET_CHUNK_CHARS // 50) * 3
        segments = make_segments(n, words_per_segment=8, seconds_per_segment=3.0)
        doc = {
            "id": "longvideo",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=longvideo",
            "title": "Long Video",
            "feed_date": "2026-09-10",
            "text": " ".join(s["text"] for s in segments),
            "text_source": "captions",
            "fallback_reason": None,
            "segments": segments,
        }
        chunks = chunk_youtube_document(doc)

        self.assertGreater(len(chunks), 1)
        # First chunk starts at the very first segment's real timestamp.
        self.assertEqual(chunks[0].start_seconds, 0.0)
        # Every chunk after the first starts later than the one before -
        # timestamps are real and monotonically increasing.
        for prev, cur in zip(chunks, chunks[1:]):
            self.assertLess(prev.start_seconds, cur.start_seconds)
        # Citation links carry a real &t=SECONDS, not a placeholder.
        for c in chunks:
            self.assertIn(f"&t={int(c.start_seconds)}", c.url)
        # No text is dropped: every chunk's text, rejoined, reproduces all
        # segment text (order preserved).
        rejoined = " ".join(c.text for c in chunks)
        self.assertEqual(rejoined, " ".join(s["text"] for s in segments))

    def test_fallback_reason_propagates_through_the_windowed_path_too(self):
        """T-013 verification found this: flush() (the windowed/multi-chunk
        path) passed text_source but not fallback_reason, so a Whisper
        document's real fallback_reason ("IpBlocked" - why captions were
        skipped, D-009) was silently dropped from every chunk. Invisible for
        captions (fallback_reason is always None there) until a real
        Whisper-sourced document with real segments exercised this path."""
        segments = make_segments(60)
        doc = {
            "id": "whispervid", "source": "youtube",
            "url": "https://www.youtube.com/watch?v=whispervid",
            "title": "T", "feed_date": "2026-09-10", "text": "x",
            "text_source": "whisper", "fallback_reason": "IpBlocked", "segments": segments,
        }
        chunks = chunk_youtube_document(doc)
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertEqual(c.text_source, "whisper")
            self.assertEqual(c.fallback_reason, "IpBlocked")

    def test_ids_are_unique_and_ordered(self):
        segments = make_segments(60)
        doc = {
            "id": "v1", "source": "youtube", "url": "https://www.youtube.com/watch?v=v1",
            "title": "T", "feed_date": "2026-09-10", "text": "x",
            "text_source": "captions", "fallback_reason": None, "segments": segments,
        }
        chunks = chunk_youtube_document(doc)
        ids = [c.id for c in chunks]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [f"youtube:v1:{i}" for i in range(len(chunks))])


class ChunkDocumentDispatchTests(unittest.TestCase):
    def test_dispatches_by_source(self):
        self.assertEqual(len(chunk_document(HF_DOC)), 1)

    def test_unknown_source_raises(self):
        with self.assertRaises(ValueError):
            chunk_document({"source": "carrier_pigeon"})


if __name__ == "__main__":
    unittest.main()


class ChannelPropagationTests(unittest.TestCase):
    """T-054: a video's channel reaches every one of its chunks, on both chunking paths;
    a paper has none."""

    def test_windowed_and_single_chunk_youtube_documents_carry_the_channel(self):
        base = {"id": "v1", "source": "youtube", "url": "https://www.youtube.com/watch?v=v1",
                "title": "t", "feed_date": "2026-09-10", "text": "x", "channel": "alpha"}
        windowed = chunk_youtube_document({**base, "segments": make_segments(400)})
        self.assertGreater(len(windowed), 1)
        self.assertEqual({c.channel for c in windowed}, {"alpha"})
        self.assertEqual(chunk_youtube_document(base)[0].channel, "alpha")

    def test_a_document_without_the_key_and_a_paper_have_no_channel(self):
        old = {"id": "v1", "source": "youtube", "url": "u", "title": "t",
               "feed_date": "2026-09-10", "text": "x"}
        self.assertIsNone(chunk_youtube_document(old)[0].channel)
        paper = {"id": "2609.1", "source": "hf", "url": "u", "title": "t",
                 "feed_date": "2026-09-10", "text": "x"}
        self.assertIsNone(chunk_hf_document(paper)[0].channel)
