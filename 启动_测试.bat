@echo off
chcp 65001 > nul 2>&1
title BB System

echo ======================================================================
echo BaiButi System - Test Mode
echo ======================================================================
echo.

cd /d "%~dp0"

REM Stop existing backend service
echo [0/4] Checking existing services...
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
echo [1/4] Checking environment...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
echo      [OK] Python is ready

cd web > nul 2>&1
npm --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)
cd ..
echo      [OK] Node.js is ready
echo.

echo [2/4] Skipping dependency installation (test mode)...
echo.

echo [3/4] Starting frontend service...
echo.
start "BB-Frontend" cmd /c "title BB-Frontend && cd /d "%~cd%\web" && echo Starting frontend... && echo. && npm run dev && echo. && echo Frontend stopped && pause"
echo      [Frontend] Starting in background...

timeout /t 3 /nobreak > nul

echo [4/4] Starting backend service...
echo.
echo ======================================================================
echo Backend:    http://localhost:9000
echo API Docs:   http://localhost:9000/docs
echo Frontend:   Check BB-Frontend window for URL
echo ======================================================================
echo.
echo Starting backend...
echo.

REM Start backend in current window
python start_web.py

REM Cleanup when backend stops
echo.
echo ======================================================================
echo Backend stopped
echo Closing frontend...
taskkill /FI "WINDOWTITLE eq BB-Frontend*" /F >nul 2>&1
echo All services stopped
echo ======================================================================
pause
