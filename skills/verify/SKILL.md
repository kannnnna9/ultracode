---
name: verify
description: Prove work is done with fresh commands before claiming it.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers verification-before-completion (MIT) + ECC verification-loop (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, evidence, tests, quality-gate]
    related_skills: [build, review, ship]
---

# Verify — evidence before assertions

```
NO COMPLETION CLAIM WITHOUT A COMMAND RUN IN THIS TURN AND ITS OUTPUT READ.
```

If you have not run it now, you cannot say it passes. Confidence is not evidence. A previous run is
not evidence. A subagent's report is not evidence.

## Pick the tier

| Tier | For | Phases |
|---|---|---|
| **1 — quick** | S tasks, one or two files | the one relevant command + read your own diff |
| **2 — standard** | M tasks, a feature slice | build/typecheck, tests, lint, diff review |
| **3 — full** | L/XL, before merge or release | tier 2 + coverage on touched files, security grep, e2e if it exists, requirements checklist, changelog |

Never run tier 3 on a typo fix; never ship a feature on tier 1.

## Discover the commands (do this once per project)

Look, in order: `package.json` scripts, `Makefile`/`justfile`, `pyproject.toml`
(pytest/ruff/mypy), `Cargo.toml`, `go.mod`, `pom.xml`/`build.gradle`, CI config (`.github/workflows`).
CI is the authority on what "green" means — copy its commands, not your guesses.

If no command exists for a phase, say "no <phase> configured" — never invent one and never count it
as passed.

## Phases (tier 3)

1. **Build** — compile/bundle. Exit code is the result.
2. **Types** — `tsc --noEmit`, `mypy`, `go vet`, `cargo check`.
3. **Lint** — the project's linter, unchanged config. If it fails on pre-existing code, report the
   baseline; do not "fix" unrelated files.
4. **Tests** — full suite for the touched area, with counts. Coverage only where the project tracks
   it, and only for files you touched.
5. **Security grep** — secrets, tokens, `.env` values, debug endpoints, `eval`, raw SQL built from
   input, new dependencies with loose ranges.
6. **Diff review** — read `git diff` end to end. Every hunk traces to the request; nothing
   unrelated, nothing orphaned, no commented-out code, no console.log, no TODO without a name.

Then the **requirements checklist**: re-read the spec/plan, one line per requirement, each marked
met / not met / deferred with a reason. Tests passing is not requirements met.

## Report format

```
Verification — <tier>
PASS  build      npm run build            exit 0
PASS  tests      vitest run               42/42 passed
FAIL  lint       eslint .                 3 errors (2 pre-existing in src/legacy)
SKIP  e2e        none configured
Diff             14 files, all traced to Task 2–4

Verdict: NOT READY — lint has 1 new error in src/api/orders.ts:88
```

State the verdict plainly. If anything failed, the work is not done; say what remains.

## Red flags

| Thought | Reality |
|---|---|
| "should pass now" | run it |
| "I'm confident" | confidence is not a result |
| "the agent said it succeeded" | check the diff |
| "linter passed, so the build is fine" | a linter is not a compiler |
| "partial check is enough" | partial proves nothing about the whole |
| "I'll note it as passing and fix later" | that is a false claim with extra steps |

## When it fails

Do not retry the same command hoping for a different result. Classify: environment (missing dep,
wrong node/python), flake (re-run once, note it), real failure → `ultra:debug`. Three attempts on
the same error is the loop breaker: stop and re-derive.
