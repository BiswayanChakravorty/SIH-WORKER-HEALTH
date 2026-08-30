@echo off
title MineGuard AI — SIH Mine Worker Safety Server
echo ================================================================
echo  MINEGUARD AI: IoT Mine Worker Health & Gas Hazard Safety Gateway
echo  Smart India Hackathon (SIH) Edition
echo ================================================================
echo.
echo Starting FastAPI Backend Server on http://127.0.0.1:8000 ...
echo Press CTRL+C to stop the server.
echo.

set Path=C:\Users\Admin\.local\bin;%Path%
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    uv venv .venv --python 3.11
    uv pip install -r backend\requirements.txt --python .venv\Scripts\python.exe
)

start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
