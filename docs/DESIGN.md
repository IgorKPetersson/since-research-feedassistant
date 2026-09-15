# DESIGN

<How the system is built. This is the document read before touching architecture, the data
model or core logic. Keep it current — a design doc that lies is worse than none.>

## Architecture

```
<A diagram, even an ASCII one. Boxes and arrows beat three paragraphs.>
```

<One paragraph on what is deliberately absent — no backend, no queue, no cache — because
absences are what people accidentally add back.>

## Core model

<The central data structure or domain model, in code. If there is one thing the project
must get right, it is described here.>

```
<type definitions>
```

## Key flows

<For each important operation: what triggers it, what it touches, what it produces. A table
works well when there are several.>

| Trigger | Operation | Effect |
|---|---|---|
| <…> | <…> | <…> |

## Data model

```sql
<schema, or the storage layout>
```

<Why it is shaped this way. What a migration would cost.>

## Interfaces and contracts

<Anything two parts of the system agree on: API shapes, events, file formats. Changes here
are stop-and-ask territory.>

## What we deliberately don't build

- <…>
