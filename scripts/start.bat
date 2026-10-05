@echo off
setlocal
cd /d "%~dp0.."
pushd frontend
call npm run build
if errorlevel 1 exit /b 1
popd
call .venv\Scripts\activate.bat
set PYTHONPATH=backend
set TANK650_ALLOWED_CLIENTS=127.0.0.1,::1,192.168.18.131,192.168.18.150
rem Escucha LAN; limitar el acceso mediante Firewall a los equipos autorizados.
uvicorn app.main:app --host 0.0.0.0 --port 8000
