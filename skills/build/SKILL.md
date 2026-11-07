---
name: build
description: Execute a plan task by task with TDD, a ledger, and recorded rulings.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers executing-plans + subagent-driven-development (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [execution, tdd, ledger, subagents]
    related_skills: [plan, verify, debug, parallel, review]
---

# Build — execute the plan, prove every step

The plan did the thinking. Your job is to execute it exactly, prove each step with a test you
watched fail and then pass, and leave a record that survives your own forgetting.

## Setup (once)

1. **Isolation.** Work on a branch. Use a worktree when the operator wants the main checkout left
   alone, or when another agent may touch the same repo (`ultra:parallel`). Never start on
   `main`/`master` without explicit consent.
2. **Ledger.** `.ultra/ledger-<plan-basename>.md`, first line `# ledger — plan: <path>`. One line
   per task; rulings appended in the same message as the commit. The ledger is the record; todos
   are only a live view.
3. **Read** the plan and its spec. Note Global Constraints. Create one todo per task.
4. **Pre-flight interface scan.** For every task that consumes an earlier task's `produces`, check
   the pair now. Record a ruling for each conflict. This is where 80% of rework is prevented.

If the ledger already has `Task N: complete`, that task is done — trust the ledger and `git log`
over your memory after compaction. Resume at the first task without a line.

## TDD gate (every behaviour change)

```
RED    write the test, run it, watch it fail for the expected reason
GREEN  smallest change that passes; run it, watch it pass
REFACTOR  clean up; suite stays green
```

A test that passes before the implementation exists is a finding about the test. A fix without a
test that failed first is a diff and a hope.

Exempt (say so in the ledger): docs, pure config, throwaway spikes, code with no test harness —
then add a characterization test if cheap, otherwise record the manual evidence you used.

## Task loop (inline)

For each task:

1. Read the task's brief (the task block, not the whole plan). Mark the todo in progress.
2. Work its steps in order. Every command step has an `Expected:` line — run it, read the output,
   compare.
3. Three outcomes:
   - **matches** → next step;
   - **code is wrong** → `ultra:debug`, find the cause, never patch the symptom to match the step;
   - **plan is wrong** → smallest change that satisfies the spec, record
     `Task N: Ruling: <finding> — <what and why> — <cost if wrong>`, continue.
4. Commit as the plan says. A task may span commits.
5. **Completion contract** — all of these are true, with evidence in this session:
   - every test the brief names exists and ran;
   - the final run for the task passed, and you read the output;
   - every `Expected:` was compared against real output;
   - every deviation has a `Ruling:` line.
6. Append `Task N: complete (commits <a>..<b>, tests: <cmd> → <result>)`. Only if it passed.

Do not pause between tasks to ask "should I continue?". The operator chose execution to spend less
time, not to approve each task.

## Task loop (subagent per task)

Use when the plan is long, the tasks are independent, or the session context is already heavy.

1. Dispatch **one implementer** per task with a self-contained brief: goal, files, interfaces,
   constraints, the test that must fail first, and the exact evidence to return (test output, diff
   summary, rulings). Never give it the whole plan or "the repo context".
2. **Review the task** with a fresh reviewer (`ultra:review`, role `reviewer`) before the next one.
   Scope: the task's diff against its brief and its tests.
3. **Fix loop:** cap 3 rounds. Each round is RED→GREEN plus a green suite, recorded in the ledger.
   Round 4 means the task or the plan is wrong — stop and re-plan, do not keep nudging.
4. A subagent's "done" is a claim. Read `git diff` for the task range yourself before accepting.

| Mode | Cost | Buys |
|---|---|---|
| inline | one context + one final review | cheapest; no per-task second pair of eyes |
| subagent | fresh context per task + per review | isolation, per-task gate, long plans |

## Final review

1. Produce the review package: `git diff <merge-base>..HEAD`, plan, spec, Review Focus, ledger
   rulings.
2. Dispatch a fresh reviewer on the most capable available model (or review it yourself as a
   separate pass if delegation is unavailable — and say that it was self-review).
3. Re-grade findings by **effect on the user**, not by the spec's silence. Critical/Important go
   into **one** fix pass, each RED→GREEN. Minor goes to the ledger as deferred. No second fix pass.
4. Clean up the workspace, then `ultra:ship`.

## Rulings

A ruling is how a decision made alone becomes visible:

```
Task 3: Ruling: users table has no soft-delete column — filter on deleted_at IS NULL in the query,
not a migration — if wrong, deletes stay hard and we add the column later.
```

Every ruling reaches the final message under "Rulings I made", with its cost if wrong. Silent
deviation is forbidden; a stalled agent is worse.

## Rationalisations to refuse

| Excuse | Reality |
|---|---|
| "I remember what Task 4 says" | you remember a summary; the brief has the values |
| "skip watching it fail, obviously it fails" | a test you never saw fail proves nothing |
| "run the whole suite at the end instead" | per-step runs tell you which step broke it |
| "the plan is wrong, I'll just do the right thing" | do the right thing **and** ledger the ruling |
| "I'll write the ledger after a few tasks" | compaction does not wait for a convenient moment |
| "the reviewer said Minor" | re-grade by what a user gets, then gate |
