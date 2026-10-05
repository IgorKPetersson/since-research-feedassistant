# Session tree · 2026-10-05 (evening) · Slidev deck and the security baseline

**Tickets:** T-048, T-070–T-079 · **Handoff:** docs/HANDOFF.md § 2026-10-05 (evening)
**Previous:** docs/sessions/2026-10-05-self-update-answer-fixes-frozen-eval.md
**Read this if you want to know:** why the app renders its own answer HTML, why the source
markers carry no number, and why the deck lives on its own branch.

## 1. Recovery after the previous session ran out of tokens  [T-069]
   - 1.1 Read the previous transcript's tail; nothing half-done in code
     · outcome: tree, KB-029–031 and handoff written from it (d16ad11)
   - 1.2 "Report" in GOAL/PLAN contradicted the 2026-10-02 "no written report"
     · outcome: wording fixed (f746f40); later partly reversed by T-076

## 2. Presentation as a Slidev deck  [T-048, T-070, D-019]
   - 2.1 Slidev, in Since's own look,
     timeline as carrying visual, the three graded runs as a chart
     · outcome: draft on branch `t/T-048-slidev-deck`, not merged
   - 2.2 **Incident:** `slidev --remote false` exposed the dev server on every interface
     · outcome: stopped in ~2 min; KB-032 (its "public address" claim is wrong, see § 5.1)
   - 2.3 `slidev build` failed with a fresh install
     · outcome: a known-good lockfile used; KB-033
   - 2.4 Slides first, then the app live; screenshot kept as a reserve slide
     · outcome: done (6364846 on the deck branch)
   - 2.5 Dashes and odd Swedish in the deck text
     · outcome: all text rewritten

## 3. The security requirement  [D-020, T-071–T-077]
   - 3.1 Audit: Streamlit on every interface; answer rendered with unsafe_allow_html;
     no source-as-data framing; Ollama already 127.0.0.1
     · outcome: spec in DESIGN § Security baseline, D-020, seven tickets
   - 3.2 Docker and authentication
   - 3.3 Re-running the graded evaluation after the prompt change
     · outcome: not done; to be stated openly

## 4. Network  [T-071]
   - 4.1 Measured before: 0.0.0.0 and [::]; only Windows Firewall kept others out
     · outcome: `server.address = 127.0.0.1`; Since.bat checked
   - 4.2 The public IPv4 belongs to the router, not the machine; the machine has global
     IPv6; Node has an inbound allow rule on Private
     · outcome: recorded in T-071; KB-032 needs superseding (unresolved)

## 5. "The links are gone" and slowness  [—]
   - 5.1 Citations bunched at the end: measured on the 2026-10-02 code vs main in a worktree
     · outcome: same rate before and after (3/12 vs 2/12): model behaviour, not a change
   - 5.2 Slowness was the agent's own measurement sharing the GPU; T-067 added ~3 s on one
     question
     · outcome: explained with numbers

## 6. "research" means papers  [T-078]
   - 6.1 T-068 had knowingly counted "research" as a paper word
     · outcome: removed; eval questions 7 and 11 affected (stated)

## 7. Chips shown as raw HTML  [T-072, KB-034]
   - 7.1 Not reproduced by 10 real answers or 8 layouts; 25 and 30 were the same video
     · outcome: ruled out titles and layouts
   - 7.2 Backtick code span swallows chips: reproduced in markdown-it-py and Streamlit
     · outcome: KB-034
   - 7.3 Render the answer in the app (markdown-it-py, HTML/links off, chips only in text)
     · outcome: built, dependency approved; injected HTML shown as text
       in a real browser

## 8. Date phrases  [T-079]
   · outcome: understood; "the 5 days before X" deliberately not

## 9. Prompt injection and citation rules  [T-073]
   - 9.1 Baseline: blunt injections 0/20; a quiet "editor's correction" steered 2/5
     · outcome: six attacks scripted, store untouched
   - 9.2 **Dead end:** V1 prompt naming "corrections addressed to you" and allowing to
     mention them: steered 4/5
     · outcome: rejected
   - 9.3 **Dead end:** numbered `<<<SOURCE N BEGIN>>>` markers made the model cite
     "Source N" (93–103 per run), which never becomes a chip; all unit tests still passed
     · outcome: rejected; unnumbered markers
   - 9.4 V3 shipped: 0/30 steered, 0 "Source N", 0 bunched, no bare "Yes"
     · outcome: `docs/eval-results/2026-10-05-t073-prompt-injection.md`

## 10. Reach and no tools  [T-074, T-075]
   - 10.1 HF feed date became a folder name unchecked; ids validated to real formats
     · outcome: done; Streamlit usage statistics were on by default, now off
   - 10.2 Google Fonts loaded by the browser
     · outcome: explained, kept (unresolved: could be self-hosted)
   - 10.3 No-tools test and CLAUDE.md hard rule
     · outcome: done, shown to catch a planted `tools` field

## 11. Open
   - T-076 overview (English), T-077 deck slides, T-070 day-of checks: todo
   - Deck branch not merged; KB-032 correction and INDEX merge pending: unresolved
