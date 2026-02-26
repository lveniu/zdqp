@echo off
chcp 65001 > nul 2>&1
title BB System - Backend

echo ======================================================================
echo BaiButi Automation System
echo ======================================================================
echo.

cd /d "%~dp0"

REM Check and stop existing services
echo [0/6] Checking existing services...
netstat -ano | findstr ":9000.*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo      [Detected] Backend is running, stopping...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9000.*LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
)
echo.

REM Check environment
echo [1/6] Checking environment...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

cd web > nul 2>&1
npm --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)
cd ..

echo [2/6] Installing Python dependencies...
pip install fastapi uvicorn sqlalchemy pydantic httpx -q > nul 2>&1

echo [3/6] Installing frontend dependencies...
cd web
if not exist "node_modules\" (
    echo First run, installing frontend dependencies, please wait...
    npm install
)
cd ..

echo [4/6] Starting frontend service...
echo.
start "BB-Frontend" cmd /c "title BB-Frontend && cd /d "%~cd%\web" && echo Starting frontend service... && echo. && npm run dev && echo. && echo Frontend service stopped && pause"
echo      [Frontend] Starting in background...

timeout /t 3 /nobreak > nul

echo [5/6] Waiting for services ready...
timeout /t 2 /nobreak > nul

echo [6/6] Starting backend service...
echo.
echo ======================================================================
echo Backend API:    http://localhost:9000
echo API Docs:      http://localhost:9000/docs
echo Frontend:      Check BB-Frontend window for URL
echo ======================================================================
echo.
echo Tips:
echo   - Frontend runs in separate window
echo   - Backend runs in current window
echo   - Press Ctrl+C to stop backend
echo   - Run this script again to restart all services
echo.
echo Starting backend...
echo.

REM Start backend in current window
python start_web.py

REM Cleanup when backend stops
echo.
echo ======================================================================
echo Backend service stopped
echo Closing frontend...
taskkill /FI "WINDOWTITLE eq BB-Frontend*" /F >nul 2>&1
echo All services stopped
echo ======================================================================
pause
