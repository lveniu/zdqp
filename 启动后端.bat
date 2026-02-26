@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

title 百亿补贴自动化系统

cls
echo ======================================================================
echo 百亿补贴自动化系统 - 一键启动
echo ======================================================================
echo.

cd /d "%~dp0"

REM 检查Python
echo [环境检查] Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo   [失败] 未找到Python，请先安装Python 3.8+
    echo.
    pause
    exit /b 1
)
echo   [OK] Python已安装
python --version

REM 检查Node.js
echo [环境检查] Node.js...
cd web > nul 2>&1
npm --version > nul 2>&1
if errorlevel 1 (
    echo   [失败] 未找到Node.js，请先安装Node.js
    echo.
    pause
    exit /b 1
)
cd ..
echo   [OK] Node.js已安装

REM 安装依赖
echo.
echo [依赖检查] Python库...
pip show fastapi > nul 2>&1
if errorlevel 1 (
    echo   [安装] 正在安装Python依赖...
    pip install fastapi uvicorn sqlalchemy pydantic -q
) else (
    echo   [OK] Python依赖已安装
)

echo [依赖检查] 前端库...
cd web
if not exist "node_modules\" (
    echo   [安装] 正在安装前端依赖...
    call npm install > nul 2>&1
) else (
    echo   [OK] 前端依赖已安装
)
cd ..

echo.
echo ======================================================================
echo 正在启动服务...
echo ======================================================================
echo.

REM 启动前端（后台）
echo [启动] 前端服务...
start "百亿补贴-前端" /min cmd /c "cd /d "%~cd%\web" && npm run dev"

REM 等待前端启动
timeout /t 3 /nobreak > nul

echo [启动] 后端API服务...
echo.
echo ======================================================================
echo 服务已启动！
echo ======================================================================
echo.
echo 后端API:    http://localhost:8000
echo API文档:    http://localhost:8000/docs
echo 前端界面:   http://localhost:5173 (或自动分配的端口)
echo.
echo 系统日志:
echo.
python start_web.py

echo.
echo.
echo ======================================================================
echo 所有服务已停止
echo ======================================================================
pause
