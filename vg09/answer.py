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
NUM_PREDICT = 2000  # docs/DESIGN.md's measured reasoning+answer reservation (T-008) -
# a real ceiling enforced via this call, not just a budget estimate

# T-008's representative system prompt (scripts/t008_context_budget.py, measured at
# 171 qwen3 tokens) - already accounts for citing sources and respecting an implied
# time range; adopted as-is rather than redrafted, since nothing found during Phase 2
# gave a reason to change it.
SYSTEM_PROMPT = """You are a research-feed assistant. You answer questions about Hugging Face Daily Papers and a set of YouTube channels the user follows, using ONLY the source excerpts provided below - never information from outside them or your own prior knowledge. If the sources don't contain the answer, say so plainly instead of guessing.

For every claim, cite the source: title, URL, and feed date (the date it appeared in the watched feed - not necessarily its original publish date). Cite inline like [Title, YYYY-MM-DD].

If the question implies a time range ("this week", "last month", "since Tuesday"), only use sources whose feed date falls inside that range, and say so plainly if none match.

Be concise. Synthesize an answer from the sources; do not just repeat them verbatim."""


@dataclass
class AnswerResult:
    reasoning: str
    answer: str
    done_reason: str
    incomplete: bool  # True iff done_reason == "length" - a genuinely cut-off answer
    prompt_eval_count: int


def _format_source(c: Candidate, n: int) -> str:
    m = c.metadata
    return f"[{n}] {m['title']} ({m['url']}, feed date {m['feed_date']})\n{c.text}"


def build_user_message(question: str, chunks: list[Candidate]) -> str:
    """Chunks are expected in relevance/recency-descending order (T-022's own output
    order) - reversed here to least-relevant-first before the question, per
    docs/DESIGN.md's defense-in-depth ordering (KB-005: if packing ever has a bug and
    the assembled prompt overflows, the casualty should be the least relevant source,
    not the question). Empty `chunks` produces an honest "no sources" note rather than
    a special-cased response - the system prompt's own instruction ("say so plainly")
    handles a query with nothing relevant retrieved."""
    if not chunks:
        sources_block = "(No sources were retrieved for this question.)"
    else:
        least_relevant_first = list(reversed(chunks))
        sources_block = "\n\n".join(
            _format_source(c, n) for n, c in enumerate(least_relevant_first, start=1)
        )
    return f"Sources:\n\n{sources_block}\n\nQuestion: {question}"


def generate_answer(question: str, chunks: list[Candidate]) -> AnswerResult:
    """The real `/api/chat` call. `think=True` always - never `False` (T-011/KB-007:
    `False` merges reasoning into the answer text with no way to cleanly split it back
    out). Checks `done_reason` (a real "length" result is flagged as incomplete, not
    silently presented as finished) and `prompt_eval_count` against `num_ctx`
    (CLAUDE.md's hard rule) on every real call."""
    resp = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(question, chunks)},
            ],
            "stream": False,
            "think": True,
            "options": {"num_ctx": NUM_CTX, "num_predict": NUM_PREDICT},
        },
        timeout=300,
    ).json()

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
    )
