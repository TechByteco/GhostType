@echo off
title GhostType Quick (Hotkey Listener)
cd /d "%~dp0"
python autotyper_quick.py
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
