@echo off
cd /d "%~dp0"
py -3 Lab2.py
if errorlevel 1 pause
