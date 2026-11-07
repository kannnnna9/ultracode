# ULTRACODE — Design

**One stack from three lineages:**

| Upstream | What it actually is | What we take | What we drop |
|---|---|---|---|
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | A 67-line behavioural constitution for coding agents (4 principles) | The four laws: think before coding, simplicity first, surgical changes, goal-driven execution | Nothing — it is absorbed almost verbatim into the always-on contract |
| [obra/superpowers](https://github.com/obra/superpowers) | A development **process state machine**: brainstorm → design gate → plan → worktree → execute → verify → finish, plus meta-skills (writing skills, debugging, review) | The spine: gates, plan format, task loop, ledger, evidence rule, review discipline | Its Claude-Code-specific tooling, its 15-skill index cost, its absolutist "1% rule" |
| [affaan-m/ecc](https://github.com/affaan-m/ecc) | A **surface**: 314 skills, 71 agents, 98 commands, rules, hooks, memory vault, evals | The domain library, eval/regression discipline, context hygiene, memory promotion, hook ports, role prompts | 98 slash commands, 71 agent files, duplicated process skills, marketing surface, harness-specific JSON |

ULTRACODE is not a merge of files. It is a **layer model** where each upstream owns exactly one
layer, so nothing is stated twice and nothing contradicts.

---

## 1. Why a naive merge fails

Copying all three in produces four measurable defects:

1. **Name collisions.** `systematic-debugging`, `test-driven-development`, `requesting-code-review`
   exist in both Superpowers and Hermes's bundled skills; `manim-video` exists in both ECC and
   Hermes. Loading both versions gives two procedures for one trigger.
2. **Index cost.** Hermes writes every registered skill's name+description into the system prompt
   on every turn. Superpowers adds 15 lines (~1.2k tokens). ECC's 314 would add ~10k tokens per
   turn, before a single file is read — the exact failure ECC's own `context-budget` skill warns
   about.
3. **Contradictory instructions.** "Invoke a skill before any response, including clarifying
   questions" (Superpowers) vs "stop when confused and ask" (Karpathy) vs "ask clarifying
   questions if needed" (ECC planner). Three rules, one situation, no tie-breaker.
4. **Double bootstraps.** Both Superpowers' Hermes plugin and any ECC port want a first-turn
   context injection plus their own hooks. Two injections per session is pure overhead and the
   hooks can fight (one blocks, one approves).

Anything that does not fix those four is decoration.

---

## 2. The layer model

```
┌──────────────────────────────────────────────────────────────┐
│ L0  CONTRACT      2 prompt sections, frozen per session       │
│     Karpathy's 4 laws + evidence rule + size ladder +        │
│     stop list + routing table + first-action rule.           │
│     ~6.8k chars / ~1.7k tokens, once.                        │
├──────────────────────────────────────────────────────────────┤
│ L1  SPINE         13 skills, registered, on-demand           │
│     discover → plan → build → verify → review → ship         │
│     plus: debug, parallel, context, learn, audit, library    │
├──────────────────────────────────────────────────────────────┤
│ L2  ROLES         6 delegate_task briefs (references/roles)  │
│     implementer, reviewer, security, explorer, tester, docs  │
├──────────────────────────────────────────────────────────────┤
│ L3  LIBRARY       70+ vendored domain packs, NOT registered  │
│     read on demand via ultra:library index                   │
├──────────────────────────────────────────────────────────────┤
│ L4  RULES         AGENTS.md template + 12 invariants         │
├──────────────────────────────────────────────────────────────┤
│ L5  HOOKS         one plugin: config-protection, no-verify   │
│                   guard, console.log observer                │
└──────────────────────────────────────────────────────────────┘
```

**Rule of ownership.** A fact lives in exactly one layer:

- Behaviour that must apply *every* turn → L0 contract.
- A procedure with steps and a completion criterion → L1 skill.
- A persona with a narrow brief → L2 role.
- Reference knowledge for a technology → L3 library.
- A hard invariant a linter could check → L4 rule / L5 hook.

If two layers both want a fact, the higher layer wins and the lower one links to it.

---

## 3. Conflict matrix (the actual work)

| # | Conflict | Sources | Ruling |
|---|---|---|---|
| 1 | Skill before questions vs ask when confused | SP `using-superpowers` / Karpathy §1 | **The process skill is the clarification protocol.** Load the spine skill first; its first step is asking. You never choose between "load a skill" and "ask a question" — asking *is* step 1 of the skill. |
| 2 | Absolute autonomy vs confirmation | SP `executing-plans` / Karpathy §1 / ECC proactive agents | **The Stop List has exactly four items**: irreversible/destructive op, security-sensitive action, side effect outside the worktree (merge/push/publish), or a plan where every path is a guess. Everything else is a ledgered `Ruling:` and forward motion. |
| 3 | TDD as absolute law vs YAGNI | SP `test-driven-development` / Karpathy §2 | **TDD governs behaviour with a testable seam.** Exempt: docs, config, throwaway spikes, and code with no harness (add a characterization test if cheap, else record manual evidence). ECC's 80% coverage is *project policy* if the project says so — never a global law. |
| 4 | Process weight vs trivial tasks | SP `brainstorming` hard gate / Karpathy "use judgment for trivial tasks" | **Size ladder.** S (one file, obvious) → do it, verify, no ceremony. M → plan in chat, 3–6 tasks. L → design doc + plan + build gate. XL → design doc + blueprint + phased execution. The gate scales with size, it does not disappear. |
| 5 | Three memory systems | ECC vault / Hermes memory / skills | **One home per fact type**: durable identity+env → memory; reusable procedure → skill; project state → repo file (`PROGRESS.md`, ADR); conversation history → `session_search`. No second brain. |
| 6 | Context budgeting | ECC `context-budget` / Hermes auto-compaction | Compact at **phase boundaries** (after design, after a task group, before review), never mid-task. Delegate reads that would exceed ~10% of the window. |
| 7 | Reviewer proliferation | SP one fresh reviewer / ECC 71 agents | **Four reviewer roles only**: correctness, security, architecture, tests. Dispatched via `delegate_task` with a role brief; one pass per gate, no re-review loop after a TDD-verified fix. |
| 8 | Hook frameworks | SP plugin bootstrap / ECC hooks.json / Hermes plugin hooks | **One plugin, one bootstrap.** No JSON hook files ship. Blocking hooks are limited to things a linter cannot catch (weakening the linter itself, `--no-verify`). |
| 9 | 98 slash commands | ECC commands/ | **Zero slash commands.** Skills and natural-language triggers only — ECC's own docs call commands a legacy shim. |
| 10 | Always-on rules vs on-demand skills | ECC rules/ / Hermes skill loader | **≤12 invariants always on** (AGENTS.md), everything else procedural. Rules state *what must never happen*; skills state *how to do things*. |
| 11 | Proactive review vs minimal diff | ECC auto-review / Karpathy §3 | Review scope = **the diff**. Findings outside the diff are reported, never fixed silently. |
| 12 | Model routing | SP model tiers / ECC per-agent `model:` / Hermes single model | Route by **role tier** in `ultra:parallel`; apply through delegation config, not per-call fantasy. Never claim a model was used when the harness has one model. |

Each ruling is encoded in exactly one skill, and the contract carries a one-line pointer.

---

## 4. What lives where

| Capability | Skill | Upstream DNA |
|---|---|---|
| Session constitution, routing, size ladder | `ultra:contract` | Karpathy 4 laws + SP iron laws + our rulings |
| Requirements discovery, design doc, approval gate | `ultra:discover` | SP brainstorming, compressed ~60%; ECC `product-lens`, `intent-driven-development` pointers |
| Implementation plan, task/step granularity, self-review, XL blueprint mode | `ultra:plan` | SP writing-plans + ECC `blueprint` dependency-graph mode |
| Task loop, ledger, inline vs subagent, rulings | `ultra:build` | SP executing-plans + subagent-driven-development, merged |
| Evidence gate, 3 verification tiers | `ultra:verify` | SP verification-before-completion + ECC `verification-loop` 6 phases |
| Root cause before fix | `ultra:debug` | SP systematic-debugging + ECC `silent-failure-hunter` |
| Request/receive review, 4 reviewer roles | `ultra:review` | SP requesting/receiving-code-review + ECC code-reviewer prompt |
| Branch finish, PR, cleanup | `ultra:ship` | SP finishing-a-development-branch + ECC `git-workflow` |
| Parallel dispatch, worktrees, model tiers | `ultra:parallel` | SP dispatching-parallel-agents + ECC multi-* / dmux |
| Context hygiene, compaction timing | `ultra:context` | ECC `context-budget` + `strategic-compact` |
| Skill authoring, memory promotion, rules distillation | `ultra:learn` | SP writing-skills + ECC `continuous-learning-v2`, `rules-distill` |
| Domain depth index | `ultra:library` | ECC 314-skill catalogue, curated to ~70 |
| Stack self-audit | `ultra:audit` | ECC `skill-stocktake`, `skill-comply` |

---

## 5. What was dropped, and why

- **ECC's 71 agent files** → 6 role briefs. Agent files are Claude Code's subagent format; Hermes
  delegates with `delegate_task(goal, context)`. 65 of the 71 were language variants of the same
  reviewer/resolver prompt, already covered by library packs.
- **ECC's 98 commands** → 0. A command is a skill with a worse discovery story.
- **ECC's duplicated process skills** (`tdd-workflow`, `verification-loop`, `plan-orchestrate`,
  `autonomous-loops`) → folded into `build`/`verify`/`plan`. Kept in library only where they add
  concrete per-language commands (`python-testing`, `rust-testing`, …).
- **ECC vertical packs** (healthcare, freight, customs, energy, carrier ops, retail forecasting) →
  excluded from the default library. They are real expertise, but they are not this operator's
  work and would sit in the index forever.
- **Superpowers' 15-skill surface** → 13 skills, no `using-superpowers` (its content is the
  contract), no `diagnosing-superpowers` (Hermes has session transcripts), no separate
  `requesting`/`receiving` review skills (one `review`), no worktree skill (folded into `parallel`
  + `build`).
