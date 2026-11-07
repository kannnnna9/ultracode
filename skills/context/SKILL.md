---
name: context
description: Keep the window healthy; compact at phase boundaries.
version: 1.0.0
author: Hermes operator, derived from ECC context-budget + strategic-compact (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [context, tokens, compaction, handoff]
    related_skills: [build, parallel]
---

# Context — the window is the budget

Every file you read, every log you print, and every tool result stays in the window for the rest of
the session. Cost is not the only issue: quality degrades as the window fills, and compaction loses
exactly the details you were relying on.

## Read narrowly

- Search before reading: `search_files` for the symbol, then `read_file` with `offset`/`limit`
  around it. Never open a 2,000-line file to find one function.
- Prefer `rg -n` through `terminal` for a wide sweep; it returns lines, not files.
- Do not re-read a file you just wrote. You know its contents; a verification command is cheaper.
- Skip generated files, lockfiles, minified bundles, and `node_modules` — say you skipped them.

## Keep output small

- Long test/build output: redirect to a file, read the last ~80 lines, and grep for
  `error|fail|warning` instead of dumping the whole log.
- Never print a whole diff into the conversation; write it to a file and read the hunks you need.
- For a big exploration, dispatch a subagent and take back a summary — that is what its isolated
  context is for.

## Compact at phase boundaries, never mid-task

Good moments: after the design is approved, after a task group is committed, before the final
review, before switching to an unrelated request.

Bad moments: mid-task, with uncommitted work, before the ledger line is written.

Before compacting, write the handoff (below) so the next context can resume without re-deriving.
Hermes compacts automatically when it must; the handoff is what makes that survivable.

## Handoff file — `.ultra/handoff.md`

```markdown
# Handoff <date>
Goal:        what we are building, one paragraph.
Done:        tasks/commits completed (sha + one line each).
Next:        the exact next action, with file paths.
Decisions:   rulings and why, one line each.
Open:        what is blocked and on what.
Read first:  the three files that matter most.
```

Update it at every phase boundary. It is also the file to hand a fresh subagent or a new session.

## Signals you are in trouble

| Signal | Move |
|---|---|
| you have re-read the same file twice | stop, write down what you know, then read once more |
| you cannot remember why a change was made | check the ledger/handoff; if absent, that is the lesson |
| tool output is longer than your reasoning | redirect to a file |
| you are summarising the conversation to yourself | compact now, at this boundary |
| the same search returns the same 40 hits | narrow the query, add a file glob |

## Rules of thumb

- One task's work should fit in roughly a third of the window. If it does not, the task is too big —
  split it (`ultra:plan`).
- Load a skill when you need its procedure, not to "have it around".
- The library is on disk: read the one pack you need, not the category.
