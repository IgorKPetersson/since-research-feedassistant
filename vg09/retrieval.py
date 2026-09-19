"""T-022: similarity search with an optional date-range filter or recency sort,
packed to T-008's measured 13789-token budget (docs/DESIGN.md § "Context budget").

Two independent mechanisms (docs/DESIGN.md § "Filtering by date and sorting by date are
two different mechanisms"):

- **Filter** - a `date_range` narrows candidates to a `feed_date_ordinal` window before
  ranking (KB-004: filter on the int ordinal, never the `feed_date` string).
- **Sort** - `ranking=True` re-orders an already similarity-matched candidate set by
  `feed_date_ordinal` descending instead of by similarity, for a ranking question
  ("det senaste", `vg09.date_range.detect_recency_ranking()`).

Either, both, or neither can be active for a given query - this module takes them as
two independent parameters rather than inferring one from the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import requests

from vg09.store import embed_batch, get_collection

OLLAMA = "http://localhost:11434"
CHAT_MODEL = "qwen3:30b-a3b"  # D-005
NUM_CTX = 16000  # D-005 - the real, explicit num_ctx every call must set (CLAUDE.md)

# docs/DESIGN.md § "Remaining budget for retrieved chunks":
# 16000 (num_ctx) - 157 (system prompt, re-measured after T-024's citation-instruction
# wording change - was 171) - 40 (question) - 2000 (reasoning+answer) = 13803
CHUNK_BUDGET_TOKENS = 13803
MAX_CHUNKS_PER_DOC = 2  # T-027: a document with many chunks (a long YouTube
# transcript) can otherwise fill most/all of the top of the ranking by volume alone,
# crowding out other, equally- or more-relevant documents represented by only one
# chunk each - a real, measured effect (see dedup_by_doc()'s docstring)

# docs/DESIGN.md's "34 = 13789 // 400" (now ~34 = 13803 // 400, T-024's re-measurement
# doesn't change this meaningfully) is a worst-case ceiling (every chunk at the
# 400-token cap), not a target - packing here is purely token-budget-driven, not
# chunk-count-driven, so a real candidate pool of smaller-than-cap chunks can (and in
# scripts/t022_verify_retrieval.py's real run, did: 45) pack more than 34 while still
# safely fitting the budget. CANDIDATE_POOL_SIZE is generous headroom over that
# worst-case ceiling so packing always has real candidates to skip past (an oversized
# one, or a date-filtered-out one) without running dry before reaching a usable top-k.
CANDIDATE_POOL_SIZE = 60


@dataclass
class Candidate:
    id: str
    text: str
    metadata: dict


@dataclass
class RetrievalResult:
    chunks: list[Candidate] = field(default_factory=list)
    total_tokens: int = 0
    dropped_oversized: list[str] = field(default_factory=list)  # ids
    date_range_used: tuple[date, date] | None = None
    ranking_used: bool = False
    candidates_considered: int = 0


def count_qwen_tokens(text: str) -> int:
    """Real qwen3 token count for one chunk of text, via the same technique T-008
    measured the whole budget with: `num_predict:1` is the minimal-cost way to read a
    real `prompt_eval_count` without generating a real answer (KB-009 - `num_predict:0`
    does NOT mean "generate nothing")."""
    resp = requests.post(
        f"{OLLAMA}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": text,
            "stream": False,
            "options": {"num_ctx": NUM_CTX, "num_predict": 1},
        },
        timeout=120,
    )
    resp.raise_for_status()
    count = resp.json()["prompt_eval_count"]
    if count >= NUM_CTX:
        print(f"  !! TRUNCATION RISK: count_qwen_tokens prompt_eval_count={count} >= "
              f"num_ctx={NUM_CTX}")
    elif count >= 0.9 * NUM_CTX:
        print(f"  !! close to num_ctx: count_qwen_tokens prompt_eval_count={count} "
              f"({100 * count / NUM_CTX:.0f}% of num_ctx={NUM_CTX})")
    return count


def embed_question(question: str) -> list[float]:
    """The question, embedded via the same explicit bge-m3/num_ctx=8192 call every
    other embedding in this project uses - never `query_texts=` (CLAUDE.md hard rule,
    docs/DESIGN.md's "Interfaces and contracts" warning: that path silently invokes
    Chroma's default embedder)."""
    return embed_batch([question])[0]


def query_candidates(
    question: str,
    date_range: tuple[date, date] | None,
    n_results: int = CANDIDATE_POOL_SIZE,
) -> list[Candidate]:
    """Real Chroma similarity search, in Chroma's own relevance order. `date_range`,
    when given, filters by `feed_date_ordinal` ($gte/$lte, KB-004) - never by the
    `feed_date` string. Passing `date_range=None` runs genuinely unfiltered, which is
    exactly what Phase 3's "plain retrieval" comparison arm calls with, regardless of
    what `vg09.date_range` would have extracted from the question."""
    collection = get_collection()
    query_embedding = embed_question(question)

    where = None
    if date_range is not None:
        start, end = date_range
        where = {
            "$and": [
                {"feed_date_ordinal": {"$gte": start.toordinal()}},
                {"feed_date_ordinal": {"$lte": end.toordinal()}},
            ]
        }

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
    )
    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    return [Candidate(id=i, text=t, metadata=m) for i, t, m in zip(ids, documents, metadatas)]


