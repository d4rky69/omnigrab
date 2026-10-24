@echo off
set SCRIPT_DIR=%~dp0
set VBS_PATH=%SCRIPT_DIR%start_silent.vbs

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut(\"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\OmniGrab.lnk\"); " ^
  "$s.TargetPath = 'wscript.exe'; " ^
  "$s.Arguments = '\"%VBS_PATH%\"'; " ^
  "$s.WorkingDirectory = '%SCRIPT_DIR%'; " ^
  "$s.Save(); " ^
  "Write-Host 'OmniGrab has been registered to start automatically on Windows boot!'"

pause
