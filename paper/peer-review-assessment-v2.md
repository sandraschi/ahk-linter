# Peer Review (Round 2): *ahk-lint: Detecting and Repairing AutoHotkey v1 Patterns in the Age of LLMs*

## Summary

This is a re-assessment after the fatal issues from Round 1 were addressed. The paper describes `ahk-lint`, a Python linter for detecting AutoHotkey v1 syntax patterns in v2 code. It covers 167 patterns across 7 rule modules, provides auto-fix for 10 patterns, and wraps the tool as an MCP server. Evaluation covers 7 legacy v1 scripts (343 issues), 19 production v2 scripts (0 false positive errors), and 5 transcribed LLM interaction examples (32 issues). Coverage against the community converter is 51%.

All three fatal issues from Round 1 are resolved. Two new citation concerns are identified. The paper now presents its contributions honestly and acknowledges limitations explicitly.

---

## Scores and Critiques

### 1. Originality: **5/10** (was 3/10)

The tool remains an engineering artifact, not a research contribution. The core technique — regex-based pattern matching against a JSON mapping extracted from a community converter — requires no novel algorithmic work. What has improved is the paper's honesty about its scope. It no longer frames the LLM "experiment" as empirical science, and it no longer fabricates a citation to support the 90% v1 corpus claim.

**Contribution #4 (MCP integration)** remains the weakest claim. The MCP server is ~30 lines, the feedback loop (lint → detect → report → fix) is described but never evaluated. No study shows LLMs actually correct their AHK code when given linter feedback. This is asserted, not demonstrated. Either evaluate it or demote it from "contribution" to "feature" in the text.

**Action items:**
- Evaluate the MCP feedback loop experimentally or downgrade it from Contribution #4
- Consider a head-to-head comparison: running the linter on LLM-generated code before and after MCP feedback

---

### 2. Soundness: **6/10** (was 2/10)

All three fatal problems from Round 1 are genuinely fixed:

**(a) Fake citation resolved.** The arXiv:1908.09453 claim is replaced by a footnote describing a manual sample of 200 GitHub repositories. The methodology is stated (check for `#Requires AutoHotkey v2` directive or exclusive v2 syntax). This is honest if unremarkable.

**(b) LLM "experiment" reframed.** The section is now titled "LLM Interaction Observations" (L205). The text explicitly states: "These are not the output of a controlled experiment but rather a documentation of a recurring phenomenon" (L208). The table caption calls them "representative LLM interactions," not experimental results. The limitation is acknowledged: "A controlled study with systematic prompt variation across multiple models remains future work" (L228). This is scientifically defensible for an arXiv paper.

**(c) V2 corpus now has fixtures.** The paper claims 13 native v2 scripts with 0 false positive errors, plus 6 auto-migrated scripts with 48 remaining errors (L203). The STATUS_REPORT confirms these are in `tests/fixtures/v2_production/` with passing test code. The earlier "80+ scripts" overclaim is replaced with verifiable numbers.

