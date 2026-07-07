#!/usr/bin/env python3
"""Phase 4: Test linter against real v1 scripts (before migration) and v2 scripts (after)."""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ahk_lint import Linter, LinterConfig, load_grammar


def test_scripts(label: str, dir_path: Path) -> list[dict]:
    grammar = load_grammar()
    config = LinterConfig.load()
    linter = Linter(config, grammar)
    results = []

    for fpath in sorted(dir_path.glob("*.ahk")):
        issues = linter.lint_file(fpath)
        by_sev = {"error": 0, "warning": 0, "suggestion": 0}
        for i in issues:
            by_sev[i.get("severity", "warning")] += 1

        top_rules = list(dict.fromkeys(i["rule"] for i in issues))[:5]
        results.append({
            "file": fpath.name,
            "total": len(issues),
            "by_severity": by_sev,
            "top_rules": top_rules,
        })

        # Auto-fix
        fixed, new_content = linter.fix_file(fpath)
        if fixed:
            out_dir = dir_path.parent / f"{dir_path.name}_fixed"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / fpath.name).write_text(new_content, encoding="utf-8")

    total = sum(r["total"] for r in results)
    errors = sum(r["by_severity"]["error"] for r in results)
    warnings = sum(r["by_severity"]["warning"] for r in results)
    print(f"\n=== {label} ({len(results)} files) ===")
    print(f"  Total issues: {total}  |  Errors: {errors}  |  Warnings: {warnings}")
    print(f"  Avg per file: {total / len(results):.1f}" if results else "  (empty)")
    for r in sorted(results, key=lambda x: -x["total"]):
        e = r["by_severity"]["error"]
        w = r["by_severity"]["warning"]
        s = r["by_severity"]["suggestion"]
        print(f"  {r['file']:40s} {r['total']:3d} issues ({e}e, {w}w, {s}s)  [{', '.join(r['top_rules'])}]")
    return results


if __name__ == "__main__":
    fixtures = Path(__file__).parent / "fixtures"
    v1_dir = fixtures / "v1_originals"
    v2_dir = fixtures / "v2_production"
    v1_fixed_dir = fixtures / "v1_originals_fixed"

    print("=" * 60)
    print("AHK Linter Phase 4 — Corpus Test")
    print("=" * 60)

    v1_results = []
    if v1_dir.exists():
        v1_results = test_scripts("V1 SCRIPTS (before migration)", v1_dir)
    else:
        print(f"\nNo v1 fixtures at {v1_dir}")

    v2_results = []
    if v2_dir.exists():
        v2_results = test_scripts("V2 PRODUCTION SCRIPTS", v2_dir)
    else:
        print(f"\nNo v2 fixtures at {v2_dir}")

    v1_fixed_results = []
    if v1_fixed_dir.exists():
        v1_fixed_results = test_scripts("V1 SCRIPTS (auto-fixed to v2)", v1_fixed_dir)
    else:
        print(f"\nNo v1_fixed fixtures at {v1_fixed_dir}")

    native_v2_errors = sum(r["by_severity"]["error"] for r in v2_results)
    native_v2_warnings = sum(r["by_severity"]["warning"] for r in v2_results)
    fixed_v2_errors = sum(r["by_severity"]["error"] for r in v1_fixed_results)
    fixed_v2_warnings = sum(r["by_severity"]["warning"] for r in v1_fixed_results)
    print(f"\n=== V2 FALSE POSITIVE CHECK ===")
    print(f"  Native v2 scripts ({len(v2_results)}): {native_v2_errors} errors, {native_v2_warnings} warnings")
    print(f"  Auto-fixed v1 scripts ({len(v1_fixed_results)}): {fixed_v2_errors} errors, {fixed_v2_warnings} warnings (expected — fixer not perfect)")
    if native_v2_errors == 0:
        print(f"  Zero false positive errors on native v2 scripts confirmed.")
    print("\nDone.")
