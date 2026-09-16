"""HF Daily Papers collector -> normalized Document shape (T-009).

Field mapping confirmed in KB-002, not assumed: the abstract is `summary`, not
`abstract`; the arXiv id lives at `paper.id`, not the entry's top level; and the
date the `date=` query matches on is `paper.submittedOnDailyAt`, not the top-level
`publishedAt` (which is the paper's own arXiv date - kept as `arxiv_published_at`
metadata only, per D-002).
"""

from __future__ import annotations

from datetime import date

import requests

from vg09.document import Document

API_URL = "https://huggingface.co/api/daily_papers"


def fetch_day(d: date) -> list[dict]:
    """Raw entries for one day. An empty list is a normal response on weekends
    (KB-002), not a failure."""
    resp = requests.get(API_URL, params={"date": d.isoformat()}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize(entry: dict) -> Document | None:
    paper = entry.get("paper") or {}
    arxiv_id = paper.get("id")
    feed_date_raw = paper.get("submittedOnDailyAt")  # e.g. "2026-09-15T00:00:00.000Z"
    if not arxiv_id or not feed_date_raw:
        return None
    feed_date = feed_date_raw.split("T", 1)[0]
    return Document(
        id=arxiv_id,
        source="hf",
        url=f"https://huggingface.co/papers/{arxiv_id}",
        title=entry.get("title", ""),
        feed_date=feed_date,
        text=entry.get("summary", ""),
        arxiv_published_at=paper.get("publishedAt"),
    )


def collect_day(d: date) -> list[Document]:
    """Fetch, normalize and persist one day's papers to data/raw/hf/. Returns what
    was written; skips entries missing an arXiv id or feed date rather than
    writing an incomplete document - per KB-002 this shouldn't happen, so a skip
    is reported rather than swallowed, in case the API's shape has changed."""
    docs = []
    for entry in fetch_day(d):
        doc = normalize(entry)
        if doc is not None:
            doc.write()
            docs.append(doc)
        else:
            print(f"  skipping entry missing arxiv id or feed_date: {entry.get('title')!r}")
    return docs
