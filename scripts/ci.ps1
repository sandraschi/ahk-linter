$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot\..
uv sync --group dev
uv run ruff check ahk_lint.py checks config.py mcp_server.py lsp_client.py
uv run ruff format --check ahk_lint.py checks config.py mcp_server.py lsp_client.py
uv run pytest -q --tb=short --ignore=tests/scrape_v1_corpus.py --ignore=tests/llm_generation_test.py --ignore=tests/phase4_corpus_test.py --ignore=tests/mcp_feedback_loop.py --ignore=tests/baseline_compare.py --ignore=tests/corpus_stats.py --ignore=tests/semgrep_scan.py
exit $LASTEXITCODE
