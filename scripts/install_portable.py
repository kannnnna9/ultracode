#!/usr/bin/env python3
"""Install ULTRACODE into a non-Hermes harness.

  python scripts/install_portable.py --target claude
  python scripts/install_portable.py --target project --path /path/to/repo
  python scripts/install_portable.py --target generic --path /path/to/agent-home

Writes:
  <root>/.../ultra-<skill>/SKILL.md      the 13 spine skills
  <root>/.../ultra-roles/*.md            delegate_task role briefs
  <root>/.../ultracode-library/          the 92 domain packs + INDEX.md
  <root>/AGENTS.md                       the contract, in a marked block (idempotent)

For Hermes use scripts/install.py instead (it installs the plugin + hooks).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

BLOCK_START = "<!-- ULTRACODE:start -->"
BLOCK_END = "<!-- ULTRACODE:end -->"
SKIP = ("__pycache__", ".git")


def contract_body(repo: Path) -> str:
    text = (repo / "skills" / "contract" / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    body = parts[2] if len(parts) == 3 else text
    return body.replace("<!-- ultra-section-2 -->", "").strip()


def write_agent_block(root: Path, repo: Path, skills_root: Path, library_root: Path) -> Path:
    agents = root / "AGENTS.md"
    block = (
        f"{BLOCK_START}\n"
        f"{contract_body(repo)}\n\n"
        "## Where the skills live\n\n"
        f"- Spine skills: `{skills_root.as_posix()}/ultra-<name>/SKILL.md` — load the one the routing table names.\n"
        f"- Roles: `{skills_root.as_posix()}/ultra-roles/` — briefs for subagent dispatch.\n"
        f"- Domain library: `{library_root.as_posix()}/<category>/<pack>/SKILL.md`, index: "
        f"`{library_root.as_posix()}/INDEX.md`.\n"
        f"{BLOCK_END}\n"
    )
    if agents.is_file():
        current = agents.read_text(encoding="utf-8")
        if BLOCK_START in current and BLOCK_END in current:
            head, _, rest = current.partition(BLOCK_START)
            _, _, tail = rest.partition(BLOCK_END)
            agents.write_text(head + block + tail.lstrip("\n"), encoding="utf-8")
        else:
            agents.write_text(current.rstrip() + "\n\n" + block, encoding="utf-8")
    else:
        agents.write_text(block, encoding="utf-8")
    return agents


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["claude", "project", "generic"], default="project")
    ap.add_argument("--path", help="root for project/generic targets (default: cwd)")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    if args.target == "claude":
        root = Path(args.path).expanduser() if args.path else Path.home() / ".claude"
        skills_root = root / "skills"
        library_root = root / "ultracode-library"
    else:
        root = Path(args.path).expanduser().resolve() if args.path else Path.cwd()
        skills_root = root / ".agent" / "skills"
        library_root = root / ".agent" / "ultracode-library"

    skills_root.mkdir(parents=True, exist_ok=True)
    installed = 0
    for skill in sorted((repo / "skills").glob("*/SKILL.md")):
        dst = skills_root / f"ultra-{skill.parent.name}"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(skill.parent, dst)
        installed += 1
    print(f"skills  -> {skills_root} ({installed})")

    if library_root.exists():
        shutil.rmtree(library_root)
    shutil.copytree(repo / "library", library_root, ignore=shutil.ignore_patterns(*SKIP))
    shutil.copy2(repo / "references" / "library-index.md", library_root / "INDEX.md")
    print(f"library -> {library_root}")

    roles_dst = skills_root / "ultra-roles"
    if roles_dst.exists():
        shutil.rmtree(roles_dst)
    shutil.copytree(repo / "references" / "roles", roles_dst)
    print(f"roles   -> {roles_dst}")

    agents = write_agent_block(root, repo, skills_root, library_root)
    print(f"contract-> {agents}")
    print("\nOpen a new agent session in that root; the AGENTS.md block is the contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
