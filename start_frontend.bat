@echo off
chcp 65001 > nul 2>&1
title 百亿补贴自动化系统 - 前端服务

echo ======================================================================
echo 百亿补贴自动化系统 - 前端界面
echo ======================================================================
echo.

cd /d "%~dp0web"

REM 检查Node.js
npm --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules\" (
    echo [安装] 正在安装前端依赖...
    call npm install
)

echo.
echo ======================================================================
echo 正在启动前端开发服务器...
echo ======================================================================
echo.
echo 前端界面:   将自动打开浏览器
echo.
echo 按 Ctrl+C 停止服务
echo ======================================================================
echo.

call npm run dev

echo.
echo 服务已停止
pause
