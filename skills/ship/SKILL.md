---
name: ship
description: Finish a branch — merge, PR, or park — with tests green.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers finishing-a-development-branch (MIT) + ECC git-workflow (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, merge, pull-request, release, cleanup]
    related_skills: [verify, review]
---

# Ship — land the work or park it deliberately

## 1. Verify first

Run `ultra:verify` at tier 3 (or tier 2 for a small change). No ship with a red suite. Record the
evidence in the message — command + result, not "tests pass".

## 2. Establish the ground

```bash
git status --short          # uncommitted work?
git log --oneline <base>..HEAD
git merge-base --is-ancestor <base> HEAD && echo "up to date"
```

Know: base branch, commit count, files touched, whether a worktree was used.

## 3. Present the options (one message)

| Option | What happens | When |
|---|---|---|
| **Merge locally** | squash or merge into base, verify on the merged result | solo repo, small diff |
| **Push + PR** | branch up, PR with the body below | review needed, shared repo |
| **Keep as-is** | branch stays, work recorded, no integration | waiting on a decision |
| **Discard** | delete branch + worktree | only on explicit instruction — never on your own initiative |

Recommend one with a one-line reason. If the operator already said which, skip the question.

## 4. Execute

**Merge locally**

```bash
git checkout <base> && git pull --ff-only
git merge --no-ff <branch>        # or: git merge --squash <branch>
<test command>                    # verify on the merged result, not before the merge
git branch -d <branch>
```

**Push + PR**

```bash
git push -u origin <branch>
gh pr create --base <base> --title "<type>: <summary>" --body-file <file>
```

PR body: what changed · why · how it was verified (commands) · risks/rollback · deferred minors ·
rulings made. No emoji, no "Generated with" footer unless asked.

**Keep** — say where the branch is and what it waits for.

**Discard** — confirm once, then delete the branch and its worktree. Never discard unmerged commits
without an explicit "yes, delete it".

## 5. Clean up

- Remove the worktree: `git worktree remove <path>` (then `git worktree prune`).
- Delete merged local branches; leave remote branches until the PR merges.
- Close the ledger entry: append `Shipped: <mode> <sha>`.
- Update `PROGRESS.md` / changelog if the project keeps one.

## Rules

- **Never** `git push --force` to a shared branch. `--force-with-lease` only on your own branch,
  and say so.
- **Never** `--no-verify`. The plugin blocks it; a hook that is wrong gets fixed or reported.
- Do not rewrite history that others may have pulled.
- Commit messages: `<type>(<scope>): <imperative summary>` — what and why in the body, not how.
- One logical change per commit; a task may be several commits, a commit may not span tasks.
