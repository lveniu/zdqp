@echo off
chcp 65001 > nul 2>&1
cd /d "%~dp0"

echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9000.*LISTENING" 2^>nul') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting backend...
start "BB-Backend" cmd /c "python start_web.py"

timeout /t 3 /nobreak >nul

echo Starting frontend...
start "BB-Frontend" cmd /c "cd web && npm run dev"

echo Services started!
echo Backend: http://localhost:9000
echo Frontend: Check BB-Frontend window
