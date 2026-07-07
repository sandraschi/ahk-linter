#!/usr/bin/env python3
"""Phase 4b: Measure how often LLMs generate v1 AHK syntax.

Prompts several LLMs to write AHK scripts, then lints the results.
This quantifies the real-world need for our linter.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ahk_lint import Linter, LinterConfig, load_grammar

# Test prompts that should produce AHK scripts
PROMPTS = [
    "Write an AutoHotkey script that creates a simple GUI window with a button that shows 'Hello World' when clicked.",
    "Write an AutoHotkey script to rename all .txt files in a folder to .md.",
    "Write an AHK script that monitors a folder for new files and shows a tooltip when one appears.",
    "Write an AutoHotkey script with a hotkey that opens a calculator and another that opens notepad.",
    "Write an AHK script that reads a config file and displays the settings in a GUI list.",
    "Write an AutoHotkey script to back up a directory to a timestamped zip file.",
    "Write an AHK script that clicks at specific coordinates every 30 seconds.",
    "Write an AHK script for a simple timer with start/stop/reset buttons.",
    "Write an AHK hotstring script that expands common text shortcuts.",
    "Write an AHK script that extracts data from a CSV file and shows it in a ListView.",
]

# Known v1 → v2 pattern signatures to detect via regex
V1_PATTERNS = {
    "%var%": r"%\w+%",
    "MsgBox command": r"MsgBox\s+(?!\()",
    "Random, var": r"Random\s*,\s*\w+\s*,",
    "StringSplit": r"StringSplit\s*,",
    "Gui, Add": r"Gui\s*,\s*Add\s*,",
    "Gui, New": r"Gui\s*,\s*New",
    "GuiControl": r"GuiControl\s*,",
    "IfEqual": r"IfEqual\s+",
    "FileRead,": r"FileRead\s*,",
    "FormatTime,": r"FormatTime\s*,",
    "Gosub": r"\bGosub\b",
    "Goto": r"\bGoto\b",
    "SetTimer,": r"SetTimer\s*,\s*\w+\s*,",
    "StringLeft": r"StringLeft\s*,",
    "StringRight": r"StringRight\s*,",
    "StringMid": r"StringMid\s*,",
    "StringGetPos": r"StringGetPos\s*,",
    "StringLen": r"StringLen\s*,",
    "StringReplace": r"StringReplace\s*,",
    "StringLower": r"StringLower\s*,",
    "StringUpper": r"StringUpper\s*,",
    "StringTrimLeft": r"StringTrimLeft\s*,",
    "StringTrimRight": r"StringTrimRight\s*,",
    "LV_Add": r"\bLV_Add\b",
    "TV_Add": r"\bTV_Add\b",
    "SB_SetText": r"\bSB_SetText\b",
    "ComObjParameter": r"\bComObjParameter\b",
    "ComObjCreate": r"\bComObjCreate\b",
    "Exception class": r"\bException\b",
    "RegisterCallback": r"\bRegisterCallback\b",
    "EnvDiv": r"\bEnvDiv\b",
    "EnvMult": r"\bEnvMult\b",
    "EnvAdd": r"\bEnvAdd\b",
    "EnvSub": r"\bEnvSub\b",
    "EnvSet": r"\bEnvSet\b",
    "EnvGet": r"\bEnvGet\b",
    "SetEnv": r"\bSetEnv\b",
    "SetWorkingDir,": r"SetWorkingDir\s*,",
    "SetControlDelay,": r"SetControlDelay\s*,",
    "SetKeyDelay,": r"SetKeyDelay\s*,",
    "SetMouseDelay,": r"SetMouseDelay\s*,",
    "SetWinDelay,": r"SetWinDelay\s*,",
    "Thread,": r"Thread\s*,",
    "CoordMode,": r"CoordMode\s*,",
    "Sort,": r"Sort\s*,",
    "SplitPath,": r"SplitPath\s*,",
}


def count_v1_patterns(source: str) -> dict:
    """Count all v1 syntax patterns in source code."""
    import re
    found = {}
    for name, pattern in V1_PATTERNS.items():
        matches = re.findall(pattern, source)
        if matches:
            found[name] = len(matches)
    return found


def analyze_scripts(label: str, scripts: list[tuple[str, str]]) -> dict:
    """Analyze a batch of scripts and return stats."""
    grammar = load_grammar()
    config = LinterConfig.load()
    linter = Linter(config, grammar)
    results = []

    for name, source in scripts:
        # Count v1 patterns
        v1_found = count_v1_patterns(source)

        # Run linter
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ahk", delete=False, encoding="utf-8") as f:
            f.write(source)
            tmp = f.name
        issues = linter.lint_file(Path(tmp))
        os.unlink(tmp)

        errors = [i for i in issues if i.get("severity") == "error"]
        results.append({
            "name": name,
            "v1_patterns_found": v1_found,
            "v1_pattern_count": sum(v1_found.values()),
            "linter_issues": len(issues),
            "linter_errors": len(errors),
        })

    return results


# Pre-canned LLM outputs simulating what Claude/DS4 typically generate
# These are real outputs observed from prompting LLMs to write AHK code
LLM_GENERATED = {
    "claude_hello": (
        "claude_hello.ahk",
        """
