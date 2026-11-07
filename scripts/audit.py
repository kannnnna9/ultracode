#!/usr/bin/env python3
"""Static audit for the ULTRACODE stack.

Checks: frontmatter validity, description budget, index cost, cross-references,
library index freshness, role/checklist presence. Exit 1 on a hard failure.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CORE = (
    "contract", "discover", "plan", "build", "verify", "debug", "review",
    "ship", "parallel", "context", "learn", "library", "audit",
)
INDEX_BUDGET = 2500  # chars of name + description for the registered set


def frontmatter(text: str):
    if not text.startswith("---"):
        return None
    m = re.search(r"\n---\s*\n", text[3:])
    if not m:
        return None
    fm = {}
    for line in text[3:m.start() + 3].splitlines():
        key, sep, value = line.partition(":")
        if sep and re.match(r"^[A-Za-z_][\w-]*$", key.strip()):
            fm[key.strip()] = value.strip().strip("\"'")
    return fm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    problems, notes = [], []
    index_cost = 0

    for name in CORE:
        path = root / "skills" / name / "SKILL.md"
        if not path.is_file():
            problems.append(f"missing skill: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if not fm:
            problems.append(f"{name}: no frontmatter")
            continue
        if fm.get("name") != name:
            problems.append(f"{name}: frontmatter name is {fm.get('name')!r}")
        desc = fm.get("description", "")
        if not desc:
            problems.append(f"{name}: empty description")
        if len(desc) > 100:
            problems.append(f"{name}: description {len(desc)} chars (>100)")
        index_cost += len(name) + len(desc) + 4

    if index_cost > INDEX_BUDGET:
        problems.append(f"index cost {index_cost} chars > budget {INDEX_BUDGET}")
    else:
        notes.append(f"index cost {index_cost} chars (budget {INDEX_BUDGET})")

    # cross-references
    refs = 0
    for path in (root / "skills").glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8")
        for target in set(re.findall(r"ultra:([a-z-]+)", text)):
            refs += 1
            if target not in CORE:
                problems.append(f"{path.parent.name}: references ultra:{target} which does not exist")
        for rel in set(re.findall(r"references/(?:roles|checklists)/[\w./-]+\.md", text)):
            refs += 1
            if not (root / rel).is_file():
                problems.append(f"{path.parent.name}: missing {rel}")
    notes.append(f"{refs} cross-references checked")

    # library
    packs = sorted((root / "library").glob("*/*/SKILL.md")) if (root / "library").is_dir() else []
    notes.append(f"{len(packs)} library packs")
    index = root / "references" / "library-index.md"
    if not index.is_file():
        problems.append("references/library-index.md missing (run scripts/build_index.py)")
    elif packs:
        listed = len(re.findall(r"^- `", index.read_text(encoding="utf-8"), re.MULTILINE))
        if listed != len(packs):
            problems.append(f"library index lists {listed} packs, disk has {len(packs)}")

    roles = sorted((root / "references" / "roles").glob("*.md"))
    notes.append(f"{len(roles)} role briefs")
    if len(roles) < 4:
        problems.append("fewer than 4 role briefs")

    print("Audit —", root.name)
    for n in notes:
        print("  OK   ", n)
    for p in problems:
        print("  FAIL ", p)
    print(f"\n{'PASS' if not problems else 'FAIL'} ({len(problems)} problem(s))")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
