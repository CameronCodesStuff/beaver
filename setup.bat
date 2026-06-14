@echo off
cd /d "%~dp0"
setlocal

echo.
echo  ============================
echo      BEAVER  -  SETUP
echo  ============================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo  [X] Python not found.
  echo      Install Python 3.9+ from https://www.python.org/downloads/
  echo      and tick "Add Python to PATH", then run this again.
  pause
  exit /b 1
)

if not exist "requirements.txt" (
  echo  [X] requirements.txt not found in this folder:
  echo      %cd%
  echo      Make sure setup.bat is in the same folder as requirements.txt.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo  [*] Creating virtual environment...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"

echo  [*] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo  ============================
echo    SETUP COMPLETE
echo    Run start_beaver.bat to launch.
echo    The voice model installs itself
echo    inside the app on first run.
echo  ============================
echo.
pause
