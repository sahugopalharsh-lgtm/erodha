@echo off
rem Double-click to start Erodha (backend + dashboard). Uses the venv automatically.
cd /d "%~dp0"
set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"
if exist "%~dp0..\venv\Scripts\python.exe" set "PY=%~dp0..\venv\Scripts\python.exe"
"%PY%" run.py
pause
