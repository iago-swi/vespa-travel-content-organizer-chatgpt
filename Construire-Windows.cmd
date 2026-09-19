@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller==6.22.2
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean Vespa.spec
if errorlevel 1 goto error
echo Application disponible dans dist\Vespa travel content organizer
pause
exit /b
:error
echo La construction a echoue. Consultez les informations ci-dessus.
pause