- **Superpowers' `references/*-tools.md` per harness** → one Hermes mapping table in the contract.
- **Karpathy's `EXAMPLES.md`, `CURSOR.md`, `.cursor/rules`** → not portable; the four laws survive
  in the contract.

---

## 6. Anti-collision guarantees

1. **Namespace.** Every skill is registered under `ultra:`; no bare name can shadow a bundled skill.
2. **No duplicate triggers.** `ultra:debug` explicitly supersedes bundled `systematic-debugging`
   for this profile; the bundled skill stays untouched but the contract routes to `ultra:`.
3. **One injection.** The contract is two Hermes plugin *system-prompt sections*, rendered once per
   session and frozen into the prompt bytes; no `pre_llm_call` bootstrap, no second copy. Subagents
   get a 3-line condensation instead of the full text.
4. **One hook set.** The plugin registers `pre_tool_call` and `post_tool_call` only.
5. **Library is not registered.** 92 packs on disk cost zero tokens until read.
6. **Cross-references are tested.** `tests/test_manifest.py` fails if any skill points at a
   non-existent sibling or library pack.

---

## 7. Simulation plan

| Test | Type | What it proves |
|---|---|---|
| `tests/test_manifest.py` | static | frontmatter valid, descriptions ≤ 100 chars, no collision with bundled skills, every cross-reference resolves, library index matches disk |
| `tests/test_hooks.py` | unit | two prompt sections register under the 4k/8k budgets; subagent condensation; config-protection blocks an existing linter config, allows creating one, allows normal files; `--no-verify` blocked; observer never blocks |
| `tests/test_routing.py` | table | 24 natural-language scenarios map to the intended skill chain and size tier |
| `sim/run_sim.py` | dry-run | renders both section sizes, the registered index cost, the routing table, and the hook decisions |
| `sim/probe_contract.py` | A/B model probe | same request with and without the contract: with it, the first action is `skill_view("ultra:debug")`; without it, a blind `terminal` call and an invented skill name |
| live run | integration | plugin loaded in the gateway (13 skills in the prompt, contract bytes present), a TDD task completed with corpus evidence, `--no-verify` blocked at the tool layer |

---

## 8. Provenance & licence

MIT. Upstream texts are MIT (karpathy-skills, superpowers) and MIT (ECC). Every adapted skill
carries a `source:` line naming the upstream. The vendored library keeps upstream files intact
except for a mechanical tool-name normalisation pass (`scripts/normalize_library.py`), which is
reversible and logged.
