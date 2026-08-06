param([switch]$Headless)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSCommandPath
$BackendPort = 11076
$FrontendPort = 11077

Write-Host "=== ahk-lint WebApp ===" -ForegroundColor Cyan

Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "-> Starting backend on port $BackendPort..." -ForegroundColor Yellow
uv add fastapi uvicorn | Out-Null
$BackendJob = Start-Job -Name "ahk-lint-backend" -ScriptBlock { param($Root,$Port) Set-Location $Root\backend; uv run uvicorn server:app --host 127.0.0.1 --port $Port --no-access-log --log-level info } -ArgumentList $Root, $BackendPort

for ($i = 0; $i -lt 60; $i++) { try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue; if ($r.StatusCode -eq 200) { Write-Host "  Backend ready on http://127.0.0.1:$BackendPort" -ForegroundColor Green; break } } catch {}; Start-Sleep 1 }

Write-Host "-> Starting frontend on port $FrontendPort..." -ForegroundColor Yellow
$FeJob = Start-Job -Name "ahk-lint-frontend" -ScriptBlock { param($Root,$Port) Set-Location $Root\frontend; npm install --silent 2>$null; npx vite --port $Port } -ArgumentList $Root, $FrontendPort

if (-not $Headless) { Start-Sleep 3; Start-Process "http://127.0.0.1:$FrontendPort" }

Write-Host "=== ahk-lint WebApp running ===" -ForegroundColor Green
Write-Host "  Frontend : http://127.0.0.1:$FrontendPort"
Write-Host "  Backend  : http://127.0.0.1:$BackendPort"
Write-Host "  Press Ctrl+C to stop"

while ($true) { Start-Sleep 5; if ($BackendJob.State -eq "Failed") { Write-Host "Backend failed:" -ForegroundColor Red; Receive-Job $BackendJob; break } }
