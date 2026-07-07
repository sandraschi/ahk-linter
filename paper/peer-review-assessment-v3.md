# Peer Review (Round 3): *ahk-lint: Detecting and Repairing AutoHotkey v1 Patterns in the Age of LLMs*

## Summary

This is the third review round. Round 2 gave WEAK ACCEPT after the three fatal issues from Round 1 were resolved, but flagged two unverified citations (`gu2024repair`, `dsl_linter`) and a 7-item checklist. This round checks v5 of the paper.

The two replacement arXiv IDs (`fan2024survey`, `bouzenia2024repair`) are verified as real papers. Several low-priority checklist items were addressed (abstract tightened, retrieval dates added to 4 of 8 URL entries, Lark version pinned). MCP loop evaluation and v1 fixtures remain unaddressed.

Three minor citation issues remain — all are mechanical cleanup errors, not fraudulent claims.

---

## Scores and Critiques

### 1. Originality: **5/10** (unchanged from R2: 3→5)

The tool remains an engineering artifact, not a research contribution. The core technique — regex-based pattern matching against a JSON mapping extracted from a community converter — requires no novel algorithmic work. The paper's honesty about its scope, demonstrated across three review rounds, is now its strongest posture.

Contribution #4 (MCP integration) ~30 lines, feedback loop described but never evaluated. This is the weakest numbered claim.

### 2. Soundness: **6/10** (unchanged from R2: 2→6)

All three R1 fatal issues remain resolved through two subsequent rounds. The paper acknowledges limitations openly (v1 corpus size, LLM methodology as observations not experiment, coverage gaps). The MCP feedback loop is still asserted, not demonstrated.

### 3. Reproducibility: **7/10** (unchanged from R2: 5→7)

Lark version now pinned to `~=1.1` (L292). V1 fixtures still not shipped in the repository. No `uv.lock`.

### 4. Related Work: **6/10** (unchanged from R2: 4→6)

Text-level citations are correct: `fan2024survey` (arXiv:2308.10620) and `bouzenia2024repair` (arXiv:2403.17134) are both verified, real papers. `dsl_linter` removed from text body.

Three mechanical citation issues remain:

| Bib key | Lines | Issue | Severity |
|---|---|---|---|
| `fan2024survey` | 347--348 | **Wrong author name** — cites "X. Fan et al." but arXiv:2308.10620 is by Xinyi Hou et al. No author named "Fan" exists on the paper. Real paper, wrong attribution. | Error |
| `gu2024repair` | 329--330 | **Orphaned** — replaced in text by the two new citations, but old bib entry not removed. | Clutter |
| `dsl_linter` | 333--334 | **Orphaned** — removed from text (L87), but old bib entry not removed. | Clutter |

The L87 language-specific tooling sentence now makes a concrete claim ("even simple tooling can significantly improve code quality in under-tooled language ecosystems") with no supporting citation — this is a regression from having a citation (even if it was to an unverified paper in R2).

### 5. Writing & Presentation: **7/10** (unchanged from R2: 4→7)

Addressed: abstract's final sentence now reads "this paper describes the tool that automated that process and evaluates its coverage against both legacy and modern AHK codebases." Still informal but has a scientific component. Retrieval dates added to lark, semgrep, treesitter, and astgrep entries. Lark version pinned.

Still missing: retrieval dates on rustfix, mcp, thqby, and converter. Two orphaned bib entries. `\begin{thebibliography}{20}` declares room for 20 entries; 16 exist.

### 6. Impact: **4/10** (unchanged from R2: 3→4)

