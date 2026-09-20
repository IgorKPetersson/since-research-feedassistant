"""T-038: real measurement of the "[N] Title (url, feed date)\\n" wrapper's token cost,
to re-derive docs/DESIGN.md's "max top-k" ceiling honestly instead of assuming it's
negligible. Real `count_qwen_tokens()` calls, no synthetic filler.

Scans every real chunk's metadata in the production store (one Chroma metadata read, no
embedding calls) to find the chunk with the longest real title+url+feed_date combination
- the real worst case, not a guessed one - then measures its real token cost with and
without the wrapper via two real Ollama calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.retrieval import PACKING_PLACEHOLDER_SOURCE_NUMBER, Candidate, count_qwen_tokens, format_source
from vg09.store import get_collection


def main() -> None:
    collection = get_collection()
    result = collection.get(include=["metadatas", "documents"])
    ids = result["ids"]
    documents = result["documents"]
    metadatas = result["metadatas"]
    print(f"real chunks in store: {len(ids)}")

    def wrapper_len(m: dict) -> int:
        # real chars, not tokens - a cheap proxy to find the longest real combination
        # before spending a real Ollama call on it
        return len(m.get("title", "")) + len(m.get("url", "")) + len(m.get("feed_date", ""))

    longest_idx = max(range(len(ids)), key=lambda i: wrapper_len(metadatas[i]))
    c = Candidate(id=ids[longest_idx], text=documents[longest_idx], metadata=metadatas[longest_idx])
    print(f"\nlongest real title/url/feed_date combination: {c.id}")
    print(f"  title: {c.metadata['title']!r}")
    print(f"  url: {c.metadata['url']!r}")

    bare_tokens = count_qwen_tokens(c.text)
    wrapped_tokens = count_qwen_tokens(format_source(c, PACKING_PLACEHOLDER_SOURCE_NUMBER))
    overhead = wrapped_tokens - bare_tokens
    print(f"\nbare c.text tokens: {bare_tokens}")
    print(f"wrapped (format_source) tokens: {wrapped_tokens}")
    print(f"real wrapper overhead: {overhead} tokens")

    # also sample the chunk with the SHORTEST title, for a real min-overhead data point
    shortest_idx = min(range(len(ids)), key=lambda i: wrapper_len(metadatas[i]))
    c2 = Candidate(id=ids[shortest_idx], text=documents[shortest_idx], metadata=metadatas[shortest_idx])
    bare2 = count_qwen_tokens(c2.text)
    wrapped2 = count_qwen_tokens(format_source(c2, PACKING_PLACEHOLDER_SOURCE_NUMBER))
    print(f"\nshortest real title/url/feed_date combination: {c2.id}")
    print(f"  title: {c2.metadata['title']!r}")
    print(f"bare tokens: {bare2}  wrapped tokens: {wrapped2}  overhead: {wrapped2 - bare2}")


if __name__ == "__main__":
    main()
