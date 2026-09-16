# KB-011 — Ollama's chat template for `qwen3:30b-a3b` always renders the system message first, regardless of its position in the `messages` array

**Area:** Local model (Ollama) — `/api/chat` message rendering
**Status:** verified
**Date:** 2026-09-16  ·  **From:** T-012

## Claim
`/api/chat`'s rendered prompt always places the system block
(`<|im_start|>system ... <|im_end|>`) first, before any other message, regardless of where a
`{"role": "system", ...}` message appears in the `messages` array passed to the API. Ollama
extracts system-role content into a separate `.System` template variable at request time,
independent of message order; the Go chat template then unconditionally renders `.System`
before iterating `.Messages`. Message *order* in the API call therefore does not control
rendered prompt order the way building a raw string for `/api/generate` does.

## Evidence
`scripts/t012_check_chat_template.py`: `POST /api/show` with `{"model": "qwen3:30b-a3b"}`,
reading the real `template` field. Relevant excerpt:

```
{{- if or .System .Tools }}<|im_start|>system
{{ if .System }}{{ .System }}
...
<|im_end|>
{{ end }}
{{- range $i, $_ := .Messages }}
...
```

The system block's `if`/render happens before the `range` over `.Messages` unconditionally -
not inside a branch that depends on message order. This is the actual Go template Ollama
uses for this model, not inferred from generation behavior.

## Consequences
For Phase 2's answer-generation design (`docs/DESIGN.md` § Answer generation): the system
prompt should go in its own `{"role": "system", ...}` message (matches `/api/chat`'s
intended usage) rather than being concatenated into the user message's content - but doing
so means the system prompt is *always* the first thing in the rendered prompt, with no way
to reorder it by rearranging the `messages` array. This is a real change from T-008's
raw-`/api/generate` string-concatenation experiment, where prompt order was fully controlled
by literal string order and the system prompt could deliberately be placed *last* as a
defense against KB-005's front-truncation. Under `/api/chat`, that specific mitigation
doesn't transfer: if front-truncation ever fires, it eats the system prompt first, not the
retrieved chunks. The token-budget packing (T-008/T-012, keeping the assembled prompt safely
under `num_ctx`) becomes the primary defense once `/api/chat` is used, not prompt ordering.

## Confidence and limits
Checked for one model (`qwen3:30b-a3b`) via its own `/api/show` template. Not checked:
whether `qwen3:8b` uses an identical template (likely, same family, not confirmed), whether
this holds across an Ollama version upgrade, or whether a multi-turn conversation (multiple
user/assistant messages) changes anything about where `.System` renders (conversation
history is a `docs/GOAL.md` non-goal for v1, so this wasn't exercised).
