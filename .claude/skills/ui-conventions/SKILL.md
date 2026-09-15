---
name: ui-conventions
description: This project's interface rules — layout and component conventions, states that are not the happy path, copy and labelling, accessibility floor, and the code conventions that go with them. Use this skill before writing or changing any component, screen, control or piece of user-visible text, including error messages, empty states and placeholder copy. Also use it when deciding how a new capability should be presented to the user, or when the user asks how something should look or behave.
---

<!--
  ADAPT BEFORE USE. This is a template.
  Replace every <angle-bracket> section with what is actually true for this project, and
  delete the rest. Generic UI advice teaches the model nothing it doesn't know; the value
  here is entirely in the project-specific parts.
-->

# Interface conventions

<One or two sentences on what the interface is for and what it must not become.>

## Non-negotiables

<The three to six rules that are actually violated in practice. Examples of the shape:>

1. **<State flows in one direction.>** <No component holds and sends domain state
   directly; it goes through the designated layer.>
2. **<Defaults preserve what the user already has.>** <Nothing is silently reset.>
3. **<Speak the user's language, not the system's.>** <No internal parameter name is ever
   visible in the UI.>
4. **<The user never re-enters what they already gave us.>**

## Components and controls

<Which component library or primitives, and what not to reach for.>

Pick the control that needs least explanation:

| Kind of value | Control |
|---|---|
| Continuous with a natural range | Slider, with the value shown |
| Small enumeration | Select or segmented control |
| Open-ended | Text field |
| Approximate or best-effort | A suggestion, **never** a precise-looking control |

That last row matters more than it looks. A control that presents itself as a setting but
is really a hint teaches the user a false model, and when it doesn't hold they stop
trusting the controls that do work. Represent approximate things honestly.

## States that are not the happy path

Every screen needs these, written before the feature is called done:

- **Loading** — <real progress if the numbers exist; a spinner is a choice to hide them>
- **Empty** — no data yet. Point at the next action, don't just say "nothing here"
- **Error** — what happened, whose fault it is, what to do next. No stack traces, no codes
  without words
- **Offline / dependency unavailable** — <the most likely first-run state>
- **Permission denied** — <distinct from error>
- **Destructive action** — <confirmation policy>

## Copy

- <Voice: plain, second person, no exclamation marks…>
- <Terminology list: say "X" not "Y">
- Never lose what the user typed, in any error path

## Accessibility floor

Keyboard reachable, visible focus, labels tied to controls, contrast checked, no
information carried by colour alone. This is a small cost during the build and an expensive
retrofit afterwards.

## Code conventions

- <Framework, version, function vs class components>
- <Styling approach; what is banned>
- <Where types live and that they are imported, never redeclared>
- <What components may not do directly — network calls, storage, navigation>
- <File and folder naming>

## Before adding a new control

<If adding a control means touching several layers, name the skill or checklist that covers
it. Building the control alone produces something that looks like it works and changes
nothing — the most expensive kind of bug to find.>
