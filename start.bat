@echo off
REM Simple startup script for AI OS (Windows)

echo ==================================
echo AI OS Launcher
echo ==================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    exit /b 1
)

echo Using: python
echo.

REM Get mode from command line argument, default to browser
if "%1"=="" (
    set MODE=browser
) else (
    set MODE=%1
)

echo Starting in %MODE% mode...
echo.

REM Run the unified launcher
python unified_launcher.py --mode %MODE%
