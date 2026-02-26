@echo off
chcp 65001 > nul
echo ============================================================
echo 百亿补贴自动化系统 - 一键启动
echo ============================================================
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查Node.js是否安装
cd web
npm --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)
cd ..

REM 检查依赖
echo [1/4] 检查Python依赖...
pip show fastapi > nul 2>&1
if errorlevel 1 (
    echo 正在安装Python依赖...
    pip install fastapi uvicorn sqlalchemy pydantic
)

echo [2/4] 检查Node.js依赖...
if not exist "web\node_modules\" (
    echo 正在安装Node.js依赖...
    cd web
    call npm install
    cd ..
)

echo [3/4] 启动后端API服务...
start "百亿补贴API" cmd /k "python start_web.py"

REM 等待后端启动
timeout /t 3 /nobreak > nul

echo [4/4] 启动前端界面...
cd web
start "百亿补贴前端" cmd /k "npm run dev"
cd ..

echo.
echo ============================================================
echo 启动完成！
echo ============================================================
echo.
echo 🌐 前端界面: http://localhost:5173
echo 🔧 后端API:  http://localhost:8000
echo 📚 API文档:  http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口（服务将继续运行）
pause > nul
