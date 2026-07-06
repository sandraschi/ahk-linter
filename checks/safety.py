"""Safety checks — error handling, uninitialized variables, missing directives."""

import re
from typing import Optional
from lark import Tree
from checks.base import BaseCheck


class SafetyCheck(BaseCheck):
    def __init__(self, config):
        super().__init__(config)
        self.name = "safety"

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []
        lines = source.split("\n")

        # S001: Missing #Requires directive
        if not re.search(r"#Requires\s+AutoHotkey", source, re.IGNORECASE):
            issues.append(self._make_issue("S005", "Missing #Requires AutoHotkey v2.0+ directive", 1))

        # S002: Missing #SingleInstance
        if not re.search(r"#SingleInstance", source, re.IGNORECASE):
            issues.append(self._make_issue("S005", "Missing #SingleInstance Force", 1))

        # S003: FileRead/FileOpen without try/catch
        io_funcs = re.finditer(r"\b(FileRead|FileOpen|FileAppend|FileDelete|FileMove)\b", source)
        for m in io_funcs:
            line_num = source[:m.start()].count("\n") + 1
            # Check if this line is inside a try block
            if not self._inside_try(source, line_num):
                issues.append(self._make_issue("S003", f"{m.group(1)} without try/catch", line_num))

        return issues

    @staticmethod
    def _inside_try(source: str, line_num: int) -> bool:
        """Rough check if a line is inside a try block."""
        lines = source.split("\n")
        depth = 0
        in_try = False
        for i, line in enumerate(lines[:line_num]):
            stripped = line.strip()
            if stripped.startswith("try") and stripped.endswith("{"):
                in_try = True
                depth += 1
            elif stripped.startswith("try ") or stripped == "try":
                in_try = True
            elif "{" in stripped and in_try:
                depth += stripped.count("{") - stripped.count("}")
            elif "}" in stripped and in_try:
                depth -= stripped.count("}")
                if depth <= 0:
                    in_try = False
            elif stripped.startswith("catch") or stripped.startswith("finally"):
                in_try = True
        return in_try
