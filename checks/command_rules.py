"""Command-style v1→v2 conversion checks using rule data."""

import json
import re
from pathlib import Path

from lark import Tree

from checks.base import BaseCheck


class CommandRulesCheck(BaseCheck):
    """Flags v1 command-style usage across ~200+ window, control, file, string, etc. commands."""

    def __init__(self, config):
        super().__init__(config)
        self.name = "v1_syntax"
        self.rules = self._load_rules()

    @staticmethod
    def _load_rules() -> dict:
        rules_path = Path(__file__).resolve().parent.parent / "rules" / "v1_to_v2.json"
        if not rules_path.exists():
            return {}
        with open(rules_path) as f:
            return json.load(f)

    def run(self, source: str, ast: Tree | None) -> list[dict]:
        issues = []
        for _category_name, commands in self.rules.items():
            for cmd_name, rule in commands.items():
                if isinstance(rule, str):
                    # Simple deprecated message
                    pattern = rf"\b{cmd_name}\b"
                    for m in re.finditer(pattern, source, re.MULTILINE):
                        line = source[: m.start()].count("\n") + 1
                        issues.append(self._make_issue(f"V1_{cmd_name}", rule, line))
                    continue
                if isinstance(rule, dict) and "handler" in rule:
                    continue  # Complex handlers — skip for now
                if isinstance(rule, dict):
                    # Command pattern: match "CommandName," at start of statement
                    pattern = rf"(?m)^\s*{cmd_name},"
                    for m in re.finditer(pattern, source):
                        line = source[: m.start()].count("\n") + 1
                        to = rule.get("to", "Use v2 function syntax")
                        issues.append(
                            self._make_issue(
                                f"V1_{cmd_name}",
                                f"Use v2 function syntax: {to}",
                                line,
                                fixable=False,
                            )
                        )
        return issues
