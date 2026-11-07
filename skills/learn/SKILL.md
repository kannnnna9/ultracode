---
name: learn
description: Turn a repeated lesson into a skill, a rule, or a memory entry.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers writing-skills (MIT) + ECC continuous-learning-v2 / rules-distill (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, memory, rules, authoring, distillation]
    related_skills: [audit, library]
---

# Learn — where a lesson goes

A lesson repeated twice is a candidate. Three times is a defect in the stack.

## Choose the home

| The lesson is… | Home | Example |
|---|---|---|
| a durable fact about the operator, machine, or standing preference | Hermes memory | "user works from phone, wants the agent to run commands" |
| a procedure with steps, pitfalls, and a check | a skill | "how to mod an APK on this VM" |
| an invariant that must never be violated | `AGENTS.md` rule (≤12 lines) | "never weaken a lint config to pass" |
| project state or a decision | repo file (`PROGRESS.md`, `docs/adr/`) | "we chose SQLite because…" |
| something that happened | `session_search` | — |

Never duplicate. If a fact is in memory, the skill links to it; it does not restate it.

## Writing a skill

Frontmatter (Hermes):

```yaml
---
name: kebab-case-name
description: Trigger first, ≤60 chars, ends with a period.
version: 0.1.0
author: <human>, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [..]
    related_skills: [..]
---
```

Body order: **When to use** (with counter-triggers) → **Prerequisites** → **Procedure** (numbered,
each step with a checkable completion criterion) → **Pitfalls** → **Verification**. Cut anything
that does not change behaviour: "be careful", "use best practices", and marketing intros are noise.

- The `description` is paid on every turn of every session — front-load the trigger, no marketing.
- Reference Hermes tools (`read_file`, `patch`, `terminal`, `search_files`, `delegate_task`), not
  shell utilities the tools already wrap.
- No machine-local paths in a skill meant to be reused.
- Heavy material goes in `references/` next to the skill, pointed to from the body.

## Test it like code (RED → GREEN)

1. **RED** — write the task prompt that currently fails without the skill. Run it. Note the failure.
2. **GREEN** — write the minimal skill that fixes that failure. Run the same prompt again.
3. **REFACTOR** — tighten wording, close the loophole the model rationalised through, re-run.

A skill you never tested is a wish. The failure mode to design against is rationalisation: if the
model can talk itself out of a rule, the rule needs a red-flags table or a checkable gate, not
stronger adjectives.

## Distilling a rule

Promote a skill line into `AGENTS.md` only when it is (a) violated repeatedly, (b) checkable, and
(c) short. Format: one imperative line + why in parentheses. Delete the older wording it replaces —
rules accumulate sediment otherwise.

## Pruning

At `ultra:audit` time: a skill that has not been loaded in months, or whose content duplicates a
newer one, gets merged or deleted. A skill index that only grows is a tax on every session.

## Memory hygiene

- Write facts, not instructions: "User prefers X" ✓, "Always do X" ✗ (imperative entries get
  re-read as directives and override the current request).
- One fact per entry, declarative, dated when it can go stale.
- When memory is full, consolidate or delete stale entries — never skip the save silently.
