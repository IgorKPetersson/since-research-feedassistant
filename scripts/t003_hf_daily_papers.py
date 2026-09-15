"""T-003: HF Daily Papers API feasibility test.

Calls https://huggingface.co/api/daily_papers?date=YYYY-MM-DD for each of the
last 14 days, confirms which fields exist (title, abstract, publication date,
arXiv id), and confirms a date more than 10 days in the past still returns
data. Saves one raw response into the repo as evidence.

Makes real network calls; run it manually, it is not a test.
"""

import json
from datetime import date, timedelta
from pathlib import Path

import requests

API_URL = "https://huggingface.co/api/daily_papers"
DAYS_BACK = 14
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_SAMPLE_PATH = Path(__file__).resolve().parent.parent / "docs" / "kb" / "samples"


def fetch_day(d: date) -> dict:
    try:
        resp = requests.get(API_URL, params={"date": d.isoformat()}, timeout=30)
    except requests.RequestException as exc:
        return {
            "date": d.isoformat(),
            "status_code": None,
            "ok": False,
            "body": None,
            "error": f"{type(exc).__name__}: {exc}",
        }
    try:
        body = resp.json() if resp.ok else resp.text
    except ValueError as exc:  # 200 with a non-JSON body
        return {
            "date": d.isoformat(),
            "status_code": resp.status_code,
            "ok": False,
            "body": resp.text,
            "error": f"non-JSON body: {exc}",
        }
    return {
        "date": d.isoformat(),
        "status_code": resp.status_code,
        "ok": resp.ok,
        "body": body,
        "error": None,
    }


def field_report(entries: list[dict]) -> dict:
    # Real shape (confirmed 2026-09-15 against a live response, not assumed):
    # top-level: title, summary (abstract), publishedAt, paper {...}, plus
    # engagement fields (numComments, thumbnail, ...). The arXiv id lives at
    # paper.id, not top-level.
    if not entries:
        return {}
    sample = entries[0]
    paper = sample.get("paper", {})
    return {
        "has_title": "title" in sample,
        "has_abstract_as_summary": "summary" in sample,
        "has_publishedAt": "publishedAt" in sample,
        "has_arxiv_id_at_paper.id": "id" in paper,
        "arxiv_id_sample": paper.get("id"),
        "top_level_keys": sorted(sample.keys()),
        "paper_keys": sorted(paper.keys()) if isinstance(paper, dict) else None,
    }


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    RAW_SAMPLE_PATH.mkdir(parents=True, exist_ok=True)

    today = date.today()
    results = []
    for i in range(DAYS_BACK):
        d = today - timedelta(days=i)
        result = fetch_day(d)
        entry_count = len(result["body"]) if result["ok"] and isinstance(result["body"], list) else 0
        result["entry_count"] = entry_count
        results.append(result)
        status = f"status={result['status_code']}  entries={entry_count}"
        if result.get("error"):
            status += f"  ERROR: {result['error']}"
        print(f"{d.isoformat()}  {status}")

    out_path = DATA_DIR / "t003_hf_daily_papers.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")

    # Field report from the most recent day that actually had entries
    non_empty = [r for r in results if r["ok"] and r["entry_count"] > 0]
    if non_empty:
        report = field_report(non_empty[0]["body"])
        print("\nField report (most recent non-empty day):")
        print(json.dumps(report, indent=2))

        # Save a few entries into the repo as committed evidence of the real
        # shape - not the whole day, to avoid bloating git with author/avatar
        # metadata nobody needs to look at again.
        sample_path = RAW_SAMPLE_PATH / f"daily_papers_{non_empty[0]['date']}_sample.json"
        sample_path.write_text(
            json.dumps(non_empty[0]["body"][:3], indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Saved raw sample (first 3 entries) to {sample_path}")

    # Confirm a date more than 10 days back returns data
    past = [r for r in results if r["entry_count"] > 0 and
            (today - date.fromisoformat(r["date"])).days > 10]
    print(f"\nDates >10 days back with data: {[r['date'] for r in past]}")


if __name__ == "__main__":
    main()
