# Session tree · 2026-09-20 · T-028 close-out, Phase 2 adversarial review, T-029/T-030, Phase 2 closed, Phase 3 opened and T-031/T-038/T-032 run

**Tickets:** T-028, T-029, T-030, T-031, T-037, T-038, T-032 · **Handoff:** docs/HANDOFF.md
§ 2026-09-20
**Read this if you want to know:** why D-011 was replaced by D-012, what adversarial review actually
found in Phase 2's code, why the system prompt now pins the answer's language, why the
packing budget silently undercounted every real prompt since T-008, or where the real
evaluation results live.

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

## 2. Phase 2 adversarial review  [none — a review, not a ticket]
   - 2.1 Read `vg09/llm.py`, `answer.py`, `citations.py`, `app.py`, `store.py`,
     `date_range.py`, `retrieval.py` and their tests in full, against Mode 1's checklist
   - 2.2 Found: D-011's text ("pin eval to 2026-09-16") was never actually followed by
     T-027's or T-028's real re-runs (both used 2026-09-17) — and would, if followed
     literally, re-exclude `YTG0rdHPTDE`, the exact case D-011 exists to prevent
     · outcome: reported as the top finding — reality (the practice) was right, the
       decision log was wrong, per the project's own flag-don't-silently-adapt rule
   - 2.3 Found: `generate_answer()` had no `raise_for_status()`, unlike `embed_batch()`
     · outcome: reported as Serious — real Ollama failures would surface as an opaque
       `KeyError`, not a diagnosable error, in the single most-exercised code path
   - 2.4 Found (Minor): `app.py` hand-rolls T-021's override precedence instead of calling
     `resolve_date_range(..., manual_override=...)`; real titles unescaped in markdown
     links; `latest_feed_date()` scanned up to twice per interaction
     · outcome: all reported, none fixed yet (review only)

## 3. T-029 — fixing what adversarial review found  [T-029]
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
     · outcome: **self-correction** — the adversarial review finding was wrong about
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
   - 5.1 `docs/PLAN.md`'s "Current phase" block rewritten: all tickets done, adversarial review run
     and every finding triaged/fixed (T-029) or deferred to the risk register, T-030 landed
     · outcome: declared complete. Phase 3 **not** started yet

## 6. Phase 3 opened  [T-037]
   - 6.1 Phase 3 started, with the scope for this round:
     evaluation harness + two comparisons, README/LICENSE/fresh-clone, project rename
     (scoped), the two deferred risk-register test tickets — not the
     report/presentation checklist item
   - 6.2 Six tickets written (T-031-T-036) plus T-037 itself, `docs/PLAN.md`'s current phase
     set to Phase 3
     · outcome: T-035 (rename) deliberately scoped narrow while writing it — found the
       `vg09` package (41 importing files) and `vg09.store.COLLECTION_NAME` (a real stored
       Chroma identifier) mid-write and excluded both, flagged as separate decisions rather
       than folded into a routine rename
   - 6.3 None of T-031-T-036 executed this round · outcome: done,
     committed (`b2a9490`)

