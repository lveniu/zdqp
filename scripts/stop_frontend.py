"""
停止前端服务
使用 Click 框架美化输出
"""

import subprocess
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from src.core.click_output import get_output, Icons


def stop_frontend():
    """停止前端服务"""
    output = get_output()

    output.print_header("停止前端服务", level=1)

    # 强制终止所有 Node.js 进程
    click.secho("停止前端服务 (Node.js)...", fg="blue", bold=True)

    try:
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'node.exe'],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )

        if result.returncode == 0:
            click.secho(f"  {Icons.SUCCESS} 前端服务已强制停止", fg="green")
        else:
            if "not found" in result.stderr.lower() or "没有找到" in result.stderr:
                click.secho("  未发现运行中的前端服务", fg="yellow")
            else:
                click.secho(f"  {Icons.ERROR} 停止失败", fg="red")
    except Exception as e:
        click.secho("  未发现运行中的前端服务", fg="yellow")

    click.echo()

    # 显示结果
    output.print_separator()
    click.secho("前端服务已停止", fg="green", bold=True)
    output.print_separator()
    click.echo()

    # 手动停止方法
    click.secho("如需手动停止:", fg="cyan", bold=True)
    click.echo(f"  {Icons.ARROW} 在对应窗口按 Ctrl+C")
    click.echo(f"  {Icons.ARROW} 运行: taskkill /F /IM node.exe")
    click.echo()


if __name__ == "__main__":
    try:
        stop_frontend()
    except KeyboardInterrupt:
        click.secho("\n操作已取消", fg="yellow")
        sys.exit(0)
    except Exception as e:
        click.secho(f"发生错误: {e}", fg="red", bold=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
