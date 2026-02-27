@echo off
chcp 65001 > nul 2>&1
title 整点抢券 - 停止服务

python "%~dp0stop.py"

if errorlevel 1 (
    echo.
    echo [错误] 停止服务失败
    echo.
    pause
)
