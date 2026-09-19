@echo off
cd /d "%~dp0"
if exist "Windows\Vespa travel content organizer.exe" (
  start "" "Windows\Vespa travel content organizer.exe"
  exit /b
)
if not exist ".venv\Scripts\pythonw.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto error
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto error
)
start "" ".venv\Scripts\pythonw.exe" app.py
exit /b
:error
echo Impossible de preparer Python. Utilisez la version Windows fournie ou installez Python 3.12 ou plus recent.
pause
