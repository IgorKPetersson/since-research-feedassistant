"""T-022: similarity search with an optional date-range filter or recency sort,
packed to the current chunk budget (`CHUNK_BUDGET_TOKENS`, docs/DESIGN.md §
"Context budget" - originally T-008's 13789, then T-028's 13261, T-030's 13245, now
T-039's 11787).

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

OLLAMA = "http://127.0.0.1:11434"  # not "localhost" - see vg09/store.py (KB-024)
CHAT_MODEL = "qwen3:30b-a3b"  # D-005
NUM_CTX = 16000  # D-005 - the real, explicit num_ctx every call must set (CLAUDE.md)

# docs/DESIGN.md § "Remaining budget for retrieved chunks":
# 16000 (num_ctx) - 173 (system prompt, T-030 - the English-answer instruction added
# 16 tokens over T-024's 157) - 40 (question) - 2542
# (reasoning+answer, T-039 - raised from T-028's 2542 after T-032's real run still
# truncated 4 of 30 calls) = 11787, - 70 (T-061's date line before the question, 63
# measured with a date range, the longer form) = 11717
CHUNK_BUDGET_TOKENS = 11717
MAX_CHUNKS_PER_DOC = 2  # T-027: a document with many chunks (a long YouTube
# transcript) can otherwise fill most/all of the top of the ranking by volume alone,
# crowding out other, equally- or more-relevant documents represented by only one
# chunk each - a real, measured effect (see dedup_by_doc()'s docstring)

# docs/DESIGN.md's max-top-k ceiling: 11717 // 488 = 24 (T-061; 11787 under T-039 gave 24
# too - was 27 at 13245; T-038
# corrected the earlier 13245 // 400 = 33, which silently assumed zero cost for the real
# "[N] Title (url, feed date)\n" wrapper every packed chunk actually carries; 488 is the
# real worst-case chunk-plus-wrapper cost measured against the production store,
# scripts/t038_measure_wrapper_overhead.py) - still a worst-case ceiling, not a target -
# packing here is purely token-budget-driven, not chunk-count-driven, so a real
# candidate pool of smaller-than-cap chunks can (and in scripts/t022_verify_retrieval.py's
# real run, did: 45, pre-T-038 fix) pack more than the ceiling while still safely fitting
# the budget. CANDIDATE_POOL_SIZE is generous headroom over that worst-case ceiling so
# packing always has real candidates to skip past (an oversized one, or a
# date-filtered-out one) without running dry before reaching a usable top-k.
#
# T-067: raised from 60, which was sized before T-027's per-document dedup existed. A
# generic question ("What's new this week?") matched 60 chunks from only 6 news videos;
# dedup left 12, filling 38% of the chunk budget, and none of the week's 248 paper chunks
# (the first ranked 71st) were ever seen. Measured over the 18-question probe set: at 200,
# every question fills 96-99% of the budget (that one 97%, with 18 papers); 11 of 18
# packed sets change, the 7 that were already full do not. Cost: +0.2 s median retrieval.
CANDIDATE_POOL_SIZE = 200


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
    candidates_after_dedup: int = 0  # T-042: surfaces dedup_by_doc()'s own already-
    # computed output count, for the UI's pipeline strip - not a new pipeline stage,
    # just exposing one that already ran


def count_qwen_tokens(text: str) -> int:
    """Real qwen3 token count for one chunk of text, via the same technique T-008
    measured the whole budget with: `num_predict:1` is the minimal-cost way to read a
    real `prompt_eval_count` without generating a real answer (KB-009 - `num_predict:0`
    does NOT mean "generate nothing")."""
    http_resp = requests.post(
        f"{OLLAMA}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": text,
            "stream": False,
            "options": {"num_ctx": NUM_CTX, "num_predict": 1},
        },
        timeout=120,
    )
    # T-029: fail loudly on a non-2xx Ollama response here, not later as an opaque
    # KeyError from reading a partial/error body.
    http_resp.raise_for_status()
    count = http_resp.json()["prompt_eval_count"]
    if count >= NUM_CTX:
        print(f"  !! TRUNCATION RISK: count_qwen_tokens prompt_eval_count={count} >= "
              f"num_ctx={NUM_CTX}")
    elif count >= 0.9 * NUM_CTX:
        print(f"  !! close to num_ctx: count_qwen_tokens prompt_eval_count={count} "
              f"({100 * count / NUM_CTX:.0f}% of num_ctx={NUM_CTX})")
    return count


def format_source(c: Candidate, n: int) -> str:
    """The exact text a packed chunk becomes once placed in the real prompt
    (`vg09.answer.build_user_message()`) - "[N] Title (url, feed date)\\n{text}". Used
    both to measure a candidate's real token cost during packing (T-038) and to build
    the real prompt itself, from the same source, so packing-time measurement and
    generation-time content can never drift apart the way they did before T-038 (packing
    measured bare `c.text` alone; the real prompt included this wrapper, uncounted)."""
    m = c.metadata
    return f"[{n}] {m['title']} ({m['url']}, feed date {m['feed_date']})\n{c.text}"


# T-038: packing happens before vg09.answer.number_sources() assigns real citation
# numbers (least-relevant-first, only after packing decides what's included) - a
# placeholder is used for the packing-time measurement. Two digits, matching the real
# range seen in production (T-031: up to 45 packed chunks) - biases the measurement
# very slightly conservative rather than optimistic (KB-005's safe direction), since the
# number itself costs ~1 token regardless of its exact value; the wrapper's title/url/
# date text is what actually mattered.
PACKING_PLACEHOLDER_SOURCE_NUMBER = 99


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
    source: str | None = None,
) -> list[Candidate]:
    """Real Chroma similarity search, in Chroma's own relevance order. `date_range`,
    when given, filters by `feed_date_ordinal` ($gte/$lte, KB-004) - never by the
    `feed_date` string. Passing `date_range=None` runs genuinely unfiltered, which is
    exactly what Phase 3's "plain retrieval" comparison arm calls with, regardless of
    what `vg09.date_range` would have extracted from the question."""
    collection = get_collection()
    query_embedding = embed_question(question)

    conditions = []
    if date_range is not None:
        start, end = date_range
        conditions += [
            {"feed_date_ordinal": {"$gte": start.toordinal()}},
            {"feed_date_ordinal": {"$lte": end.toordinal()}},
        ]
    if source is not None:  # T-068: "hf" or "youtube", from vg09.source_filter
        conditions.append({"source": source})
    # Chroma refuses an "$and" of a single condition.
    where = None if not conditions else conditions[0] if len(conditions) == 1 \
        else {"$and": conditions}

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
        # T-038: measure the real formatted source string that actually gets sent to
        # the model (title/url/feed-date wrapper included), not bare c.text alone -
        # the bare-text measurement silently undercounted the real prompt since T-008.
        tokens = count_qwen_tokens(format_source(c, PACKING_PLACEHOLDER_SOURCE_NUMBER))
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
    source: str | None = None,
) -> RetrievalResult:
    """The full pipeline: similarity search (optionally date-filtered) -> order
    (similarity or recency) -> dedup by document (T-027) -> pack to T-008's measured
    budget. `date_range` and `ranking` are both explicit parameters here, not derived
    from the question inside this function - callers (T-023, or Phase 3's evaluation
    script) decide those via `vg09.date_range.resolve_date_range()`/
    `detect_recency_ranking()`, or override them directly for a "plain retrieval"
    comparison run."""
    candidates = query_candidates(question, date_range, n_results, source=source)
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
        candidates_after_dedup=len(deduped),
    )
