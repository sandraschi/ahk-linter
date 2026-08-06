#!/usr/bin/env python3
"""Compute per-script density stats for the expanded v1 corpus.

Output: tests/fixtures/v1_corpus_stats.json  (used by paper tables)
         prints summary table to stdout
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ahk_lint import Linter, LinterConfig, load_grammar


def analyze_corpus(corpus_dir: Path) -> list[dict]:
    grammar = load_grammar()
    config = LinterConfig.load()
    linter = Linter(config, grammar)

    results = []
    for fpath in sorted(corpus_dir.glob("*.ahk")):
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        loc = len(source.splitlines())
        try:
            issues = linter.lint_file(fpath)
        except Exception:
            continue
        errors = [i for i in issues if i.get("severity") == "error"]
        warnings = [i for i in issues if i.get("severity") == "warning"]
        top_rules = list(dict.fromkeys(i["rule"] for i in issues))[:3]
        results.append(
            {
                "file": fpath.name,
                "loc": loc,
                "total": len(issues),
                "errors": len(errors),
                "warnings": len(warnings),
                "density": len(issues) / max(loc, 1) * 1000,
                "top_rules": top_rules,
            }
        )

    return results


if __name__ == "__main__":
    corpus_dir = Path(__file__).parent / "fixtures" / "v1_corpus_external"
    results = analyze_corpus(corpus_dir)

    if not results:
        print("No scripts found. Run scrape_v1_corpus.py first.")
        sys.exit(1)

    total_issues = sum(r["total"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    total_loc = sum(r["loc"] for r in results)
    avg_density = sum(r["density"] for r in results) / len(results)

    print("\n=== Corpus summary ===")
    print(f"Scripts: {len(results)}")
    print(f"Total LOC: {total_loc:,}")
    print(f"Total issues: {total_issues}  |  Errors: {total_errors}")
    print(f"Avg density: {avg_density:.1f} issues/KLOC")
    print(
        f"\n{'Script':50s} {'LOC':6s} {'Iss':5s} {'Err':5s} {'Warn':5s} {'Dens':7s}  Top patterns"
    )
    print("-" * 100)
    for r in sorted(results, key=lambda x: -x["density"]):
        d = f"{r['density']:.0f}/KLOC"
        try:
            print(
                f"{r['file']:50s} {r['loc']:6d} {r['total']:5d} {r['errors']:5d} "
                f"{r['warnings']:5d} {d:7s}  {', '.join(r['top_rules'])}"
            )
        except UnicodeEncodeError:
            safe_name = r["file"][:40].encode("ascii", errors="replace").decode("ascii")
            print(
                f"{safe_name:50s} {r['loc']:6d} {r['total']:5d} {r['errors']:5d} "
                f"{r['warnings']:5d} {d:7s}  {', '.join(r['top_rules'])}"
            )

    # Top patterns across corpus
    all_rules: Counter = Counter()
    for r in results:
        for rule in r["top_rules"]:
            all_rules[rule] += 1
    print("\nMost common patterns across corpus:")
    for rule, count in all_rules.most_common(10):
        print(f"  {rule}: {count} scripts")

    # Write JSON for paper
    stats_path = Path(__file__).parent / "fixtures" / "v1_corpus_stats.json"
    stats_path.write_text(json.dumps(results, indent=2))
    print(f"\nStats written to {stats_path}")
