# Knowledge base — index

What this project knows about **the world**: verified behaviour, measurements, dead ends,
workarounds and constraints. Decisions live in `docs/DECISIONS.md`; design intent lives in
`docs/DESIGN.md`; session narrative lives in `docs/HANDOFF.md` and `docs/sessions/`.

Written and read via the `kb-entry` skill. **Read the relevant area before starting work in
it.** An entry not listed here does not exist, because nobody browses directories.

Entries are `docs/kb/KB-0NN-slug.md`. IDs sequential, never reused. A wrong entry is never
edited in place — it is superseded by a new one and marked.

## Areas

<list the subsystems and dependencies this project will accumulate knowledge about>

## Entries

| ID | Claim | Area | Status | Date |
|---|---|---|---|---|
| | | | | |

_One row per entry, newest at the bottom, added in the same commit as the entry itself._

## What belongs here

- Verified behaviour that contradicts documentation — always write it
- A measurement, with numbers and conditions
- A dead end and the reason it failed
- A non-obvious workaround, its cost, and what would let us drop it
- A platform, licence, quota or library constraint discovered the hard way

## What does not

- Vendor documentation that behaved as documented — link instead of copying
- Our decisions → `DECISIONS.md`
- Session narrative → `HANDOFF.md`, `sessions/`
- Design intent → `DESIGN.md`
