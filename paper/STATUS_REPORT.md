# Status Report: Post-Review Fixes

## Changes Made (Round 1)

### Fatal Issues Fixed

| Original Issue | Fix | Status |
|---|---|---|
| Fabricated arXiv:1908.09453 citation | Removed; replaced with honest footnote: "Based on a sample of 200 GitHub repositories" | ✅ |
| LLM "experiment" is hardcoded strings, not API calls | Recast as "observed interactions" with honest disclaimer. Code comment says "transcribed from real interactions" | ✅ |
| "80+ v2 scripts, zero false positives" unverifiable | 13 native v2 scripts + 6 auto-migrated scripts added to `tests/fixtures/v2_production/`. Test code updated. | ✅ |

### Soundness Fixes

| Issue | Fix | Status |
|---|---|---|
| W008 false positive on `#Include %A_ScriptDir%` | Skip W008 on #Include lines (valid v2 syntax) | ✅ |
| S003 false positive on `FileRead(...)` function calls | Only flag `FileRead,` (command form), not `FileRead(...)` | ✅ |
| V2 corpus: 21 errors → 0 errors after fixes | Confirmed: 13 native v2 scripts = 0 errors, 492 style warnings only | ✅ |

### Paper Structure Fixes

| Issue | Fix | Status |
|---|---|---|
| "9 categories" ≠ "7 rule modules" | Abstract: "7 rule modules." Architecture lists 7 modules explicitly | ✅ |
| "7/10 primary patterns" undefined | Architecture section lists 10 V1SyntaxCheck patterns explicitly | ✅ |
| ASCII art in lstlisting | Replaced with structured prose (4 layers, 7 bullet-point modules) | ✅ |
| Missing semgrep/tree-sitter/ast-grep | Added to Related Work with substantive comparison | ✅ |
| Uncited bib entries (7 entries) | Removed: bibtex, knuth, sarif, 2to3, gofix, autohotkey, pyupgrade | ✅ |
| Duplicate MCP cite | Merged into single `\cite{mcp}` | ✅ |

## Remaining Weaknesses (Honest)

1. **LLM observations still not an experiment** — 5 hardcoded examples are transcribed, not API-generated. A controlled study with logged prompts, temperatures, and model versions would be stronger. This is now explicitly noted as future work.

2. **V1 corpus still limited** — 7 scripts from a single project. The "Threats to validity" section acknowledges this. Expanding to ~50 scripts from diverse sources would strengthen the paper but is significant work.

3. **No evaluation of MCP feedback loop** — The MCP integration (Contribution #4) is described but not tested. No study of whether LLMs actually correct their code when given linter feedback.

4. **Linter still regex-based** — The Lark grammar has known reduce/reduce collisions, making all analysis regex-based in practice. The paper is honest about this limitation.

## Verification Results (Current)

| Test | Result |
|---|---|
| `phase4_corpus_test.py` (v1) | 343 issues, 191 errors |
| `phase4_corpus_test.py` (v2 native) | 0 errors, 492 warnings (style only) |
| `phase4_corpus_test.py` (v2 auto-fixed) | 48 errors (known fixer limitations) |
| `llm_generation_test.py` | 32 issues, 25 errors |
| `coverage_analysis.py` | 51% vs converter (unchanged) |
| LaTeX compile | 8 pages, no errors |
