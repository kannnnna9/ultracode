---
name: debug
description: Find the root cause before proposing any fix.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers systematic-debugging (MIT) + ECC silent-failure-hunter (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, root-cause, regression, silent-failure]
    related_skills: [build, verify]
---

# Debug — root cause before fix

```
NO FIX WITHOUT A CAUSE YOU CAN STATE, AND A TEST THAT REPRODUCES IT.
```

A symptom patch is a second bug with better manners. If you cannot say *why* it broke, you are not
done investigating.

## Phase 1 — Read the actual evidence

- Read the full error, stack trace, and the lines it names. Not the summary someone gave you.
- Reproduce it deterministically. Minimal input, one command, same result twice.
- Establish the boundary: last known good vs first known bad. `git log`, `git bisect`, dependency
  diff, config diff.
- Check the boring causes first: wrong cwd, stale build, missing env var, wrong runtime version,
  cache, port already in use, file saved but not reloaded.

Write down: expected, actual, reproduction command, and what you have ruled out.

## Phase 2 — Pattern analysis

- Where else does this shape of code/state appear? A bug in one handler is usually a bug in three.
- What does the surrounding code assume that the failing path violates? Find the violated invariant.
- Compare with a working sibling: what differs — input, ordering, lifecycle, permissions?
- If the failure is silent (wrong value, no error), hunt the masks: `catch {}` and `catch (e) {}`,
  fallback defaults, `||`/`??` that swallow empty values, retries that hide timeouts,
  `try/except: pass`, promise rejections nobody awaits, nullable fields defaulted to `""`.

## Phase 3 — One hypothesis, one experiment

State it as a prediction: *"if X is the cause, then Y will change Z"*. Run the smallest experiment
that can falsify it. Change one variable. Read the output.

- Confirmed → Phase 4.
- Refuted → record what it ruled out, form the next hypothesis. Three refuted hypotheses on the same
  symptom means your model of the system is wrong: re-read the code path end to end instead of
  guessing again.

Do not "fix and see". That produces a diff you cannot explain, and you will not know which line did
it.

## Phase 4 — Fix, prove, harden

1. Write the test that reproduces the bug. Run it. **Watch it fail for the right reason.**
2. Fix the cause, not the symptom.
3. Run the test → green. Run the whole suite → green.
4. Prove the test is real: revert the fix, watch red, restore, watch green.
5. Add the neighbouring case the same cause would have hit, if it is cheap.
6. Say what the root cause was, in one paragraph a human can follow.

## Red flags

| Thought | Reality |
|---|---|
| "let me just try changing this" | you are guessing with the user's codebase |
| "it works now" | what changed, and why would it stay fixed? |
| "add a try/catch so it stops crashing" | you converted a bug into a silent failure |
| "increase the timeout" | you moved the symptom, not the cause |
| "it's flaky, re-run it" | flakiness has a cause: ordering, time, state, concurrency |
| "the test is wrong" | prove it: what should the behaviour be, per the spec? |

## When there is genuinely no root cause

Environment-only failures (DNS, CI image, a third-party outage) exist. Then: prove it is external
with evidence (curl the endpoint, check status page, reproduce outside the app), record it, and
report it as environmental — never quietly retry until green.

## Handoff

If the fix changes behaviour the spec did not anticipate, that is a design decision: surface it,
do not bury it in the commit.
