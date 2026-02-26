@echo off
chcp 65001 > nul 2>&1

echo ============================================
echo 测试启动脚本
echo ============================================
echo.

cd /d "%~dp0"

echo [测试1] 检查现有服务...
echo 检查端口9000:
netstat -ano | findstr ":9000.*LISTENING"
if errorlevel 1 (
    echo      端口9000未被占用
) else (
    echo      端口9000已被占用
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9000.*LISTENING"') do (
        echo      发现PID: %%a
    )
)
echo.

echo [测试2] 检查前端服务...
tasklist | findstr "node.exe"
if errorlevel 1 (
    echo      未发现node.exe进程
) else (
    echo      发现node.exe进程正在运行
)
echo.

echo [测试3] 停止现有后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9000.*LISTENING" 2^>nul') do (
    echo      正在关闭PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)
echo      完成
echo.

echo [测试4] 等待2秒后检查端口状态...
timeout /t 2 /nobreak >nul
netstat -ano | findstr ":9000.*LISTENING"
if errorlevel 1 (
    echo      端口9000已释放 ✓
) else (
    echo      端口9000仍被占用
)
echo.

echo [测试5] 检查Python环境...
python --version
if errorlevel 1 (
    echo      Python未找到 ✗
) else (
    echo      Python环境正常 ✓
)
echo.

echo [测试6] 检查Node.js环境...
cd web >nul 2>&1
npm --version
if errorlevel 1 (
    echo      Node.js未找到 ✗
    cd ..
) else (
    echo      Node.js环境正常 ✓
    cd ..
)
echo.

echo ============================================
echo 测试完成
echo ============================================
pause
