# KB-033 — Slidev 52.20.1's build fails under a fresh install; an older lockfile builds

**Area:** Presentation (Slidev) — production build
**Status:** provisional
**Date:** 2026-10-05  ·  **From:** T-048

## Claim
With `@slidev/cli` 52.20.1 pinned, a fresh `npm install` (2026-10-05) resolved vite 8.3.2 and
@unhead 3.4.2, and `slidev build` failed in CSS minification:
`[lightningcss minify] Invalid token in pseudo element: Dimension … 1.5rem`. The offending
CSS was Slidev's own (`.slidev-code-line-numbers …`), not the deck's. The dev server worked.

## Evidence
- Same deck, same `package.json`, installed from an older, known-good `package-lock.json`
  (vite 8.3.1, @unhead 3.4.1): `✓ built in 1.51s`.

## Consequences
`presentation/package-lock.json` is that older lockfile with the package name
changed. Install with `npm ci`, not `npm install`, so the transitive versions stay as they are.

## Confidence and limits
Provisional: which of the changed transitive packages causes it was not isolated (vite
8.3.1 → 8.3.2 is the likeliest). It may be fixed upstream later.
