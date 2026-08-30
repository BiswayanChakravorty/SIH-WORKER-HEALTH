# MineGuard AI — PowerShell Server Launcher
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " MINEGUARD AI: IoT Mine Worker Health & Gas Hazard Safety Gateway" -ForegroundColor Green
Write-Host " Smart India Hackathon (SIH) Edition" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

$env:Path = "C:\Users\Admin\.local\bin;$env:Path"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv venv .venv --python 3.11
    uv pip install -r backend\requirements.txt --python .venv\Scripts\python.exe
}

Write-Host "Opening Dashboard at http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

& .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
