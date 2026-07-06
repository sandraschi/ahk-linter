"""Output formatters — terminal, SARIF, JSON."""

import json
from datetime import datetime


class TerminalReporter:
    """Human-readable terminal output with colors."""

    COLORS = {"error": "\033[31m", "warning": "\033[33m", "suggestion": "\033[36m", "reset": "\033[0m"}

    def report(self, all_issues: dict[str, list[dict]]) -> None:
        total = sum(len(v) for v in all_issues.values())
        by_severity = {"error": 0, "warning": 0, "suggestion": 0}

        for path, issues in sorted(all_issues.items()):
            print(f"\n{path}:")
            for issue in issues:
                sev = issue.get("severity", "warning")
                by_severity[sev] = by_severity.get(sev, 0) + 1
                color = self.COLORS.get(sev, "")
                fix = " [fixable]" if issue.get("fixable") else ""
                print(f"  {color}{sev.upper():10}{self.COLORS['reset']} "
                      f"L{issue['line']:5}  {issue['rule']:6}  {issue['message']}{fix}")

        print(f"\n{'='*50}")
        print(f"Total: {total} issues "
              f"({by_severity.get('error', 0)} errors, "
              f"{by_severity.get('warning', 0)} warnings, "
              f"{by_severity.get('suggestion', 0)} suggestions)")


class SARIFReporter:
    """Static Analysis Results Interchange Format — GitHub code scanning."""

    def report(self, all_issues: dict[str, list[dict]]) -> str:
        results = []
        rules_seen = set()

        for path, issues in all_issues.items():
            for issue in issues:
                rule_id = issue["rule"]
                rules_seen.add(rule_id)
                results.append({
                    "ruleId": rule_id,
                    "level": issue.get("severity", "warning"),
                    "message": {"text": issue["message"]},
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": path},
                            "region": {
                                "startLine": issue["line"],
                                "startColumn": issue.get("col", 1),
                            },
                        }
                    }],
                })

        rules = [{"id": rid, "shortDescription": {"text": rid}} for rid in sorted(rules_seen)]

        sarif = {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {"driver": {"name": "ahk-lint", "version": "2.0.0", "rules": rules}},
                "results": results,
                "columnKind": "utf16CodeUnits",
            }],
        }
        return json.dumps(sarif, indent=2)


class JSONReporter:
    """Machine-readable JSON output."""

    def report(self, all_issues: dict[str, list[dict]]) -> str:
        output = {
            "tool": "ahk-lint",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "files": len(all_issues),
                "total": sum(len(v) for v in all_issues.values()),
            },
            "issues": [{"path": path, "issues": issues} for path, issues in sorted(all_issues.items())],
        }
        return json.dumps(output, indent=2)
