@echo off
title Start All Services
echo Starting Backend and Frontend services...
echo.

start "" /B cmd /c "scripts\start_backend.bat"
timeout /t 2 /nobreak > nul
start "" /B cmd /c "scripts\start_frontend.bat"

echo.
echo Services started!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173
echo.
echo To stop all services, run: scripts\stop.bat
timeout /t 3
