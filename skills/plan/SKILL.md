---
name: plan
description: Write an implementation plan a fresh engineer can execute task by task.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers writing-plans (MIT) + ECC blueprint (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, tasks, blueprint, interfaces]
    related_skills: [discover, build]
---

# Plan — the decisions the implementer cannot make alone

Input: an approved design, a spec, or a precise request. Output: a plan file where every step is
one action with a checkable result.

Save to `docs/ultra/plans/YYYY-MM-DD-<feature>.md`, commit it, and link it for review.

## 1. Scope check

If the spec covers independent subsystems, split into one plan per subsystem. Each plan must
produce working, testable software on its own. Say so rather than writing a 40-task monster.

## 2. File structure first

Map every file created or modified and its single responsibility, before writing tasks. Prefer
small focused files; files that change together live together; in an existing codebase follow its
patterns instead of restructuring it.

## 3. Right-size the tasks

A task is the smallest unit that carries its own test cycle and deserves a fresh reviewer's gate.
Fold setup, config, and docs into the task whose deliverable needs them. Split only where a
reviewer could reject one task and approve its neighbour.

## 4. Plan header (required)

```markdown
# <Feature> Implementation Plan

**Goal:** one sentence.
**Architecture:** 2–3 sentences.
**Tech stack:** key libraries.
**Spec:** path to the design doc this plan argues from.

## Global Constraints
- exact versions, naming rules, platform requirements, one per line, copied verbatim from the spec

## Review Focus
- the five input classes / failure modes the spec implies but no task's tests cover, most likely first
```

Every task's requirements implicitly include Global Constraints.

## 5. Task shape

```markdown
### Task N: <component>

**Files:** create/modify/test, exact paths
**Interfaces:**
- consumes: exact signatures from earlier tasks
- produces: exact names and types later tasks rely on

- [ ] Step 1: write the failing test  → code block with the test and its exact values
- [ ] Step 2: run it                → command, expected: FAIL with "<reason>"
- [ ] Step 3: implement <signature> → file; body only if the algorithm is not implied
- [ ] Step 4: run it                → command, expected: PASS
- [ ] Step 5: commit                → exact git add paths + message
```

**Step granularity:** one action, one checkable result. A test step carries the test code and its
assertions. A code step carries the signature, the file, and the values the spec pins — the
implementer writes the body. A verification step carries the command and the output that means
passed.

A plan longer than the code it describes has written the code instead. A step that decides nothing
("handle edge cases", "add validation", "TBD") is the opposite failure. Both get fixed in self-review.

## 6. Self-review (run it, do not skip)

1. **Spec coverage** — every requirement points at a task. List gaps and add the tasks.
2. **Step scan** — every step lets the implementer write exactly one reasonable thing; nothing more.
3. **Type consistency** — names and signatures in later tasks match earlier `produces` blocks.
4. **Review Focus** — each listed failure mode has a test in the owning task. Empty means you
   checked, not that you skipped.
5. **Proportion** — plan vs spec length; if code blocks dominate, replace bodies with signatures.

Fix inline; no second review pass.

## 7. Blueprint mode (XL only)

For multi-session or multi-agent work, add before the task list:

```markdown
## Dependency graph
T1 → T2 → T4
T3 ─────→ T4        (T2 ∥ T3: no shared files)

## Lanes
- Lane A (serial): T1, T2, T4
- Lane B (serial): T3, then join at T4
```

Rules:

- A step may only run in parallel when it touches no file another lane touches.
- Each task gets a self-contained **context brief** (≤15 lines): what exists, what to read, what to
  produce. A subagent sees only its brief — never "read the repo and figure it out".
- **Mutation protocol:** if implementation proves a task wrong, update the plan file (task text +
  graph), record `Plan change: <task> — <why>` at the bottom, and only then continue. A plan that
  drifts without a diff is a plan nobody can resume.

## 8. Handoff

Say: plan path, task count, and which execution mode you recommend.

| Mode | When |
|---|---|
| `ultra:build` inline (this session) | tasks depend on each other's interfaces; plan is short; cheapest |
| `ultra:build` subagent-per-task | long plan, independent tasks, want a review gate per task, or the session context is already heavy |
| `ultra:parallel` | two or more lanes with no shared files |

Ask for plan review before implementing unless the operator already told you to go.
