"""T-008: measure the real context budget for the RAG prompt.

Everything here is measured against the real, already-pulled models via Ollama
(D-005: qwen3:30b-a3b at num_ctx=16000, bge-m3 for embeddings) - never
estimated from words or characters, per explicit instruction. Two separate
tokenizers matter for two separate reasons:

- qwen3's tokenizer governs the actual `num_ctx=16000` budget: system prompt +
  retrieved chunks + question + generated reasoning/answer all share it
  (no conversation history - GOAL.md non-goal).
- bge-m3's tokenizer governs what fits in one embeddable chunk (its own
  context window is 8192 tokens, KB-007) - a real chunk's *qwen3* token cost
  can differ from its bge-m3 token cost, so both are measured on the same real
  text rather than assumed equal.

Context material is real HF Daily Papers abstracts already in data/raw/ (from
T-009's verification run) - not synthetic filler.

Makes real network calls to a local Ollama server; run it manually.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

OLLAMA = "http://localhost:11434"
CHAT_MODEL = "qwen3:30b-a3b"
EMBED_MODEL = "bge-m3"
NUM_CTX = 16000
EMBED_NUM_CTX = 8192  # bge-m3's own context window, per KB-007 - never left implicit
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_HF_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "hf" / "2026-09-16"

SYSTEM_PROMPT = """You are a research-feed assistant. You answer questions about Hugging Face Daily Papers and a set of YouTube channels the user follows, using ONLY the source excerpts provided below - never information from outside them or your own prior knowledge. If the sources don't contain the answer, say so plainly instead of guessing.

For every claim, cite the source: title, URL, and feed date (the date it appeared in the watched feed - not necessarily its original publish date). Cite inline like [Title, YYYY-MM-DD].

If the question implies a time range ("this week", "last month", "since Tuesday"), only use sources whose feed date falls inside that range, and say so plainly if none match.

