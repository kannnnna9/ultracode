#!/usr/bin/env python3
"""Dry-run the runtime artefacts without spending a model call.

Renders exactly what Hermes will inject, sizes it, lists the registered index as
the model sees it, then walks 10 archetypal requests through the contract's
routing table and prints the gate each one must pass. Also exercises the two
blocking hooks so you can see the guard text.

  python sim/run_sim.py
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCENARIOS = [
    ("add SSO to the admin panel", "L", "discover -> plan -> build -> verify -> review -> ship",
     "design approval"),
    ("here is the spec, write the plan", "L", "plan -> build", "plan review"),
    ("plan approved, go", "L", "build", "per-task RED->GREEN + ledger"),
    ("is it done?", "M", "verify", "command + output"),
    ("tests fail with ECONNREFUSED", "M", "debug", "reproduce -> root cause -> regression test"),
    ("review this PR", "M", "review", "findings with file:line"),
    ("merge and open a PR", "M", "ship", "green suite on merged result"),
    ("three independent test files failing", "M", "parallel", "no shared files"),
    ("the window is getting long", "S", "context", "handoff written before compaction"),
    ("how do I structure a Rust workspace", "S", "library", "pack read, not guessed"),
]


def load():
    spec = importlib.util.spec_from_file_location("ultra_plugin", ROOT / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frontmatter_desc(text: str) -> str:
    m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else ""


def main() -> int:
    mod = load()
    first, second = mod.contract_parts()
    bootstrap = mod.build_bootstrap()
    tokens = len(bootstrap) // 4

    print("=" * 72)
    print("ULTRACODE simulation — what the model actually receives")
    print("=" * 72)
    print(f"prompt section 1: {len(first):,} chars (max 4,000)")
    print(f"prompt section 2: {len(second):,} chars (max 4,000)")
    print(f"aggregate       : {len(first) + len(second):,} chars of the 8,000 budget")
    print(f"total contract  : {len(bootstrap):,} chars (~{tokens:,} tokens, frozen per session)")
    print(f"marker          : {mod.BOOTSTRAP_MARKER}")
    print()

    print("-- registered skill index (paid every turn) --")
    total = 0
    for name in mod.SKILL_NAMES:
        desc = frontmatter_desc((ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8"))
        line = f"ultra:{name} — {desc[:57]}"
        total += len(line)
        print(f"  {line}")
    print(f"  total index: {total} chars (~{total // 4} tokens/turn)")
    print()

    packs = list((ROOT / "library").glob("*/*/SKILL.md"))
    print(f"-- library: {len(packs)} packs on disk, 0 registered (0 tokens until read) --")
    print()

    print("-- routing simulation --")
    contract = bootstrap
    failures = 0
    for request, tier, chain, gate in SCENARIOS:
        first = chain.split(" -> ")[0]
        routed = f"ultra:{first}" in contract
        if not routed:
            failures += 1
        print(f"  [{tier}] {request:<42} -> {chain:<52} gate: {gate}"
              + ("" if routed else "   !! not routed"))
    print()

    print("-- hook simulation --")
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        cfg = d / ".eslintrc.json"
        cfg.write_text("{}")
        src = d / "app.js"
        src.write_text("const a = 1\n")

        cases = [
            ("edit existing .eslintrc.json", mod.pre_tool_call(tool_name="write_file", args={"path": str(cfg)})),
            ("create new .eslintrc.json", mod.pre_tool_call(tool_name="write_file", args={"path": str(d / "new" / ".eslintrc.json")})),
            ("edit app.js", mod.pre_tool_call(tool_name="patch", args={"path": str(src)})),
            ("git commit --no-verify", mod.pre_tool_call(tool_name="terminal", args={"command": "git commit --no-verify -m x"})),
            ("git commit -m \"x\"", mod.pre_tool_call(tool_name="terminal", args={"command": 'git commit -m "x"'})),
        ]
        for label, result in cases:
            verdict = f"BLOCK — {result['message'][:60]}..." if result else "allow"
            print(f"  {label:<32} {verdict}")

    print()
    print(f"bootstrap size headroom: {20000 - len(bootstrap):,} chars before the 20k guard")
    print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures} unrouted)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
