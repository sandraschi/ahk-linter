# Peer Review: *ahk-lint: Detecting and Repairing AutoHotkey v1 Patterns in the Age of LLMs*

## Summary

The paper describes `ahk-lint`, a Python linter that detects AutoHotkey v1 syntax patterns (167 regex/declarative rules) and provides auto-fix for a subset. It claims 51% coverage against the community `AHK-v2-script-converter`, evaluates on 7 legacy scripts (343 issues), 5 "LLM-generated" scripts (32 issues), and 80+ v2 scripts (zero false positives), and wraps the linter as an MCP server.

---

## Scores and Critiques

### 1. Originality: **3/10**

The tool is an engineering artifact, not a research contribution. The core technique — regex-based pattern matching against a JSON file of syntax mappings extracted from a community converter — requires zero novel algorithmic work. The paper's claim that "no academic work exists on AHK v2 migration tooling" is technically true but deceptive: the absence of prior work does not make a task novel. A regex-driven linter for a domain-specific language is a weekend hack, not a publishable result.

**Critical**: The paper's claim about the 90% v1 corpus imbalance cites `\cite{ahk_survey}` as "arXiv:1908.09453" — but arXiv:1908.09453 is a grocery shopping dataset paper, not an AHK survey. The bib entry for `ahk_survey` is a live GitHub search URL, not a published source. This citation is either fabricated or wildly garbled. A 2024 survey of AHK repositories is cited as if it's a peer-reviewed artifact; it's a query string.

**Action items**:
- Remove the arXiv:1908.09453 claim entirely or do an actual quantitative analysis of AHK GitHub repos with a reproducible methodology
- Distinguish between "what the community converter does" and "what this paper contributes" more honestly — the paper's only original contribution is the Python wrapper, not the rules

---

### 2. Soundness: **2/10**

This is where the paper fails catastrophically. Three fatal problems:

**(a) The LLM generation test is fabricated.** The paper presents Table 4 as if it evaluates real LLM output. Reading the code at `tests/llm_generation_test.py:125-190` reveals that the "LLM-generated scripts" are hardcoded Python string literals written by the author, with names like `claude_backup` and `ds4_rename`. The comment on line 123-124 reads: *"Pre-canned LLM outputs simulating what Claude/DS4 typically generate — These are real outputs observed from prompting LLMs to write AHK code"*. Even if they are transcriptions of past observations, presenting them as an experimental result with a table of "LLM generation test results" is misleading. There is no API call to any LLM, no prompt logging, no temperature parameter, no sampling methodology. The 10 PROMPTS at lines 18-29 are never used — they are dead code. This is not an experiment; it's a demonstration script.

**(b) The "80+ v2 scripts, zero false positives" claim is unverifiable.** The test file `phase4_corpus_test.py` only tests a `v1_dir` (`tests/fixtures/v1_originals`). There is no v2 test path in the code. No v2 fixtures appear to exist in the repository. The claim in Table 3 and the text is an assertion, not an experimental result.

**(c) The 7-script v1 corpus is from a single project archive (`autohotkey-test` depot).** The "Threats to validity" section acknowledges this and then does nothing about it. A paper claiming to tool the AHK ecosystem should at minimum scrape public AHK repositories for a diverse corpus — as the paper itself notes in §6 (Future Work), ~10,000 v1 scripts are "publicly available." This is self-indicting: the paper admits a larger corpus exists and was not used.

**Action items**:
- Remove the LLM generation test table or rewrite it honestly as "observed examples," clearly labeled as anecdotal
- Either provide reproducible v2 test code with actual fixtures or remove the "80+ scripts, zero false positives" claim
- Expand the v1 corpus beyond 7 single-project scripts, or recast the paper as a short tool/demo paper

---

### 3. Reproducibility: **5/10**

The good: all code is on GitHub, installation and test commands are provided, the rules are machine-readable JSON. The paper passes the basic bar of OSS tool papers.

The bad:
- **The "LLM generation test" does not actually call any LLM.** A reviewer who clones the repo and runs `python tests/llm_generation_test.py` gets results, but from hardcoded strings, not from LLM APIs. The methodology section says nothing about model versions, API endpoints, temperature, or prompt templates. This is not reproducible in the scientific sense — no one else can run the experiment the paper claims was conducted.
- **The v1 corpus scripts are not included in the repository.** The test references `tests/fixtures/v1_originals/*.ahk` but these files are from an external depot. No download script is provided.
- **Dependencies are under-specified.** "Python 3.11+" and "Lark" — but which Lark version? The Lark LALR parser behavior is version-sensitive.

**Action items**:
- Ship a small representative v1 script corpus in the repository
- Either make the LLM experiment real (with API calls, logged prompts, model versions) or remove the experimental framing
- Pin Lark version

---

### 4. Related Work: **4/10**

The paper covers the expected program transformation lineage (Stratego/XT, TXL, 2to3, rustfix) and API migration mining. However, it wholly omits the **general-purpose linting ecosystem** that is the most direct comparison:

- **semgrep**: A multi-language pattern-matching linter with declarative rules. `ahk-lint`'s architecture of JSON-encoded pattern→fix mappings is essentially a poor man's semgrep for a single language. This comparison should be front and center.
- **tree-sitter + ast-grep**: tree-sitter has an AHK grammar (`tree-sitter-ahk`). A tree-sitter-based approach would solve the paper's parser limitation in ~50 lines. ast-grep (`ast-grep/ast-grep`) provides declarative AST pattern matching with auto-fix — directly comparable to the paper's approach but far more mature.
- **lintr / ESLint**: The broader literature on DSL-specific linting is represented by a single citation (`\cite{dsl_linter}`) with no engagement with the methodology.

