@echo off
REM 设置 UTF-8 编码
chcp 65001 > nul 2>&1

REM 设置窗口标题
title 整点抢券 - 后端服务

REM 切换到项目根目录
cd /d "%~dp0.."

REM 显示启动信息
echo.
echo ========================================
echo     整点抢券 - 启动后端服务
echo ========================================
echo.
echo 正在启动 Python FastAPI 服务...
echo.
echo 启动后:
echo   后端API:  http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 启动服务
python start_web.py

REM 如果服务异常退出，暂停显示错误
if errorlevel 1 (
    echo.
    echo [错误] 服务启动失败
    echo.
    pause
)
