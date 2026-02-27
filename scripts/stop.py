"""
停止项目服务 - 可靠版本
使用 PowerShell 方式停止进程
"""

import subprocess
import sys
import os


def stop_processes_powershell(name_pattern):
    """使用 PowerShell 停止进程"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', f'Get-Process {name_pattern} -ErrorAction SilentlyContinue | Stop-Process -Force'],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )
        return result.returncode == 0
    except:
        return False


def main():
    print("=" * 60)
    print("停止项目服务")
    print("=" * 60)
    print()

    # 停止后端
    print("[INFO] 停止后端服务...")
    python_stopped = stop_processes_powershell('python*')

    if python_stopped:
        print("[SUCCESS] 后端服务已停止")
    else:
        print("[INFO] 未发现运行中的后端服务")

    print()

    # 停止前端
    print("[INFO] 停止前端服务...")
    node_stopped = stop_processes_powershell('node')

    if node_stopped:
        print("[SUCCESS] 前端服务已停止")
    else:
        print("[INFO] 未发现运行中的前端服务")

    print()
    print("=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
        os.system("pause > nul 2>&1")
    except KeyboardInterrupt:
        print("\n[INFO] 操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
