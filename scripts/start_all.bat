@echo off
chcp 65001 > nul 2>&1
title Start All Services
cd /d "%~dp0"

echo Starting services...
echo.

echo Starting backend...
start "Backend" cmd /k "cd /d "%~dp0.." && python start_web.py"

timeout /t 3 /nobreak > nul

echo Starting frontend...
start "Frontend" cmd /k "cd /d "%~dp0.." && cd web && npm run dev"

timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo Services started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo To stop: scripts\stop.bat
echo.
timeout /t 5