Be concise. Synthesize an answer from the sources; do not just repeat them verbatim."""


def load_abstracts() -> dict[str, dict]:
    papers = {}
    for path in sorted(RAW_HF_DIR.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        papers[d["id"]] = d
    return papers


def format_source(doc: dict, n: int) -> str:
    return f"[{n}] {doc['title']} ({doc['url']}, feed date {doc['feed_date']})\n{doc['text']}"


def _warn_if_truncation_risk(label: str, prompt_eval_count: int, num_ctx: int) -> None:
    """project hard rule: every call compares prompt_eval_count against the
    num_ctx that was sent. KB-005: an undersized num_ctx silently drops the
    FRONT of the prompt with no error - prompt_eval_count landing at or near
    num_ctx is the only signal that happened."""
    if prompt_eval_count >= num_ctx:
        print(f"  !! TRUNCATION RISK: {label} prompt_eval_count={prompt_eval_count} >= num_ctx={num_ctx}")
    elif prompt_eval_count >= 0.9 * num_ctx:
        print(f"  !! close to num_ctx: {label} prompt_eval_count={prompt_eval_count} "
              f"({100 * prompt_eval_count / num_ctx:.0f}% of num_ctx={num_ctx})")


def count_qwen_tokens(text: str) -> int:
    """Real qwen3 tokenizer count for `text` alone, via a minimal-cost call -
    prompt_eval_count reflects the prompt as tokenized, independent of how
    much (if anything) gets generated afterward.

    Uses num_predict=1, not 0: a smoke test found num_predict=0 does NOT mean
    "generate nothing" (it ran a full, unbounded generation - 485 tokens on a
    9-word prompt); num_predict=1 correctly caps it to one generated token
    while prompt_eval_count stays identical either way. See KB-009.
    """
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
    _warn_if_truncation_risk("count_qwen_tokens", count, NUM_CTX)
    return count


def count_bge_tokens(text: str) -> int:
    resp = requests.post(
        f"{OLLAMA}/api/embed",
        json={
            "model": EMBED_MODEL,
            "input": text,
            "options": {"num_ctx": EMBED_NUM_CTX},
        },
        timeout=120,
    )
    resp.raise_for_status()
    body = resp.json()
    count = body.get("prompt_eval_count")
    _warn_if_truncation_risk("count_bge_tokens", count, EMBED_NUM_CTX)
    return count


def generate(prompt: str, think: bool, num_predict: int) -> dict:
    resp = requests.post(
        f"{OLLAMA}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": think,
            "options": {"num_ctx": NUM_CTX, "num_predict": num_predict},
        },
        timeout=600,
    )
    resp.raise_for_status()
    body = resp.json()
    _warn_if_truncation_risk("generate", body.get("prompt_eval_count", 0), NUM_CTX)
    return body


def build_prompt(question: str, sources: list[dict]) -> tuple[str, list[str]]:
    numbered = [format_source(doc, i + 1) for i, doc in enumerate(sources)]
    prompt = (
        f"{SYSTEM_PROMPT}\n\nSources:\n\n" + "\n\n".join(numbered) +
        f"\n\nQuestion: {question}"
    )
    return prompt, numbered


def main() -> None:
    papers = load_abstracts()
    results: dict = {"run_at": datetime.now(timezone.utc).isoformat(), "num_ctx": NUM_CTX}

    # 1. System prompt and representative questions, alone, under qwen3's tokenizer.
    results["system_prompt_tokens"] = count_qwen_tokens(SYSTEM_PROMPT)
    print(f"system_prompt_tokens = {results['system_prompt_tokens']}")

    questions = [
        (
            "whats_new",
            "What's new in AI research this week?",
            ["2609.16679", "2609.17521", "2609.14005", "2609.16034", "2609.15195"],
        ),
        (
            "did_x_come_up",
            "Did anyone work on continual learning or catastrophic forgetting recently?",
            ["2609.06986", "2609.13680", "2609.15975", "2609.16204"],
        ),
        (
            "progress_over_weeks",
            "How has work on recursive self-improvement progressed recently?",
            ["2609.11873", "2609.14857", "2609.17523", "2609.13770"],
        ),
    ]

    results["questions"] = {}
    for key, question, paper_ids in questions:
        sources = [papers[pid] for pid in paper_ids if pid in papers]
        prompt, numbered = build_prompt(question, sources)
        q_tokens = count_qwen_tokens(question)
        prompt_tokens = count_qwen_tokens(prompt)

        print(f"\n== {key} ==")
        print(f"  question_tokens={q_tokens}  full_prompt_tokens={prompt_tokens}  n_sources={len(sources)}")

        gen = generate(prompt, think=True, num_predict=-1)
        thinking = gen.get("thinking", "") or ""
        response = gen.get("response", "") or ""
        entry = {
            "question": question,
            "paper_ids": paper_ids,
            "question_tokens": q_tokens,
            "prompt_tokens_reported": prompt_tokens,
            "prompt_eval_count": gen.get("prompt_eval_count"),
            "eval_count": gen.get("eval_count"),
            "thinking_chars": len(thinking),
            "response_chars": len(response),
            "done_reason": gen.get("done_reason"),
        }
        results["questions"][key] = entry
        print(f"  prompt_eval_count={entry['prompt_eval_count']}  eval_count={entry['eval_count']}"
              f"  thinking_chars={entry['thinking_chars']}  response_chars={entry['response_chars']}"
              f"  done_reason={entry['done_reason']}")

    # 2. Per-source token cost under BOTH tokenizers, on every real abstract
    #    available (not just the ones used above) - gives a real distribution
    #    to base chunk-size/top-k on, not a single sample.
    results["per_source"] = []
    for pid, doc in papers.items():
        text = doc["text"]
        qwen_t = count_qwen_tokens(text)
        bge_t = count_bge_tokens(text)
        results["per_source"].append(
            {"id": pid, "chars": len(text), "qwen_tokens": qwen_t, "bge_tokens": bge_t}
        )
    counts_qwen = [r["qwen_tokens"] for r in results["per_source"]]
    counts_bge = [r["bge_tokens"] for r in results["per_source"]]
    print(f"\n== per-source token cost across {len(counts_qwen)} real abstracts ==")
    print(f"  qwen3 tokens: min={min(counts_qwen)} median={sorted(counts_qwen)[len(counts_qwen)//2]} "
          f"max={max(counts_qwen)} mean={sum(counts_qwen)/len(counts_qwen):.0f}")
    print(f"  bge-m3 tokens: min={min(counts_bge)} median={sorted(counts_bge)[len(counts_bge)//2]} "
          f"max={max(counts_bge)} mean={sum(counts_bge)/len(counts_bge):.0f}")

    out_path = DATA_DIR / "t008_context_budget.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
