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
