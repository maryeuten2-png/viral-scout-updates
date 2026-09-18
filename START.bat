@echo off
setlocal
cd /d "%~dp0"
set "URL=https://raw.githubusercontent.com/maryeuten2-png/viral-scout-updates/main/scout.py"
set "TMP=scout.new.py"

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing '%URL%' -OutFile '%TMP%' -TimeoutSec 12; exit 0 } catch { exit 1 }" >nul 2>nul

if exist "%TMP%" (
  py -m py_compile "%TMP%" >nul 2>nul
  if not errorlevel 1 (
    move /y "%TMP%" "scout.py" >nul
  ) else (
    del /q "%TMP%" >nul 2>nul
  )
)

py scout.py
if errorlevel 1 python scout.py
pause
