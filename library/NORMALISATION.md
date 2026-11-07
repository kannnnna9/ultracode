# Library normalisation

Vendored ECC packs are upstream files with mechanical substitutions:

- ``Bash`` -> ``terminal``
- ``Read`` -> ``read_file``
- ``Grep`` -> ``search_files``
- ``Glob`` -> ``search_files` (target='files')`
- ``Edit`` -> ``patch``
- ``Write`` -> ``write_file``
- ``MultiEdit`` -> ``patch``
- ``TodoWrite`` -> ``todo_list``
- ``WebFetch`` -> ``web_extract``
- ``WebSearch`` -> ``web_search``
- ``NotebookEdit`` -> ``patch``
- `\bTodoWrite\b` -> `todo_list`
- `~/.claude/skills/` -> `~/.hermes/skills/`
- `~/\.claude/` -> `~/.hermes/`
- `\.claude/skills/` -> `~/.hermes/skills/`
- `\.claude/agents/` -> `~/.hermes/agents/`
- `\bCLAUDE\.md\b` -> `AGENTS.md`
- `(?m)^model:\s*opus\s*$` -> `model: strong`
- `(?m)^model:\s*sonnet\s*$` -> `model: standard`
- `(?m)^model:\s*haiku\s*$` -> `model: cheap`

No prose was rewritten; re-run `scripts/normalize_library.py` after re-vendoring.