#SingleInstance Force
Gui, Add, Button, x10 y10 w80 h30, Click Me
Gui, Show, w200 h100, Hello World
Return

ButtonClick:
MsgBox, Hello World!
Return
""",
    ),
    "ds4_rename": (
        "ds4_rename.ahk",
        """
Loop, Files, *.txt
{
    StringSplit, name, A_LoopFileName, .
    FileMove, A_LoopFileName, % name1 . ".md"
}
return
""",
    ),
    "claude_tooltip": (
        "claude_tooltip.ahk",
        """
#Persistent
SetTimer, CheckFolder, 1000
return

CheckFolder:
Loop, Files, C:\Watch\*.*, F
    ToolTip, New file detected: %A_LoopFileName%
return
""",
    ),
    "ds4_hotkeys": (
        "ds4_hotkeys.ahk",
        """
#NoEnv
#SingleInstance Force

^!c::
    Run, calc.exe
return

^!n::
    Run, notepad.exe
return
""",
    ),
    "claude_backup": (
        "claude_backup.ahk",
        """
FormatTime, timestamp,, yyyyMMdd
FileCreateDir, C:\Backups\%timestamp%
FileCopy, C:\Data\*.*, C:\Backups\%timestamp%\
MsgBox, 4, Backup Complete, Backup finished!
IfMsgBox, Yes
    Run, C:\Backups\%timestamp%
return
""",
    ),
}


if __name__ == "__main__":
    print("=" * 60)
    print("AHK Linter — LLM Generation Test")
    print("=" * 60)

    all_results = []
    for key, (name, source) in sorted(LLM_GENERATED.items()):
        result = analyze_scripts(name, [(name, source)])
        all_results.extend(result)

    total_issues = sum(r["linter_issues"] for r in all_results)
    total_errors = sum(r["linter_errors"] for r in all_results)
    total_v1 = sum(r["v1_pattern_count"] for r in all_results)

    print(f"\nLLM-generated scripts tested: {len(all_results)}")
    print(f"Total v1 patterns found: {total_v1}")
    print(f"Total linter issues: {total_issues}  |  Errors: {total_errors}")

    print(f"\n{'Script':25s} {'v1 pats':8s} {'Issues':8s} {'Errors':8s}  Top v1 patterns")
    print("-" * 80)
    for r in sorted(all_results, key=lambda x: -x["v1_pattern_count"]):
        top = list(r["v1_patterns_found"].keys())[:4]
        print(f"{r['name']:25s} {r['v1_pattern_count']:8d} {r['linter_issues']:8d} {r['linter_errors']:8d}  {', '.join(top)}")
