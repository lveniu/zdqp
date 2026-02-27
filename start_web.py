"""
启动Web服务器
运行后端API和前端界面
使用 Click 框架美化输出
"""

import sys
import os
import socket
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

import click


def get_available_port(start_port=8000):
    """获取可用端口，从指定端口开始查找"""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None


def main():
    """主函数"""
    from src.core.click_output import get_output, Icons

    output = get_output()

    # 打印欢迎横幅
    output.print_banner(
        "整点抢券",
        subtitle="Web界面 (多用户版) v2.0.0"
    )

    # 获取端口配置：环境变量 > 固定端口 > 自动分配
    port_env = os.getenv("PORT", os.getenv("BACKEND_PORT", ""))
    if port_env.isdigit():
        port = int(port_env)
    else:
        # 优先使用固定端口，如果被占用则自动查找
        port = 8000  # 默认固定端口
        try:
            if not get_available_port(port):
                # 8000 被占用，从 9000 开始查找
                port = get_available_port(9000)
                if port is None:
                    output.error("无法找到可用端口")
                    sys.exit(1)
        except:
            port = get_available_port(9000)
            if port is None:
                output.error("无法找到可用端口")
                sys.exit(1)

    # 显示启动信息
    output.print_key_value({
        "启动时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "后端API": f"http://localhost:{port}",
        "API文档": f"http://localhost:{port}/docs",
        "前端界面": "http://localhost:5173",
        "数据库": "data/baibuti.db",
        "端口": str(port),
    }, title="服务信息")

    # 前端启动说明
    output.panel(
        f"{Icons.ARROW} cd web\n"
        f"{Icons.ARROW} npm install (首次运行)\n"
        f"{Icons.ARROW} npm run dev",
        title="前端启动步骤"
    )

    # 主要功能
    click.echo()
    click.secho("  主要功能", fg="cyan", bold=True)
    features = [
        ("用户注册/登录", "多用户独立数据", "每日打卡领积分"),
        ("积分查询", "自动抢5元券", "历史记录查询"),
    ]
    for row in features:
        click.echo("  ".join([f"{Icons.CHECK} {item}" for item in row]))
    click.echo()

    output.print_separator()
    output.info("按 Ctrl+C 停止服务")
    output.print_separator()

    # 启动服务器
    try:
        import uvicorn
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        output.warning("\n服务已停止")
    except Exception as e:
        output.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
