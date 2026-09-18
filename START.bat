@echo off
setlocal
cd /d "%~dp0"

set "TMP=scout.new.py"
set "URL1=https://raw.githubusercontent.com/maryeuten2-png/viral-scout-updates/main/scout.py"
set "URL2=https://github.com/maryeuten2-png/viral-scout-updates/raw/refs/heads/main/scout.py"

del /q "%TMP%" >nul 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing '%URL1%' -OutFile '%TMP%' -TimeoutSec 10; exit 0 } catch { exit 1 }" >nul 2>nul

if not exist "%TMP%" (
  curl.exe -L --fail --silent --show-error "%URL2%" -o "%TMP%" >nul 2>nul
)

if exist "%TMP%" (
  py -m py_compile "%TMP%" >nul 2>nul
  if not errorlevel 1 (
    move /y "%TMP%" "scout.py" >nul
  ) else (
    del /q "%TMP%" >nul 2>nul
  )
)

if not exist "scout.py" (
  echo.
  echo Viral Scout: scout.py is missing.
  echo Re-extract the corrected package once. After that updates are automatic.
  echo.
  pause
  exit /b 1
)

py scout.py
if errorlevel 1 python scout.py
pause
