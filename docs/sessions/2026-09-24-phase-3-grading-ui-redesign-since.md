# Session tree · 2026-09-22 → 2026-09-24 · Phase 3: grading, rename/README, UI redesign, "Since"

**Tickets:** T-039, T-040, T-035, T-034, T-036, T-041, T-033, T-042, T-043, T-044, T-045,
T-046, T-047 · **Handoff:** docs/HANDOFF.md § 2026-09-24
**Previous tree:** docs/sessions/2026-09-20-phase-2-grillme-and-closeout.md
**Read this if you want to know:** why a citation bracket with more than 5 numbers is
"descriptive" (D-015), why a top-level `[theme]` in `.streamlit/config.toml` is wrong,
why the chips have dark text, why the visual-identity ticket is T-045 and not T-044, or
why the logo mark is nudged -0.5px.

## 1. T-032 grading lands, T-039 committed, T-040 range citations  [T-039, T-040]
   - 1.1 T-032 graded (A better 8, B better 0, equivalent 5, both wrong 2)
     · outcome: committed under T-039
   - 1.2 Range brackets `[1-20]` weren't linked (T-028 only handled commas)
     · outcome: T-040 built. Threshold is ≤5 numbers = citation, more = descriptive, a
       decision recorded as **D-015**. `[1-31]` in F12 is enumeration, not 31 citations.

## 2. Pre-merge verification of T-039/T-040  [T-039, T-040]
   - 2.1 Live retry probe: `NUM_PREDICT` patched to 500 in-process only, 3 real questions
     · outcome: all four retry checks passed live. This closed T-039's "only mocked" gap (`ca55d61`)
   - 2.2 deep-review: `expand_part()` materialised `range()` before the threshold check
     (7.4s for `[1-500000000]`)
     · outcome: fixed as `part_bounds()`, which checks the size first (`a03650b`), then merged and pushed

## 3. T-035 rename and T-034 README/LICENSE/fresh clone  [T-035, T-034]
   - 3.1 Process slip: T-035 was committed straight onto local `main`
     · outcome: moved to its branch and `main` reset to `origin/main` before any push
   - 3.2 A YouTube backfill was running mid-T-034
     · outcome: it was T-034's own fresh-clone test, writing only inside the scratch clone
       (`RAW_DIR` is relative to that copy of `vg09/`), not the real `data/raw/`. Explained
       and verified, not stopped. **Lesson: announce a long real run before starting it.**
   - 3.3 Fresh clone passed end to end, nothing needed fixing (`52c2619`)

## 4. T-036 tests for the two risk-register modules  [T-036]
   - 4.1 · outcome: 13 tests, no production defects found; merged

## 5. Phase 3 grill-me, then T-041  [T-041]
   - 5.1 Findings: stale DESIGN.md numbers (27/13245 → 24/11787); comma-list bypass of
     D-015; missing `prompt_eval_count` check in a probe script
     · outcome: all three fixed in T-041. D-015's threshold now uses the summed span across
       all pieces (D-015 Follow-up paragraph).
   - 5.2 Phase **not** declared done: report and presentation remain
     · outcome: unresolved

## 6. T-033 model-size comparison  [T-033]
   - 6.1 · outcome: run, then graded (A better 4, B better 0, equivalent 9, both
     wrong 2). Notes kept: 8b is slower (dense vs MoE, D-005); 8b enumerates instead of
     ranking (F03/F04/F06); drifted into Chinese in F13; F12/F14 missed by both models, so
     that's a retrieval problem, not model size

## 7. T-042 UI redesign  [T-042]
   - 7.1 Asked: switch the UI from Swedish to English?
     · outcome: English, recorded as **D-016**
   - 7.2 Live-found: `st.metric` truncated "Unfiltered" and the freshness date
     · outcome: shorter labels; freshness moved to a caption
   - 7.3 Live-found: a stale Streamlit server kept serving old code
     · outcome: practice from here on is to stop the server and restart on a fresh port
       before every live check

## 8. T-043 English date parsing  [T-043]
   - 8.1 · outcome: English phrases mirror the Swedish rules. Real English translations of
     all 15 eval questions give 8 right, 0 wrong, 7 unresolvable-and-correctly-so, identical
     to Swedish. Merged together with T-042

## 9. T-044 pipeline strip tweaks and the 1184-vs-1225 question  [T-044]
   - 9.1 · outcome: "Date range" tile shows the real resolved window; metrics sized below the
     answer; screenshots retaken. 1184 papers + 41 videos = 1225, so not a bug

## 10. T-044/T-045 numbering mix-up  [T-044, T-045]
   - 10.1 The unnumbered pipeline tweaks had been numbered T-044. The visual identity
     was also called "T-044" and was filed as T-045.
   - 10.2 A merge of `t/T-044-ui-polish` was expected to include the visual identity
     · outcome: caught before any merge. Decision: numbers stay as they are, and the
       mix-up is recorded in T-045's ticket. **Lesson: a renumbering is a question to raise,
       not a status line.**

## 11. T-045 visual identity  [T-045]
   - 11.1 Asked: single accent on chips too (reversing T-042's paper/video chip colours)?
     · outcome: one accent everywhere
   - 11.2 Six real Streamlit bugs found live, all fixed. The list is in T-045's ticket
     · outcome: promoted to KB-020 (theme sections) and KB-021 (CSS injection)
   - 11.6 Retrieval took ~40–100s per question in every live run today
     · outcome: **unresolved**, recorded as provisional KB-023
   - 11.3 Ask button's white label on the amber is 3.32:1
     · outcome: **unresolved**, flagged as a design call (change the accent or override
       Streamlit's button states)
   - 11.4 One run answered only "Yes [18]"
     · outcome: noted as answer variance, no ticket unless it recurs
   - 11.5 Follow-ups: grey source badges (red read as an error), text-colour links with an amber
     underline, placeholder confirmed on an empty field
     · outcome: done (`192ab15`)

## 12. T-046 logo mark and lockup  [T-046]
   - 12.1 Mark SVG in the header and as the favicon (the same file; `page_icon` accepts a `.svg` path)
     · outcome: done
   - 12.2 "Slightly heavier" wordmark isn't possible: 700 is Instrument Sans's maximum
     · outcome: weight left at 700, flagged; KB-022
   - 12.3 Lockup brief was self-contradictory: the dot (9px) is already smaller than the S
     (15px), so "match the S" would enlarge an "oversized" dot
     · outcome: compared zoomed; 26px kept
   - 12.4 Dead end: `margin-top: -1px` to raise the mark
     · outcome: abandoned. A margin in a flex row moves the whole row and only half-shifted
       the mark. `line-height: 26px` plus `top: -0.5px` gives 0.0px centre error at 1×.
       **Not obvious from the code.**

## 13. Merge, README, close  [T-047]
   - 13.1 T-044..T-046 fast-forwarded to `main` and pushed (`c21b19b`), 207/207 tests
   - 13.2 README: "Since" name and logo, plus three stale UI statements corrected
     · outcome: committed on `t/T-047-readme-since`, **not merged** (not asked)
