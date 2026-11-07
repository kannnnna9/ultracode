"""Hook behaviour: registration, bootstrap, the two blocks, the observer."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_plugin():
    spec = importlib.util.spec_from_file_location("ultra_plugin", ROOT / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeCtx:
    def __init__(self):
        self.skills = {}
        self.hooks = {}
        self.sections = {}

    def register_skill(self, name, path, description=""):
        self.skills[name] = (str(path), description)

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def register_system_prompt_section(self, section_id, content, *, position="after_memory", max_chars=4000):
        self.sections[section_id] = (content, position, max_chars)


class TestRegistration(unittest.TestCase):
    def setUp(self):
        self.mod = load_plugin()
        self.ctx = FakeCtx()
        self.mod.register(self.ctx)

    def test_all_skills_registered_with_descriptions(self):
        self.assertEqual(len(self.ctx.skills), 13)
        for name, (path, desc) in self.ctx.skills.items():
            self.assertTrue(Path(path).is_file(), name)
            self.assertTrue(desc, f"{name} has no description")

    def test_hooks_registered(self):
        self.assertEqual(set(self.ctx.hooks), {"pre_tool_call", "post_tool_call"})

    def test_two_prompt_sections_under_the_limit(self):
        self.assertEqual(len(self.ctx.sections), 2)
        total = 0
        for section_id, (content, position, max_chars) in self.ctx.sections.items():
            text = content({"platform": "desktop"})
            self.assertTrue(text.startswith("#") or text.startswith("ULTRACODE"), section_id)
            self.assertLessEqual(len(text), max_chars, f"{section_id} exceeds max_chars")
            self.assertLessEqual(max_chars, 4000)
            self.assertEqual(position, "after_memory")
            total += len(text)
        self.assertLessEqual(total, 7900, "sections exceed the 8k aggregate budget")

    def test_subagents_get_the_condensed_note(self):
        one = self.ctx.sections["ultra-contract-1"][0]
        two = self.ctx.sections["ultra-contract-2"][0]
        note = one({"platform": "subagent"})
        self.assertLess(len(note), 600)
        self.assertIn("brief is authoritative", note)
        self.assertIsNone(two({"platform": "subagent"}))


class TestPreToolCall(unittest.TestCase):
    def setUp(self):
        self.mod = load_plugin()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_edit_of_existing_lint_config(self):
        cfg = self.dir / ".eslintrc.json"
        cfg.write_text("{}")
        result = self.mod.pre_tool_call(tool_name="write_file", args={"path": str(cfg)})
        self.assertIsNotNone(result)
        self.assertEqual(result["action"], "block")
        self.assertIn("linter", result["message"])

    def test_allows_creating_a_new_config(self):
        cfg = self.dir / ".eslintrc.json"
        self.assertIsNone(self.mod.pre_tool_call(tool_name="write_file", args={"path": str(cfg)}))

    def test_allows_normal_source_files(self):
        src = self.dir / "app.py"
        src.write_text("print(1)")
        self.assertIsNone(self.mod.pre_tool_call(tool_name="patch", args={"path": str(src)}))

    def test_allows_reading_a_config(self):
        cfg = self.dir / "ruff.toml"
        cfg.write_text("")
        self.assertIsNone(self.mod.pre_tool_call(tool_name="read_file", args={"path": str(cfg)}))

    def test_blocks_no_verify(self):
        for cmd in ("git commit --no-verify -m 'x'", "git push --no-verify", "git commit -m x --no-verify"):
            result = self.mod.pre_tool_call(tool_name="terminal", args={"command": cmd})
            self.assertIsNotNone(result, cmd)
            self.assertEqual(result["action"], "block")

    def test_does_not_block_normal_git(self):
        for cmd in ("git commit -m 'fix: thing'", "git status", "gh pr create --fill",
                    "git commit -m 'note about --no-verify policy'"):
            self.assertIsNone(
                self.mod.pre_tool_call(tool_name="terminal", args={"command": cmd}), cmd
            )

    def test_bad_payload_fails_open(self):
        self.assertIsNone(self.mod.pre_tool_call(tool_name="write_file", args=None))
        self.assertIsNone(self.mod.pre_tool_call(tool_name=None, args={"path": 3}))


class TestPostToolCall(unittest.TestCase):
    def setUp(self):
        self.mod = load_plugin()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _edit(self, name: str, body: str):
        path = self.dir / name
        path.write_text(body)
        err = io.StringIO()
        with redirect_stderr(err):
            result = self.mod.post_tool_call(tool_name="write_file", args={"path": str(path)})
        return result, err.getvalue()

    def test_warns_on_console_log(self):
        result, err = self._edit("a.ts", "export const a = 1;\nconsole.log(a);\n")
        self.assertIsNone(result)  # observer never blocks
        self.assertIn("console.log", err)

    def test_ignores_test_files(self):
        _, err = self._edit("a.test.ts", "console.log('debug')\n")
        self.assertEqual(err, "")

    def test_ignores_non_js(self):
        _, err = self._edit("a.py", "print('hi')\n")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
