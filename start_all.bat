@echo off
REM Multi-Agent Researcher Control Script for Windows
REM This batch file provides Windows-specific support for managing services

echo 🚀 Multi-Agent Researcher Control Script (Windows)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or later.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if we have the cross-platform Python script
if not exist "start_all.py" (
    echo ❌ start_all.py not found in current directory
    pause
    exit /b 1
)

REM Parse command line arguments and pass to Python script
if "%1"=="stop" (
    python start_all.py --stop
) else if "%1"=="status" (
    python start_all.py --status
) else if "%1"=="restart" (
    python start_all.py --restart
) else (
    REM Default: start all services
    python start_all.py
)

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ An error occurred. Check the output above for details.
    pause
)