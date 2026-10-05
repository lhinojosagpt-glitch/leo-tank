@echo off
setlocal
cd /d "%~dp0.."
call .venv\Scripts\activate.bat
set PYTHONPATH=backend
python -m pytest backend\tests

