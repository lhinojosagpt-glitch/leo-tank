@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pushd frontend
call npm install
popd
set PYTHONPATH=backend
python -c "from app.db import init_db; init_db(); print('SQLite ready')"
echo TANK650 ENGINE setup complete.