def order_candidates(candidates: list[Candidate], ranking: bool) -> list[Candidate]:
    """`ranking=True` re-sorts by feed_date_ordinal descending (most recent first) -
    for a "det senaste" question, per docs/DESIGN.md. `ranking=False` keeps Chroma's
    own similarity order untouched. Either way this is a stable sort, so within equal
    dates (ranking) the original relevance order survives as the tiebreak."""
    if not ranking:
        return candidates
    return sorted(candidates, key=lambda c: c.metadata["feed_date_ordinal"], reverse=True)


def dedup_by_doc(
    candidates: list[Candidate], max_per_doc: int = MAX_CHUNKS_PER_DOC
) -> list[Candidate]:
    """T-027: at most `max_per_doc` chunks from the same document survive, in the
    order given - i.e. the highest-ranked ones, since this runs after
    `order_candidates()` and before `pack_to_budget()`. Real finding that motivated
    this: for several of T-014's real questions, a single video's chunks filled 3-4
    of the top 5 candidate slots (e.g. one video occupied ranks 1, 3, 5, 10 for a real
    "GUI agents" query), while genuinely on-topic documents ranked respectably
    (7th-36th of 60 real candidates) but never surfaced. Applies identically in
    filter and ranking mode - it runs on whatever order those produced, without
    knowing or caring which one was used."""
    counts: dict[str, int] = {}
    deduped: list[Candidate] = []
    for c in candidates:
        doc_id = c.metadata["doc_id"]
        if counts.get(doc_id, 0) >= max_per_doc:
            continue
        counts[doc_id] = counts.get(doc_id, 0) + 1
        deduped.append(c)
    return deduped


def pack_to_budget(
    candidates: list[Candidate], budget_tokens: int = CHUNK_BUDGET_TOKENS
) -> tuple[list[Candidate], int, list[str]]:
    """Greedy pack in the given order (docs/DESIGN.md § "What happens if retrieved
    chunks don't fit"):

    1. A candidate whose own token count exceeds the *entire* budget can never fit,
       regardless of what's already packed - dropped, and packing continues past it
       (a later, smaller candidate may still fit).
    2. Otherwise, once adding a candidate would push the running total over budget,
       packing stops there - the remaining, lower-priority candidates are not sent,
       matching "stop adding once the running total would exceed the budget" exactly
       (not a bin-packing best-fit search for a smaller one that might still squeeze
       in later).
    """
    packed: list[Candidate] = []
    dropped_oversized: list[str] = []
    total = 0
    for c in candidates:
        tokens = count_qwen_tokens(c.text)
        if tokens > budget_tokens:
            dropped_oversized.append(c.id)
            continue
        if total + tokens > budget_tokens:
            break
        packed.append(c)
        total += tokens
    return packed, total, dropped_oversized


def retrieve(
    question: str,
    date_range: tuple[date, date] | None,
    ranking: bool,
    n_results: int = CANDIDATE_POOL_SIZE,
) -> RetrievalResult:
    """The full pipeline: similarity search (optionally date-filtered) -> order
    (similarity or recency) -> dedup by document (T-027) -> pack to T-008's measured
    budget. `date_range` and `ranking` are both explicit parameters here, not derived
    from the question inside this function - callers (T-023, or Phase 3's evaluation
    script) decide those via `vg09.date_range.resolve_date_range()`/
    `detect_recency_ranking()`, or override them directly for a "plain retrieval"
    comparison run."""
    candidates = query_candidates(question, date_range, n_results)
    ordered = order_candidates(candidates, ranking)
    deduped = dedup_by_doc(ordered)
    packed, total_tokens, dropped = pack_to_budget(deduped)
    return RetrievalResult(
        chunks=packed,
        total_tokens=total_tokens,
        dropped_oversized=dropped,
        date_range_used=date_range,
        ranking_used=ranking,
        candidates_considered=len(candidates),
    )
