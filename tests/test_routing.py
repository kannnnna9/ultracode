"""Routing coverage: every archetypal request maps to a skill the contract names."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = (ROOT / "skills" / "contract" / "SKILL.md").read_text(encoding="utf-8")

# (request, expected skill, size tier) — the simulation table.
SCENARIOS = [
    ("add a dark mode toggle to the settings page", "discover", "L"),
    ("we need to migrate payments from Stripe to Adyen", "discover", "XL"),
    ("build me a CLI that renames files by EXIF date", "discover", "M"),
    ("here is the spec for the auth service, what next", "plan", "L"),
    ("turn this design doc into tasks", "plan", "L"),
    ("the plan is approved, start implementing", "build", "L"),
    ("keep going with task 4", "build", "L"),
    ("is it done?", "verify", "M"),
    ("run the tests before I commit", "verify", "S"),
    ("the login test fails with ECONNREFUSED", "debug", "M"),
    ("this worked yesterday and now it returns undefined", "debug", "M"),
    ("review my changes", "review", "M"),
    ("check this diff for security issues", "review", "M"),
    ("merge the branch and open a PR", "ship", "M"),
    ("clean up the worktree after the merge", "ship", "S"),
    ("fix these 3 unrelated failing test files in parallel", "parallel", "M"),
    ("split this into two agents, one for the API one for the UI", "parallel", "L"),
    ("the context is getting long, what do I do", "context", "S"),
    ("remember that I always deploy on Fridays", "learn", "S"),
    ("turn this workflow into a skill", "learn", "M"),
    ("what skills do you have for Rust", "library", "S"),
    ("how should I structure a FastAPI project", "library", "S"),
    ("are the skills actually being followed", "audit", "M"),
    ("the stack feels bloated, prune it", "audit", "M"),
]

ROUTING_NAMES = ("discover", "plan", "build", "verify", "debug", "review", "ship",
                 "parallel", "context", "learn", "library", "audit")


class TestRouting(unittest.TestCase):
    def test_every_scenario_skill_is_routed_in_contract(self):
        routing = CONTRACT.split("## 9. Routing")[1].split("## 10.")[0]
        for name in ROUTING_NAMES:
            self.assertIn(f"ultra:{name}", routing, f"{name} missing from routing table")

    def test_every_skill_has_a_trigger_line(self):
        routing = CONTRACT.split("## 9. Routing")[1].split("## 10.")[0]
        rows = [line for line in routing.splitlines() if line.startswith("|") and "ultra:" in line]
        self.assertGreaterEqual(len(rows), 12, "routing table lost rows")

    def test_descriptions_are_front_loaded(self):
        """The system-prompt index truncates at ~57 chars: the trigger must survive it."""
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            fm = re.search(r"^description:\s*(.+)$", text, re.MULTILINE).group(1).strip().strip("\"'")
            head = fm[:57].lower()
            self.assertTrue(
                any(w in head for w in ("use", "write", "turn", "keep", "prove", "find", "request",
                                        "finish", "fan", "check", "index", "session", "execute")),
                f"{path.parent.name}: trigger buried past 57 chars -> {fm[:57]!r}",
            )

    def test_no_skill_claims_another_skills_trigger(self):
        """Two skills must not both claim the same phase keyword as their own."""
        owners = {}
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            fm = re.search(r"^description:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE).group(1)
            for word in ("plan", "build", "verify", "debug", "review", "merge", "prune"):
                if re.search(rf"\b{word}\b", fm, re.IGNORECASE):
                    owners.setdefault(word, []).append(path.parent.name)
        duplicates = {w: o for w, o in owners.items() if len(o) > 3}
        self.assertEqual(duplicates, {}, f"keyword claimed by too many skills: {duplicates}")

    def test_size_ladder_is_defined(self):
        for tier in ("**S**", "**M**", "**L**", "**XL**"):
            self.assertIn(tier, CONTRACT)

    def test_stop_list_has_exactly_four_items(self):
        block = CONTRACT.split("## 7. Stop list")[1].split("## 8.")[0]
        items = [line for line in block.splitlines() if re.match(r"^\d\.\s", line.strip())]
        self.assertEqual(len(items), 4, items)


if __name__ == "__main__":
    unittest.main()