## 7. T-031 — the evaluation harness, first real run  [T-031]
   - 7.1 Built `scripts/t031_evaluation_harness.py`: loads the 15 real questions *and* their
     full facit blocks live from `docs/eval-questions.md`, runs the real pipeline, writes
     one Markdown file with question/mode/answer/sources/facit side by side plus a grading
     checkbox line
     · outcome: format extended beyond the ticket's original scope (facit reproduced
       verbatim) — noted in the ticket rather than treated as the original plan
   - 7.2 First real run hit a genuine `ReadTimeout` (300s) on F03 · outcome: a clean retry
     completed all 15 with no error — treated as transient, not investigated further at
     this point (later re-examined in T-038, § 8.4)
   - 7.3 Reviewing the real output found F07's answer completely empty, `done_reason==
     "length"`
     · outcome: root-caused, not just noted — `pack_to_budget()` measured only bare chunk
       text, never the real `"[N] Title (url, feed date)\n"` wrapper actually sent to the
       model. Real `prompt_eval_count` 15349 vs. the ~13458 the budget assumed. **Not fixed
       as part of T-031** — deferred to a new ticket (T-038), to be fixed before T-032

## 8. T-038 — fixing the packing-budget undercount  [T-038]
   - 8.1 Ticket written: move the formatting logic to one shared place, measure the real
     formatted string during packing, recompute what actually needs recomputing, write a
     KB entry, re-verify for real, check the timeout
   - 8.2 `vg09.answer._format_source()` moved to `vg09.retrieval.format_source()` (public),
     reused by both `pack_to_budget()` and `build_user_message()`
     · outcome: a 2-digit placeholder citation number used for packing-time measurement
       (real number isn't known until after packing) — documented as a safe-direction
       approximation, not a real inaccuracy source
   - 8.3 Real measurement (`scripts/t038_measure_wrapper_overhead.py` against the
     production store, 1971 real chunks): wrapper overhead 41-83 real tokens/chunk
     · outcome: `CHUNK_BUDGET_TOKENS`'s own arithmetic (13245) did **not** need to change —
       the reservation formula was always right, only the per-chunk measurement was wrong.
       What did need recomputing: max top-k, corrected 33 → 27 (`13245 // 488`, 488 being a
       real observed worst-case chunk: 405 bare + 83 wrapper)
   - 8.4 Real re-verification: all 15 questions re-run, timing instrumentation added to the
     harness
     · outcome: **15/15 `done_reason=="stop"`**, zero empty answers, max `prompt_eval_count`
       81% of `num_ctx`. Real elapsed `generate_answer()` times 7.7s-18.4s — ~16x margin
       under the 300s timeout, so the earlier F03 timeout (§ 7.2) is now confidently read as
       transient (GPU/network hiccup), not an undersized timeout. Left unchanged
   - 8.5 KB-018 written (the under-counted-since-T-008 finding); tests updated (fixtures
     gained real title/url/feed_date, new regression test); committed (`2e6665d`)

## 9. T-032 — the date-aware-vs-plain comparison, first real run  [T-032]
   - 9.1 Built `scripts/t032_date_aware_vs_plain_comparison.py`, reusing T-031's question/
     facit loader directly (import, not a copy) so the two harnesses can't drift on what
     "the 15 real questions" means
     · outcome: import needed `scripts/` itself on `sys.path` (no `__init__.py` there) —
       caught by a dry-run sanity check before spending the real 2x-cost run on a broken
       import
   - 9.2 Real run: 30/30 calls (15 questions × 2 modes) completed
     · outcome: 4/30 hit `done_reason=="length"` despite T-038's fix (F06-A, F07-A, F11-B,
       F14-A) — checked against T-038's own re-verification numbers and found identical
       `prompt_eval_count` for the same arm/question in at least one case, confirming this
       is real sampling variance (T-028's own already-documented residual risk), not a
       packing regression. Each instance visibly flagged in the output, not fixed or hidden
   - 9.3 User asked twice whether the background run was still active while waiting
     · outcome: confirmed both times via real process CPU time / Ollama's own CPU
       accumulation and TCP connection state, not by guessing or polling the (buffered)
       output file
   - 9.4 Committed (`4a148a5`)

## 10. Moving the real results into the tracked repo  [T-032]
   - 10.1 Decision: the project's own generated results belong in the repo/report,
     not gitignored `data/`
     · outcome: the two valid runs (T-031's post-fix run, T-032's comparison) moved to new
       `docs/eval-results/` (tracked); the earlier pre-fix buggy T-031 run deliberately left
       in `data/eval_results/` (gitignored) — a bug artifact, not a result, already quoted
       in full in T-031's ticket entry and KB-018. Both harness scripts' `OUTPUT_DIR`
       updated so future runs land in the tracked location by default. Committed (`62ab286`)
   - 10.2 User reported the moved files "missing" from `docs/eval-results/` (IDE only
     showed the unrelated `data/`-side file)
     · outcome: verified directly against the real filesystem (`ls`) and git
       (`git show --stat`) rather than trusting the report at face value or the IDE's own
       view — both confirmed the files were correctly present and committed all along; the
       IDE's file tree had simply not refreshed. Nothing was actually wrong, nothing fixed
       — **the correct response to "it's missing" was to verify independently, not to
       assume the user's report was right and start "fixing" a problem that didn't exist**
