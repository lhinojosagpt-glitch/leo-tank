@echo off
setlocal
cd /d "%~dp0.."
pushd frontend
call npm run build
if errorlevel 1 exit /b 1
popd
call .venv\Scripts\activate.bat
set PYTHONPATH=backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

