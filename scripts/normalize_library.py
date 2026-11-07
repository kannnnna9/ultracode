#!/usr/bin/env python3
"""Normalise vendored ECC packs for Hermes.

Mechanical, reversible substitutions only:

  Claude tool names   -> Hermes tool names (Bash->terminal, Read->read_file, ...)
  ~/.claude/          -> ~/.hermes/
  CLAUDE.md           -> AGENTS.md
  model: opus|sonnet|haiku -> model: strong|standard|cheap

Writes `library/NORMALISATION.md` recording every substitution, and prints a
per-file count. Run with --dry-run first.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOL_MAP = [
    (r"`Bash`", "`terminal`"),
    (r"`Read`", "`read_file`"),
    (r"`Grep`", "`search_files`"),
    (r"`Glob`", "`search_files` (target='files')"),
    (r"`Edit`", "`patch`"),
    (r"`Write`", "`write_file`"),
    (r"`MultiEdit`", "`patch`"),
    (r"`TodoWrite`", "`todo_list`"),
    # `Task` is deliberately NOT mapped: in C#/Rust packs it is the language's own type.
    (r"`WebFetch`", "`web_extract`"),
    (r"`WebSearch`", "`web_search`"),
    (r"`NotebookEdit`", "`patch`"),
    (r"\bTodoWrite\b", "todo_list"),
    (r"~/.claude/skills/", "~/.hermes/skills/"),
    (r"~/\.claude/", "~/.hermes/"),
    (r"\.claude/skills/", "~/.hermes/skills/"),
    (r"\.claude/agents/", "~/.hermes/agents/"),
    (r"\bCLAUDE\.md\b", "AGENTS.md"),
    (r"(?m)^model:\s*opus\s*$", "model: strong"),
    (r"(?m)^model:\s*sonnet\s*$", "model: standard"),
    (r"(?m)^model:\s*haiku\s*$", "model: cheap"),
]

HEADER = "source: affaan-m/ECC (MIT, normalised for Hermes)"


def normalise(text: str):
    counts = {}
    for pattern, repl in TOOL_MAP:
        new, n = re.subn(pattern, repl, text)
        if n:
            counts[pattern] = counts.get(pattern, 0) + n
            text = new
    return text, counts


def add_source(text: str) -> str:
    """Record provenance inside the frontmatter (a prefix comment would break it)."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    head = text[:end]
    if re.search(r"(?m)^source:", head):
        return text
    return head + "\n" + HEADER + text[end:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    lib = root / "library"
    if not lib.is_dir():
        print("no library/ directory", file=sys.stderr)
        return 2

    total_files = 0
    total_subs = 0
    changed = 0
    for path in sorted(lib.glob("*/*/SKILL.md")):
        total_files += 1
        original = path.read_text(encoding="utf-8", errors="replace")
        text, counts = normalise(original)
        text = add_source(text)
        if text == original:
            continue
        changed += 1
        subs = sum(counts.values())
        total_subs += subs
        if counts:
            print(f"{path.relative_to(root)}: {subs} substitution(s) {counts if args.dry_run else ''}")
        if not args.dry_run:
            path.write_text(text, encoding="utf-8")

    print(f"\n{total_files} packs, {changed} changed, {total_subs} substitutions"
          + (" (dry run)" if args.dry_run else ""))
    if not args.dry_run and changed:
        note = root / "library" / "NORMALISATION.md"
        note.write_text(
            "# Library normalisation\n\n"
            "Vendored ECC packs are upstream files with mechanical substitutions:\n\n"
            + "\n".join(f"- `{p}` -> `{r}`" for p, r in TOOL_MAP)
            + "\n\nNo prose was rewritten; re-run `scripts/normalize_library.py` after re-vendoring.\n",
            encoding="utf-8",
        )
        print(f"wrote {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
