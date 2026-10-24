@echo off
title OmniGrab - Universal Media Downloader
cd /d "%~dp0"
echo ====================================================
echo Starting OmniGrab Universal Media Downloader...
echo Server running at: http://127.0.0.1:8000
echo Press Ctrl+C in this window to stop the server.
echo ====================================================
call .venv\Scripts\python.exe main.py
pause
