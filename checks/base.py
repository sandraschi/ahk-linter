"""Base check class."""

from typing import Optional
from lark import Tree


class BaseCheck:
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__.replace("Check", "").lower()

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        """Run checks on the given source and AST."""
        raise NotImplementedError

    def fix(self, source: str) -> str:
        """Apply auto-fixes. Return modified source."""
        return source

    def _make_issue(self, rule: str, message: str, line: int, col: int = 1, fixable: bool = False) -> dict:
        return {
            "rule": rule,
            "severity": self.config.check_severity(self.name),
            "message": message,
            "line": line,
            "col": col,
            "fixable": fixable,
        }
