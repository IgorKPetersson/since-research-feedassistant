@echo off
rem T-060: start the app with a double-click. Runs from this file's own folder whatever
rem the current directory is, so a desktop shortcut to this file works too.
cd /d "%~dp0"
title Since
if not exist ".venv\Scripts\streamlit.exe" (
    echo Since isn't installed yet: the .venv folder is missing. See "Install" in README.md.
    echo.
    pause
    exit /b 1
)
echo Starting Since. Your browser opens on it in a moment.
echo Keep this window open while you use the app; closing it stops the app.
echo.
".venv\Scripts\streamlit.exe" run app.py
rem Only reached if the app stopped by itself: keep the reason on screen.
if errorlevel 1 pause
