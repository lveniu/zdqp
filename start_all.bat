@echo off
chcp 65001 > nul 2>&1

echo ======================================================================
echo 百亿补贴自动化系统 - 一键启动
echo ======================================================================
echo.
echo 此脚本将启动后端和前端服务
echo.

cd /d "%~dp0"

REM 启动后端
echo [1/2] 正在启动后端API服务...
start "百亿补贴-后端" cmd /k "call start_backend.bat"

REM 等待后端启动
timeout /t 3 /nobreak > nul

REM 启动前端
echo [2/2] 正在启动前端界面...
start "百亿补贴-前端" cmd /k "call start_frontend.bat"

echo.
echo ======================================================================
echo 启动完成！
echo ======================================================================
echo.
echo 后端API:    http://localhost:8000
echo API文档:    http://localhost:8000/docs
echo 前端界面:   http://localhost:5173 (或自动分配的端口)
echo.
echo 两个服务窗口已打开，可以在对应窗口查看日志
echo 关闭窗口即可停止服务
echo.
echo ======================================================================
pause
