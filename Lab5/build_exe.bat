@echo off
cd /d "%~dp0"
python -m pip install pyinstaller
if errorlevel 1 goto error
python -m PyInstaller --noconfirm --onefile --windowed --name Lab5 --add-data "assets;assets" Lab5.py
if errorlevel 1 goto error
echo Ready: dist\Lab5.exe
pause
exit /b 0
:error
 echo Build failed.
 pause
 exit /b 1
