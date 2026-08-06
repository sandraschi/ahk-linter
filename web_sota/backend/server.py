import json
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ahk_lint import Linter, LinterConfig, load_grammar

app = FastAPI(title="ahk-lint API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

grammar = load_grammar()
config = LinterConfig.load()
linter = Linter(config, grammar)

PAPER_DATA = {
    "title": "ahk-lint: Detecting and Repairing AutoHotkey v1 Patterns in the Age of LLMs",
    "authors": ["Sandra Schipal"],
    "abstract": "AutoHotkey (AHK) is a widely-used Windows automation language with millions of installations. Its 2022 v2 release broke compatibility with thousands of existing scripts, yet no academic work exists on AHK v2 migration tooling. We present ahk-lint, a dedicated linter for detecting and repairing v1-to-v2 migration patterns. It covers 167 known patterns across 7 rule modules, provides auto-fix for 10 common v1 syntax patterns, and integrates with the Model Context Protocol for agent self-checking. Evaluation on 676 v1 scripts from 25 GitHub repositories (189K LOC) detects 95,651 issues at an average density of 903 issues per 1,000 lines. On 19 production v2 scripts, the linter reports zero false positive errors.",
    "scores": {
        "Originality": 5,
        "Soundness": 6,
        "Reproducibility": 7,
        "Related Work": 6,
        "Writing": 7,
        "Impact": 4,
    },
    "verdict": "ACCEPT for arXiv cs.SE",
    "github_url": "https://github.com/sandraschi/ahk-linter",
    "arxiv_url": None,
    "review_status": "Accepted for arXiv cs.SE",
}

CHECKS_DATA = [
    {"module": "V1SyntaxCheck", "description": "Common v1-to-v2 syntax conversions (assignment, MsgBox, ToolTip, control flow, variable dereferencing)", "pattern_count": 10, "has_auto_fix": True},
    {"module": "CommandRulesCheck", "description": "Regex/declarative rules for every AHK v1 command mapped to v2 equivalent", "pattern_count": 167, "has_auto_fix": False},
    {"module": "FunctionRenamesCheck", "description": "Renamed built-in functions (LV_Add -> ListView.Add, etc.)", "pattern_count": 45, "has_auto_fix": False},
    {"module": "OldObjectModelCheck", "description": "Legacy pseudo-arrays (Array%i%), ComObj* functions, pre-v2 COM patterns", "pattern_count": 12, "has_auto_fix": False},
    {"module": "SafetyCheck", "description": "Dangerous patterns (NoEnv, unguarded file operations)", "pattern_count": 8, "has_auto_fix": False},
    {"module": "StyleCheck", "description": "Deprecated directives and formatting issues", "pattern_count": 6, "has_auto_fix": False},
    {"module": "DeadCodeCheck", "description": "Unreachable code after Exit or Return", "pattern_count": 2, "has_auto_fix": False},
]


class LintRequest(BaseModel):
    source: str


class FixRequest(BaseModel):
    source: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "server": "ahk-lint", "version": "2.0.0", "backend_port": 11076}


@app.post("/api/lint")
async def lint(req: LintRequest):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ahk", delete=False, encoding="utf-8") as f:
        f.write(req.source)
        tmp = Path(f.name)
    try:
        issues = linter.lint_file(tmp)
        total = len(issues)
        errors = sum(1 for i in issues if i.get("severity") == "error")
        warnings = sum(1 for i in issues if i.get("severity") == "warning")
        return {
            "issues": issues,
            "total": total,
            "by_severity": {"errors": errors, "warnings": warnings},
            "clean": total == 0,
        }
    finally:
        tmp.unlink(missing_ok=True)


@app.post("/api/fix")
async def fix(req: FixRequest):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ahk", delete=False, encoding="utf-8") as f:
        f.write(req.source)
        tmp = Path(f.name)
    try:
        fixed, new_content = linter.fix_file(tmp)
        return {"fixed": fixed, "source": new_content, "message": "Code is clean" if not fixed else "Auto-fix applied"}
    finally:
        tmp.unlink(missing_ok=True)


@app.get("/api/paper")
async def paper():
    return PAPER_DATA


@app.get("/api/checks")
async def checks():
    return {"modules": CHECKS_DATA, "total_patterns": sum(c["pattern_count"] for c in CHECKS_DATA)}
