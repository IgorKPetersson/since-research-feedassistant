---
name: project-conventions
description: How code is written in this repository — language and typing rules, error handling, naming, file layout, testing conventions, and the patterns this project deliberately avoids. Use before writing or changing any code here, when deciding where a new file goes, or when a review needs to check a change against how this codebase actually works. Fill it in from the code rather than from general best practice.
user-invocable: false
---

<!--
  STILL A TEMPLATE. Only the language is settled (Python, see CLAUDE.md); everything else
  here needs real code to derive from. Fill in once there's a pattern to describe, not
  before — an invented convention is worse than an absent one.

  `user-invocable: false` is deliberate: this is background knowledge Claude should load
  when relevant, not a command anyone types.
-->

# How we write code here

## Language and typing

- Python. Version, typing strictness (e.g. `mypy --strict`) and annotation policy not yet
  decided — nothing has been written to decide it from.

## Error handling

- <What we do on failure, and what we never do. Where errors are logged, where they are
  surfaced. If empty catch blocks are the recurring sin here, say so.>

## Structure

- <Where things live: directory layout, what belongs in each layer>
- <What may not import what>
- <Where shared types live and that they are imported, never redeclared>

## Naming

- <Files, components, tests, branches, database columns — only where a real convention
  exists. Don't invent one here that the code doesn't follow.>

## Testing

- <Framework, where tests live, naming>
- <What must have a test: the boundary, the failure path, the regression>
- <What we deliberately don't test>

## Patterns we avoid, and why

<The most valuable section, because it encodes bugs already paid for.>

- <e.g. No singletons for anything holding request state — caused a cross-request data leak>
- <e.g. No new date library; the codebase standardised on one>

## When you're unsure

<Point at the closest good example: "match `src/features/billing/`, it's the pattern we're
converging on." A worked example beats a paragraph of description.>
