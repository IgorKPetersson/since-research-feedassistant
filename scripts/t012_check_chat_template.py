"""Check whether /api/chat's chat template always renders the system message
first, regardless of its position in the `messages` array - relevant to
Phase 2's answer-generation prompt structure (docs/DESIGN.md).

No YouTube calls; Ollama only."""

import requests

resp = requests.post(
    "http://localhost:11434/api/show",
    json={"model": "qwen3:30b-a3b"},
    timeout=30,
)
resp.raise_for_status()
body = resp.json()
print("template:\n")
print(body.get("template"))
