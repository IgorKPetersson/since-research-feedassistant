# HANDOFF

Newest note at the top. The agent reads the top note at the start of every session and
prepends a new one at the end via the `session-handoff` skill.

## Why this exists

Each session starts with no memory of the last one. Without this file, every session
re-derives context from the code, guesses at half-finished intentions, and sometimes undoes
deliberate choices. This note is the memory.

A good note answers: what did I do, what is half-done, what did I learn that isn't in the
code, and what should the next session do first.

## Order at the end of a session

1. `session-tree` → `docs/sessions/YYYY-MM-DD-slug.md`
2. `kb-entry` → anything learned about real behaviour, into `docs/kb/`
3. `session-handoff` → this file, referencing both

## Rules

- Write the note **before** the context window is exhausted, not after.
- "Learned" is the highest-value section. Anything discovered about how a dependency really
  behaves goes to `docs/kb/` as well as here.
- Decisions go in `DECISIONS.md`; this note only cites the ID.
- Never delete old notes. They are the project diary.

---

## 2026-10-05 — Self-update on open, answer fixes from real use, frozen re-evaluation

**Tickets:** T-059–T-069  ·  **Tree:** docs/sessions/2026-10-05-self-update-answer-fixes-frozen-eval.md

The session ran out of tokens right after its last answer, before the wrap-up. This note,
the tree and KB-029–031 were written from the transcript in the next session, the same
day. No code or data was lost: everything was committed and pushed.

**Done this session:**
- T-059 (D-018): the app starts an update when it opens and nothing has been fetched today,
  with a setting on the Sources page to turn it off. T-060: `Since.bat` starts the app with
  a double-click; the browser opened.
- T-061: the model is told today's date and the applied range. "What has happened with AI
  today?" had answered that the day's papers were "from the future" (KB-029).
- T-062: a citation number links straight to its paper or video, title on hover; the
  source list stays. T-063: a quoted video sentence links to the second it is spoken.
- T-064/T-065: a warning under the answer when a quote is not in its credited source
  (KB-030); quoted titles no longer flagged.
- 18-question probe → T-066 (date phrases like "yesterday", "since Monday", "between X and
  Y"; weekday given to the model), T-067 (candidate pool 60 → 200, KB-031), T-068 (a
  question naming papers or videos searches only that source).
- T-069: date-aware vs plain re-run against the frozen dataset in a separate store, graded:
  A better 7, B better 1, equivalent 5, both wrong 2. PLAN.md, the ticket and
  `docs/presentation.md` (three runs side by side, "never worse" dropped) updated.
- Data caught up to 2026-10-05.

**In progress / half-finished:**
- Nothing in code. T-048 and T-056 are `review` (below).

**Learned (not obvious from the code):**
- KB-029: without today's date the model assumes 2023/2024 and discards current sources.
  Retrieval was right, so no unit test could see it; found in the app.
- KB-030: the model quotes accurately but credits quotes to the wrong source (4 of 5 in one
  answer); exact matching rejects correct loose quotes.
- KB-031: news-video wording crowds papers out of retrieval; a bigger pool helps but
  doesn't fix F14 (semantic gap, in PLAN.md's risk register).
- Dead end, not built: 15-second video excerpts so every link is precise. It needs a
  reindex and a graded re-run for a link nicety.
- Dead end, rejected: a Windows scheduled task for daily updates. It runs while the app is
  closed, which GOAL rules out (D-018).
- `retrieve()`'s `n_results` default is bound when the function is defined, so changing
  `CANDIDATE_POOL_SIZE` at runtime (e.g. in an eval script) does not change it; pass it in.

**Blocked / needs me:**
- **T-048 / Phase 3 "Report and presentation":** the only unchecked Phase 3 item. Waiting on
  the outline for the presentation. Then the demo questions are asked in the
  running app and `defense-prep` is run.
- **"24/7"** in `docs/GOAL.md`: the reading ("always caught up when you ask") is not
  confirmed.
- **T-056:** the stale-data marker has never been seen in a browser. With T-059 it only
  shows if self-update is off and the data is over 2 days old.
- **Probe findings, not ticketed. Do they get tickets?** The model
  guesses channel names (it is never told the channel); "the three latest videos" picks
  the wrong ones; an old "next week" is read as the future; one answer had the right
  sources but no citations; Palantir is not linked to "Palunteer" (F12).

**Next session should start with:**
- Ask I for the presentation outline (one question, nothing else), then rework
  `docs/presentation.md` to it under T-048.

**Doc updates made:** D-018 · KB-029, KB-030, KB-031 · PLAN.md risk register and Phase 3 ·
TICKETS T-059–T-069 · presentation.md results section

---

## 2026-10-02 (evening) — Finishing pass, data caught up, Sources page built

**Tickets:** T-048–T-058  ·  **Tree:** docs/sessions/2026-10-02-finishing-pass-and-sources-page.md

**Done this session:**
- T-049: retrieval 68.6s → 1.2s. Ollama is addressed as `127.0.0.1`, not `localhost`.
- T-050: accent darkened to `#A26B16` so white text reaches 4.5:1;
  chips now white. T-051: Enter or one click on Ask submits. T-039 closed after its
  retry notice was seen in the running app.
- Data caught up from 2026-09-17 to 2026-10-02 (1610 papers, 62 videos, 2853 chunks).
- T-048: `docs/presentation.md`, a run-of-show for the live demo, with demo questions
  verified against the caught-up data.
- T-052–T-056, T-058 (D-017): sources chosen in the app. `data/sources.json`, a `channel`
  field on documents and chunks (62 existing videos migrated), ingest as a background
  job, a Sources page (list, add, remove, Update now with progress), at most 5 channels.
