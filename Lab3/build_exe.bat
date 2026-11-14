@echo off
cd /d "%~dp0"
python -m pip install pyinstaller
if errorlevel 1 goto error
python -m PyInstaller --noconfirm --onefile --windowed --name Lab3 --add-data "assets;assets" Lab3.py
if errorlevel 1 goto error
echo Ready: dist\Lab3.exe
pause
exit /b 0
:error
 echo Build failed.
 pause
 exit /b 1