The MCP feedback loop (Contribution #4) remains unevaluated. The v1 corpus remains 7 scripts from a single project. No empirical baseline comparison exists.

---

## Meta Verdict

**RECOMMENDATION: ACCEPT for arXiv cs.SE** (up from WEAK ACCEPT in R2, up from REJECT in R1)

The paper is clean enough to post. The three remaining citation issues are mechanical — wrong author name on a real paper, two orphaned bib entries — not fraudulent. They should be fixed before posting (3 single-line edits, ~5 minutes).

**Trajectory across rounds:**

| Round | Verdict | Citation Severity | Core Claims |
|---|---|---|---|
| R1 | REJECT | FRAUD (fabricated arXiv ID, fictional experiment) | Dishonest |
| R2 | WEAK ACCEPT | SUSPICIOUS (two unverified citations) | Honest, unverified |
| R3 | **ACCEPT** | ERROR (wrong author name + orphaned entries) | Honest, verified |

---

## Citation Audit (Complete, All Rounds)

| Round | Bib key | Finding | Status |
|---|---|---|---|
| R1 | `ahk_survey` | Fabricated arXiv:1908.09453 — grocery shopping paper | **Removed R2** |
| R1 | `bibtex`, `knuth`, `sarif`, `2to3`, `gofix`, `autohotkey`, `pyupgrade` | 7 uncited entries | **Removed R2** |
| R1 | `mcp` / `mcp_patterns` | Duplicate entries | **Merged R2** |
| R2 | `gu2024repair` | "J. Gu et al., ICSE 2024" — no such paper | **Orphaned R3** (replaced in text, bib not cleaned) |
| R2 | `dsl_linter` | "J. Källäinen et al., SoSyM 2021" — unconfirmed | **Orphaned R3** (removed from text, bib not cleaned) |
| R3 | `fan2024survey` | Real arXiv:2308.10620, wrong author: "X. Fan" should be "X. Hou" | **Active bug** |
| R3 | `bouzenia2024repair` | Real arXiv:2403.17134, correct author I. Bouzenia | **Clean** |

---

## Pre-Posting Checklist (arXiv)

Three single-line edits, ~5 minutes:

| # | Fix | Location |
|---|---|---|
| 1 | Change "X. Fan et al." to "X. Hou et al." | L348 |
| 2 | Remove orphaned `\bibitem{gu2024repair}` (L329--330) | L329--330 |
| 3 | Remove orphaned `\bibitem{dsl_linter}` (L333--334) | L333--334 |

Optionally, add a citation to the uncited claim on L87 or soften the wording to "Prior work suggests that..."

---

---

# Minimum Viable Upgrade for a Peer-Reviewed Venue

The paper would be competitive for SANER tool track or ICPC with ~3 person-days of additional work. What follows is the minimum set of additions that move the paper from arXiv-ready to conference-track-ready. No restructuring needed — just additional tables, paragraphs, and data.

## 1. Diverse v1 corpus (30--50 scripts)

**Current state:** 7 scripts from a single project (`autohotkey-test` depot). A single-project corpus means you cannot claim the tool generalizes to arbitrary AHK codebases. Conference reviewers will flag this immediately.

**What to do:**
- GitHub code search for `#Requires AutoHotkey v1`, `#NoEnv` (v1-only directive), or scripts with command-style syntax (comma-separated parameters)
- Clone the top 50 results, classify manually (exclude non-.ahk files, empty files, translation-only files with no commands)
- Run `ahk-lint` on all of them
- Report: total issues, error/warning breakdown, per-category distribution, issues-per-LOC density

**What this gives you:** A per-project results table (like Table 3 but for 30--50 rows instead of 7). A density metric (issues per KLOC) that shows whether the tool catches proportionally more issues in larger scripts. External validity that the current paper claims as "threat" but doesn't fix.

**Effort:** 1--2 days. Most of it is waiting for GitHub search API rate limits. The linter already runs in batch mode.

## 2. Baseline comparison against one tool

Every tool paper at SANER/ICPC needs "compared to what?" The current paper has zero empirical baselines. Add one. Three options, ordered by effort:

### Option A: ast-grep (recommended — cheapest, strongest signal)

**Rationale:** Already discussed in Related Work (L85--86). `tree-sitter-ahk` grammar exists. ast-grep is a single binary with YAML rule format. You can write 3--5 AHK v1 rules in ~30 minutes and run them on the same v1 corpus.

**What to do:**
- Install ast-grep, write 3--5 YAML rules covering the most common patterns (e.g., `MsgBox,`, `StringSplit,`, `%var%` dereference)
- Run on the same v1 corpus
- Report: how many issues each tool catches, overlap, where each tool has blind spots

**What this gives you:** A concrete answer to the reviewer question "why not just use ast-grep?" — which is already implicit in the paper's Related Work. Shows your tool catches migration-specific patterns that a general-purpose tool misses, while acknowledging ast-grep's advantages (mature parser, no reduce/reduce collisions).

### Option B: mmikeww converter (full)

**Rationale:** Your paper positions the converter as the gold standard (51% coverage claim). Running the converter on the same corpus and comparing output validates your claim with per-script data.

**What to do:**
- Run `AHK-v2-script-converter` on each v1 script, capture the transformed output
- Compare: which v1 patterns did the converter catch that your linter missed? Which did your linter catch that the converter didn't? (This second case would be a finding — you might have patterns the converter doesn't cover.)

