#!/usr/bin/env python3
"""AHK Linter v2 — AST-based analysis, auto-fix, config, SARIF output."""

import json
import os
import re
import sys
import hashlib
from pathlib import Path
from typing import Optional

import click
from lark import Lark, Tree, Token, UnexpectedInput

from checks.v1_syntax import V1SyntaxCheck
from checks.safety import SafetyCheck
from checks.style import StyleCheck
from checks.dead_code import DeadCodeCheck
from checks.command_rules import CommandRulesCheck
from checks.function_renames import FunctionRenamesCheck, OldObjectModelCheck
from config import LinterConfig
from reporter import TerminalReporter, SARIFReporter, JSONReporter
from lsp_client import LSPClient


def load_grammar() -> Optional[Lark]:
    grammar_path = Path(__file__).parent / "grammar.lark"
    try:
        return Lark.open(grammar_path, parser="lalr", maybe_placeholders=True)
    except Exception as e:
        click.echo(f"Warning: Grammar loading failed ({e}). Falling back to regex-only mode.", err=True)
        return None


def parse_file(source: str, grammar: Optional[Lark]) -> Optional[Tree]:
    if grammar is None:
        return None
    try:
        return grammar.parse(source)
    except UnexpectedInput:
        return None


def collect_suppressions(source: str) -> list:
    """Extract per-line suppression comments."""
    suppressions = []
    for i, line in enumerate(source.split("\n"), 1):
        m = re.search(r";\s*@ahk-lint-disable-next-line\s+(\S+)", line)
        if m:
            suppressions.append({"line": i + 1, "rules": m.group(1).split(",")})
        m = re.search(r";\s*@ahk-lint-(?:ignore|disable)\s+(\S+)", line)
        if m:
            suppressions.append({"line": i, "rules": m.group(1).split(","), "whole_line": True})
    return suppressions


class Linter:
    def __init__(self, config: LinterConfig, grammar: Lark, use_lsp: bool = False):
        self.config = config
        self.grammar = grammar
        self.use_lsp = use_lsp
        self.lsp = LSPClient() if use_lsp else None
        self.checks = [
            V1SyntaxCheck(config),
            SafetyCheck(config),
            StyleCheck(config),
            DeadCodeCheck(config),
            CommandRulesCheck(config),
            FunctionRenamesCheck(config),
            OldObjectModelCheck(config),
        ]

    def lint_file(self, path: Path) -> list:
        source = path.read_text(encoding="utf-8")
        issues = []
        suppressions = collect_suppressions(source)
        ast = parse_file(source, self.grammar)
        if ast is None:
            source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
            issues.append({
                "rule": "P001",
                "severity": "warning",
                "message": f"Could not parse file (hash: {source_hash}) — falling back to regex checks",
                "line": 1,
                "col": 1,
                "fixable": False,
            })

        for check in self.checks:
            for issue in check.run(source, ast):
                if not self._is_suppressed(issue, suppressions):
                    issues.append(issue)

        # LSP second pass (optional)
        if self.use_lsp and self.lsp:
            lsp_issues = self.lsp.lint(source)
            for li in lsp_issues:
                if not self._is_suppressed(li, suppressions):
                    issues.append(li)

        return issues

    def _is_suppressed(self, issue: dict, suppressions: list) -> bool:
        for s in suppressions:
            if s.get("whole_line") and s["line"] == issue["line"]:
                if issue["rule"] in s["rules"] or "all" in s["rules"]:
                    return True
            elif s["line"] == issue["line"]:
                if issue["rule"] in s["rules"] or "all" in s["rules"]:
                    return True
        return False

    def fix_file(self, path: Path) -> tuple[bool, str]:
        """Apply auto-fixes. Returns (fixed, new_content)."""
        source = path.read_text(encoding="utf-8")
        result = source
        for check in self.checks:
            result = check.fix(result)
        return result != source, result


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--fix", is_flag=True, help="Auto-fix issues")
@click.option("--format", "output_format", default="terminal", type=click.Choice(["terminal", "sarif", "json"]))
@click.option("--config", "config_path", default=None, help="Config file path")
@click.option("--backup", is_flag=True, default=True, help="Create .bak files when fixing")
@click.option("--lsp", is_flag=True, help="Use thqby LSP server for deeper analysis (requires Node.js)")
def cli(paths, fix, output_format, config_path, backup, lsp):
    """ahk-lint: AutoHotkey v2 linter with AST analysis and auto-fix."""
    grammar = load_grammar()
    config = LinterConfig.load(config_path)
    linter = Linter(config, grammar, use_lsp=lsp)

    if lsp:
        linter.lsp.start()

    # Collect files
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".ahk":
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*.ahk"))

    if not files:
        click.echo("No .ahk files found.", err=True)
        sys.exit(1)

    # Lint
    all_issues = {}
    for f in files:
        rel = f.relative_to(Path.cwd()) if f.is_relative_to(Path.cwd()) else f
        issues = linter.lint_file(f)
        if issues:
            all_issues[str(rel)] = issues

    # Fix
    if fix:
        fixed_count = 0
        for f in files:
            fixed, new_content = linter.fix_file(f)
            if fixed:
                if backup:
                    bak = f.with_suffix(f"{f.suffix}.bak")
                    f.rename(bak)
                f.write_text(new_content, encoding="utf-8")
                fixed_count += 1
        click.echo(f"Fixed {fixed_count} files.")

    # Output
    if output_format == "terminal":
        reporter = TerminalReporter()
        reporter.report(all_issues)
    elif output_format == "sarif":
        reporter = SARIFReporter()
        click.echo(reporter.report(all_issues))
    elif output_format == "json":
        reporter = JSONReporter()
        click.echo(reporter.report(all_issues))

    # Exit code
    total = sum(len(v) for v in all_issues.values())
    if lsp:
        linter.lsp.stop()
    sys.exit(1 if total > 0 else 0)


if __name__ == "__main__":
    cli()
