#!/usr/bin/env python3
"""MCP feedback loop evaluation: measure LLM self-correction rate.

Protocol:
  1. Prompt LLM to write AHK v2 code (10 prompts)
  2. Run lint_check on output -> collect errors
  3. Feed errors back: "Your code has these v1 errors. Fix them."
  4. Run lint_check again -> measure fix rate

Uses OpenAI-compatible API. Set env vars:
  MCP_LOOP_API_BASE  (default: http://localhost:11434/v1)
  MCP_LOOP_API_KEY   (default: ollama)
  MCP_LOOP_MODEL     (default: llama3.2:3b)
"""

import json
import os
import re
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ahk_lint import Linter, LinterConfig, load_grammar

API_BASE = os.environ.get("MCP_LOOP_API_BASE", "http://localhost:11434/v1")
API_KEY = os.environ.get("MCP_LOOP_API_KEY", "ollama")
MODEL = os.environ.get("MCP_LOOP_MODEL", "llama3.2:3b")
N_EXAMPLES = 10

SYSTEM_PROMPT = (
    "You are an AutoHotkey v2 expert. Always write AHK v2 syntax "
    "(function-call style, := assignment, no command syntax). "
    "Return ONLY the AHK code in a ```ahk code block."
)

SYSTEM_FIX = (
    "You are an AutoHotkey v2 expert. Fix the v1 syntax errors in the code below. "
    'Use function-call syntax (MsgBox("text") not MsgBox, text), '
    ":= for assignment, try/catch for error handling, object syntax for arrays. "
    "Return ONLY the corrected AHK v2 code in a ```ahk code block."
)

PROMPTS = [
    "Write an AutoHotkey v2 script that creates a simple GUI window with a "
    "button that shows 'Hello World' when clicked.",
    "Write an AutoHotkey v2 script to rename all .txt files in a folder to .md.",
    "Write an AHK v2 script that monitors a folder for new files and shows a "
    "tooltip when one appears.",
    "Write an AutoHotkey v2 script with a hotkey that opens a calculator and "
    "another that opens notepad.",
    "Write an AHK v2 script that reads a config file and displays the settings in a GUI list.",
    "Write an AutoHotkey v2 script to back up a directory to a timestamped zip file.",
    "Write an AHK v2 script that clicks at specific coordinates every 30 seconds.",
    "Write an AHK v2 script for a simple timer with start/stop/reset buttons.",
    "Write an AHK v2 script that extracts data from a CSV file and shows it in a ListView.",
    "Write an AHK v2 script that sends keystrokes to a specific window by title.",
]


