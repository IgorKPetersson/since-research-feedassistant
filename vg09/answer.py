"""T-023: the real answer-generation call - a packed set of chunks (T-022/T-027) plus
the question, in one real `qwen3:30b-a3b` `/api/chat` call, following exactly what
T-008/KB-011 already measured and specified.

Message structure (docs/DESIGN.md § "Answer generation"): the system prompt is its own
`{"role": "system", ...}` message; the packed chunks and the question go together in
one `{"role": "user", ...}` message. KB-011's real chat-template finding means message
*order* in the API call does not control *rendered* prompt order once `/api/chat` is
used (the system block always renders first, regardless) - so ordering chunks
least-relevant-first *inside* the user message is defense-in-depth, not the primary
truncation safeguard (T-022's token-budget packing is).
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from vg09.llm import split_reasoning_and_answer
from vg09.retrieval import CHAT_MODEL, NUM_CTX, Candidate

OLLAMA = "http://localhost:11434"
# T-028: raised from 2000 after a real truncation I found (done_reason=="length")
# on "Vad har hänt med AI-agenter senaste veckan?". Three real re-runs of that exact
# question (same retrieved context, only sampling varied) measured reasoning alone at
# 1230/1842/1349 qwen tokens (61.5%/92.1%/67.5% of the old 2000 cap) - reasoning, not
# the answer, was eating the budget. New value derived from that measurement, not a
# round number: 1842 (worst observed reasoning) + 400 (room for a full answer - real
# complete answers measured 176-322 tokens) + 300 (margin - roughly half the 612-token
# spread already observed across just three samples, hedging against further variance
# without inflating the chunk budget more than three data points can justify) = 2542.
# docs/DESIGN.md's budget math and CHUNK_BUDGET_TOKENS updated to match (13261, down
# from 13803 - this reservation now costs 542 more tokens against the chunk budget).
NUM_PREDICT = 2542

# T-008's representative system prompt (scripts/t008_context_budget.py), with one
# change (T-024): the citation instruction asked for [Title, YYYY-MM-DD] inline, but
# a real end-to-end run (T-023) found the model doesn't follow that - it cites the
# bracketed *source number* shown in the prompt instead ("source [27]"), matching the
# numbering `number_sources()` already assigns for the prompt's own sake. Rather than
# fighting that, the instruction now asks for exactly what it already does -
# T-024 resolves those numbers back to real citations (vg09/citations.py). Re-measured
# after this change: 157 qwen3 tokens (was 171) - docs/DESIGN.md's budget math and
# CHUNK_BUDGET_TOKENS updated to match (13803, up from 13789 - more headroom, the safe
# direction).
SYSTEM_PROMPT = """You are a research-feed assistant. You answer questions about Hugging Face Daily Papers and a set of YouTube channels the user follows, using ONLY the source excerpts provided below - never information from outside them or your own prior knowledge. If the sources don't contain the answer, say so plainly instead of guessing.

For every claim, cite the source using the bracketed number shown before it, like [3] - do not invent a different citation format.

If the question implies a time range ("this week", "last month", "since Tuesday"), only use sources whose feed date falls inside that range, and say so plainly if none match.

Be concise. Synthesize an answer from the sources; do not just repeat them verbatim."""


@dataclass
class AnswerResult:
    reasoning: str
    answer: str
    done_reason: str
    incomplete: bool  # True iff done_reason == "length" - a genuinely cut-off answer
    prompt_eval_count: int
    source_map: dict[int, Candidate]  # T-024: the exact number -> chunk mapping shown
    # in the prompt, so the model's own positional citations ("source [27]") can be
    # resolved back to a real chunk after the call


def number_sources(chunks: list[Candidate]) -> dict[int, Candidate]:
    """Chunks are expected in relevance/recency-descending order (T-022's own output
    order) - reversed here to least-relevant-first, per docs/DESIGN.md's
    defense-in-depth ordering (KB-005: if packing ever has a bug and the assembled
    prompt overflows, the casualty should be the least relevant source, not the
    question), then numbered 1..N in that order. This is the *only* place source
    numbering happens - both the prompt (`build_user_message`) and the citation
    resolution after the call (`vg09.citations`) use this same mapping, so a number
    always means the same chunk on both ends."""
    least_relevant_first = list(reversed(chunks))
    return {n: c for n, c in enumerate(least_relevant_first, start=1)}


def _format_source(c: Candidate, n: int) -> str:
    m = c.metadata
    return f"[{n}] {m['title']} ({m['url']}, feed date {m['feed_date']})\n{c.text}"


def build_user_message(question: str, source_map: dict[int, Candidate]) -> str:
    """Empty `source_map` produces an honest "no sources" note rather than a
    special-cased response - the system prompt's own instruction ("say so plainly")
    handles a query with nothing relevant retrieved."""
    if not source_map:
        sources_block = "(No sources were retrieved for this question.)"
    else:
        sources_block = "\n\n".join(_format_source(c, n) for n, c in source_map.items())
    return f"Sources:\n\n{sources_block}\n\nQuestion: {question}"


def generate_answer(question: str, chunks: list[Candidate]) -> AnswerResult:
    """The real `/api/chat` call. `think=True` always - never `False` (T-011/KB-007:
    `False` merges reasoning into the answer text with no way to cleanly split it back
    out). Checks `done_reason` (a real "length" result is flagged as incomplete, not
    silently presented as finished) and `prompt_eval_count` against `num_ctx`
    (CLAUDE.md's hard rule) on every real call. Returns the number -> chunk mapping
    used in the prompt (T-024), so the model's own positional citations can be
    resolved afterward."""
    source_map = number_sources(chunks)
    http_resp = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(question, source_map)},
            ],
            "stream": False,
            "think": True,
            "options": {"num_ctx": NUM_CTX, "num_predict": NUM_PREDICT},
        },
        timeout=300,
    )
    # T-029: a non-2xx Ollama response (model not pulled, OOM, ...) must fail loudly
    # here, not surface later as an opaque KeyError from reading a partial/error body.
    http_resp.raise_for_status()
    resp = http_resp.json()

    prompt_eval_count = resp.get("prompt_eval_count", 0)
    if prompt_eval_count >= NUM_CTX:
        print(f"  !! TRUNCATION RISK: generate_answer prompt_eval_count={prompt_eval_count} "
              f">= num_ctx={NUM_CTX}")
    elif prompt_eval_count >= 0.9 * NUM_CTX:
        print(f"  !! close to num_ctx: generate_answer prompt_eval_count={prompt_eval_count} "
              f"({100 * prompt_eval_count / NUM_CTX:.0f}% of num_ctx={NUM_CTX})")

    reasoning, answer = split_reasoning_and_answer(resp)
    done_reason = resp.get("done_reason", "")

    return AnswerResult(
        reasoning=reasoning,
        answer=answer,
        done_reason=done_reason,
        incomplete=(done_reason == "length"),
        prompt_eval_count=prompt_eval_count,
        source_map=source_map,
    )
