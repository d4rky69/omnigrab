@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Remove-Item \"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\OmniGrab.lnk\" -Force -ErrorAction SilentlyContinue; " ^
  "Write-Host 'OmniGrab has been removed from Windows startup.'"

pause
