---
name: parallel
description: Fan out independent workstreams without collisions.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers dispatching-parallel-agents (MIT) + ECC multi-* (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagents, worktrees, fan-out]
    related_skills: [build, review, ship]
---

# Parallel — one agent per independent domain

## Decide first

```
2+ tasks?  ──no──▶ do it inline
   │yes
independent? ──no──▶ sequential (shared state, one fixes the other)
   │yes
share files? ──yes──▶ sequential, or split by file ownership
   │no
fan out
```

Fan out only when each lane can be understood and finished without the others. If fixing one might
fix another, they are one lane.

## Isolation

Each lane that writes code gets its own worktree and branch:

```bash
git worktree add ../<repo>-<lane> -b <lane> <base>
```

Read-only lanes (research, review, audit) need no worktree. Never let two lanes write the same file;
if the plan cannot avoid it, the lanes are not independent.

## The brief

Every child gets exactly this and nothing else:

```markdown
Goal:        one sentence, one deliverable.
Context:     the files to read, the interfaces it consumes, the exact values it needs.
Constraints: what it must not touch; the style to match; the stop list.
Do:          the steps, in order (TDD where behaviour changes).
Return:      diff summary · commands run + output · rulings · what it could not verify.
```

Never "you have full context" — the child has none of your conversation. Never paste the whole plan;
give the lane's tasks.

## Model tiers

| Work | Tier |
|---|---|
| transcription from a fully specified plan, single-file mechanical fix | cheapest available |
| implementing from prose, multi-file integration | standard |
| architecture, subtle concurrency, security, final whole-branch review | most capable available |

Turn count beats token price: a cheap model that takes 3× the turns costs more. Specify the model
where the harness allows it; where it does not, do the judgment work inline and delegate the
mechanical work.

## Integration

1. Read every returned diff yourself. A child's "done" is a claim.
2. Check for cross-lane collisions: same file, same interface, competing migrations.
3. Merge lanes in dependency order, running the suite after each merge.
4. Run the full verification once on the combined result — lanes that pass alone can fail together.
5. One final review of the combined branch (`ultra:review`, correctness + security).

## Anti-patterns

| Pattern | Why it fails |
|---|---|
| 6 agents on one feature | they collide on files and interfaces; you spend longer integrating |
| dispatching to avoid thinking | a vague brief returns vague work you must redo |
| trusting the report | the diff is the only truth |
| parallel writes to one database/app | state races; isolate or serialise |
| fan-out for a 20-line change | coordination costs more than the work |
