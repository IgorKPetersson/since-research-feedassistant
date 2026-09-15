# CLAUDE.md — VG-09

Read this first, every session. It is the contract for how we work together on this repo.

## What this is

A local-first, open-source (Apache-2) research-feed assistant that collects Hugging Face
Daily Papers and a handful of chosen YouTube channels, and lets one person ask in plain
language what's new, whether a topic came up, or how a topic has developed over the last
n weeks — running entirely on their own machine with a local model.

See `docs/GOAL.md` for the full goal, problem, success criteria and non-goals, and
`docs/PLAN.md` for the phased plan and current phase.

## Read before you act

| File | When |
|---|---|
| `docs/GOAL.md` | Start of every session. What we're building and what "done" means. |
| `docs/DESIGN.md` | Before touching architecture, data model or core logic. |
| `docs/PLAN.md` | To find out what phase we're in and what's next. |
| `docs/TICKETS.md` | Before starting work. All work is a ticket. |
| `docs/DECISIONS.md` | Before proposing a change to a settled decision. |
| `docs/kb/INDEX.md` | Before working in an area we've already learned things about. |
| `docs/HANDOFF.md` | Start and end of every session. |

## Stack — settled, do not re-litigate

- Python (version not yet pinned)
- Everything else — framework, storage, key libraries — undecided; no code exists yet

If you think one of these is wrong, say so and stop. Don't route around it.

## Hard rules

Not yet written — there is no code to derive real rules from. Write these once the stack
and architecture in `docs/DESIGN.md` are settled, not before; invented rules are worse than
none.

## In-loop: when to stop and ask

Work autonomously inside a ticket, but **stop and ask me** when:

- A change would alter a schema, a public contract or a stored data format
- Reality contradicts our reference documentation (fix the doc, flag it, don't adapt
  silently)
- A milestone or phase gate is reached — that's a checkpoint, not a green light
- You're about to add a dependency
- You're about to contradict something in `docs/DECISIONS.md`
- A task would run more than ~10 tool calls with no natural review point
- Something is ambiguous in a way that affects the design, not just the code

**Do not** stop to ask permission for ordinary implementation work inside a ticket. Ask
about direction, not about typing.

## Work is tickets

Every change belongs to a ticket in `docs/TICKETS.md`.

- Unshaped idea → `spec-from-idea`, then `ticket-write`. Don't start coding from a chat
  message.
- No ticket for what you're about to do → write one first.
- Branch `t/T-0NN-slug` · commit `T-0NN: imperative summary` · PR `T-0NN — Title`
- One ticket ID per commit. Work that spills into a second concern becomes a new ticket.
- Think you're done → run `ticket-done` before saying so.

## Conventions

Not yet settled beyond the stack choice above. See `.claude/skills/project-conventions` —
also still a placeholder pending real code to derive it from.

- Comments explain *why*, not *what*. If the why is a project decision, cite `D-0NN`.
- Every non-obvious decision gets an entry in `docs/DECISIONS.md`.
- Anything learned about how a dependency really behaves goes in `docs/kb/` via `kb-entry`.

## Session protocol

**Start:** read `docs/HANDOFF.md` (latest note at the top), then `docs/PLAN.md` and the
open tickets. State in one line which ticket you're picking up before touching anything.

**During:** one ticket at a time. When something contested or consequential comes up, think
with `dual-pass` rather than agreeing quickly.

**End, in this order:**
1. `session-tree` → `docs/sessions/`
2. `kb-entry` → anything learned, into `docs/kb/`
3. `session-handoff` → the note that references both

## What the harness does on its own

The `workflow-harness` plugin runs four hooks so the process doesn't depend on anyone
remembering it:

- **Session start** — the latest handoff note, the open tickets and the git state are
  already in context. Don't ask for them; read what's there.
- **Before a commit** — a commit message with no ticket ID is blocked. That is deliberate,
  not a glitch. If the work has no ticket, write one.
- **Before compaction** — a reminder to write the session tree while the detail still exists.
- **Session end** — a note is left behind if the session ended with no handoff.

## Available skills

From the plugin (`/workflow-harness:<name>`, or just `/<name>` when unambiguous):

**Process** — `spec-from-idea`, `ticket-write`, `ticket-done`, `session-handoff`,
`session-tree`, `kb-entry`, `write-skill`, `harness-init`

**Thinking** — `dual-pass`, `grill-me`, `deep-review`, `defense-prep`, `parallel-agents`

**Subagents** — `reviewer` (adversarial review in a clean context), `verifier` (runs the
checks and reports evidence), `kb-librarian` (what this project already knows)

Project-local, in `.claude/skills/` — adapt these, they describe this repo:
`dev-environment`, `project-conventions`, `ui-conventions`.

Skills are triggered by what the work is, not by being asked. If a task matches a skill's
description, read the skill first.
