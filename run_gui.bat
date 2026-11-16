@echo off
title GhostType Pro - GUI
cd /d "%~dp0"
python autotyper_gui.py
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
