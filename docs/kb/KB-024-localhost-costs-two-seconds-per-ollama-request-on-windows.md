# KB-024 — Addressing Ollama as `localhost` costs about 2 seconds per request on Windows; `127.0.0.1` does not

**Area:** Local model (Ollama) — request latency
**Status:** verified
**Date:** 2026-10-02  ·  **From:** T-049

## Claim
On this Windows machine every HTTP request to `http://localhost:11434` takes about 2
seconds longer than the same request to `http://127.0.0.1:11434`. `localhost` is tried
over IPv6 (`::1`) first, Ollama listens on IPv4 only, and the client waits for that
attempt to give up before falling back. This is the whole cause of KB-023's 40–100s
retrieval: retrieval makes about 30 separate requests per question.

## Evidence
`scripts/t049_time_retrieval_steps.py`, same question, same store, both models loaded
throughout (checked via `/api/ps` after every step, so model unloading is ruled out):

| Step | `localhost` | `127.0.0.1` |
|---|---|---|
| one `embed_batch()` call | 2.09s | 0.05s |
| one `count_qwen_tokens()` call | 2.11–2.73s | 0.05–0.17s |
| whole `retrieve()` | 68.56s | 1.36s |

Both runs packed the same 29 chunks, 11444 tokens. After changing the constants, a
third run measured `retrieve()` at 1.17s. An earlier session had already seen the
symptom without recognising it: a connection from the Python process to `::1` port
11434 sitting in state `SynSent`.

## Consequences
`vg09.store.OLLAMA`, `vg09.retrieval.OLLAMA` and `vg09.answer.OLLAMA` are now
`http://127.0.0.1:11434`; `tests/test_store.py::OllamaAddressTests` asserts all three.
Every wall-clock time recorded before 2026-10-02 includes this overhead: the harness
runs, T-038's "7.7–18.4s" generation times (about 2s each too high), and T-033's finding
that the smaller model was slower on average (the overhead was the same for both models,
so the comparison between them still holds). The old feasibility scripts under
`scripts/` still say `localhost`; they are records of past runs and were left as they are.

## Confidence and limits
Measured on one Windows 11 machine with Ollama 0.34.x. The IPv6-first explanation fits
the `SynSent` observation and the fixed 2-second cost, but the resolver's behaviour was
not inspected directly. On a machine where Ollama also listens on `::1`, `localhost`
would not show this cost.
