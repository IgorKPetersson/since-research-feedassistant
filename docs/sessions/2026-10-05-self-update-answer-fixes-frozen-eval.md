# Session tree · 2026-10-05 · Self-update, answer fixes, frozen re-evaluation

**Tickets:** T-059–T-069 · **Handoff:** docs/HANDOFF.md § 2026-10-05
**Previous:** docs/sessions/2026-10-02-finishing-pass-and-sources-page.md
**Read this if you want to know:** why the app updates itself on open, why the model is
told today's date, why the candidate pool is 200, and what T-069's numbers mean.

## 1. Session start: data 3 days behind  [—]
   - 1.1 Catch-up run by the agent: 136 papers, 3 videos → 1721 items, 2984 chunks
     · outcome: done, faster than the 10+ min estimate

## 2. The app must update itself  [T-059, T-060]
   - 2.1 A manual update does not meet GOAL, which promises "always caught
     up when you ask"
     · outcome: update starts when the app opens, setting to turn it off, Update now
       kept — D-018. A daily Windows scheduled task was **rejected**: it runs while the app
       is closed, which GOAL rules out (parked)
   - 2.2 Starting from a terminal is not how a user would open it
     · outcome: `Since.bat` double-click launcher (T-060); the browser opened
   - 2.3 Two browser tabs opened at launch
     · outcome: accepted as normal

## 3. "What has happened with AI today?" answered nothing  [T-061]
   - 3.1 Root cause (systematic-debugging): retrieval found 34 papers from 2026-10-05, but
     the model assumed its training-era date and discarded them as future
     · outcome: prompt carries today's date and the applied range; KB-029.
       **Invisible to every unit test.**

## 4. Context budget and inline links  [T-062, T-063]
   - 4.1 Is 73% of the budget waste? → no: 4000 tokens are reserved for the answer (D-005)
     · outcome: explained; relabelling offered, not taken up
   - 4.2 Citation numbers should link straight to the source; keep the source list
     · outcome: T-062 built, checked in a browser (hover text not captured by screenshots)
   - 4.3 Video link opened at 9:32 but the quote is at 9:50
     · outcome: a verbatim quote is located in the caption lines and linked 2 s early
       (T-063); paraphrases keep the excerpt start with an honest hover text
   - 4.4 Dead end, not built: 15-second excerpts so every link is precise
     · outcome: rejected — reindex plus re-run of the graded evaluation for a link nicety

## 5. Quotes credited to the wrong source  [T-064, T-065]
   - 5.1 The model said a second video contained the same Claude Code quote; it didn't
     · outcome: T-064 warns under the answer when a quote is not in its cited source; KB-030
   - 5.2 The new check flagged quoted titles
     · outcome: fixed, T-065

## 6. Probe: 18 made-up questions  [T-066, T-067, T-068]
   - 6.1 Date phrases ignored ("yesterday", "on Friday", "since Monday", "between X and Y")
     and wrong weekdays from the model
     · outcome: T-066 — phrases parsed, weekday given to the model
   - 6.2 "What's new" answers had no papers: 60 candidates all from 6 news videos, the
     2-per-document cap left 12 excerpts, 39% of the budget
     · outcome: pool 60 → 200 (T-067): 18 papers, 97% (the ticket's numbers; the chat
       said 39%/98%); KB-031
   - 6.3 "papers yesterday" got 0 papers even at 400 candidates
     · outcome: a question naming papers or videos filters to that source (T-068)
   - 6.4 Findings reported but **not ticketed:** model guesses channel names (#4), "three
     latest videos" picks wrong ones (#5), old "next week" read as future (#6), an answer
     with right sources but no citations, Palantir not linked to "Palunteer" (F12)
     · outcome: **unresolved** — parked, optional

## 7. Re-run of the evaluation on the frozen dataset  [T-069]
   - 7.1 The live store has 5 papers ≤ 2026-09-16 the frozen set lacks, so the answer key
     doesn't apply to it
     · outcome: separate store from the frozen archive, manifest-checked, live data untouched
   - 7.2 Graded: A 7 · B 1 · equivalent 5 · both wrong 2. F06 is a ranking error,
     F14 failed for the sixth time (semantic gap, not pool size)
     · outcome: ticket, PLAN risk register, presentation updated; file corrected
       after a mismatch between boxes and totals
   - 7.3 Presentation: three runs side by side, "never worse" claim dropped; T-069's arm A
     is full production behaviour, not a pure measure of the date claim
     · outcome: done (3df81d0)

## 8. What is left  [T-048, T-056]
   - 8.1 Only Phase 3 "Report and presentation" remains; waiting on an outline
     · outcome: **unresolved**
   - 8.2 The reading of "24/7" in GOAL.md is not confirmed
     · outcome: **unresolved**
   - 8.3 Session wrap-up promised but not done before tokens ran out
     · outcome: done next session (this file)
