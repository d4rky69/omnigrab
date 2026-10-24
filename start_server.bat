@echo off
cd /d "%~dp0"
call .\.venv\Scripts\activate.bat
start /b python main.py
timeout /t 2 >nul
start /b python run_tunnel.py