### Option C: THQBY LSP

**Rationale:** The paper describes the LSP (L73) as "the only complete parser." Running it on v1 scripts shows what the LSP's diagnostics catch vs. what your migration-specific linter catches.

**What to do:**
- Install `vscode-autohotkey2-lsp`, run diagnostics on the v1 corpus
- Compare LSP error output vs. `ahk-lint` detection categories
- Report: overlap, unique detections per tool

**Effort:** 2--4 hours for ast-grep. An afternoon for the converter comparison. A few hours for the LSP comparison.

**Recommendation:** ast-grep (cheapest, strongest signal, directly addresses the "why not just use an existing tool?" question).

## 3. MCP loop: evaluate or drop

Contribution #4 claims "MCP integration enabling agents to self-check generated code in a feedback loop." Conference reviewers will flag this as an unevaluated claim. Two options:

### Option A: Evaluate (recommended)

**What to do:**
- Prompt an LLM (Claude, GPT-4, or DeepSeek) to write 10 AHK functions covering representative patterns (file I/O, GUI, hotkeys, string manipulation)
- Run `lint_check` on each generated function
- Feed the lint errors back to the LLM in a follow-up prompt: "Your code has these v1 patterns: [errors]. Rewrite it in v2 syntax."
- Report: fix rate on second attempt, token cost, average loop iterations to clean

**What this gives you:** A novel, citable result — nobody has measured LLM self-correction rates for AHK code generation. Even a small experiment (N=10, two LLMs) is publishable as a preliminary finding. The good outcome (high fix rate) validates your Contribution #4. The honest outcome (low fix rate, models need multiple iterations) is still interesting and supports your thesis that a linter is needed.

### Option B: Drop

Remove "MCP integration" from the enumerated contributions list. Keep it as an architecture detail in §3.3. The paper goes from 4 contributions to 3. This is honest scoping and doesn't weaken the paper — it removes an unevaluated claim.

**Effort:** 3 hours for Option A (prompting + analysis + writing). 10 minutes for Option B (deleting one line from the contributions list).

**Recommendation:** Option A. It adds a genuine finding. Even a "we tried this on 10 examples and got 7/10 fixed" result is more than most tool papers provide for their LLM integration claims.

## 4. Reproducibility package (hygiene)

| Item | What | Effort |
|---|---|---|
| Ship v1 fixtures | Commit the 7 v1 scripts to `tests/fixtures/v1_originals/` with license headers | 30 min |
| Add `uv.lock` | Run `uv lock` and commit the lockfile | 2 min |
| Version manifest | One sentence in README: Python 3.11+, Lark~=1.1, tested on Windows | 5 min |

These are already tested and confirmed working — just not committed to the repository.

## 5. Fix remaining citation errors (hygiene)

Already listed in the pre-posting checklist above. Three single-line edits. Should be fixed regardless of conference submission.

---

## Effort Summary

| Upgrade | Time | Risk | Category |
|---|---|---|---|
| Fix citation errors (3 lines) | 5 min | None | Hygiene |
| Reproducibility package | 30 min | None | Hygiene |
| MCP loop evaluation (10 examples) | 3 hours | Medium — LLM output is stochastic; report honestly | Research |
| Baseline comparison (ast-grep) | 3--4 hours | Low — tool is mature, grammar exists | Research |
| Diverse corpus (30--50 scripts) | 1--2 days | Low — GitHub search is deterministic | Research |
| **Total** | **~3 person-days** | | |

All upgrades are additive — the paper structure, claims, and presentation don't need restructuring, just additional tables and paragraphs.

## Score Projection (Post-Upgrade)

| Dimension | Current (R3) | Post-Upgrade | Delta |
|---|---|---|---|
| Originality | 5 | 5 | — (tool remains an engineering artifact) |
| Soundness | 6 | 7.5 | +1.5 (larger corpus, baselined, MCP evaluated) |
| Reproducibility | 7 | 8.5 | +1.5 (fixtures shipped, lockfile, pinned deps) |
| Related Work | 6 | 7 | +1 (empirical comparison vs. ast-grep) |
| Writing | 7 | 7 | — (already clean) |
| Impact | 4 | 6 | +2 (MCP result is novel, baselines add credibility) |

Averaged ~7/10 post-upgrade — competitive for SANER tool track and ICPC.

---

*Reviewer: Same as Rounds 1 and 2. Re-assessment based on paper.tex v5. Upgrade roadmap for conference-track readiness.*
