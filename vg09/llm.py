"""T-011: separate Qwen3's reasoning (chain-of-thought) from its final answer.

KB-007, verified against real /api/generate AND /api/chat calls: `think:false` does
NOT suppress reasoning - it leaves `thinking` empty and merges the chain-of-thought
narrative straight into `content` instead (the real `content` in that case opens with
visible reasoning: "Okay, the user is asking..."). The only clean way to get an
answer-only string is `think:true`, reading `thinking` and `content` back as two
separate fields - there is no reliable way to strip merged reasoning back out of
`content` after the fact, so this refuses rather than guessing.
"""

from __future__ import annotations


def split_reasoning_and_answer(response: dict) -> tuple[str, str]:
    """`response` is a raw Ollama `/api/chat` response dict. Returns
    `(reasoning, answer)`. Requires the call to have been made with `think=True` -
    raises if `message["thinking"]` is empty, which is exactly the real, observed
    signature of a `think=False` call (KB-007) rather than a hypothetical one."""
    message = response["message"]
    thinking = message.get("thinking", "")
    content = message["content"]
    if not thinking:
        raise ValueError(
            "response.message['thinking'] is empty - this requires a call made with "
            "think=True (KB-007: think=False leaves 'thinking' empty and merges the "
            "reasoning narrative into 'content' instead, with no other signal that "
            "happened - never call the chat model with think=False)"
        )
    return thinking, content
