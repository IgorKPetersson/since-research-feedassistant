# Session tree · 2026-09-20 · T-028 close-out, Phase 2 grill-me, T-029/T-030, Phase 2 closed

**Tickets:** T-028, T-029, T-030 · **Handoff:** docs/HANDOFF.md § 2026-09-20
**Read this if you want to know:** why D-011 was replaced by D-012, what grill-me actually
found in Phase 2's code, or why the system prompt now pins the answer's language.

## 1. Resuming T-028's last open criterion  [T-028]
   - 1.1 Re-read HANDOFF/PLAN/TICKETS to find where the project stood
     · outcome: T-028's chunk-budget-impact re-check was the one open item, with exact
       resume instructions already written in its own ticket Notes
   - 1.2 Built `scripts/t028_verify_chunk_budget_impact.py`, real run against the
     production store/Ollama, `today=2026-09-17`
     · outcome: packed chunk count dropped 1-2 on 5/15 broad/unfiltered questions; **top-5
       unchanged on all 15 of 15**, confirmed directly, not assumed. T-027's F15/F06
       checkpoints reproduced exactly. 11/14 headline holds
   - 1.3 User asked to verify the background run was actually progressing, not hung
     · outcome: confirmed via a live TCP connection to Ollama's port and accumulated CPU
       time on both processes — not by polling the (buffered, empty until exit) log file
   - 1.4 T-028 closed: ticket updated, `docs/PLAN.md` updated, committed (`4edf310`)

## 2. Phase 2 `grill-me`  [none — a review, not a ticket]
   - 2.1 Read `vg09/llm.py`, `answer.py`, `citations.py`, `app.py`, `store.py`,
     `date_range.py`, `retrieval.py` and their tests in full, against Mode 1's checklist
   - 2.2 Found: D-011's text ("pin eval to 2026-09-16") was never actually followed by
     T-027's or T-028's real re-runs (both used 2026-09-17) — and would, if followed
     literally, re-exclude `YTG0rdHPTDE`, the exact case D-011 exists to prevent
     · outcome: reported as the top finding — reality (the practice) was right, the
       decision log was wrong, per `CLAUDE.md`'s own flag-don't-silently-adapt rule
   - 2.3 Found: `generate_answer()` had no `raise_for_status()`, unlike `embed_batch()`
     · outcome: reported as Serious — real Ollama failures would surface as an opaque
       `KeyError`, not a diagnosable error, in the single most-exercised code path
   - 2.4 Found (Minor): `app.py` hand-rolls T-021's override precedence instead of calling
     `resolve_date_range(..., manual_override=...)`; real titles unescaped in markdown
     links; `latest_feed_date()` scanned up to twice per interaction
     · outcome: all reported, none fixed yet (review only)

## 3. T-029 — fixing what grill-me found  [T-029]
   - 3.1 Ticket written bundling all four fixes as one
     (fifth finding scoped out to the risk register only)
   - 3.2 D-011 marked `superseded by D-012`, original text kept intact (not deleted)
   - 3.3 D-012 written: one anchor (`latest_feed_date()`) for production and evaluation
     alike
     · outcome: a real, honest residual gap found while writing this, not smoothed over —
       a single anchor can't reproduce every individually-written HF-only facit window
       exactly (one day off), harmless for this frozen dataset specifically (confirmed:
       HIT/MISS outcomes unaffected) but recorded as a real mismatch, not a coincidence
   - 3.4 `docs/eval-questions.md`'s anchor callout rewritten to match; facit content
     (F01-F15) verified untouched via `git diff`
   - 3.5 `raise_for_status()` added to `generate_answer()`
     · outcome: **self-correction** — the grill-me finding was wrong about
       `count_qwen_tokens()`, which already had it since T-022; only `generate_answer()`
       was actually missing it. Corrected in the ticket's own Notes rather than left
       standing
   - 3.6 `app.py` wrapped in `try/except requests.exceptions.RequestException`, clear
     Swedish error message; switched to calling `resolve_date_range(...,
     manual_override=manual_range)` directly
   - 3.7 `vg09.ui_helpers.escape_markdown_link_text()` added, tested against a real title
     ("He Built The Ultimate Spy Tool (Free and Open-Source)") and a synthetic
     `[SOTA]`-shaped one for the actually-dangerous character
     · outcome: the real title's parens turned out not to be the dangerous character
       under CommonMark (only `]`/`[`/backslash are) — noted honestly rather than
       overclaiming the real example proved more than it did
   - 3.8 110/110 tests pass; committed (`1b7dd27`)

## 4. T-030 — the English-answer language decision  [T-030]
   - 4.1 Decision: answers always in English regardless of question language,
     for OSS/international usability; questions keep working in any language (bge-m3,
     T-006/D-005)
   - 4.2 Ticket written, D-013 recorded (with the rejected "mirror the question's
     language" alternative and its cost)
     · outcome: caught and corrected an overclaim mid-write — "docs/GOAL.md's explicit
       'usable internationally' framing" doesn't actually exist in GOAL.md; reattributed
       to the decision itself instead of misciting the doc
   - 4.3 `SYSTEM_PROMPT` line added; real token re-measurement: **173** (was 157, +16)
     · outcome: `CHUNK_BUDGET_TOKENS` 13261 → 13245; max top-k unchanged at 33 (same
       400-token band); `docs/DESIGN.md` updated to match
   - 4.4 Unit test added (`SystemPromptTests`); real end-to-end verification
     (`scripts/t030_verify_english_answer.py`) — two real Swedish questions against the
     real store/Ollama, both produced English answers
     · outcome: done, 111/111 tests pass, committed (`0d7a3c0`)

## 5. Phase 2 declared complete  [none — a plan-level decision]
   - 5.1 `docs/PLAN.md`'s "Current phase" block rewritten: all tickets done, `grill-me` run
     and every finding triaged/fixed (T-029) or deferred to the risk register, T-030 landed
     · outcome: declared complete. Phase 3 **not** started yet
