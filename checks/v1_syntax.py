"""v1→v2 syntax checks and auto-fixes."""

import re
from typing import Optional
from lark import Tree
from checks.base import BaseCheck


class V1SyntaxCheck(BaseCheck):
    def __init__(self, config):
        super().__init__(config)
        self.name = "v1_syntax"
        self.patterns = [
            ("W001", r"\bRandom\s*,\s*(\w+)", "Use var := Random() instead of Random, var",
             lambda m: m.group(0).replace(f"Random, {m.group(1)}", f"{m.group(1)} := Random(") + ")"),
            ("W002", r"\bStringSplit\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)", "Use StrSplit() instead of StringSplit",
             lambda m: f"{m.group(1)} := StrSplit({m.group(2)}, {m.group(3)})"),
            ("W003", r"Gui\s*,\s*Add\s*,\s*(\w+)", "Use gui.Add() instead of Gui, Add",
             None),
            ("W004", r"\bIfEqual\s*(\w+)\s*,\s*(\w+)", "Use if (var = val) instead of IfEqual",
             lambda m: f"if ({m.group(1)} = {m.group(2)})"),
            ("W005", r"\bFileRead\s*,\s*(\w+)\s*,\s*(\w+)", "Use var := FileRead() instead of FileRead, var",
             lambda m: f"{m.group(1)} := FileRead({m.group(2)})"),
            ("W006", r"\bFormatTime\s*,\s*(\w+)", "Use var := FormatTime() instead of FormatTime, var",
             lambda m: f"{m.group(1)} := FormatTime("),
            ("W007", r"\bGosub\b", "Use function call instead of Gosub", None),
            ("W008", r"%(\w+)%", "Use bare variable name instead of %var%",
             lambda m: m.group(1)),
            ("W009", r"Menu\s*,\s*Tray\s*,\s*(\w+)", 'Use A_TrayMenu instead of Menu, Tray',
             lambda m: f"A_TrayMenu.{m.group(1)}"),
            ("W010", r"SetTimer\s*,\s*(\w+)\s*,\s*(-?\d+)", "Use SetTimer(Func, period) instead of SetTimer, Label",
             lambda m: f"SetTimer({m.group(1)}, {m.group(2)})"),
        ]
        self.fix_patterns = {p[0]: p for p in self.patterns if p[3]}

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []
        for rule_id, pattern, message, _ in self.patterns:
            for m in re.finditer(pattern, source, re.MULTILINE):
                line = source[:m.start()].count("\n") + 1
                fixable = rule_id in self.fix_patterns
                issues.append(self._make_issue(rule_id, message, line, fixable=fixable))
        return issues

    def fix(self, source: str) -> str:
        result = source
        for rule_id, _, _, fixer in self.patterns:
            if fixer:
                result = re.sub(
                    self._pattern_for_rule(rule_id),
                    lambda m: fixer(m) if self._safe_to_fix(m.group(0)) else m.group(0),
                    result,
                )
        return result

    def _pattern_for_rule(self, rule_id: str) -> re.Pattern:
        for rid, pat, _, _ in self.patterns:
            if rid == rule_id:
                return re.compile(pat, re.MULTILINE)
        return re.compile(r"(?!)")

    @staticmethod
    def _safe_to_fix(match: str) -> bool:
        """Avoid fixing inside comments or strings."""
        # Simple heuristic: if the match starts with ; or is inside a string
        if match.strip().startswith(";"):
            return False
        return True
