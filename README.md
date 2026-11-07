# ULTRACODE

[![ci](https://github.com/kannnnna9/ultracode/actions/workflows/ci.yml/badge.svg)](https://github.com/kannnnna9/ultracode/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

One agent stack built from three lineages that are good at different things:

| Upstream | Owns | Why it is there |
|---|---|---|
| [Karpathy skills](https://github.com/multica-ai/andrej-karpathy-skills) | **judgment** | the four laws that stop an agent from inventing a different project |
| [Superpowers](https://github.com/obra/superpowers) | **process** | brainstorm → design gate → plan → build → verify → ship, with a ledger |
| [ECC](https://github.com/affaan-m/ecc) | **surface** | 92 vendored domain packs, eval/regression discipline, context hygiene |

They do not overlap by accident: each one owns a layer, and the layers are wired so a fact lives in
exactly one place. The design and the twelve conflict rulings are in [DESIGN.md](DESIGN.md).

## What you get

```
L0  contract      2 prompt sections, frozen per session (~6.8k chars, ~1.7k tokens once)
L1  13 skills     ultra:discover plan build verify debug review ship parallel context learn library audit
L2  6 roles       implementer, reviewer, security, architect, test-reviewer, explorer
L3  92 packs      vendored ECC domain library, NOT registered (0 tokens until read)
L4  rules         AGENTS.md template + 12 invariants
L5  hooks         config-protection block, --no-verify block, console.log observer
```

The contract rides Hermes's plugin **system-prompt sections** (`register_system_prompt_section`),
not a `pre_llm_call` injection: it lands in the prompt bytes of every new session, survives
resumes, and is re-read from disk per session so edits apply without a restart.

## Install

**Hermes** (plugin: registers the skills, injects the contract as two prompt sections, installs the
guard hooks):

```bash
git clone https://github.com/kannnnna9/ultracode.git ~/dev/ultracode
cd ~/dev/ultracode
python scripts/install.py            # copy to $HERMES_HOME/plugins/ultra + enable
hermes plugins list | grep ultra     # verify
```

Start a **new** Hermes session. The first install needs one `hermes gateway restart` (or an app
restart) so the running gateway imports the plugin module; after that, contract edits take effect in
the next new session with no restart.

**Any other agent** (Claude Code, Codex, Cursor, OpenCode, …): the spine is plain `SKILL.md` files.

```bash
python scripts/install_portable.py --target claude             # ~/.claude/skills/ultra-* + AGENTS.md
python scripts/install_portable.py --target project --path .   # ./.agent/skills + AGENTS.md block
python scripts/install_portable.py --target generic --path ~/.my-agent
```

That writes `ultra-<skill>/SKILL.md`, `ultra-roles/`, the 92-pack `ultracode-library/` with its
`INDEX.md`, and an idempotent ULTRACODE block in `AGENTS.md` at the target root.

**Manual**: copy `skills/*` next to your agent's skills directory and paste `AGENTS.md` into your
project root. Nothing else is required — no daemon, no dependency, no build step.

Update (Hermes): `python scripts/install.py --update` · Uninstall: `python scripts/install.py --uninstall`

## Use

Nothing to memorise. Say what you want:

```
build me a CLI that renames files by EXIF date     -> ultra:discover (asks, designs, gates)
here is the spec, write the plan                   -> ultra:plan
plan approved, go                                  -> ultra:build
is it done?                                        -> ultra:verify
tests fail with ECONNREFUSED                       -> ultra:debug
review this diff                                   -> ultra:review
merge and open a PR                                -> ultra:ship
```

The size ladder decides how much ceremony a request gets: **S** do-and-verify, **M** short plan,
**L** design doc + plan + build, **XL** blueprint with dependency graph. A typo never triggers a
design document.

## Layout

```
plugin.yaml          manifest (name, hooks)
__init__.py          registration, bootstrap injection, 3 hooks
skills/              13 SKILL.md — the spine
references/roles/    6 delegate_task briefs
references/library-index.md   generated catalogue of the 92 packs
library/<cat>/<pack>/SKILL.md vendored ECC packs, normalised
rules/AGENTS.md.template      project rules to copy into a repo
scripts/             install, vendor, normalise, build_index, audit
tests/               28 unit tests (manifest, hooks, routing)
sim/run_sim.py       dry-run: renders the bootstrap, sizes it, walks scenarios
```

## Verify

```bash
python -m unittest discover -s tests      # 30 tests
python scripts/audit.py                   # index cost, links, library freshness
python sim/run_sim.py                     # what the model actually receives
python sim/probe_contract.py              # A/B: does the contract change the first action?
```

## Maintenance

- Re-vendor after an ECC release: `python scripts/vendor_library.py --from <ecc>/skills
  && python scripts/normalize_library.py && python scripts/build_index.py`
- Audit monthly: `ultra:audit` (index budget, dead skills, compliance sample).
- A lesson that repeats twice goes into a skill (`ultra:learn`), not into the contract.

## Licence & provenance

MIT. The contract and spine skills are adapted from Karpathy skills (MIT), Superpowers (MIT) and
ECC (MIT); each file carries a `source:`/`author:` line. The vendored library keeps upstream text
intact apart from a mechanical, logged tool-name normalisation (`library/NORMALISATION.md`).
