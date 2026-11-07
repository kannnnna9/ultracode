---
name: audit
description: Check the stack itself — costs, dead skills, drift, compliance.
version: 1.0.0
author: Hermes operator, derived from ECC skill-stocktake + skill-comply (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, stocktake, compliance, maintenance]
    related_skills: [learn, context]
---

# Audit — is the stack still earning its keep

Run monthly, or when quality drifts, or after adding skills. Not on every task.

## 1. Static audit (script)

```bash
python scripts/audit.py --root .
```

Reports:

- **Index cost** — characters of every registered skill's name + description (what every turn pays).
  Budget: ≤ 2,500 chars for the core set. Over budget → cut descriptions or retire a skill.
- **Dead weight** — skills with no inbound reference and no trigger overlap.
- **Broken links** — `related_skills`, `references/`, library paths that do not exist.
- **Library size** — packs on disk (cheap) vs packs actually read in recent sessions (useful).
- **Drift** — vendored packs older than their upstream, contract version vs plugin version.

## 2. Compliance sample

Take the last 3–5 sessions (`session_search`) and check:

| Question | Evidence |
|---|---|
| Was a process skill loaded before implementation? | tool calls in the transcript |
| Was verification run before "done"? | the command + output in the final message |
| Were rulings recorded when the plan was deviated from? | ledger / message |
| Did the contract fire once (not twice)? | the injected marker appears once |
| Did any task take more than a third of the window? | transcript length |

A skill that is never followed is either wrong or invisible. Fix the trigger, or delete it.

## 3. Prune

For each skill: **keep** (used, correct), **merge** (overlaps a sibling), **rewrite** (right idea,
wrong trigger), **delete** (never used, duplicated, or harness-specific). Deleting is normal
maintenance — an index that only grows is a tax on every session.

Rules for pruning:

- Never delete a skill whose only home is the stack and whose content is still true — rewrite the
  description first.
- Merge before you add. Two skills with the same trigger are one skill.
- Keep the contract under ~2,000 words; it is paid every turn.

## 4. Report

```
Audit — <date>
Index     core 13 skills, 1,840 chars (budget 2,500)  PASS
Links     42 checked, 0 broken                        PASS
Library   71 packs, 12 read in last 30 days           OK
Drift     3 packs behind upstream                     NOTE
Compliance  4/5 sessions verified before "done"       NOTE — see session 2
Actions   merge ultra:context into ultra:build? no — different triggers; rewrite description
```