- T-057: README and presentation rewritten around the Sources page, then a fresh clone
  taken through it in a browser: opened on Sources, three channels removed, one week of
  history, update finished in 121s, first question answered with citations. The first
  attempt hung in Whisper (KB-028) and was fixed before the run that passed.
- Everything is on `main` and pushed.

**In progress / half-finished:**
- **T-056 is `review`:** the stale-data marker in the header is unit-tested but has not
  been seen in a browser, because the data is current.
- The fresh-clone run used one week and one channel, and the main project's Python
  environment. The default eight weeks and four channels were not run from the page.
- T-048: the presentation draft is not yet reviewed; length, language and audience
  are assumptions.

**Learned (not obvious from the code):**
- KB-024: `localhost` costs about 2s per Ollama request on Windows. Every time measured
  before today includes it.
- KB-025: `os.replace()` onto a file another process has open raises `PermissionError`
  on Windows. It killed the first real job run.
- KB-026: a Chroma client goes stale when another process writes the store. Queries fail
  with "Error finding id" while counts still look right. `store.reset_client()` fixes it.
- KB-027 (provisional): the first question after an update that used Whisper hung 120s
  on Ollama, once. It did not happen again in the fresh-clone run, which also used Whisper.
- KB-028: with Whisper's CUDA libraries not on PATH, the first transcription raises and
  the second hangs. The lookup assumed `<repo>/.venv`; it now uses the running
  interpreter's site-packages. A hung transcription is not caught by the job's heartbeat.
- **Process lesson:** items were reported as done from documents and tests without
  running the app that day, and real gaps were called small.
  Run it before saying it works, and say plainly what was not run.
- **Process lesson:** all three defects in the Sources work (KB-025, KB-026, the 316s
  no-op update) were invisible to 250 passing unit tests and appeared in the first real
  run. For anything with two processes or a browser, the real run is the test.
- Dead end not built: a second store directory swapped in after the job. Renaming a
  directory the app holds open fails on Windows.

**Blocked / needs me:**
- The presentation's content is not yet decided. `docs/presentation.md` is a draft;
  expect to rework it rather than polish it. The presentation is the only
  Definition of done item left.

**Next session should start with:** check how old the data is and remind I
(their standing request). Then ask whether they have read `docs/presentation.md`.

**Doc updates made:** D-017 · KB-024–028 (KB-023 superseded) · DESIGN § Sources page ·
PLAN · TICKETS T-048–T-058 · README · presentation · session tree 2026-10-02

---

## 2026-10-02 — T-047 merged to `main`; only the report and presentation remain

**Tickets:** T-047  ·  **Tree:** — (short session, nothing beyond this note)

**Done this session:**
- `t/T-047-readme-since` fast-forwarded into `main` and pushed (`c21b19b..0dffd65`), as
  the first Definition of done item. 207/207 tests pass
  before and after. The 2026-09-24 note below, KB-020–023 and that session's tree are
  now on `main`.
- `docs/PLAN.md` corrected to say so.

**In progress / half-finished:** nothing.

**Learned:** nothing new.

**Blocked / needs me:**
- **Presentation** — Definition of done item 5, the only one not met.
- Not required for done, still open: T-039 is `review` (the retry notice in the UI has
  never been seen in a running Streamlit session); the Ask button's 3.32:1 contrast.

**Next session should start with:** the presentation.

**Doc updates made:** PLAN (T-047 merged, Definition of done status)

---

## 2026-09-24 — Evaluations graded, UI redesigned and renamed "Since", logo mark

**Tickets:** T-039, T-040, T-035, T-034, T-036, T-041, T-033, T-042, T-043, T-044, T-045,
T-046, T-047  ·  **Tree:** docs/sessions/2026-09-24-phase-3-grading-ui-redesign-since.md

**Done this session (2026-09-22 → 24):**
- **Evaluation:** T-032 and T-033 both graded and committed. T-039 (retry on
  truncation) verified live; T-040 range citations, with the ≤5-number threshold as
  D-015. T-041 fixed the Phase 3 grill-me findings. T-036 added the last
  risk-register tests.
- **Publish:** T-035 rename, then T-034 README + Apache-2.0 LICENSE, then a real
  fresh-clone test that passed with no fixes needed.
- **UI:** T-042 redesign (live pipeline strip, citation chips, source cards; UI in
  English per D-016); T-043 English date parsing (8/0/7/0 on real English translations,
  same as Swedish); T-044 "Date range" tile; T-045 name "Since", Instrument Sans, one
  amber accent `#C17F1A`, compact header, grey badges, text-colour links; T-046 timeline
  logo mark in the header and as the favicon, lockup tuned from pixel measurements.
- `main` = `c21b19b`, pushed. It contains everything through T-046, with 207/207 tests.

**In progress / half-finished:**
- **T-047 (README: "Since" name, logo, three stale UI facts) is on `t/T-047-readme-since`,
  committed (`0cf025d`), not merged.** The README update was asked for, not
  its merge. This session's docs commit (tree, KB-020–023, this note, PLAN) is on the
  same branch, so this note is only on `main` once that branch is merged.
- The screenshots in `docs/screenshots/` are still named `t042-ui-*-theme.png` even
  though they now show T-046's UI. They were kept on purpose because other
  documents reference those paths.

**Learned (not obvious from the code):**
- KB-020: a bare `[theme]` in `.streamlit/config.toml` silently removes dark mode for
  everyone. Keep `[theme.light]` and `[theme.dark]`.
- KB-021: Streamlit 1.64 custom CSS loses to its own markdown styles unless scoped under
  `[data-testid]` with `!important`. `st.html()` strips `<link>`. The broad selector
  breaks Material icons unless they're restored.
