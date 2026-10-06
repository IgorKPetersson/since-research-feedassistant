# KB-039 — Claude Code signs commits by default, and runs a cached copy of a local plugin

**Area:** Tooling (Claude Code) — commits and plugins
**Status:** verified
**Date:** 2026-10-06  ·  **From:** T-081

## Claim
1. Unless `attribution` is set in the user settings, Claude Code ends every commit message
   it writes with `Co-Authored-By: Claude …` and every PR description with a "Generated
   with Claude Code" line. 157 of this repository's first 158 commits carried it. Setting
   `"attribution": { "commit": "", "pr": "" }` in `~/.claude/settings.json` stops it; a
   session picks the change up without a restart.
2. A settings file holding two JSON objects back to back is invalid, and Claude Code then
   ignores the whole file: permissions, hooks and plugins included. Nothing warns.
3. A plugin installed from a local directory marketplace runs from a copy under
   `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. Editing the source folder
   changes nothing until the plugin is reinstalled; with an unchanged version number,
   `uninstall` then `install` is the reliable way.

## Evidence
- `git log --format=%B | grep -c "Co-Authored-By: Claude"` → 157 before the rewrite.
- `python -c "json.load(...)"` on settings.json → `Extra data: line 229 column 2`; after
  repair the session received an instruction not to add attribution lines.
- After `claude plugin uninstall` and `install`, `diff -rq` between the cache and
  the plugin's source folder → no differences.

## Consequence for this project
History was rewritten with `git filter-repo` to remove the lines (it also removes the
`origin` remote every time it runs). New sessions must not add attribution lines.
