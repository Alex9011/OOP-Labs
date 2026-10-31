@echo off
cd /d "%~dp0"
py -3 -m pip install pyinstaller
if errorlevel 1 goto error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name Lab2 Lab2.py
if errorlevel 1 goto error
echo EXE: dist\Lab2.exe
pause
exit /b 0
:error
 echo Build failed.
 pause
 exit /b 1
