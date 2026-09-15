"""T-006 part 2: verify the new model stack (qwen3:8b + qwen3:30b-a3b + bge-m3).

1. Compare qwen3:30b-a3b response time with think mode on (default) vs off.
2. Test bge-m3 cross-lingual retrieval: a Swedish question embedded and
   compared against English candidate sentences, confirming the closest
   match is topically right despite the language mismatch.

Makes real local calls; run it manually, it is not a test.
"""

import json
import time
from pathlib import Path

import numpy as np
import requests

OLLAMA_URL = "http://localhost:11434/api"
LARGE_MODEL = "qwen3:30b-a3b"
EMBED_MODEL = "bge-m3"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

QUESTION = "What causes rain?"


def ask(think: bool) -> dict:
    start = time.monotonic()
    resp = requests.post(
        f"{OLLAMA_URL}/generate",
        json={
            "model": LARGE_MODEL,
            "prompt": QUESTION,
            "stream": False,
            "think": think,
            "options": {"num_ctx": 16000},
        },
        timeout=300,
    )
    elapsed = time.monotonic() - start
    resp.raise_for_status()
    body = resp.json()
    return {
        "elapsed_s": elapsed,
        "response": body.get("response", ""),
        "thinking": body.get("thinking", None),
        "eval_count": body.get("eval_count"),
    }


def embed(texts: list[str]) -> np.ndarray:
    resp = requests.post(f"{OLLAMA_URL}/embed", json={"model": EMBED_MODEL, "input": texts}, timeout=60)
    resp.raise_for_status()
    return np.array(resp.json()["embeddings"])


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    results = {}

    for label, think in [("think_default_on", True), ("think_off", False)]:
        print(f"== {label} ==")
        r = ask(think)
        results[label] = r
        print(f"  time: {r['elapsed_s']:.1f}s  eval_count: {r['eval_count']}")
        print(f"  thinking: {(r['thinking'] or '')[:150]!r}")
        print(f"  response: {r['response'][:200]!r}")

    # Cross-lingual retrieval: Swedish question against English candidates.
    swedish_query = "Vad orsakar regn?"  # "What causes rain?"
    candidates = [
        "Rain forms when water vapor in clouds condenses into droplets that become too heavy to stay airborne.",
        "The stock market fluctuates based on investor sentiment and economic indicators.",
        "Cats are popular pets known for their independence and agility.",
        "A new machine learning paper proposes a faster attention mechanism for transformers.",
    ]
    query_emb = embed([swedish_query])[0]
    cand_embs = embed(candidates)
    sims = [cosine(query_emb, c) for c in cand_embs]
    ranked = sorted(zip(candidates, sims), key=lambda x: -x[1])

    print("\nCross-lingual retrieval (Swedish query vs English candidates):")
    for text, sim in ranked:
        print(f"  {sim:.4f}  {text[:70]!r}")

    top_is_rain = ranked[0][0].startswith("Rain forms")
    print(f"\nTop match is the rain sentence: {top_is_rain}")

    results["cross_lingual"] = {
        "query": swedish_query,
        "ranked": [{"text": t, "cosine": s} for t, s in ranked],
        "top_match_correct": top_is_rain,
    }

    out_path = DATA_DIR / "t006_model_stack.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
