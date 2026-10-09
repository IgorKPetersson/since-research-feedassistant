"""T-095: retrieval-level evaluation on the frozen dataset, before and after a change.

Run (each run imports `vg09` from the checkout given with --code):

    python scripts/t095_retrieval_eval.py run --code <checkout> --version v1 --out a.json
    python scripts/t095_retrieval_eval.py compare a.json b.json > report.md

Every question uses the explicit date filter, ranking flag and expected sources in
docs/eval-expectations.json, the same for both code versions, so a date-parser change
can't show up as a retrieval change. The store is the frozen copy T-069 builds in
data/eval_frozen/ from the archive, checked against docs/eval-dataset-manifest.txt first;
the live data/ is never read. Makes real Ollama calls for embeddings and token counts,
none for answers. Measures what reaches the model: the packed chunks.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FROZEN = REPO / "data" / "eval_frozen"
EXPECTATIONS = REPO / "docs" / "eval-expectations.json"


def expectations(version: str) -> dict:
    data = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
    questions = {k: dict(v) for k, v in data["versions"]["v1"]["questions"].items()}
    if version != "v1":
        for key, change in data["versions"][version]["changes"].items():
            questions[key].update(change)
    return questions


def run(code: Path, version: str, out: Path) -> None:
    sys.path.insert(0, str(code))
    sys.path.insert(1, str(REPO / "scripts"))
    import t020_verify_eval_dataset as t020

    t020.RAW_DIR = FROZEN / "raw"
    if t020.main() != 0:
        sys.exit("The frozen copy does not match the manifest - stopping.")
    import vg09.document
    import vg09.store

    vg09.document.RAW_DIR = FROZEN / "raw"
    vg09.store.RAW_DIR = FROZEN / "raw"
    vg09.store.STORE_PATH = FROZEN / "chroma_store"
    from vg09.retrieval import retrieve
    from vg09.source_filter import detect_source

    results = {}
    for key, q in expectations(version).items():
        date_range = tuple(date.fromisoformat(d) for d in q["filter"]) if q["filter"] else None
        source = detect_source(q["question"])
        r = retrieve(q["question"], date_range=date_range, ranking=q["ranking"], source=source)
        packed = []
        for c in r.chunks:
            m = c.metadata
            if m["doc_id"] not in [p["doc_id"] for p in packed]:
                packed.append({"doc_id": m["doc_id"], "source": m["source"], "feed_date": m["feed_date"]})
        results[key] = {
            "question": q["question"], "filter": q["filter"], "ranking": q["ranking"], "source": source,
            "packed_docs": packed, "packed_chunks": len(r.chunks),
            "absent_text_in_packed": sum(q.get("absent_text", "\0").lower() in c.text.lower()
                                         for c in r.chunks),
            "name_doc_counts": getattr(r, "name_doc_counts", {}),
        }
        print(f"{key}: {len(packed)} docs packed", file=sys.stderr)
    out.write_text(json.dumps({"code": str(code), "version": version, "results": results},
                              indent=1, ensure_ascii=False), encoding="utf-8")


def answers(code: Path, version: str, out: Path) -> None:
    """Generate an answer for every question with `code`'s retrieval and prompt, the same
    explicit filters as `run`, and the frozen reference date as "today". Real model calls,
    about 15 x 25 s. The scope line is passed only when `code` has `vg09.scope` (T-095)."""
    sys.path.insert(0, str(code))
    import vg09.document
    import vg09.store

    vg09.document.RAW_DIR = FROZEN / "raw"
    vg09.store.RAW_DIR = FROZEN / "raw"
    vg09.store.STORE_PATH = FROZEN / "chroma_store"
    from vg09.answer import generate_answer
    from vg09.retrieval import retrieve
    from vg09.source_filter import detect_source

    try:
        from vg09.scope import scope_prompt, search_scope
    except ImportError:
        scope_prompt = None
    reference = date.fromisoformat(json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
                                   ["dataset"]["reference_date"])
    results = {}
    for key, q in expectations(version).items():
        date_range = tuple(date.fromisoformat(d) for d in q["filter"]) if q["filter"] else None
        source = detect_source(q["question"])
        r = retrieve(q["question"], date_range=date_range, ranking=q["ranking"], source=source)
        extra = {}
        if scope_prompt is not None:
            extra["scope_note"] = scope_prompt(search_scope(date_range, source, r.name_doc_counts))
        a = generate_answer(q["question"], r.chunks, date_range=date_range, today=reference, **extra)
        results[key] = {"question": q["question"], "answer": a.answer, "incomplete": a.incomplete,
                        "prompt_eval_count": a.prompt_eval_count,
                        "sources": {n: [c.metadata["doc_id"], c.metadata["feed_date"], c.metadata["title"]]
                                    for n, c in a.source_map.items()},
                        "scope_note": extra.get("scope_note")}
        print(f"{key}: {len(a.answer)} chars, prompt {a.prompt_eval_count}", file=sys.stderr)
    out.write_text(json.dumps({"code": str(code), "version": version, "results": results},
                              indent=1, ensure_ascii=False), encoding="utf-8")


def measure(q: dict, r: dict) -> dict:
    docs = r["packed_docs"]
    ids = [d["doc_id"] for d in docs]
    found = [e for e in q["expected"] if e in ids]
    m = {"expected_found": f"{len(found)}/{len(q['expected'])}" if q["expected"] else "—",
         "papers": sum(d["source"] == "hf" for d in docs),
         "videos": sum(d["source"] == "youtube" for d in docs)}
    if q.get("cross_source"):
        hf = [e for e in found if "." in e]
        yt = [e for e in found if "." not in e]
        m["cross_source"] = f"expected paper {'yes' if hf else 'no'}, expected video {'yes' if yt else 'no'}"
    if "expected_open_set" in q:
        s = q["expected_open_set"]
        inside = [d for d in docs if d["source"] == s["source"] and s["from"] <= d["feed_date"] <= s["through"]]
        m["open_set"] = f"{len(inside)} of {len(docs)} packed docs are {s['source']} papers in {s['from']}–{s['through']}"
    if q.get("absence"):
        m["absence"] = f"'{q['absent_text']}' in {r['absent_text_in_packed']} packed chunks"
    return m


def compare(before_path: Path, after_path: Path) -> None:
    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    qs = expectations(after["version"])
    print("| Question | Filter | Expected in context, before → after | Papers / videos in context, "
          "before → after | Notes |")
    print("|---|---|---|---|---|")
    for key in qs:
        q, b, a = qs[key], measure(qs[key], before["results"][key]), measure(qs[key], after["results"][key])
        filt = "ranking" if q["ranking"] else (" – ".join(q["filter"]) if q["filter"] else "none")
        notes = []
        for field in ("cross_source", "open_set", "absence"):
            if field in a:
                notes.append(b[field] if b[field] == a[field] else f"{b[field]} → {a[field]}")
        names = after["results"][key].get("name_doc_counts")
        if names:
            notes.append("exact names: " + ", ".join(f"{n} in {c} docs" for n, c in names.items()))
        print(f"| {key} | {filt} | {b['expected_found']} → {a['expected_found']} | "
              f"{b['papers']}/{b['videos']} → {a['papers']}/{a['videos']} | {'; '.join(notes)} |")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--code", type=Path, default=REPO)
    r.add_argument("--version", default="v1")
    r.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("compare")
    c.add_argument("before", type=Path)
    c.add_argument("after", type=Path)
    a = sub.add_parser("answers")
    a.add_argument("--code", type=Path, default=REPO)
    a.add_argument("--version", default="v1")
    a.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "run":
        run(args.code.resolve(), args.version, args.out)
    elif args.cmd == "answers":
        answers(args.code.resolve(), args.version, args.out)
    else:
        compare(args.before, args.after)


if __name__ == "__main__":
    main()