def llm_chat(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 2000,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def extract_ahk_code(response: str) -> str:
    m = re.search(r"```(?:ahk|autohotkey)?\s*\n(.*?)```", response, re.DOTALL)
    if m:
        return m.group(1).strip()
    if response.strip().startswith("#") or "::" in response[:200]:
        return response.strip()
    return response.strip()


def lint_code(source: str, linter: Linter) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ahk", delete=False, encoding="utf-8") as f:
        f.write(source)
        tmp = f.name
    try:
        issues = linter.lint_file(Path(tmp))
    except Exception:
        issues = []
    Path(tmp).unlink()

    errs = [i for i in issues if i.get("severity") == "error"]
    warns = [i for i in issues if i.get("severity") == "warning"]
    return {
        "total": len(issues),
        "errors": len(errs),
        "warnings": len(warns),
        "error_rules": list(set(i["rule"] for i in errs)),
        "error_messages": [i.get("message", "") for i in errs],
    }


def format_feedback(lint_result: dict) -> str:
    if lint_result["errors"] == 0:
        return "No v1 syntax errors found."
    lines = [
        f"Your code has {lint_result['errors']} AHK v1 syntax errors that "
        f"need fixing for v2 compatibility:\n"
    ]
    for msg in lint_result["error_messages"]:
        lines.append(f"  - {msg}")
    lines.append("\nPlease rewrite the code in correct AHK v2 syntax.")
    return "\n".join(lines)


def main():
    grammar = load_grammar()
    config = LinterConfig.load()
    linter = Linter(config, grammar)

    results = []
    print(f"Model: {MODEL}  |  API: {API_BASE}  |  Prompts: {N_EXAMPLES}")
    print("=" * 70)

    for i, prompt in enumerate(PROMPTS[:N_EXAMPLES]):
        print(f"\n[{i + 1}/{N_EXAMPLES}] ", end="", flush=True)

        # Round 1: generate
        try:
            r1 = llm_chat(prompt, SYSTEM_PROMPT)
            code1 = extract_ahk_code(r1)
            lint1 = lint_code(code1, linter)
        except Exception as e:
            print(f"SKIP (API error: {e})")
            results.append(
                {
                    "prompt": prompt[:80] + "...",
                    "round1_errors": 0,
                    "round2_errors": 0,
                    "errors_fixed": 0,
                    "fix_rate": 0.0,
                    "persistent_rules": [],
                    "api_error": str(e),
                }
            )
            time.sleep(1)
            continue

        # Round 2: fix
        if lint1["errors"] > 0:
            try:
                feedback = format_feedback(lint1)
                r2 = llm_chat(feedback, SYSTEM_FIX)
                code2 = extract_ahk_code(r2)
                lint2 = lint_code(code2, linter)
            except Exception as e:
                print(f"R2 API error: {e}")
                lint2 = {
                    "total": 0,
                    "errors": lint1["errors"],
                    "warnings": 0,
                    "error_rules": [],
                    "error_messages": [],
                }
        else:
            lint2 = {"total": 0, "errors": 0, "warnings": 0, "error_rules": []}

        fixed = lint1["errors"] - lint2["errors"]
        fix_rate = fixed / max(lint1["errors"], 1)

        results.append(
            {
                "prompt": prompt[:80] + "...",
                "round1_errors": lint1["errors"],
                "round2_errors": lint2["errors"],
                "errors_fixed": fixed,
                "fix_rate": fix_rate,
                "persistent_rules": lint2.get("error_rules", []),
            }
        )

        status = "clean after fix" if lint2["errors"] == 0 else f"{lint2['errors']} errors remain"
        print(
            f"R1: {lint1['errors']} err -> R2: {lint2['errors']} err | "
            f"fix: {fix_rate:.0%} | {status}"
        )
        time.sleep(1)

    # Summary
    valid = [r for r in results if "api_error" not in r]
    total_r1 = sum(r["round1_errors"] for r in valid)
    total_r2 = sum(r["round2_errors"] for r in valid)
    overall_fix = (total_r1 - total_r2) / max(total_r1, 1) if total_r1 else 0.0
    mean_fix = sum(r["fix_rate"] for r in valid) / len(valid) if valid else 0.0
    fully_fixed = sum(1 for r in valid if r["round2_errors"] == 0)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total R1 errors: {total_r1}")
    print(f"Total R2 errors: {total_r2}")
    print(f"Overall fix rate: {overall_fix:.0%}")
    print(f"Mean per-prompt fix rate: {mean_fix:.0%}")
    print(f"Fully fixed (0 errors R2): {fully_fixed}/{len(valid)}")

    from collections import Counter

    persistent: Counter = Counter()
    for r in valid:
        for rule in r["persistent_rules"]:
            persistent[rule] += 1
    if persistent:
        print("\nPatterns most resistant to LLM self-correction:")
        for rule, count in persistent.most_common(5):
            print(f"  {rule}: {count} prompts")

    out_path = Path(__file__).parent / "mcp_feedback_loop_results.json"
    out_path.write_text(
        json.dumps(
            {
                "model": MODEL,
                "api_base": API_BASE,
                "n_examples": N_EXAMPLES,
                "results": results,
                "summary": {
                    "total_r1_errors": total_r1,
                    "total_r2_errors": total_r2,
                    "overall_fix_rate": overall_fix,
                    "mean_fix_rate": mean_fix,
                    "fully_fixed": fully_fixed,
                    "persistent_patterns": dict(persistent.most_common(10)),
                },
            },
            indent=2,
        )
    )
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
