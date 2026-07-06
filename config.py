"""Linter configuration — .ahklintrc TOML loader."""

import tomllib
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG = {
    "checks": {
        "v1_syntax": "error",
        "style": "warning",
        "safety": "error",
        "dead_code": "warning",
    },
    "suppressions": {},
    "fix": {
        "enabled": True,
        "backup": True,
    },
}


class LinterConfig:
    def __init__(self, data: dict = None):
        self.data = {**DEFAULT_CONFIG, **(data or {})}

    @classmethod
    def load(cls, path: Optional[str] = None) -> "LinterConfig":
        if path:
            p = Path(path)
            if p.exists():
                with open(p, "rb") as f:
                    return cls(tomllib.load(f))
        # Search for .ahklintrc
        for candidate in [Path(".ahklintrc"), Path("pyproject.toml")]:
            if candidate.exists():
                with open(candidate, "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "ahk-lint" in data["tool"]:
                        return cls(data["tool"]["ahk-lint"])
                    if "tool" not in data:
                        return cls(data)
        return cls()

    def check_enabled(self, check_name: str) -> bool:
        return check_name in self.data.get("checks", {})

    def check_severity(self, check_name: str) -> str:
        return self.data.get("checks", {}).get(check_name, "warning")

    def is_path_suppressed(self, path: str, rule: str) -> bool:
        for pattern, rules in self.data.get("suppressions", {}).items():
            if pattern in path:
                if "all" in rules or rule in rules:
                    return True
        return False
