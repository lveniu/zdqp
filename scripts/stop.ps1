# 整点抢券 - 停止服务 (PowerShell 版本)
# 使用方法：右键点击 -> 使用 PowerShell 运行

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "整点抢券 - 停止服务" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$stoppedCount = 0

# 步骤 1: 停止后端服务
Write-Host "[步骤 1/3] 停止后端服务 (Python)..." -ForegroundColor Yellow
Write-Host ""

# 查找所有包含 start_web.py 的 Python 进程
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $_.MainWindowTitle -like "*start_web*" -or $_.Path -like "*python*"
    } catch {
        $false
    }
}

# 如果上面的方法没找到，尝试通过命令行参数查找
if ($pythonProcesses.Count -eq 0) {
    try {
        $pythonProcesses = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*start_web.py*"
        } | ForEach-Object { Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
    } catch {
        # 忽略错误
    }
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        try {
            Write-Host "  发现 Python 进程: $($proc.Id) - $($proc.ProcessName)" -ForegroundColor Green
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Write-Host "  [成功] 后端服务已停止" -ForegroundColor Green
            $stoppedCount++
        } catch {
            Write-Host "  [失败] 无法停止进程 $($proc.Id): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [信息] 未发现运行中的后端服务" -ForegroundColor Gray
}

Write-Host ""

# 步骤 2: 停止前端服务
Write-Host "[步骤 2/3] 停止前端服务 (Node.js)..." -ForegroundColor Yellow
Write-Host ""

# 查找包含 vite 的 Node.js 进程
try {
    $nodeProcesses = Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*"
    } | ForEach-Object { Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }

    if ($nodeProcesses) {
        foreach ($proc in $nodeProcesses) {
            try {
                Write-Host "  发现 Node.js 进程: $($proc.Id) - Vite" -ForegroundColor Green
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Write-Host "  [成功] 前端服务已停止" -ForegroundColor Green
                $stoppedCount++
            } catch {
                Write-Host "  [失败] 无法停止进程 $($proc.Id): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  [信息] 未发现运行中的前端服务" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [信息] 未发现运行中的前端服务" -ForegroundColor Gray
}

Write-Host ""

# 步骤 3: 验证服务状态
Write-Host "[步骤 3/3] 验证服务状态..." -ForegroundColor Yellow
Write-Host ""

$stillRunning = 0

$remainingPython = Get-Process python -ErrorAction SilentlyContinue
if ($remainingPython) {
    Write-Host "  [警告] 仍有 Python 进程在运行" -ForegroundColor Yellow
    $stillRunning++
}

$remainingNode = Get-Process node -ErrorAction SilentlyContinue
if ($remainingNode) {
    Write-Host "  [警告] 仍有 Node.js 进程在运行" -ForegroundColor Yellow
    $stillRunning++
}

if ($stillRunning -eq 0) {
    Write-Host "  [确认] 所有服务已停止" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "[结果总结]" -ForegroundColor Cyan
Write-Host ""

if ($stoppedCount -eq 0) {
    Write-Host "  未发现需要停止的项目服务" -ForegroundColor Gray
} else {
    Write-Host "  已停止 $stoppedCount 个服务" -ForegroundColor Green
}

Write-Host ""
Write-Host "[手动停止方法]" -ForegroundColor Cyan
Write-Host "  如需手动停止，可以使用:"
Write-Host "  1. 在对应窗口按 Ctrl+C"
Write-Host "  2. 运行: Stop-Process -Name python -Force"
Write-Host "  3. 运行: Stop-Process -Name node -Force"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
