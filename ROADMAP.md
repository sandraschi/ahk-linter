# ahk-lint Roadmap

Based on Opus's review and analysis of thqby's LSP parser and mmikeww's v1→v2 converter.

## Current State

17 checks, Lark PEG grammar, CLI only. Works for the fleet. Missing:
- Hard parsing problems (expression-vs-command ambiguity)
- ~300 known v1→v2 patterns we don't check
- MCP wrapper for agent use
- LLM-generated test corpus

## Phase 1 — Rule Completeness (1-2 days)

Extract the full rule set from mmikeww's converter and add the missing checks.

**Source:** `mmikeww/AHK-v2-script-converter` has ~325 rule entries + ~70 handler functions.

**Missing categories to add:**

| Category | Source | Rules | Effort |
|----------|--------|-------|--------|
| Window commands (WinGet, WinSet, etc.) | converter `1Commands.ahk` | ~25 | 2h |
| Control commands (ControlClick, ControlGetPos, etc.) | converter `1Commands.ahk` | ~12 | 1h |
| File commands (FileCopy, FileDelete, FileReadLine, etc.) | converter `1Commands.ahk` | ~18 | 1h |
| Registry commands | converter `1Commands.ahk` | 3 | 15m |
| Mouse commands | converter `1Commands.ahk` | 4 | 15m |
| Sound commands | converter `1Commands.ahk` | 4 | 15m |
| Send/Input commands | converter `1Commands.ahk` | ~10 | 1h |
| String commands (StringCaseSense, StringLower/Upper) | converter `1Commands.ahk` | 3 | 15m |
| Process/System commands | converter `1Commands.ahk` | ~6 | 30m |
| GUI commands (Gui, GuiControl, GuiControlGet) | converter `1Commands.ahk` | 3 | 2h (complex) |
| Menu commands | converter `1Commands.ahk` | 1 | 30m |
| Loop variants (Files, Reg, Parse, Read) | converter `1Commands.ahk` | 1+modes | 1h |
| Function renames (LV_*, TV_*, SB_*, etc.) | converter `2Functions.ahk` | ~45 | 3h |
| Object methods (HasKey → Has, etc.) | converter `3Methods.ahk` | 3 | 15m |
| Array methods (Insert → InsertAt, Remove → RemoveAt, etc.) | converter `4ArrayMethods.ahk` | 6 | 30m |
| Keyword renames (A_IPAddress1 → SysGetIPAddresses(), etc.) | converter `5Keywords.ahk` | ~14 | 1h |
| Deprecated/removed commands | converter `1Commands.ahk` | 15 | 30m |
| Old object model (obj.key → obj["key"], pseudo-arrays) | converter `PseudoHandling.ahk` | ~10 | 2h |
| Hotkey/Hotstring syntax deltas | converter `1Commands.ahk` | 2 | 30m |
| try/catch/throw object shape changes | converter `AhkLangConv.ahk` | 1 | 30m |

**Total new rules:** ~200+ (conservative)
**Total time:** ~20h spread across 5 days

**Goal:** Pass the fleet's 80+ scripts with zero errors + flag at least 200 v1 patterns the current linter misses.

## Phase 2 — Better Parsing (1-2 weeks)

Our Lark grammar is naive. thqby's LSP server (`vscode-autohotkey2-lsp`, 9,525 lines of TypeScript) is the reference implementation.

**Option A — Call the LSP server from Python** (recommended, 2-3 days)
- The existing `server/dist/` build speaks LSP over stdin/stdout
- Wrap it with a Python subprocess manager
- Use LSP diagnostics as a second pass (catch what our parser misses)
- Saves porting 9,525 lines of TypeScript

```python
# pseudocode
class THQBYLSP:
    def __init__(self):
        self.proc = subprocess.Popen(["node", "server/dist/server.js", "--stdio"], ...)
    def lint(self, source: str) -> list[dict]:
        # Send textDocument/didOpen → get diagnostics
        return diagnostics
```

**Option B — Port the tokenizer state machine to Python** (2-3 weeks)
- The core parsing logic is in `server/src/lexer.ts` (7,309 lines)
- Must replicate: `topofline` flag, `isContinuousLine()`, `isYieldsOperand()`, operator disambiguation, hotkey detection before tokenization
- High effort, high maintenance, high fidelity

**Decision:** Start with Option A. If the LSP subprocess overhead proves problematic, consider Option B.

## Phase 3 — MCP Wrapper (1 day)

```python
from fastmcp import FastMCP
mcp = FastMCP("ahk-lint")

@mcp.tool()
def lint_ahk_script(source: str, fix: bool = False) -> dict:
    """Lint an AHK script and return diagnostics."""
    issues = linter.lint_string(source)
    return {"issues": issues, "total": len(issues)}

@mcp.tool()
def lint_ahk_file(path: str) -> dict:
    """Lint an AHK file."""
    ...
```

- Lets Claude/Cursor call the linter before executing generated AHK scripts
- Agents can self-check their own output

## Phase 4 — LLM Test Corpus (1 day)

Generate 30 AHK scripts from 3 LLMs (Claude, DeepSeek, GPT-4):

```bash
# Prompt: "write an AHK script that..."
# Collect output → lint → measure false negatives
```

**Metrics:**
- False negatives: patterns our linter misses that a human would catch
- False positives: patterns our linter flags incorrectly
- Coverage: % of v1 patterns detected vs mmikeww's converter

## Phase 5 — Polish & Paper (1 week)

- Write up the approach (regex→AST hybrid, LSP integration)
- Document the rule extraction from mmikeww's converter
- Publish to arXiv

## Summary

| Phase | What | Time | Depends on |
|-------|------|------|------------|
| 1 | 200+ missing rules from converter | 5 days | — |
| 2 | LSP integration for hard parsing | 3 days | Phase 1 |
| 3 | MCP wrapper | 1 day | Phase 1 |
| 4 | LLM test corpus | 1 day | Phase 1 |
| 5 | Paper | 1 week | Phases 1-4 |
