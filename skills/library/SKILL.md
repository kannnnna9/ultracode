---
name: library
description: Index of vendored domain packs — languages, frameworks, security.
version: 1.0.0
author: Hermes operator, curated from affaan-m/ECC (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [library, domain, reference, languages]
    related_skills: [plan, build, debug]
---

# Library — domain depth on demand

The process skills say *how to work*. The library says *how this technology works*. Packs are
vendored from ECC, normalised for Hermes tools, and **not registered** — they cost nothing until
read.

## How to use it

1. Identify the stack from the repo (manifest files), not from the prompt.
2. Look it up in `references/library-index.md` (one line per pack: name — when to use).
3. Read the pack you need: `library/<category>/<pack>/SKILL.md`.
4. Follow its content as reference, translated through the contract's tool table. If a pack names
   an upstream tool (Bash, Read, Grep, TodoWrite), use the Hermes equivalent: terminal, read_file,
   search_files, todo_list.

Read one pack, not the category. Two packs is already a lot of context.

## Categories

| Category | What is in it |
|---|---|
| `lang/` | Python, TypeScript, Go, Rust, Java, Kotlin, Swift, C#, C++, PHP, Ruby, Dart, Perl idioms and testing |
| `web/` | React, Vue, Angular, Next, Nuxt, Vite, Nest, accessibility, motion, performance |
| `backend/` | API design, backend patterns, Postgres/MySQL/Redis/ClickHouse, migrations, Prisma, error handling |
| `infra/` | Docker, Kubernetes, deployment, observability, MCP servers, prompt caching, cost-aware LLM pipelines |
| `mobile/` | Android clean architecture, Compose Multiplatform, React Native |
| `data/` | PyTorch, MLE workflow, eval harness, AI regression testing |
| `security/` | security review, agent security hardening, MCP dependency review, OSINT, offensive review checklists |
| `quality/` | e2e testing, test collaboration, Windows desktop E2E, benchmark loop |
| `product/` | ADRs, product lens, intent-driven development, code tours, onboarding, research-first |
| `agent/` | agentic engineering, harness construction, parallel execution, loop design, self-evaluation |

## Adding a pack

1. Copy the upstream `SKILL.md` into `library/<category>/<name>/`.
2. Run `scripts/normalize_library.py` (tool names, paths, model names).
3. Regenerate the index: `python scripts/build_index.py`.
4. Add a `source:` line at the top of the pack if it does not have one.

Nothing is registered, so no index cost and no name collision is possible.

## What does not belong here

- Vertical industry packs (healthcare, freight, customs, energy) — excluded by design.
- Anything the process skills already say. The library is depth, not process.
- Harness-specific instructions: a pack that only makes sense in Claude Code gets normalised or
  left out.
