#!/usr/bin/env python3
"""Install ULTRACODE into the active Hermes profile.

  python scripts/install.py            # copy + enable
  python scripts/install.py --update   # re-copy over an existing install, keep config
  python scripts/install.py --uninstall

Copies the plugin tree (without .git, tests, sim, __pycache__) to
$HERMES_HOME/plugins/ultra, then runs `hermes plugins enable ultra` and verifies
that Hermes lists it. A new session is required for the bootstrap to fire.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKIP = {".git", "tests", "sim", "__pycache__", ".pytest_cache", "node_modules"}


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    return Path(env).expanduser() if env else Path.home() / ".hermes"


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name in SKIP:
            continue
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target, ignore=shutil.ignore_patterns(*SKIP))
        else:
            shutil.copy2(item, target)


def run(cmd, timeout=120):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        return 127, "hermes executable not found on PATH"
    except subprocess.TimeoutExpired:
        return 124, "timed out"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true", help="overwrite an existing install")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--no-enable", action="store_true", help="copy only, do not run hermes")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    home = hermes_home()
    target = home / "plugins" / "ultra"

    if args.uninstall:
        if target.exists():
            shutil.rmtree(target)
            print(f"removed {target}")
        code, out = run(["hermes", "plugins", "disable", "ultra"])
        print(out.strip() or f"disable exit {code}")
        return 0

    if target.exists() and not args.update:
        print(f"already installed at {target}; use --update to overwrite", file=sys.stderr)
        return 1

    required = ["plugin.yaml", "__init__.py", "skills/contract/SKILL.md", "references/library-index.md"]
    missing = [r for r in required if not (repo / r).exists()]
    if missing:
        print(f"refusing to install, missing: {', '.join(missing)}", file=sys.stderr)
        print("run: python scripts/build_index.py", file=sys.stderr)
        return 1

    copy_tree(repo, target)
    print(f"installed -> {target}")

    if args.no_enable:
        return 0

    code, out = run(["hermes", "plugins", "enable", "ultra"])
    print((out or "").strip() or f"enable exit {code}")
    code, out = run(["hermes", "plugins", "list"])
    listed = "ultra" in (out or "")
    print(("verified: hermes lists ultra" if listed else
           "WARNING: 'ultra' not found in `hermes plugins list` — check `hermes doctor`"))
    print("\nStart a new Hermes session for the contract to inject.")
    return 0 if listed else 1


if __name__ == "__main__":
    raise SystemExit(main())
