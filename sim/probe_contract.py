#!/usr/bin/env python3
"""A/B probe: does the contract make the model load a spine skill first?

Sends the same coding request twice to the configured model —
once with the contract as system prompt, once without — and reports whether the
first action is a `skill_view` call. Uses the operator's own provider; one small
request per arm.

  python sim/probe_contract.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
BASE_URL = os.environ.get("ULTRA_PROBE_BASE_URL", "https://api.river.ai/v1")
MODEL = os.environ.get("ULTRA_PROBE_MODEL", "deepseek-ai/DeepSeek-V4.1-Flash-1017")
KEY_ENV = "HERMES_CUSTOM_RIVER_API_KEY"

REQUEST = (
    "Bug: title_case('hello_world') returns 'Hello_world' but it should return 'Hello World'. "
    "Fix it and prove the fix."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "skill_view",
            "description": "Load a skill's full text before acting.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]


def load_key() -> str:
    key = os.environ.get(KEY_ENV)
    if key:
        return key
    env = HERMES_HOME / ".env"
    if env.is_file():
        for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
            name, sep, value = line.partition("=")
            if sep and name.strip() == KEY_ENV:
                return value.strip().strip("\"'")
    raise SystemExit(f"{KEY_ENV} not found in env or {env}")


def contract() -> str:
    text = (ROOT / "skills" / "contract" / "SKILL.md").read_text(encoding="utf-8")
    body = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)[-1]
    return body.strip().replace("<!-- ultra-section-2 -->", "")


def ask(key: str, system: str | None):
    payload = {
        "model": MODEL,
        "messages": ([{"role": "system", "content": system}] if system else [])
        + [{"role": "user", "content": REQUEST}],
        "tools": TOOLS,
        "tool_choice": "auto",
        "max_tokens": 400,
        "temperature": 0,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    calls = [c["function"]["name"] for c in (msg.get("tool_calls") or [])]
    args = [c["function"].get("arguments", "") for c in (msg.get("tool_calls") or [])]
    return calls, args, (msg.get("content") or "")[:300]


def main() -> int:
    key = load_key()
    pack = contract()
    print(f"contract chars: {len(pack)}  model: {MODEL}\n")

    calls_off, args_off, text_off = ask(key, None)
    print(f"WITHOUT contract: tool calls={calls_off or 'none'} {args_off[:2]}")
    print(f"  says: {text_off.strip()[:160]!r}\n")

    calls_on, args_on, text_on = ask(key, pack)
    print(f"WITH contract:    tool calls={calls_on or 'none'} {args_on[:2]}")
    print(f"  says: {text_on.strip()[:160]!r}\n")

    ok = "skill_view" in calls_on
    print("RESULT:", "PASS — the contract makes the first action a skill load" if ok
          else "FAIL — model still skips the skill with the contract present")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
