# Session tree · 2026-10-06 · History cleanup, license owner, deck text

**Tickets:** T-048, T-077, T-081, T-082, T-083 · **Handoff:** docs/HANDOFF.md § 2026-10-06 (evening)
**Read this if you want to know:** why the git history was rewritten three times, why the
presentation is no longer in the repository, and where my name sits in the license.

## 1. Deck review and merge  [T-048, T-077]
   - 1.1 Slide 4: is the chunk budget always 11 560? It is a ceiling, not a fixed amount
     · outcome: slide text says "upp till"; speaker note gives the 96–99 % fill measurement
   - 1.2 Possible question: a user without 24 GB VRAM
     · outcome: answered only. `qwen3:8b` works with a one-line change in
       `vg09/retrieval.py`; no setting exists. Possible future ticket, not written
   - 1.3 Deck branch merged into `main`, pushed, branch deleted locally and on GitHub
     · outcome: done

## 2. Claude attribution removed from the history  [no ticket: history rewrite]
   - 2.1 157 of 158 commits carried a Claude co-author line
     · outcome: removed with `git filter-repo --message-callback`; tree hashes identical
   - 2.2 Force-push from the agent was blocked by Claude Code's safety check
     · outcome: uploaded manually to a new private repository, compared, then the
       old `research-feed-assistant` and renamed to
       `since-research-feed-assistant`
   - 2.3 Dead end: making the old repository public as it was
     · outcome: rejected. It would have published the process notes as they stood

## 3. Documents in first person  [T-081]
   - 3.1 Documents: 381 lines in 37 files rewritten to "I", "me", "my"
     · outcome: done; line structure unchanged; 351 tests pass
   - 3.2 Dead end: the first automatic pass joined lines and wrote "I-readable"
     · outcome: reverted and redone with rules that keep line breaks
   - 3.3 Commit messages, then every old version of every file
     · outcome: done in three passes; only news content still says "human"
   - 3.4 Mistake found afterwards: five commit messages read "me's" instead of "my"
     · outcome: fixed in a further message rewrite at the end of the session
   - 3.5 The workflow plugin was the source of the wording
     · outcome: plugin wording fixed

## 4. What stays in the repository  [T-082, T-083]
   - 4.1 The presentation is for presenting, not for the people who use Since
     · outcome: removed from the repository and its history; kept on my machine,
       listed in `.gitignore`; five slide-only commits disappeared with it
   - 4.2 License: MIT or Apache 2.0
     · outcome: Apache 2.0 kept. `NOTICE` and the README carry "Copyright 2026 Igor
       Petersson"; `LICENSE` untouched
   - 4.3 the project rules and `.claude/` stay in the repository
     · outcome: decided (reversed 2026-10-08, T-086)

## 5. Deck text, slide by slide
   - 5.1 Slides 1, 2, 3, 4, 7, 8, 9 and 10 reworded
     · outcome: done; each checked in the running deck for overflow and fixed where it ran
       past the bottom line
   - 5.2 Slide 10 said only feeds the user added are contacted; the defaults are pre-selected
     · outcome: corrected to "de flöden du har valt"
   - 5.3 Slide 11 put Claude first as the author
     · outcome: retitled "Så byggde jag Since"; Claude Code named as the tool; 82 tickets

