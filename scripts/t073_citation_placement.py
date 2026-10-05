"""T-073: where the model puts its citations, for the code in the repo given as argv[1].

Mirrors that version's app.py call sequence. For each answer: split into units (list
items and paragraphs), count units carrying at least one [N] citation, and how many of
all citation brackets sit in the final unit. Real calls; nothing is written but argv[3].
"""
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
runs = int(sys.argv[2])
sys.path.insert(0, str(repo))
sys.stdout.reconfigure(encoding="utf-8")

from vg09.answer import generate_answer  # noqa: E402
from vg09.date_range import detect_recency_ranking, resolve_date_range  # noqa: E402
from vg09.retrieval import retrieve  # noqa: E402
from vg09.store import latest_feed_date  # noqa: E402

has_source = importlib.util.find_spec("vg09.source_filter") is not None
if has_source:
    from vg09.source_filter import detect_source

QUESTIONS = [
    "What's new in AI agent research this week?",
    "Has Anthropic been mentioned in the last week?",
    "Vad har hänt med GUI agents den senaste månaden?",
]
CITE = re.compile(r"\[\s*\d+(?:\s*[,\-–]\s*\d+)*\s*\]")


def units(answer: str) -> list[str]:
    out, buf = [], []
    for line in answer.splitlines():
        s = line.strip()
        if not s:
            if buf:
                out.append(" ".join(buf)); buf = []
            continue
        if re.match(r"^(\d+\.|[-*•])\s", s):
            if buf:
                out.append(" ".join(buf)); buf = []
            out.append(s)
        else:
            buf.append(s)
    if buf:
        out.append(" ".join(buf))
    return out


today = latest_feed_date()
results = []
for q in QUESTIONS:
    date_range = resolve_date_range(q, today, manual_override=None)
    ranking = detect_recency_ranking(q)
    kwargs = {}
    if has_source:
        kwargs["source"] = detect_source(q)
    t0 = time.monotonic()
    retrieval = retrieve(q, date_range=date_range, ranking=ranking, **kwargs)
    rt = time.monotonic() - t0
    for r in range(runs):
        t0 = time.monotonic()
        try:
            res = generate_answer(q, retrieval.chunks, date_range=date_range)
        except TypeError:
            res = generate_answer(q, retrieval.chunks)
        gt = time.monotonic() - t0
        u = units(res.answer)
        cited = sum(1 for x in u if CITE.search(x))
        total = len(CITE.findall(res.answer))
        last = len(CITE.findall(u[-1])) if u else 0
        results.append({"q": q, "run": r, "packed": len(retrieval.chunks), "units": len(u),
                        "cited_units": cited, "brackets": total, "in_last": last,
                        "answer": res.answer, "retrieve_s": rt, "generate_s": gt, "prompt_tokens": res.prompt_eval_count, "retries": res.retries, "done": res.done_reason})
        print(f"{q[:40]:40} run{r} packed={len(retrieval.chunks):2} units={len(u):2} "
              f"cited={cited:2} brackets={total:2} in_last={last:2} ret={rt:4.1f}s gen={gt:5.1f}s prompt={res.prompt_eval_count} retries={res.retries}", flush=True)

out = Path(sys.argv[3])
out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