The bibliography contains padding: `\cite{bibtex}` and `\cite{knuth}` appear nowhere in the text but are listed in the bibliography. Multiple URLs are cited as bibliographic entries without DOIs, dates, or formal references.

**Action items**:
- Add semgrep, tree-sitter, and ast-grep to related work with substantive comparison
- Remove unused bibliography entries
- Actually compare against running semgrep on AHK code — this would be a strong evaluation baseline

---

### 5. Writing & Presentation: **4/10**

The abstract claims "over 90\% of public AHK code uses v1 syntax" citing a bogus arXiv ID for a GitHub search URL. This is a strong quantitative claim supported by a non-source.

The paper repeats itself: the same claim about LLMs generating v1 syntax appears in the abstract, introduction (§1), evaluation (§4.3), and conclusion (§7). The core message fits in a tool demo abstract.

Table captions are vague ("Representative v1-to-v2 syntax changes" — representative of what? The 167 rules? The 325 converter patterns?). The architecture figure is rendered as a code listing inside a figure environment — it's just ASCII art formatted as pseudocode.

The paper claims "7/10 primary patterns" have auto-fix but never enumerates the 10 "primary patterns." This number is unreproducible. The "167 patterns across 9 categories" is mentioned 4 times, but the 9 categories are never cleanly listed in one place (the paper says "7 rule modules" in the architecture diagram, "9 categories" in the abstract, and shows 7 categories in Table 2).

The "MCP integration" uses two separate bib entries (`mcp` and `mcp_patterns`) that point to the same URL.

**Action items**:
- Fix the false arXiv citation immediately
- Define "primary patterns" concretely or drop the number
- Reconcile the category/module count discrepancy (7 vs. 9)
- Remove the architecture ASCII art — use a proper diagram or present it as structured text

---

### 6. Impact: **3/10**

**For the AHK community:** A working linter is useful. But the tool is 51% complete against a community converter that already exists. The paper contributes a Python wrapper around rules extracted from `mmikeww`'s converter. An AHK user who installs `ahk-lint` gets a subset of what they'd get by running the community converter directly, minus the 73 procedural handlers. The marginal utility is unclear.

**For the language migration community:** The approach (extract patterns from existing converter → regex matching → auto-fix) is a mechanical application of known techniques. There is no new algorithm, no new insight about migration difficulty, no generalizable finding. A paper about language migration should contribute something that transfers to the next language; this paper is entirely AHK-specific.

**MCP integration:** The MCP server is ~30 lines of code wrapping the linter. The paper presents it as Contribution #4 and describes a "feedback loop" of lint → fix → re-lint. This loop is not evaluated — there is no study of whether LLMs actually correct their own AHK code when given linter feedback. The entire MCP claim is aspirational.

**Action items**:
- Either evaluate the MCP feedback loop experimentally or demote it from a "contribution" to a "feature" in the description
- Add a comparison: what does `ahk-lint` catch that running the THQBY LSP alone does not? There's an LSP integration in the code but no evaluation of it

---

## Bibliography Audit

| Entry | Status |
|---|---|
| `ahk_survey` | **FABRICATED** — cites arXiv:1908.09453 in text, bib entry is a GitHub search URL. These are irreconcilable. |
| `bibtex`, `knuth` | **UNCITED** — appear in bibliography but never referenced in text. |
| `mcp` / `mcp_patterns` | **DUPLICATE** — two entries for `https://modelcontextprotocol.io/`. |
| `2to3`, `gofix`, `sarif`, `autohotkey`, `pyupgrade` | **UNCITED** — listed in bibliography, no `\cite{}` in text body. |
| `dsl_linter` (Källäinen) | **UNCITED** — listed but never cited. |

Overall: 14 bib entries, but only ~7 are actually cited. The citation quality is poor.

---

## Meta Verdict

**RECOMMENDATION: REJECT at arXiv cs.SE level**

The paper has a fatal methodological flaw: the LLM generation test is not an experiment. The 80+ v2 script claim lacks test code. A fabricated citation (`arXiv:1908.09453`) in the first paragraph of the body text is disqualifying on its own. The related work ignores the most relevant category of tools (semgrep, tree-sitter, ast-grep). The paper describes a useful engineering project that does not reach the bar for a research contribution in its current form.

arXiv cs.SE has no formal peer review, so the paper can be posted regardless. But if the author intends to submit to a venue that does review (e.g., SANER tool track, ICPC, MSR), all of the above would be fatal.

---

## Three Most Important Changes Before Submission (arXiv)

1. **Fix the LLM generation test.** Either run actual LLM API calls with documented prompts, models, temperatures, and timestamps, or recast the entire section as illustrative examples with a clear disclaimer. The current presentation as experimental results in a table is scientifically indefensible.

2. **Remove or substantiate the "90% v1 corpus" claim.** The cite `\cite{ahk_survey}` is a GitHub search URL, not a publication, and the arXiv ID in the text is wrong. Either perform an actual quantitative analysis of public AHK repos (clone the top 100, classify version, report methodology) or drop the claim.

3. **Add the v2 false-positive test code.** The "zero false positives on 80+ v2 scripts" is an unverifiable assertion. Ship the v2 test fixtures or provide the test suite that generated this result. Without it, the paper's strongest quantitative claim is unsupported.
