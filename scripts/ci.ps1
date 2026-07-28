$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot\..
uv sync --group dev
uv run ruff check ahk_lint.py checks config.py mcp_server.py lsp_client.py
uv run ruff format --check ahk_lint.py checks config.py mcp_server.py lsp_client.py
Write-Host "Pytest skipped (no CI-safe unit tests in repo yet)." -ForegroundColor DarkGray
exit 0
