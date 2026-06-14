@echo off
cd /d "%~dp0"
setlocal
if not exist ".venv" (
  echo Virtual environment missing. Run setup.bat first.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python main.py
