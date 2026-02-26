@echo off
chcp 65001 > nul 2>&1
title 百亿补贴自动化系统 - 后端服务

echo ======================================================================
echo 百亿补贴自动化系统 - 后端API服务
echo ======================================================================
echo.

cd /d "%~dp0"

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖
echo [检查] 检查Python依赖...
pip show fastapi > nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装Python依赖...
    pip install fastapi uvicorn sqlalchemy pydantic -q
)

echo.
echo ======================================================================
echo 正在启动后端API服务...
echo ======================================================================
echo.
echo 后端API:    http://localhost:8000
echo API文档:    http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ======================================================================
echo.

python start_web.py

echo.
echo 服务已停止
pause
