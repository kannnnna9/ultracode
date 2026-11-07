"""ULTRACODE — Hermes plugin.

Registers the `ultra:*` process skills, injects the session contract once per
session, and installs three guard rails:

  pre_llm_call   first turn only, non-subagent -> inject the contract body
  pre_tool_call  block edits that weaken an existing lint/format/test config
                 block git commit/push with --no-verify
  post_tool_call warn (never block) when an edited JS/TS file gains console.log

Design notes live in DESIGN.md. Fail-open everywhere: a broken hook must never
brick the agent, but it must never fail silently either — every swallowed path
writes one diagnostic line to stderr.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

BOOTSTRAP_MARKER = "ultracode:contract bootstrap"
SKILL_NAMES = (
    "contract",
    "discover",
    "plan",
    "build",
    "verify",
    "debug",
    "review",
    "ship",
    "parallel",
    "context",
    "learn",
    "library",
    "audit",
)


# --------------------------------------------------------------------------- #
# paths & manifest helpers
# --------------------------------------------------------------------------- #

def _plugin_root() -> Path:
    return Path(os.path.realpath(__file__)).parent


def _skills_dir() -> Path:
    """Skills tree for both supported layouts (repo clone or flattened install)."""
    here = _plugin_root()
    for cand in (here / "skills", here.parent / "skills"):
        if (cand / "contract" / "SKILL.md").is_file():
            return cand
    raise RuntimeError(
        "ultra plugin: cannot find skills/contract/SKILL.md next to "
        f"{here}. Reinstall with scripts/install.py."
    )


def _strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\s*\n[\s\S]*?\n---\s*\n([\s\S]*)$", text)
    return (m.group(1) if m else text).strip()


def _frontmatter_value(text: str, key: str) -> str:
    m = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n", text)
    if not m:
        return ""
    for line in m.group(1).splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip() == key:
            return value.strip().strip("\"'")
    return ""


def _warn(msg: str) -> None:
    sys.stderr.write(f"[ultra] {msg}\n")


def _debug(msg: str) -> None:
    """Opt-in trace: ULTRA_DEBUG=<file>, or a `.trace` file next to the plugin.

    The gateway owns chat turns, so an env var set in the calling shell never
    reaches the process that fires the hooks; the sentinel file does.
    """
    target = os.environ.get("ULTRA_DEBUG")
    if not target:
        sentinel = _plugin_root() / ".trace"
        if not sentinel.exists():
            return
        target = str(_plugin_root() / ".trace.log")
    try:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(msg + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# register
# --------------------------------------------------------------------------- #

SECTION_MARKER = "<!-- ultra-section-2 -->"
MAX_SECTION = 4000

SUBAGENT_NOTE = (
    "ULTRACODE (condensed): think before coding; state assumptions; minimum code; surgical diff; "
    "evidence before claims; root cause before fixes. Your task brief is authoritative — follow it "
    "and return the evidence it asks for. `ultra:*` skills are available if the brief names one."
)


_CACHE: dict[str, tuple[float, tuple[str, str]]] = {}


def contract_parts() -> tuple[str, str]:
    """Split the contract skill into its two prompt sections (single source of truth).

    Read at render time, keyed by mtime, so editing the contract takes effect in
    the next new session without a gateway restart.
    """
    path = _skills_dir() / "contract" / "SKILL.md"
    try:
        stamp = path.stat().st_mtime
    except OSError:
        stamp = 0.0
    cached = _CACHE.get("contract")
    if cached and cached[0] == stamp:
        return cached[1]

    text = path.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    if SECTION_MARKER in body:
        first, second = body.split(SECTION_MARKER, 1)
    else:
        first, second = body, ""
    first, second = first.strip(), second.strip()
    if second:
        index = _plugin_root() / "references" / "library-index.md"
        second += (
            "\n\n## Library\n\n"
            "Domain depth (languages, frameworks, security, data) is vendored, not registered. "
            f"Index: `{index.as_posix()}`; packs live under "
            f"`{(_plugin_root() / 'library').as_posix()}/<category>/<pack>/SKILL.md`. "
            "Load `ultra:library` for the catalogue, then read the pack file you need."
        )
    _CACHE["contract"] = (stamp, (first, second))
    return first, second


def build_bootstrap() -> str:
    """Full contract text, for sim/ and tests (not the runtime injection path)."""
    first, second = contract_parts()
    return f"<ULTRACODE>\n{BOOTSTRAP_MARKER}\n\n{first}\n\n{second}\n</ULTRACODE>"


def register(ctx):
    _debug("register() called")
    skills_dir = _skills_dir()
    first, second = contract_parts()

    for name in SKILL_NAMES:
        path = skills_dir / name / "SKILL.md"
        if not path.is_file():
            _warn(f"missing skill file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        ctx.register_skill(name, path, description=_frontmatter_value(text, "description"))

    def _platform(info) -> str:
        try:
            return str(info.get("platform") or "")
        except Exception:
            return ""

    def section_one(info):
        if _platform(info) == "subagent":
            return SUBAGENT_NOTE
        return contract_parts()[0]

    def section_two(info):
        if _platform(info) == "subagent":
            return None
        return contract_parts()[1] or None

    ctx.register_system_prompt_section(
        "ultra-contract-1", section_one, position="after_memory", max_chars=MAX_SECTION
    )
    if second:
        ctx.register_system_prompt_section(
            "ultra-contract-2", section_two, position="after_memory", max_chars=MAX_SECTION
        )

    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("post_tool_call", post_tool_call)


# --------------------------------------------------------------------------- #
# pre_tool_call — the two blocks
# --------------------------------------------------------------------------- #

PROTECTED_CONFIGS = {
    ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml", ".eslintrc.yaml",
    "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs", "eslint.config.ts",
    "eslint.config.mts", "eslint.config.cts",
    ".prettierrc", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.json", ".prettierrc.yml",
    ".prettierrc.yaml", "prettier.config.js", "prettier.config.cjs", "prettier.config.mjs",
    "biome.json", "biome.jsonc", ".ruff.toml", "ruff.toml", ".shellcheckrc", ".stylelintrc",
    ".stylelintrc.json", ".stylelintrc.yml", ".markdownlint.json", ".markdownlint.yaml",
    ".markdownlintrc", "pytest.ini", "tox.ini", ".flake8", "mypy.ini", ".pylintrc",
    "checkstyle.xml", ".golangci.yml", ".golangci.yaml",
}

EDIT_TOOLS = {"patch", "write_file", "edit", "write", "apply_patch", "str_replace_editor"}
SHELL_TOOLS = {"terminal", "bash", "shell", "run_command"}


def _target_path(args: dict) -> str:
    for key in ("path", "file_path", "target", "filename"):
        value = args.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _check_protected_config(tool_name: str, args: dict):
    if tool_name not in EDIT_TOOLS:
        return None
    raw = _target_path(args)
    if not raw:
        return None
    path = Path(raw).expanduser()
    if path.name not in PROTECTED_CONFIGS:
        return None
    if not path.exists():
        return None  # creating a config in a new project is legitimate
    return {
        "action": "block",
        "message": (
            f"ULTRACODE blocked an edit to '{path.name}': it is an existing linter/formatter/test "
            "config. Weakening a check to make code pass is not a fix. Fix the code, or if the "
            "config is genuinely wrong, say so to the operator and wait for a decision."
        ),
    }


_QUOTED = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
_NO_VERIFY = re.compile(r"\bgit\b[^;&|]*\b(?:commit|push|merge)\b[^;&|]*--no-verify\b")


def _strip_quoted(command: str) -> str:
    """Ignore text inside quotes: a commit message may legitimately mention --no-verify."""
    return _QUOTED.sub("''", command)


def _check_no_verify(tool_name: str, args: dict):
    if tool_name not in SHELL_TOOLS:
        return None
    command = args.get("command") or args.get("cmd") or ""
    if not isinstance(command, str) or not command:
        return None
    if _NO_VERIFY.search(_strip_quoted(command)):
        return {
            "action": "block",
            "message": (
                "ULTRACODE blocked `--no-verify`: it skips the checks this task is supposed to "
                "satisfy. If a hook is broken, fix or report the hook; do not bypass it."
            ),
        }
    return None


def pre_tool_call(tool_name=None, args=None, **kwargs):
    try:
        tool = str(tool_name or "")
        payload = args if isinstance(args, dict) else {}
        _debug("pre_tool_call tool=%r" % tool)
        return _check_protected_config(tool, payload) or _check_no_verify(tool, payload)
    except Exception as exc:
        _warn(f"pre_tool_call failed open: {exc}")
        return None


# --------------------------------------------------------------------------- #
# post_tool_call — observer only
# --------------------------------------------------------------------------- #

_CONSOLE_RE = re.compile(r"^\s*(?!.*//).*\bconsole\.(log|debug)\s*\(", re.MULTILINE)
_JS_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte")
_EXCLUDE_RE = re.compile(r"(\.d\.ts$|\.test\.[tj]sx?$|\.spec\.[tj]sx?$|/tests?/|/__tests__/|/scripts/)")


def post_tool_call(tool_name=None, args=None, tool_result=None, **kwargs):
    try:
        if str(tool_name or "") not in EDIT_TOOLS:
            return None
        raw = _target_path(args if isinstance(args, dict) else {})
        if not raw:
            return None
        path = Path(raw).expanduser()
        posix = path.as_posix()
        if path.suffix.lower() not in _JS_EXT or _EXCLUDE_RE.search(posix):
            return None
        if not path.is_file() or path.stat().st_size > 2_000_000:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = _CONSOLE_RE.findall(text)
        if hits:
            count = sum(1 for _ in _CONSOLE_RE.finditer(text))
            _warn(f"{posix}: {count} console.log/debug left in a non-test file")
    except Exception as exc:
        _warn(f"post_tool_call failed open: {exc}")
    return None
