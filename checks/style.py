"""Style checks — naming, formatting, conventions."""

import re
from typing import Optional
from lark import Tree
from checks.base import BaseCheck


class StyleCheck(BaseCheck):
    def __init__(self, config):
        super().__init__(config)
        self.name = "style"

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []
        lines = source.split("\n")

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # S010: Tab characters
            if "\t" in line and not stripped.startswith(";"):
                issues.append(self._make_issue("S010", "Use spaces instead of tabs", i))

            # S011: Trailing whitespace
            if line.rstrip() != line and not stripped.startswith(";"):
                issues.append(self._make_issue("S011", "Remove trailing whitespace", i))

            # S012: Long lines (>120 chars)
            if len(line.rstrip("\r\n")) > 120 and not stripped.startswith(";"):
                issues.append(self._make_issue("S012", f"Line too long ({len(line.rstrip())} chars, max 120)", i))

        # S013: Inconsistent brace style
        # Check if opening brace is on same line as control flow
        if re.search(r"\b(if|else|for|while|try|catch)\s*\([^)]*\)\s*\n\s*\{", source):
            pass  # Both styles are acceptable, just warn about mixing

        return issues
