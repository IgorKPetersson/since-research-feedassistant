"""Smoke test before the full T-008 run: confirm /api/embed returns a token
count for bge-m3, and that num_predict=0 still returns prompt_eval_count for
qwen3."""

import requests

OLLAMA = "http://localhost:11434"

r1 = requests.post(
    f"{OLLAMA}/api/generate",
    json={
        "model": "qwen3:30b-a3b",
        "prompt": "The quick brown fox jumps over the lazy dog.",
        "stream": False,
        "options": {"num_ctx": 16000, "num_predict": 1},
    },
    timeout=60,
)
print("generate num_predict=1 status:", r1.status_code)
body1 = r1.json()
print("keys:", sorted(body1.keys()))
print("prompt_eval_count:", body1.get("prompt_eval_count"))
print("eval_count:", body1.get("eval_count"))
print("response repr (first 80 chars):", repr(body1.get("response", ""))[:80])

r2 = requests.post(
    f"{OLLAMA}/api/embed",
    json={
        "model": "bge-m3",
        "input": "The quick brown fox jumps over the lazy dog.",
        "options": {"num_ctx": 8192},  # bge-m3's own context window, per KB-007
    },
    timeout=60,
)
print("\nembed status:", r2.status_code)
body2 = r2.json()
print("keys:", sorted(body2.keys()))
print("prompt_eval_count:", body2.get("prompt_eval_count"))