- KB-022: Instrument Sans stops at weight 700.
- KB-023 (provisional): live retrieval took ~40–100s per question today, with `bge-m3`
  seen unloaded. Cause unknown and not investigated.
- **Process lesson:** don't self-number an unnumbered request and then silently re-file
  the next number. The T-044/T-045 collision nearly shipped the wrong branch
  (session tree § 10). Raise a numbering conflict as a question.
- **Process lesson:** a live verification that starts a long real job (T-034's
  fresh-clone YouTube backfill) should be announced before it starts, not explained
  after I notices it (session tree § 3.2).
- Dead end: `margin-top` to raise a flex item moves the row, not just the item (tree § 12.4).

**Blocked / needs me:**
- **Merge `t/T-047-readme-since`**, which also carries this note.
- **Ask button contrast:** its white label on the amber is 3.32:1, below AA (T-045 "Open").
  Choose: a different accent, or override Streamlit's primary-button styles.
- **Presentation** (Phase 3's last checklist item). No
  ticket. Phase 3 is not declared complete.

**Next session should start with:** confirm whether `t/T-047-readme-since` has been
merged. If not, decide whether to merge it before anything else, because this
note and KB-020–023 live on that branch.

**Doc updates made:** D-015, D-016 · KB-020, KB-021, KB-022, KB-023 · DESIGN (T-041
numbers, T-043 English date range) · PLAN (Phase 3 status incl. T-042–T-047) · TICKETS
T-039–T-047 · README (T-047 branch) · session tree 2026-09-24

---

## 2026-09-20 (kväll) — Phase 3 opened, T-031/T-038/T-032 run for real, evaluation results committed

**Tickets:** T-037, T-031, T-038, T-032  ·  **Tree:**
docs/sessions/2026-09-20-phase-2-grillme-and-closeout.md §§ 6-10

**Done this session (continuation of the same day's Phase 2 close-out above):**
- **T-037**: Phase 3 opened. Six tickets written (T-031-T-036)
  for this round's named scope — evaluation harness + two comparisons, README/LICENSE/
  fresh-clone, a deliberately narrow project rename, two deferred risk-register test
  tickets. Report/presentation (Phase 3's third checklist item) still has no ticket, not
  forgotten. None of T-031-T-036 executed at this point
- **T-031**: `scripts/t031_evaluation_harness.py` built and run for real — all 15 of
  T-014's questions through the real pipeline, `today` anchored via `latest_feed_date()`
  (D-012), output is one Markdown file per question with the facit reproduced verbatim
  alongside (format extended past the ticket's original scope).
  First real run found **F07's answer came back completely empty**
  (`done_reason=="length"`) — root-caused, not just noted, and **not** fixed as
  part of T-031; fixed in its own ticket first
- **T-038** (bugfix, landed before T-032): the real root cause was
  `pack_to_budget()` measuring only bare chunk text, never the real
  `"[N] Title (url, feed date)\n"` wrapper `vg09.answer._format_source()` adds before
  sending to the model. Fixed: that formatting logic moved to
  `vg09.retrieval.format_source()` (public, one source of truth for both packing-time
  measurement and real prompt construction). `CHUNK_BUDGET_TOKENS` (13245) did **not** need
  to change — the reservation formula was always correct; what needed recomputing was the
  max-top-k ceiling, corrected 33 → **27** from a real measured worst-case chunk (488
  tokens: 405 bare + 83 real wrapper overhead, `scripts/t038_measure_wrapper_overhead.py`).
  **KB-018** records the finding: the budget has under-counted the real prompt since T-008.
  Real re-verification: **15/15 `done_reason=="stop"`**, zero empty answers, max
  `prompt_eval_count` 81% of `num_ctx`. The 300s `ReadTimeout` checked against real elapsed
  times (7.7-18.4s, ~16x margin) — left unchanged, the one real timeout seen earlier reads
  as transient, not structural
- **T-032**: `scripts/t032_date_aware_vs_plain_comparison.py` built and run for real — each
  of the 15 questions through the real pipeline twice (date-aware vs. plain, no date filter)
  side by side against the same facit. 30/30 real calls completed; 4 hit
  `done_reason=="length"` despite the T-038 fix — confirmed as real sampling variance
  (identical `prompt_eval_count` to a clean T-038 re-verification run for the same
  arm/question in at least one case), matching T-028's own already-documented residual
  risk, not a regression. Each instance visibly flagged in the output
- Real evaluation results **moved into the tracked repo**: the two valid runs (T-031 post-
  fix, T-032 comparison) moved from gitignored `data/eval_results/` to tracked
  `docs/eval-results/` — these are the project's own generated
  results, not fetched source data. Both harness scripts' default output directory updated
  to match. The earlier buggy pre-fix T-031 run stays in `data/eval_results/` deliberately
  (a bug artifact, not a result — already quoted in full in T-031's ticket entry and KB-018)

**In progress / half-finished:**
- **Grading is not done.** Both real result files in `docs/eval-results/` are committed but
  **ungraded** — every `☐` checkbox in both files is still unchecked. This is a
  manual step, not automatable (no model grading, per T-031's own scope)
- `docs/PLAN.md`'s Phase 3 exit criteria ("results table committed") is satisfied for the
  *committing* half; the *graded* half is still open

**Learned (not obvious from the code):**
- A file reported as "missing" is worth verifying directly (real `ls` + `git show
  --stat`) before "fixing" something — the files were present and committed all along;
  the IDE file tree had not refreshed after the directory was created mid-session.
- KB-018 (new): the retrieval packing budget has silently under-counted the real prompt
  sent to the model since T-008 — see `docs/kb/` for the full real measurement (41-83
  tokens/chunk of real, previously-uncounted citation-wrapper overhead)

**Blocked / needs me:**
- **Grading**, on both `docs/eval-results/2026-09-20-2043-t031-harness.md` (T-031, single
  arm) and `docs/eval-results/2026-09-20-2136-t032-date-aware-vs-plain.md` (T-032, two arms
  side by side) — check the `☐` boxes against each question's facit. Nothing else is
  waiting on this to continue (T-033, the model-size comparison, doesn't depend on grading),
  but it's the one open loop from this stretch

**Next session should start with:** either grade the two committed result files, or — if
grading isn't the next priority — pick up **T-033** (the `qwen3:30b-a3b` vs `qwen3:8b`
comparison, same shape as T-032, already written and ready in `docs/TICKETS.md`). Both are
real, available next steps; neither is blocked on the other.

**Doc updates made:** KB-018 (new) · `docs/DESIGN.md` § Context budget (max top-k 33→27,
the T-038 correction) · `docs/PLAN.md` (Phase 3 current-phase block, risk register row
corrected) · `docs/TICKETS.md` (T-031, T-032, T-037, T-038 all done; T-033-T-036 written,
not started) · `docs/eval-results/` (new, tracked — two real result files)

---

## 2026-09-20 — T-028 closed, Phase 2 `grill-me` (T-029), English-answer decision (T-030), Phase 2 declared complete

**Tickets:** T-028, T-029, T-030  ·  **Tree:**
docs/sessions/2026-09-20-phase-2-grillme-and-closeout.md

**Done this session:**
- **T-028 closed:** its one open acceptance criterion (does the smaller chunk budget cost
  real recall?) finished for real — `scripts/t028_verify_chunk_budget_impact.py`, real run
  at `today=2026-09-17` (T-027's own anchor). Packed chunk count dropped 1-2 on 5/15
  broad/unfiltered questions; **top-5 unchanged on all 15 of 15**, confirmed directly.
  T-027's F15/F06 checkpoints reproduced exactly — the 11/14 headline holds
- `grill-me` run against the whole of Phase 2 (T-011, T-021–T-028, D-011) —
  found D-011's written evaluation-anchor rule was never actually followed by any real
  measurement taken under it (top finding), a missing `raise_for_status()` in the
  single most-exercised code path, and two smaller code-quality gaps
- **T-029**, fixing all four triaged findings:
  - D-011 marked `superseded by D-012`; **D-012** gives production and evaluation the same
    anchor (`vg09.store.latest_feed_date()`). A real, honest residual gap recorded rather
    than smoothed over: no single anchor reproduces every individually-written HF-only
    facit window exactly (one day off, harmless for this frozen dataset specifically —
    confirmed HIT/MISS unaffected)
  - `vg09/answer.py::generate_answer()` now calls `raise_for_status()` (self-correction
    mid-ticket: the grill-me finding was wrong that `count_qwen_tokens()` also lacked it —
    it already had it since T-022); `app.py` catches the resulting exception and shows a
    clear Swedish message instead of a traceback
  - `app.py` now calls `resolve_date_range(..., manual_override=manual_range)` directly
    instead of hand-rolling the override precedence
  - Citation titles escaped (`vg09.ui_helpers.escape_markdown_link_text()`) before going
    into markdown links, tested against a real title and a synthetic bracket-shaped one
  - Fifth finding (`latest_feed_date()` scanned twice per UI interaction) deferred to
    `docs/PLAN.md`'s risk register only
- **T-030**: **D-013** — answers are always in English regardless of the question's
  language, for OSS/international usability; questions keep working in any language
  (`bge-m3`, unaffected). `SYSTEM_PROMPT` updated, real re-measurement (173 qwen3 tokens,
  was 157) propagated through `CHUNK_BUDGET_TOKENS` (13245, down from 13261) and
  `docs/DESIGN.md`. Verified end to end: two real Swedish questions against the real
  store/Ollama both produced English answers (`scripts/t030_verify_english_answer.py`)
- **Phase 2 declared complete** in `docs/PLAN.md` — all tickets done, `grill-me` run and
  every finding triaged. Phase 3 **not** started

**In progress / half-finished:** nothing — T-028/T-029/T-030 all reached `done`, Phase 2 is
closed.

**Learned (not obvious from the code):**
- KB-017 (new): a markdown `[text](url)` link's text portion only needs `[`, `]` and
  backslash escaped under CommonMark — parentheses inside `[text]` are safe unescaped. The
  real title used to test the citation-escaping fix ("He Built The Ultimate Spy Tool (Free
  and Open-Source)") turned out not to exercise the actually-dangerous character; a
  synthetic `[SOTA]`-shaped title covers that case instead
- A decision log entry can drift out of sync with the practice it documents, silently,
  across multiple tickets, if nothing ever cross-checks the written rule against what a
  real re-run actually does. D-011 said "pin eval to 2026-09-16"; T-027's and T-028's real
  runs both used 2026-09-17, and nobody noticed until a `grill-me` pass read the decision
  log and the scripts side by side. Worth remembering as a reason to occasionally re-read a
  decision against the code that's supposed to implement it, not just trust it was followed
- A `grill-me` finding can itself be wrong in a narrow, checkable way (`count_qwen_tokens()`
  already had `raise_for_status()` before T-029) — worth verifying findings against the
  actual code before fixing, not just implementing the review verbatim

**Blocked / needs me:** nothing blocking. Phase 3 (evaluation script, README/LICENSE,
report) waits for a go-ahead per `docs/PLAN.md`'s own gating rule — not started this
session.

**Next session should start with:** Phase 3, if and when I gives the go-ahead —
turn `docs/PLAN.md`'s Phase 3 checkboxes into tickets with `ticket-write` first. One loose
end worth remembering before Phase 3's evaluation script is built: D-013 means a strict
re-grading of `docs/eval-questions.md`'s facit (written and graded in Swedish) now needs to
expect an English answer even though the facit's own descriptive text stays Swedish —
flagged in T-030's own ticket Notes, not resolved there.

**Doc updates made:** D-011 (superseded by D-012) · D-012 (new) · D-013 (new) · KB-017
(new) · `docs/DESIGN.md` § Context budget (system prompt 157→173, chunk budget
13261→13245) · `docs/eval-questions.md` (anchor callout only, facit content untouched) ·
`docs/PLAN.md` (Phase 2 declared complete, new risk-register row for `latest_feed_date()`'s
double scan) · `docs/TICKETS.md` (T-028, T-029, T-030 all closed/done)

---

## 2026-09-19 — Phase 2 built end to end (T-011, T-021–T-025), then two real bugs found and fixed via T-028

**Tickets:** T-014, T-020, T-026, T-021, T-022, T-027, T-011, T-023, T-024, T-025, T-028  ·
**Tree:** docs/sessions/2026-09-19-phase-2-built-end-to-end.md

**Done this session:**
- T-014 closed (F14/F15 cross-source questions), Phase 1 fully closed
- `grill-me` review of all Phase 1 → 6 findings, triaged: 2 now / 4 deferred → **T-020**
  (frozen-dataset SHA-256 manifest + yt-dlp timeout)
- Phase 2 opened (**T-026**) and every ticket in it shipped, real end to end:
  - **T-021** date-range extraction (`vg09/date_range.py`) - tested against all 15 real
    T-014 questions, 8/15 resolved correctly, 0 wrong, 7/15 correctly unparseable
  - **T-022** retrieval (`vg09/retrieval.py`) - filter/sort/pack, real Chroma + real Ollama
  - **T-027** two real fixes found by re-testing T-022 against the real questions: per-doc
    chunk dedup (crowding), and anchoring `today` to the whole dataset's real latest content
    instead of one source's cutoff (`vg09.store.latest_feed_date()`, **D-011**)
  - **T-011** reasoning/answer split (`vg09/llm.py`) - built as T-023's hard dependency
  - **T-023** the real `/api/chat` call (`vg09/answer.py`)
  - **T-024** citations (`vg09/citations.py`) - resolved by the model's own bracketed
    *position* citations ("source [27]"), not the originally-requested `[Title, date]`
    format, which the model never reliably followed
  - **T-025** the chat UI (Streamlit, `app.py`) - real browser smoke test of all three
    `docs/GOAL.md` question types
- **T-028**, from manual use of the shipped UI: fixed multi-number citation
  brackets (`"[17, 18]"` now resolves both, was silently dropping everything after the
  first); measured a real `done_reason=="length"` truncation (reasoning alone ate 61.5-92.1%
  of the 2000-token cap across 3 real runs); chosen: "raise `NUM_PREDICT`" over "shorter
  reasoning" - new value derived from the measurement: `1842 + 400 + 300 = 2542`, not rounded.
  `docs/DESIGN.md`'s whole context-budget section updated to match (`CHUNK_BUDGET_TOKENS`
  13803 → 13261, top-k ceiling 34 → 33)

**In progress / half-finished:**
- **T-028's last acceptance criterion is unverified.** Does the smaller chunk budget (13261)
  still pack enough real chunks across T-014's 15 questions, and does the 11/14 headline
  hold? A first attempt used the wrong `today` anchor and produced a misleading 10/14 (see
  KB-016 — this was a measurement bug, not a real regression). A corrected script
  (`today=2026-09-17`, matching exactly what the original 11/14 was measured against — **not**
  D-011's `2026-09-16` eval-pinned anchor, that's a different, already-settled question) was
  running in the background when this session ended on a token warning; never confirmed
  finished. Full instructions for resuming are in T-028's own ticket Notes in
  `docs/TICKETS.md`.

**Learned (not obvious from the code):**
- KB-016: comparing two retrieval measurements needs the *same* `today` anchor in both arms,
  or the delta is meaningless — caught a false "regression" this way, see above.
- The model reliably cites by the bracketed source *number* shown in the prompt, never
  reliably by `[Title, YYYY-MM-DD]` even when explicitly asked — T-024 leaned into this
  instead of fighting it, and it's now the system prompt's own instruction.
- Reasoning length is the real truncation risk, not answer length — T-008's original 2000
  budget was sized against *combined* reasoning+answer across different question types, but
  reasoning alone can eat 90%+ of that on a single real question; the two need separate
  measurement, not one combined estimate.
- Positional citation resolution can't tell a real evidence citation from a bracketed number
  used descriptively ("reviewed sources `[1]` to `[38]`") — a real false-positive citation
  was produced on a correct negative answer (F12). Recorded as a known limitation
  (`docs/PLAN.md` risk register), not fixed — fixing it would mean forcing the stricter
  format that was already shown not to work reliably.

**Blocked / needs me:**
- Nothing blocked on a decision right now. T-028's chunk-budget re-verification (above) just
  needs finishing and reporting — no judgment call pending, just computation.

**Next session should start with:** re-run the corrected T-028 chunk-budget-impact script
(pattern is in T-028's ticket Notes in `docs/TICKETS.md` — real per-question `pack_to_budget()`
comparison at `today=2026-09-17`, old budget 13803 vs. new 13261, plus a re-confirmed
top-5-vs-facit headline at that same anchor) and report the result. After that,
T-028 can close and Phase 2's checkpoint (all tickets done, `grill-me` not yet run — see
`docs/PLAN.md`'s "Current phase" line) is the next real decision point, not something to walk
past on autopilot.

**Doc updates made:** D-011 (amended) · KB-016 (new) · `docs/DESIGN.md` § Context budget
(system prompt, reasoning+answer reservation, remaining budget, max top-k) · `docs/PLAN.md`
risk register (2 new rows: the semantic-gap limitation, the false-positive-citation
limitation) and Phase 2 checklist (all ticked, phase not yet declared complete) ·
`docs/TICKETS.md` T-011/T-020/T-021/T-022/T-023/T-024/T-025/T-026/T-027/T-028 (T-028
in-progress, rest done)

---

## 2026-09-17 — Phase 1 closed except T-014: Whisper un-parked and wired in (T-018, T-019), T-013 finished for real

**Tickets:** T-017, T-018, T-019, T-013  ·  **Tree:**
docs/sessions/2026-09-17-whisper-integration-and-catchup.md

**Done this session:**
- KB-008 re-checked: the `IpBlocked` block that ended the previous session had cleared
  (manual re-check, 1051 real snippets) — gated **D-008** (wait it out), then T-017's real
  paced backfill got 17 real caption successes before the block recurred on `@NateBJones`'s
  first video, triggering D-008's own "would change our mind" clause
- **D-009**: un-park option (b) — `yt-dlp` audio + local Whisper — for the channels the
  block keeps hitting, scoped, not a wholesale replacement of captions
- **T-018**: Whisper feasibility test — audio download for the blocked video was not
  blocked at all (only the transcript-API endpoint is affected); real `faster-whisper`
  transcription on the RTX 4090 confirmed working after a real CUDA DLL-loading fix (KB-012)
- **T-019**: wired Whisper into `vg09/youtube.py` as a three-tier fallback (captions →
  Whisper → title+description); fixed and recalibrated `vg09/chunking.py` against the 17
  real transcripts then on disk (`TARGET_CHUNK_CHARS` 1942→1454 — the synthetic estimate
  had under-budgeted real token count, the dangerous direction per KB-005); confirmed real
  joint VRAM residency with Ollama's chat/embedding models (KB-015); re-ran the backfill for
  `@NateBJones`/`@ColeMedin` — **24/24 videos resolved via Whisper**, 0 fallbacks. **D-010**
  records that the collector no longer aborts a run on a caption block (amends D-006's
  consequence, not its missing-vs-blocked classification) — `IngestBlocked` had no
  remaining caller and was removed rather than left as dead code. T-017 marked done
  (T-019 completed what it was blocked on)
- Merged and pushed `t/T-017-youtube-backfill` → `t/T-018-whisper-feasibility` →
  `t/T-019-whisper-integration` into `main` (fast-forward, ticket branches deleted)
- **T-013 finished for real**: `catch_up_youtube()` was still a no-op stub from when
  YouTube had no transcript path — implemented it for real (reuses
  `youtube_backfill.run()`'s paced three-tier logic for the window since the watermark).
  Built the store with the full YouTube dataset for the first time ever (1184 → 1994
  chunks). Real gap simulation (removed 2026-09-10's 3 videos, mixed captions/whisper,
  rolled the watermark back, caught up for real): 2 recovered via Whisper, the 3rd
  (previously-clean `@theAIsearch`) hit `IpBlocked` **and** its Whisper audio download also
  failed (403) — the first real double-failure, correctly resolved via the third resort.
  Verified into Chroma: 1971/1971 unique ids, no duplicates. Found and fixed a real bug
  along the way: `fallback_reason` was silently dropped in `chunk_youtube_document()`'s
  windowed/multi-chunk path (only the single-chunk fallback path carried it) — invisible
  for captions (always `None` there) until a real Whisper document exercised it. Merged and
  pushed `t/T-013-youtube-catchup` into `main`

**In progress / half-finished:** nothing — every ticket started this session reached `done`
or was closed out for good (T-017 completed by T-019).

**Learned (not obvious from the code):**
- KB-012 through KB-015 (new): ctranslate2's CUDA loading ignores
  `os.add_dll_directory()` on Windows, needs a real `PATH` prepend instead; `faster-whisper`
  timing/VRAM/segment-shape measurements; real auto-captions DO have punctuation
  (contradicting an unverified assumption baked into `vg09/chunking.py`, misattributed to
  KB-001); Whisper fits alongside Ollama's chat/embedding models with real headroom to
  spare
- KB-008 (updated repeatedly, still unresolved): the picture shifted across the session
  from "block cleared" → "recurred after 17 real requests despite pacing" → "looks durably
  scoped to two specific channels" → "actually more unpredictable than that — a
  previously-clean channel later blocked too, and `yt-dlp` audio download failed once,
  which had never happened before". Five real data points across one day, still no single
  theory fits. Practically moot for data collection now — D-009's three-tier fallback
  always produces a document regardless of which layer gets blocked on a given run
- Unverified, flagged for a future session rather than fixed here: `vg09/store.py`'s
  `build_store()` only ever `upsert()`s — it never deletes a chunk id that a document no
  longer produces. Not empirically observed (this session's gap-simulation script deleted
  the affected chunks by a date-filter *before* re-adding, sidestepping the question), but
  inferred from reading the code: if a real document's chunk count ever *shrinks* between
  rebuilds without a manual deletion step first (e.g. captions later replaced by a shorter
  fallback), the old higher-index chunks would be silently orphaned in Chroma forever. Worth
  a real test before trusting `build_store()` alone as a rebuild mechanism in a scenario
  like that.

**Blocked / needs me:** nothing blocking. **T-014** (15–20 evaluation questions) is the
only open Phase 1 item — the questions are written by hand next session; the agent's job is
finding and verifying expected sources against the real frozen data, not authoring them.

**Next session should start with:** T-014 — write the 15–20 evaluation
questions (spanning both sources, including at least two built around a proper noun likely
to be garbled by auto-captions — KB-014's real examples, "Palunteer"/Palantir, "Open
AAI"/OpenAI, "Sunno V6"/Suno V6, are ready-made material), the agent finds and verifies
expected sources against `data/raw/` and freezes the cutoff date. Only once T-014 closes is
Phase 1 fully complete and Phase 2 (retrieval, answer generation, chat UI) can start —
not started this session.

**Doc updates made:** D-008, D-009, D-010 · KB-008 (updated four times), KB-012, KB-013,
KB-014, KB-015 · `docs/PLAN.md` (Phase 1: YouTube backfill and catch-up checklist items
ticked) · `docs/TICKETS.md` (T-017, T-018, T-019, T-013 all closed/done) ·
`docs/sessions/2026-09-17-whisper-integration-and-catchup.md`

---

## 2026-09-16 — Phase 1 ingest: T-016, T-009, T-010, T-008, T-015, T-017 (written, blocked), T-012, T-013

**Tickets:** T-016, T-009, T-010, T-008, T-015, T-017 (blocked), T-012, T-013 · **Tree:**
docs/sessions/2026-09-16-phase-1-ingest.md

**Done this session:**
- T-016: Phase 1 opened (`docs/PLAN.md`), tickets T-008–T-015 written then revised twice on
  review before anything started; conversation history added to `docs/GOAL.md` as a
  non-goal
- T-009: `vg09/document.py`/`hf_papers.py`/`youtube.py` — real collectors writing to
  `data/raw/`. Hit a real `IpBlocked` failure on the very first verification run
- T-010: YouTube collector splits "captions missing" (falls back, final doc) from "blocked"
  (`Pending` marker, `IngestBlocked`, abort) — **D-006**, 4 mocked tests, no live calls
- T-008: real, measured RAG context budget in `docs/DESIGN.md` — 171/40/2000-token
  reservations, 13789 left for chunks, 400-token chunk cap, top-k 34
- T-015 split into **T-015** (HF-only backfill, done) and **T-017** (YouTube backfill,
  `status: blocked`) after a manual re-check confirmed the `IpBlocked` block was still
  live
- T-015: real 8-week HF backfill (1184 papers, 2026-07-23..2026-09-16), then a follow-up fix
  — the reopen window is 2 days, not 1, since Sweden runs ahead of UTC
- T-012: `vg09/chunking.py` (HF: 1 chunk/paper; YouTube: by transcript timestamp, citation
  gets `&t=SECONDS`) + `vg09/store.py` (bge-m3, ChromaDB, numeric `feed_date_ordinal`). Real
  run: 1184 chunks, `collection.count()=1184`, idempotent. `Document` gained a `segments`
  field — a stored-schema change made without pausing to ask first, flagged prominently,
  **approved after the fact as D-007**
- T-013: `vg09/sync.py` + `vg09/catchup.py`, per-source watermarks. Verified for real: removed
  2 real days from `data/raw/` and Chroma, rolled the watermark back, ran the real pipeline —
  catch-up + store rebuild closed the gap with zero duplicates (1184 unique ids)

**In progress / half-finished:** nothing — every ticket started this session reached `done`.
T-017 was deliberately not started (blocked, see below).

**Learned (not obvious from the code):**
- KB-008 (updated, not superseded): the YouTube transcript-fetch block is real and was still
  live on a same-day manual re-check — traceback showed `yt-dlp`'s video listing still
  works, only the caption-text fetch (`youtube_transcript_api`) is blocked
- KB-009: Ollama's `num_predict:0` does **not** mean "generate nothing" — produced a full
  485-token generation on a 9-word prompt. Use `num_predict:1` for a cheap tokenizer-count
  call instead
- KB-010: `from vg09.document import RAW_DIR` in `vg09/hf_papers.py` binds a **separate**
  name at import time — patching `vg09.document.RAW_DIR` alone does not redirect
  `hf_papers`'s day-marker functions. An under-isolated test found this the hard way: it
  deleted 4 real `_done.json` markers before being caught (no document data lost; repaired by
  re-running the real backfill). **`vg09/store.py` has the identical exposure and currently
  has no tests at all** — the next test written for it must patch both
  `vg09.document.RAW_DIR` and `vg09.store.RAW_DIR`, not just the former
- KB-011: Ollama's chat template always renders the system message first, regardless of its
  position in the `messages` array (verified via the real `/api/show` template) — this means
  T-008's "system prompt last" front-truncation mitigation doesn't transfer to `/api/chat`;
  the token-budget packing has to do the real work once Phase 2 uses `/api/chat`
- KB-002 upgraded provisional → verified: the weekend-empty-list pattern held with zero
  exceptions across all 56 days of T-015's real backfill (16/16 weekends), not just the
  original 14-day sample

**Blocked / needs me:**
- **T-017** (YouTube backfill) is blocked on a transcript-path decision among (a) wait out
  the `IpBlocked` block, (b) `yt-dlp` audio + local Whisper transcription, (c)
  title+description only for this pass. **Decision day: 2026-09-18** (day 4 of the 3-week
  plan, per the mapping recorded in T-017's ticket — confirm or correct it)
- T-014's frozen evaluation dataset can't close until T-017 lands (HF-side question drafting
  can start now against T-015's real data, per T-014's updated acceptance criteria)

**Next session should start with:**
1. **A single manual transcript request against `nZYJdwM-_nI`** (manual, not an
   agent call — matches this session's "no agent YouTube calls" boundary) to check whether
   the `IpBlocked` block has cleared, **before** the T-017 decision gets made. Whether it's
   cleared or not directly changes which of options (a)/(b)/(c) are even live choices on
   2026-09-18.
2. Before writing any test for `vg09/store.py`: patch **both** `vg09.document.RAW_DIR` and
   `vg09.store.RAW_DIR` (KB-010) — not just the former, or the test will silently touch the
   real `data/raw/` directory the way `tests/test_sync.py` originally did.

**Doc updates made:** D-006, D-007 · KB-002 (upgraded to verified), KB-008 (updated with new
evidence), KB-009, KB-010, KB-011 · `docs/DESIGN.md` (§ Context budget, § YouTube chunking, §
Fallback documents and pending markers, § Answer generation, § Interfaces and contracts) ·
`docs/PLAN.md` (Phase 1: collectors, chunk/embed/store, HF backfill, HF catch-up all ticked)
· `docs/TICKETS.md` (T-008, T-009, T-010, T-012, T-013, T-015, T-016 closed; T-017 written,
`status: blocked`; T-014 dependencies split HF-now/T-017-to-close) ·
`docs/sessions/2026-09-16-phase-1-ingest.md`

---

## 2026-09-15 — Phase 0 complete (T-001–T-007)

**Tickets:** T-001, T-002, T-003, T-004, T-005, T-006, T-007 · **Tree:**
docs/sessions/2026-09-15-phase-0.md

**Done this session:**
- T-001: committed GOAL.md/PLAN.md, rewrote CLAUDE.md's "What this is"
- T-002: YouTube captions feasibility — 20/20 succeeded across 4 channels (KB-001, D-001)
- T-003: HF Daily Papers feasibility — 14-day fetch, field shapes confirmed (KB-002)
- T-004: first local-model pair test, llama3.1:8b + qwen2.5:32b (KB-003)
- T-005: ChromaDB date-range filtering confirmed working (KB-004, D-004)
- T-006: needle test (KB-005), Chroma's default embedder's 256-token dead-code bug
  (KB-006), replaced the model pair with qwen3:8b + qwen3:30b-a3b + bge-m3 embedding
  (KB-007, D-005, supersedes D-003)
- T-007: re-verified KB-007 via `/api/chat`, corrected a real error in KB-007 (VRAM does
  not grow with conversation length — it's pre-allocated at `num_ctx` load), filled in
  CLAUDE.md's "Hard rules" and "Stack" sections, ran `grill-me` on Phase 0 as a whole
- `docs/PLAN.md`'s Phase 0 checklist fully ticked; Phase 0 approved as complete

**In progress / half-finished:** nothing — Phase 0 is closed, Phase 1 has not started.

**Learned (not obvious from the code):**
- Ollama's default `num_ctx` is 32768, not the model's trained max — and an undersized
  `num_ctx` silently drops the **front** of the prompt with zero error signal (KB-005).
  This is now a hard rule, not just a KB note.
- ChromaDB's default embedding model has a hard 256-token limit, and its own "document too
  long" safety check is dead code — the tokenizer truncates before that check ever sees the
  real length (KB-006). Also now a hard rule: `bge-m3` always, explicitly.
- HF Daily Papers' `publishedAt` field is *not* the date the `date=` query matches on —
  `paper.submittedOnDailyAt` is (KB-002). This became D-002 ("feed date"), the semantic
  foundation the whole date-aware retrieval claim rests on.
- A cold-start model call can make a larger model look faster than a smaller one purely
  from one-time disk-load overhead — always compare warm timings (T-004, KB-003).
- Ollama's `think:false` does not suppress a Qwen3 model's reasoning — it just stops the
  reasoning from being separated into the `thinking` field, and merges it into the answer
  field instead. Confirmed on both `/api/generate` and `/api/chat` (KB-007).
- `qwen3:30b-a3b` (MoE) is described by VRAM footprint (~20GB), not "large" — it has fewer
  *active* parameters per token than the dense `qwen3:8b` (~6GB). "Large vs small" is the
  wrong frame for this pair (D-005).
- Dead end worth remembering: a bare `except Exception: pass` around `delete_collection`
  and around a VRAM-polling thread both looked harmless but would have silently hidden a
  real error as something else entirely — caught in `grill-me` passes, not by inspection.

**Blocked / needs me:** nothing currently blocked. One item flagged for Phase 1 design,
not a blocker: `docs/PLAN.md`'s risk register now has an unaddressed item — nobody has
estimated whether a real RAG prompt (system + retrieved chunks + history + question) stays
under `num_ctx=16000` before chunk size / retrieval top-k get finalized.

**Next session should start with:** Phase 1 planning — turn `docs/PLAN.md`'s Phase 1
checkboxes into tickets with `ticket-write`, and resolve the risk-register item above
(token-budget estimate) as part of the chunking design, before writing the collector code.

**Doc updates made:** D-001, D-002, D-003 (superseded), D-004, D-005 · KB-001 through
KB-007 · `docs/PLAN.md` Phase 0 fully ticked, Phase 1 risk register updated ·
`docs/GOAL.md` rewritten for "feed date" · `CLAUDE.md` Stack and Hard rules filled in ·
`docs/TICKETS.md` T-001–T-007 all closed

## <YYYY-MM-DD> — Project initialised

**Tickets:** — · **Tree:** —

**Done this session:**
- Harness installed: CLAUDE.md, docs, skills

**In progress:** nothing yet

**Learned:** —

**Blocked / needs me:**
- <…>

**Next session should start with:**
- <one concrete action>

**Doc updates made:** initial creation
