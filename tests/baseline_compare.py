#!/usr/bin/env python3
"""Compare ahk-lint vs ast-grep on the same v1 corpus.

Expects:
  - tests/fixtures/v1_corpus_stats.json  (from corpus_stats.py)
  - tests/ast-grep-results.json          (from: sg scan --json ...)
"""

import json
from pathlib import Path


def load_astgrep(path: Path) -> dict[str, int] | str:
    data = json.loads(path.read_text())
    if data.get("status") == "not_supported":
        return data.get("reason", "not supported")
    counts: dict[str, int] = {}
    for result in data.get("results", []):
        fname = Path(result.get("file", "")).name
        findings = result.get("findings", [])
        counts[fname] = counts.get(fname, 0) + len(findings)
    return counts


def load_ahklint(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text())
    return {r["file"]: r for r in data}


def main():
    stats_path = Path(__file__).parent / "fixtures" / "v1_corpus_stats.json"
    ast_path = Path(__file__).parent / "ast-grep-results.json"

    if not stats_path.exists():
        print("No ahk-lint stats file. Run corpus_stats.py first.")
        return
    if not ast_path.exists():
        print(
            "No ast-grep results file. Run: sg scan tests/fixtures/v1_corpus_external/ "
            "--rule ast-grep-rules/ahk-v1-migration.yml --json > tests/ast-grep-results.json"
        )
        return

    ahk = load_ahklint(stats_path)
    ast = load_astgrep(ast_path)

    if isinstance(ast, str):
        print(f"ast-grep: NOT SUPPORTED — {ast[:120]}...")
        print()
        total_ahk = sum(a["total"] for a in ahk.values())
        print(f"ahk-lint total: {total_ahk} issues across {len(ahk)} scripts")
        print("ast-grep total: 0 (no AHK language support)")
        print("Conclusion: Grammar-based tools cannot analyze AHK code.")
        print("  This validates ahk-lint's hybrid regex approach for legacy dialects.")
        return

    print(f"{'Script':50s} {'ahk-lint':9s} {'ast-grep':9s}")
    print("-" * 72)

    total_ahk = 0
    total_ast = 0
    n_ast_failed = 0

    for fname, a in sorted(ahk.items()):
        ast_count = ast.get(fname, -1)
        if ast_count == -1:
            print(f"{fname:50s} {a['total']:9d} {'(parse err)':9s}")
            n_ast_failed += 1
        else:
            print(f"{fname:50s} {a['total']:9d} {ast_count:9d}")
            total_ahk += a["total"]
            total_ast += ast_count

    print()
    print(f"ahk-lint total: {total_ahk}  |  ast-grep total: {total_ast}")
    print(f"ast-grep parse failures: {n_ast_failed}/{len(ahk)} scripts")
    if n_ast_failed > 0:
        print(
            "ast-grep parse failures on v1 scripts are expected: "
            "tree-sitter AHK grammar targets v2 syntax."
        )


if __name__ == "__main__":
    main()
