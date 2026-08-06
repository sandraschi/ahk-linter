#!/usr/bin/env python3
"""Run semgrep on the expanded v1 corpus in batches and compare with ahk-lint."""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "fixtures" / "v1_corpus_external"
RULES_FILE = Path(__file__).parent.parent / "semgrep-rules" / "ahk-v1-migration.yml"
OUTPUT_FILE = Path(__file__).parent / "semgrep-corpus-results.json"
BATCH_SIZE = 100

# Rule ID -> short label mapping
RULE_LABELS = {
    "v1-msgbox-command": "MsgBox,",
    "v1-stringsplit": "StringSplit,",
    "v1-gui-add": "Gui,Add",
    "v1-gosub": "Gosub,",
    "v1-goto": "Goto,",
    "v1-settimer-label": "SetTimer(label)",
    "v1-noenv": "#NoEnv",
    "v1-assignment": "= (legacy)",
    "v1-stringleft": "StringLeft,",
    "v1-stringright": "StringRight,",
    "v1-stringmid": "StringMid,",
    "v1-autotrim": "AutoTrim,",
    "v1-iflegacy": "IfEqual/IfExist",
    "v1-percent-deref": "%var%",
    "v1-envmath": "EnvMath",
    "v1-fileread": "FileRead,",
}


def run_semgrep(files: list[str]) -> dict:
    proc = subprocess.run(
        ["semgrep", "--config", str(RULES_FILE), *files, "--no-git-ignore", "--json", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return json.loads(proc.stdout)


def main():
    ahk_files = sorted(CORPUS_DIR.glob("*.ahk"))
    if not ahk_files:
        print("No .ahk files found. Run scrape_v1_corpus.py first.")
        return

    # Load ahk-lint stats for comparison
    lint_stats_file = Path(__file__).parent / "fixtures" / "v1_corpus_stats.json"
    lint_stats = {}
    if lint_stats_file.exists():
        lint_stats = {r["file"]: r for r in json.loads(lint_stats_file.read_text())}

    all_findings: list[dict] = []
    per_file: dict[str, int] = Counter()
    total_scanned = 0

    for batch_start in range(0, len(ahk_files), BATCH_SIZE):
        batch = ahk_files[batch_start : batch_start + BATCH_SIZE]
        batch_paths = [str(f) for f in batch]

        try:
            data = run_semgrep(batch_paths)
        except Exception as e:
            print(f"Batch {batch_start // BATCH_SIZE + 1} failed: {e}", file=sys.stderr)
            continue

        findings = data.get("results", [])
        scanned = len(data.get("paths", {}).get("scanned", []))
        all_findings.extend(findings)
        total_scanned += scanned

        for f in findings:
            fname = Path(f["path"]).name
            per_file[fname] += 1

        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(ahk_files) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Batch {batch_num}/{total_batches}: {len(findings)} findings on {scanned} files")

    # Summary
    print("\n=== Semgrep Corpus Summary ===")
    print(f"Files scanned: {total_scanned}")
    print(f"Total findings: {len(all_findings)}")

    # Per-rule breakdown
    rule_counts: Counter = Counter()
    for f in all_findings:
        rule_counts[f["check_id"].split(".")[-1]] += 1

    print("\nFindings by rule:")
    for rule_id, count in rule_counts.most_common():
        label = RULE_LABELS.get(rule_id, rule_id)
        print(f"  {label:20s}: {count:6d}")

    # Comparison with ahk-lint
    if lint_stats:
        print("\n=== Comparison with ahk-lint ===")
        overlap = sum(1 for fname in per_file if fname in lint_stats)
        ahk_total = sum(r["total"] for r in lint_stats.values())
        print(f"Scripts with semgrep findings: {len(per_file)}")
        print(f"Scripts with ahk-lint findings: {len(lint_stats)}")
        print(f"Overlap (both tools found issues): {overlap}")
        print(f"ahk-lint total issues: {ahk_total}")
        print(f"semgrep total findings: {len(all_findings)}")

    # Save
    OUTPUT_FILE.write_text(
        json.dumps(
            {
                "tool": "semgrep 1.161.0 (generic mode)",
                "corpus_size": len(ahk_files),
                "files_scanned": total_scanned,
                "total_findings": len(all_findings),
                "rule_counts": dict(rule_counts),
                "per_file": dict(per_file.most_common(50)),
                "comparison_ahklint": {
                    "ahklint_total": ahk_total,
                    "files_with_semgrep": len(per_file),
                    "files_with_ahklint": len(lint_stats),
                    "overlap_files": overlap,
                }
                if lint_stats
                else None,
            },
            indent=2,
        )
    )
    print(f"\nResults written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
