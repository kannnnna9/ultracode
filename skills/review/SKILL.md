---
name: review
description: Request a rigorous review, and receive findings without theatre.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers requesting/receiving-code-review (MIT) + ECC code-reviewer (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, security-review, findings, severity]
    related_skills: [build, verify, ship, parallel]
---

# Review — four roles, one pass, no theatre

## Requesting

Pick the role(s) the diff deserves — not all four by reflex:

| Role | Looks for | Brief |
|---|---|---|
| **correctness** | logic errors, edge cases, state, concurrency, error paths | `references/roles/reviewer.md` |
| **security** | authz gaps, injection, secrets, unsafe deserialisation, SSRF, path traversal, dependency risk | `references/roles/security-reviewer.md` |
| **architecture** | boundary violations, coupling, duplication, wrong layer, future-cost | `references/roles/architect.md` |
| **tests** | missing cases, tests that assert nothing, mocks that hide the bug | `references/roles/test-reviewer.md` |

A reviewer gets: the diff range, the spec/plan, the Review Focus section if it exists, and the
ledger's `Ruling:` lines so it can weigh your decisions. Never "review my code" alone.

Dispatch with `delegate_task`, one reviewer per role, in one call when roles are independent.

Model tier by risk: mechanical diff → cheap; subtle concurrency/auth → most capable available.

## The reviewer's rules

- **Confidence gate:** report only what you are >80% sure is a real problem, with file and line.
  Vague findings ("somewhere in the auth layer") are dropped, not softened.
- **Severity by effect on a user**, not by whether the spec mentions the input:
  - **Critical** — data loss, security hole, crash on a normal path.
  - **Important** — wrong behaviour in a plausible case, broken contract, missing test for a real risk.
  - **Minor** — polish, naming, style. Never enters a fix pass unasked.
- **Scope:** the diff. Pre-existing issues outside it get one line under "outside the diff",
  never a fix.
- **No noise:** consolidate repeats ("5 handlers miss the null check"), skip taste.

## Report format

```
Review — correctness
Critical  src/api/orders.ts:88  price read from client body, never validated  → server computes from SKU
Important src/lib/retry.ts:31   jitter uses Math.random() but is seeded per process → same backoff for all callers
Minor     src/api/orders.ts:12  `any` on the response — type it
Outside   src/legacy/auth.ts    pre-existing: token compared with ==
Verdict: 2 blocking findings
```

## Receiving

Feedback is a claim, not an instruction.

1. **Read the whole review before editing anything.**
2. For each finding, open the file and verify it. Then:
   - **correct** → fix it, with a test that fails first;
   - **wrong** → say why, with the evidence (spec line, test, upstream doc);
   - **unclear** → ask one precise question, do not guess.
3. **Forbidden responses:** "You're absolutely right!", "Great catch!", "I'll implement all of
   these" — performed agreement is not review. Restate the technical point in your own words, then
   act.
4. **YAGNI check:** a finding that asks for flexibility, configurability, or an abstraction nobody
   needs is declined with a reason. That is a design opinion, not a defect.
5. **Order:** Critical → Important → Minor. One fix pass, each RED→GREEN, then the full suite.
   Deferred minors go to the ledger and the final message, not into the diff.

## When to push back

Push back when the finding contradicts the spec, when the reviewer lacked context you have, or when
the "fix" would add a branch for an input that cannot occur. Say it plainly, then let the operator
decide if it stays contested. Do not silently comply and do not silently ignore.