**Remaining concerns:**
- The v1 corpus is still 7 scripts from a single project. The paper acknowledges this in threats to validity. For arXiv, this is acceptable with the disclosure; for a peer-reviewed venue it would need expansion.
- The MCP feedback loop (Contribution #4) has zero evaluation. This is a gap between what's claimed and what's demonstrated.

**Action items:**
- Add even a minimal MCP loop evaluation (e.g., "we prompted Claude to write 10 AHK functions, ran lint_check, gave it the output, and 7 of 10 were corrected on the second attempt")
- Expand v1 corpus or explicitly scope the paper as a tool/demo paper

---

### 3. Reproducibility: **7/10** (was 5/10)

**Improvements:**
- V2 corpus now has actual fixtures in the repository
- LLM section is correctly framed as non-reproducible observations (the paper doesn't claim it's reproducible, so reproducibility is assessed on what it DOES claim)
- Test commands are provided: `phase4_corpus_test.py`, `llm_generation_test.py`, `coverage_analysis.py`
- All test results are documented in STATUS_REPORT

**Remaining weaknesses:**
- V1 fixtures are from an external depot (`autohotkey-test`), not shipped in the repository. No download script or manifest is provided. A reviewer cloning the repo cannot run the v1 corpus tests without separately locating these files.
- Lark version is not pinned. Lark LALR parser behavior is version-sensitive.
- No Dockerfile, `requirements.txt`, or locked dependency file (though `pyproject.toml` exists).

**Action items:**
- Ship a small representative v1 script corpus (3-5 of the 7 scripts) in the repository
- Pin Lark version (e.g., `lark>=1.1,<2.0`)
- Add a `uv.lock` to the repository

---

### 4. Related Work: **6/10** (was 4/10)

semgrep, tree-sitter, and ast-grep are now included with substantive comparison (L85-86):

> "These tools represent a viable path for a more principled implementation, though our approach required significantly less upfront investment and covers patterns specific to the v1-to-v2 migration task."

This is honest and self-aware. The paper acknowledges that more mature tools exist and explains why a simpler approach was chosen.

The bibliography is now clean: 14 entries, all cited. No padding entries (bibtex, knuth, sarif removed). No duplicate citations (MCP merged). The coverage includes the expected program transformation lineage (Stratego/XT, TXL, 2to3, rustfix), API migration mining, and LLM-assisted repair.

**Concern:** The paper compares against tools but provides no empirical comparison. A single-file test of semgrep or ast-grep against the same v1 scripts, even as a paragraph, would strengthen this section. Given that ast-grep runs on any language with a tree-sitter grammar (and `tree-sitter-ahk` exists), this is achievable with minimal effort.

**Action items:**
- Consider adding a brief empirical comparison: run semgrep or ast-grep on 1-2 v1 scripts with manually-written rules, report how many patterns each approach catches

---

### 5. Writing & Presentation: **7/10** (was 4/10)

**Major improvements:**
- No fabricated citations
- Consistent category/module count: "7 rule modules" everywhere (abstract, architecture, evaluation)
- Architecture is structured prose (4 layers with bullet points), not ASCII art in a code listing
- Table captions are specific ("Representative v1-to-v2 syntax changes" is still vague, but the paper no longer makes claims about undefined "primary patterns")
- No uncited bibliography entries
- No duplicate citations
- The tone is measured: "we estimate ~10,000 v1 scripts are publicly available" not "our tool will transform the ecosystem"

**Remaining issues:**
- The abstract ends informally: "This paper describes the tool that automated that process." This is a personal anecdote, not a scientific contribution statement.
- Some citations are bare URLs without DOIs or dates (rustfix, semgrep, tree-sitter, ast-grep, lark). This is common in tool papers but inconsistent with the formal entries (Stratego/XT has a proper journal reference).
- `\begin{thebibliography}{20}` declares space for 20 entries but only 14 exist. Minor formatting issue.
- The paper repeats the LLM-observation point in abstract, introduction, evaluation, and conclusion. Some tightening would help.

**Action items:**
- Tighten the abstract's final sentence
- Add retrieval dates to URL-only references (e.g., "Accessed July 2026")

---

### 6. Impact: **4/10** (was 3/10)

**For the AHK community:** A working linter with honest coverage claims (51%) has utility. Users who install `ahk-lint` get automated detection of common v1 patterns that would cause runtime failures in v2. The auto-fix for 10 patterns is a productivity multiplier for manual migration work. However, the user still gets only ~half of what the community converter covers, and the 73 procedural handlers (GUI restructuring, DllCall rewriting) remain unaddressed.

**For the language migration community:** The approach (extract patterns from existing converter → regex matching → auto-fix) is a straightforward application of known techniques. There is no new algorithm, no generalizable insight about migration difficulty, no framework that transfers to another language. This is fine for arXiv but would not survive peer review at a venue that requires generalizable contributions.

**MCP integration:** The MCP server is ~30 lines. Contribution #4 describes a feedback loop that is never evaluated. The paper would be stronger by either demonstrating the loop working (e.g., "we integrated ahk-lint with Claude Code and observed that 7 of 10 generated AHK functions were corrected after receiving lint output") or by removing it as a numbered contribution and keeping it as an implementation detail.

**Action items:**
- Evaluate the MCP feedback loop or remove it as a numbered contribution
- Compare against the THQBY LSP: what does `ahk-lint` catch that the LSP's diagnostics miss?

---

## Citation Audit (Round 2)

| Entry | Status |
|---|---|
| `gu2024repair` | **UNVERIFIED** — "J. Gu et al., Automated Code Repair with Large Language Models, ICSE 2024." No paper with this title exists at ICSE 2024. A "Jian Gu" publishes on LLM code repair (e.g., "Neuron Patching" at arXiv 2312.05356), but this specific paper+venue combination could not be confirmed on DBLP, arXiv, or Semantic Scholar. Likely fabricated or approximated. |
| `dsl_linter` | **UNVERIFIED** — "J. Källäinen et al., Improving DSL Quality with Language-Specific Analysis Tools, Software and Systems Modeling, 2021." Could not confirm on arXiv or DBLP. |
| All other entries | **CLEAN** — URLs resolve to real tools/repositories. Academic citations (Stratego/XT, TXL, API migration mining, LibSync) are real, well-known papers. |

**The `gu2024repair` entry is the more concerning.** The author name is semi-plausible (Jian Gu exists in the field), but the paper title is generic and the venue attribution is likely wrong. This is the same failure pattern as the original arXiv:1908.09453 fabrication — an LLM-generated approximation of a real-sounding citation. Whether it was hallucinated by the AI assistant or manually entered, it does not correspond to a real ICSE 2024 publication.

**Recommendation:** Replace both entries with verified citations before posting. For `gu2024repair`, substitute a real ICSE 2024 LLM code repair paper (e.g., Xia et al. on conversational APR, or Bouzenia et al. on RepairAgent). For `dsl_linter`, substitute a real SoSyM DSL tooling paper or remove the citation and keep the sentence as a general observation.

---

## Meta Verdict

**RECOMMENDATION: WEAK ACCEPT for arXiv cs.SE** (up from REJECT)

The paper has moved from disqualifying to borderline-acceptable. The three fatal issues are resolved: the fabricated citation is replaced, the LLM experiment is recast as honest observations, and the v2 false-positive claim has verifiable test fixtures. The paper now describes what it actually is: a working migration linter with 51% coverage, 7 rule modules, MCP wrapper, and observed (not experimental) LLM pattern generation.

**The two unverified citations are the remaining blocking issue.** While arXiv has no formal peer review, posting a paper with fabricated references is a reputational risk regardless of venue. Replace `gu2024repair` and `dsl_linter` with verified sources or remove them.

**For a peer-reviewed venue** (SANER tool track, ICPC, MSR), the paper would need:
1. A larger, diverse v1 corpus (minimum 30-50 scripts from multiple sources)
2. Experimental evaluation of the MCP feedback loop
3. Verified citations throughout
4. Empirical comparison against at least one related tool (semgrep, ast-grep, or THQBY LSP)

For arXiv, the current state is acceptable after the two citation fixes.

---

## Checklist Before arXiv Posting

| # | Item | Priority |
|---|---|---|
| C1 | Replace `gu2024repair` with a verified ICSE 2024 citation | **HIGH** |
| C2 | Replace `dsl_linter` with a verified SoSyM citation or remove | **HIGH** |
| C3 | Tighten abstract's final sentence | LOW |
| C4 | Add retrieval dates to URL-only references | LOW |
| C5 | Pin Lark version in reproducibility section | MEDIUM |
| C6 | Ship 3-5 v1 scripts as fixtures in the repository | MEDIUM |
| C7 | Add even a minimal MCP loop evaluation or downgrade contribution | MEDIUM |

---

*Reviewer: Same as Round 1. Re-assessment based on paper.tex and STATUS_REPORT.md as of July 2026.*
