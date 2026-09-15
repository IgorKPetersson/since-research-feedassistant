"""T-004: local model feasibility test on the RTX 4090 (Ollama).

For each of a large (~30B class, quantized) and small (~8B) model, sends
one question with pasted context to Ollama's REST API, and records wall
time and peak GPU memory (via nvidia-smi) around the call.

Requires `ollama serve` already running (http://localhost:11434) and the
models already pulled: `ollama pull llama3.1:8b`, `ollama pull qwen2.5:32b`.
Makes real local calls; run it manually, it is not a test.
"""

import json
import subprocess
import threading
import time
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELS = {
    "small_8b": "llama3.1:8b",
    "large_30b_class": "qwen2.5:32b",
}

CONTEXT = """\
The HF Daily Papers API endpoint /api/daily_papers?date=YYYY-MM-DD returns a
list of entries. Each entry has a top-level `publishedAt` field, but that is
the paper's original arXiv publication date, not the date the query matched
on. The field that actually matches the query date is `paper.submittedOnDailyAt`.
The arXiv id is at `paper.id`, not at the entry's top level.
"""

QUESTION = "Which field should I filter on if I want papers that appeared in the feed on a specific date, and where does the arXiv id live?"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def peak_vram_mb_during(fn) -> tuple[float, dict]:
    """Run fn() while polling nvidia-smi in the background; return (peak_mb, fn_result)."""
    peak = {"mb": 0.0}
    poll_ok = {"any_success": False, "last_error": None}
    stop = threading.Event()

    def poll():
        while not stop.is_set():
            try:
                out = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    text=True,
                    timeout=5,
                )
                mb = float(out.strip().splitlines()[0])
                peak["mb"] = max(peak["mb"], mb)
                poll_ok["any_success"] = True
            except Exception as exc:
                poll_ok["last_error"] = f"{type(exc).__name__}: {exc}"
            time.sleep(0.5)

    t = threading.Thread(target=poll, daemon=True)
    t.start()
    result = fn()
    stop.set()
    t.join(timeout=2)
    if not poll_ok["any_success"]:
        print(f"  WARNING: nvidia-smi polling never succeeded ({poll_ok['last_error']}); "
              f"peak VRAM reading of {peak['mb']:.0f} MB is not real data")
    return peak["mb"], result


def ask(model: str) -> dict:
    prompt = f"{CONTEXT}\n\nQuestion: {QUESTION}"
    start = time.monotonic()
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=600,
    )
    elapsed = time.monotonic() - start
    resp.raise_for_status()
    body = resp.json()
    return {"elapsed_s": elapsed, "response": body.get("response", ""), "raw": body}


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    results = {}
    for label, model in MODELS.items():
        print(f"== {label} ({model}) ==")
        peak_mb, result = peak_vram_mb_during(lambda m=model: ask(m))
        results[label] = {
            "model": model,
            "elapsed_s": result["elapsed_s"],
            "peak_vram_mb": peak_mb,
            "response": result["response"],
        }
        print(f"  time: {result['elapsed_s']:.1f}s  peak VRAM: {peak_mb:.0f} MB")
        print(f"  response: {result['response'][:300]!r}")

    out_path = DATA_DIR / "t004_local_model.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
