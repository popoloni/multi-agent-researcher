@echo off
REM Multi-Agent Researcher Control Script for Windows
echo 🚀 Multi-Agent Researcher Control Script (Windows)

REM Change to project root directory
cd /d "%~dp0\.."

REM Check if we're in WSL environment or if bash is available
where bash >nul 2>&1
if not errorlevel 1 (
    echo ✅ Bash detected - using start_all.sh
    bash utils/start_all.sh %*
    goto :eof
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or later.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js/npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js/npm not found. Please install Node.js.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Parse command line arguments
if "%1"=="stop" goto :stop
if "%1"=="status" goto :status
if "%1"=="restart" goto :restart
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help

REM Default: start all services
goto :start

:start
echo 🚀 Starting all services...
echo.
echo ⚠️  Windows Native Support Limited
echo    For full functionality, please use:
echo    - Windows Subsystem for Linux (WSL)
echo    - Git Bash
echo    - Or run individual components manually
echo.

REM Start backend
echo 🔄 Starting backend API...
start "Backend API" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload"

REM Wait a moment
timeout /t 5 /nobreak >nul

REM Start frontend
echo 🔄 Starting frontend...
cd frontend
start "Frontend" cmd /c "npm start"
cd ..

echo.
echo ✅ Services started in separate windows
echo 📊 Access URLs:
echo   - Backend API: http://localhost:12000
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:12000/docs
echo.
echo 💡 Note: You'll need to install and start Ollama separately:
echo    1. Download Ollama from: https://ollama.ai/
echo    2. Run: ollama serve
echo    3. Pull models: ollama pull llama3.2:1b
goto :eof

:stop
echo 🛑 Stopping all services...
taskkill /f /im "uvicorn.exe" >nul 2>&1
taskkill /f /im "node.exe" >nul 2>&1
taskkill /f /im "ollama.exe" >nul 2>&1
echo ✅ Services stopped
goto :eof

:status
echo 📊 Service Status Check...
echo.
echo Checking Backend API (port 12000)...
curl -s http://localhost:12000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend API: Not running
) else (
    echo ✅ Backend API: Running
)

echo.
echo Checking Frontend (port 3000)...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend: Not running
) else (
    echo ✅ Frontend: Running
)

echo.
echo Checking Ollama (port 11434)...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: Not running
) else (
    echo ✅ Ollama: Running
)
goto :eof

:restart
echo 🔄 Restarting all services...
call :stop
timeout /t 2 /nobreak >nul
call :start
goto :eof

:help
echo 🚀 Multi-Agent Researcher Control Script (Windows)
echo.
echo Usage: start_all.bat [COMMAND]
echo.
echo Commands:
echo   start        Start all services (default)
echo   stop         Stop all services
echo   restart      Restart all services
echo   status       Show status of all services
echo   help         Show this help message
echo.
echo Examples:
echo   start_all.bat           # Start all services
echo   start_all.bat status    # Check service status
echo   start_all.bat stop      # Stop all services
echo.
echo For best experience on Windows, use WSL or Git Bash
echo to run the full-featured start_all.sh script.
goto :eof