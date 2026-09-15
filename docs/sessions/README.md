# Session trees

One file per working session: `YYYY-MM-DD-<slug>.md`, written with the `session-tree` skill
at the end of the session, or before compaction, whichever comes first.

A session tree is an **index into the conversation**, not a summary of the project. It
exists so a later agent or human can find the actual reasoning in the raw transcript
instead of trusting a paraphrase. Every node carries search anchors — literal strings from
the conversation — for exactly that reason.

| File | Answers |
|---|---|
| `docs/sessions/*.md` | Where in the conversation was this discussed, and what came of it |
| `docs/HANDOFF.md` | What state is the project in, what happens next |
| `docs/DECISIONS.md` | What was decided and why |
| `docs/kb/` | What we now know about the world outside our code |

Dead ends are the highest-value nodes in a tree. They are the one thing the code can never
tell you.
