---
name: <skill-name>
description: <What this skill does, concretely — one sentence.> Use this skill whenever <the situations it applies to>, when the user says <the words a real person would type>, or when <the sneaky case that sounds trivial but isn't>. <If a neighbouring skill exists: Do not use it for X, which is the <other-skill> skill.>
---

<!--
  The description above is the only thing seen when deciding whether to load this skill.
  Three to five lines. Third person. Include the vocabulary the user uses, not just the
  vocabulary the code uses. Use the write-skill skill for the full guidance.

  Directory name must match `name` exactly. Lowercase, hyphens.
-->

# <Skill title>

<One paragraph: what this covers and why it is easy to get wrong. If there is a
characteristic failure mode — something that breaks silently, or looks fine and isn't —
name it here. That framing is what makes the rest of the skill stick.>

## Before starting

<What to read, check or confirm first. Real paths, real commands.>

## The procedure

<The steps, in the order they must happen. Explain the *why* behind the non-obvious ones —
an agent that understands the reason handles the case you didn't anticipate.>

### 1. <step>

<what to do, and what "done" looks like for this step>

### 2. <step>

### 3. <step>

## Checklist

```
[ ] <…>
[ ] <…>
[ ] <…>
```

## When to stop and ask

<The situations where proceeding is worse than pausing. Be explicit; "use judgement" is not
an instruction.>

- <…>
- <…>
