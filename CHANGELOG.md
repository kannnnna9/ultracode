# Changelog

## 1.0.0

First release. Built from a full read of three upstreams, not from their READMEs.

### Added

- **Contract** (`ultra:contract`) — two Hermes system-prompt sections, frozen per session
  (~6.8k chars / ~1.7k tokens): Karpathy's four laws, the evidence gate, the S/M/L/XL size ladder,
  the four-item stop list, the loop breaker, the routing table, the first-action rule, and the
  Hermes tool mapping. Subagents receive a 3-line condensation instead.
- **Spine** — 12 further skills: discover, plan, build, verify, debug, review, ship, parallel,
  context, learn, library, audit.
- **Roles** — 6 briefs for `delegate_task`: implementer, reviewer, security-reviewer, architect,
  test-reviewer, explorer.
- **Library** — 92 ECC packs vendored into 9 categories, normalised for Hermes tool names, indexed
  in `references/library-index.md`, deliberately **not registered** (~0 tokens until read).
- **Rules** — `rules/AGENTS.md.template` (project invariants) + the rules-vs-skills test.
- **Hooks** — block edits to existing lint/format/test configs; block `git … --no-verify`; warn on
  `console.log` left in non-test JS/TS.
- **Tooling** — install, vendor, normalise, build_index, audit; 30 unit tests; `sim/run_sim.py`
  (renders what the model receives) and `sim/probe_contract.py` (A/B probe of the first action).
- **Live verification** — plugin loaded in the gateway, contract bytes present in the session
  prompt, a TDD task completed with real red→green evidence, `--no-verify` blocked at the tool layer.

### Deliberately not included

- ECC's 98 slash commands, 71 agent files and vertical industry packs.
- Superpowers' `using-superpowers` (its content is the contract), `diagnosing-superpowers`, and the
  per-harness tool reference files.
- Any second bootstrap or JSON hook file.

### Known limits

- Model routing is advisory: it maps role → tier, but Hermes applies delegation model through config,
  not per call.
- The library is a snapshot; upstream packs drift and are re-vendored deliberately, not automatically.
