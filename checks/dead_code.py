"""Dead code analysis — unused variables, unreachable code."""

import re
from typing import Optional, Set
from lark import Tree
from checks.base import BaseCheck


class DeadCodeCheck(BaseCheck):
    def __init__(self, config):
        super().__init__(config)
        self.name = "dead_code"

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []
        # S020: Variable assigned but never read (simple heuristic)
        assigned = self._find_assignments(source)
        referenced = self._find_references(source)
        for var in assigned:
            if var not in referenced and not var.startswith("A_") and var != "":
                lines = [i + 1 for i, line in enumerate(source.split("\n")) if var in line and ":=" in line]
                for ln in lines[:1]:
                    issues.append(self._make_issue("S020", f"Variable '{var}' assigned but never read", ln))

        # S021: Unreachable code after Return
        lines = source.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("return") or stripped.startswith("ExitApp") or stripped.startswith("Exit"):
                # Check next non-blank line
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line == "" or next_line.startswith(";"):
                        continue
                    if not next_line.startswith("}") and not next_line.startswith("#"):
                        issues.append(self._make_issue("S021", "Unreachable code after return", j + 1))
                        break
                    break

        return issues

    @staticmethod
    def _find_assignments(source: str) -> Set[str]:
        vars_found = set()
        for m in re.finditer(r'(\w+)\s*:=', source):
            name = m.group(1)
            if name.lower() not in ("if", "for", "while", "try", "catch", "global", "static", "return", "throw", "else"):
                vars_found.add(name)
        return vars_found

    @staticmethod
    def _find_references(source: str) -> Set[str]:
        vars_found = set()
        for m in re.finditer(r'(?<![:\w])(\w+)(?![:\w])', source):
            name = m.group(1)
            if name.lower() not in ("if", "for", "while", "try", "catch", "global", "static", "return", "throw", "else", "true", "false", "null", "and", "or", "not", "in", "is", "has"):
                vars_found.add(name)
        # Remove common built-in A_ variables
        builtins = {f"A_{x}" for x in ["Index", "LoopField", "TickCount", "Now", "ScriptDir", "ScriptName",
                                        "WorkingDir", "LineNumber", "ThisFunc", "Gui", "GuiControl",
                                        "EventInfo", "PriorKey", "PID", "ProcessName", "ProcessPath"]}
        return vars_found - builtins
