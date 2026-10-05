@echo off
setlocal
cd /d "%~dp0.."
start "TANK650 API" cmd /k "call .venv\Scripts\activate.bat && set PYTHONPATH=backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "TANK650 UI" cmd /k "cd frontend && npm run dev"
echo Open http://127.0.0.1:5173

