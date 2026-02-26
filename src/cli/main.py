"""
命令行接口
使用Typer实现
"""

import asyncio
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from ..core.config import get_config, reload_config
from ..core.logger import Logger
from ..core.scheduler import get_scheduler
from ..core.notifier import get_notifier
from ..models.coupon import CouponModel, CouponType, CouponStatus
from ..models.task import TaskModel, TaskPriority
from ..models.platform import Account

app = typer.Typer(
    name="coupon-grabber",
    help="多平台抢券系统",
    no_args_is_help=True,
)
console = Console()

# 添加平台子命令
from ..platforms.pinduoduo.cli import app as pdd_app
app.add_typer(pdd_app, name="pdd", help="拼多多抢券")

# 添加工具子命令
from ..tools.cookie_grabber.cli import app as cookie_app
app.add_typer(cookie_app, name="cookie", help="Cookie获取工具")


@app.callback()
def main(
    config: str = typer.Option("config/config.yaml", "--config", "-c", help="配置文件路径"),
    debug: bool = typer.Option(False, "--debug", help="调试模式"),
):
    """抢券系统命令行工具"""
    # 加载配置
    reload_config(config)

    if debug:
        from ..core.config import _config
        if _config:
            _config.debug = True


@app.command()
def init():
    """初始化项目"""
    console.print("[bold blue]初始化抢券项目...[/bold blue]")

    # 创建必要的目录
    dirs = ["logs", "data", "data/cache"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] 创建目录: {d}")

    # 复制配置文件示例
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    console.print(f"\n[bold green]项目初始化完成！[/bold green]")
    console.print("\n下一步:")
    console.print("  1. 编辑 [cyan]config/config.yaml[/cyan] 配置系统")
    console.print("  2. 编辑 [cyan]config/accounts.yaml[/cyan] 添加账号")
    console.print("  3. 运行 [cyan]python -m src.cli.main grab[/cyan] 开始抢券")


@app.command()
def info():
    """显示系统信息"""
    config = get_config()

    table = Table(title="系统信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("应用名称", config.app_name)
    table.add_row("版本", config.version)
    table.add_row("环境", config.env)
    table.add_row("调试模式", str(config.debug))
    table.add_row("日志级别", config.log.level)
    table.add_row("数据库", config.database.url)
    table.add_row("代理启用", str(config.proxy.enabled))
    table.add_row("最大并发", str(config.scheduler.max_workers))

    console.print(table)


@app.command()
def grab(
    platform: str = typer.Argument(..., help="平台名称 (taobao, jd, meituan, pinduoduo)"),
    coupon_url: str = typer.Option(..., "--url", "-u", help="优惠券链接"),
    time: str = typer.Option(..., "--time", "-t", help="抢券时间 (YYYY-MM-DD HH:MM:SS)"),
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """抢券命令"""
    console.print(f"[bold blue]准备抢券:[/bold blue] {platform}")
    console.print(f"  链接: {coupon_url}")
    console.print(f"  时间: {time}")
    console.print(f"  账号: {account}")

    # 解析时间
    try:
        scheduled_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        console.print("[red]错误: 时间格式不正确，应为 YYYY-MM-DD HH:MM:SS[/red]")
        raise typer.Exit(1)

    # 创建优惠券模型
    coupon = CouponModel(
        id=f"{platform}_{int(datetime.now().timestamp())}",
        name=f"{platform}优惠券",
        platform=platform,
        type=CouponType.FULL_REDUCTION,
        value=0,
        start_time=scheduled_time,
        end_time=scheduled_time.replace(second=59),  # 假设持续1分钟
        url=coupon_url,
        status=CouponStatus.PENDING,
    )

    console.print(f"\n[yellow]任务已创建，等待执行时间...[/yellow]")
    console.print(f"  优惠券ID: {coupon.id}")
    console.print(f"  执行时间: {scheduled_time}")

    # TODO: 实际执行抢券逻辑
    console.print("\n[bold red]注意: 平台适配器尚未实现，请先实现具体的平台适配器[/bold red]")


@app.command()
def test(
    platform: str = typer.Argument(..., help="平台名称"),
):
    """测试平台连接"""
    console.print(f"[bold blue]测试平台连接:[/bold blue] {platform}")

    # TODO: 实现连接测试
    console.print("[yellow]连接测试功能待实现[/yellow]")


@app.command()
def status():
    """查看调度器状态"""
    scheduler = get_scheduler()
    stats = scheduler.get_stats()

    table = Table(title="调度器状态")
    table.add_column("状态项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("状态", stats["state"])
    table.add_row("最大Workers", str(stats["max_workers"]))
    table.add_row("已调度任务", str(stats["scheduled_tasks"]))
    table.add_row("运行中任务", str(stats["running_tasks"]))
    table.add_row("队列中任务", str(stats["queued_tasks"]))

    console.print(table)


@app.command()
def notify(
    title: str = typer.Option(..., "--title", "-t", help="通知标题"),
    content: str = typer.Option(..., "--content", "-c", help="通知内容"),
    level: str = typer.Option("info", "--level", "-l", help="通知级别"),
):
    """测试通知功能"""
    console.print(f"[bold blue]发送通知:[/bold blue] {title}")

    async def send():
        notifier = get_notifier()
        success = await notifier.send(title, content, level=level)
        return success

    success = asyncio.run(send())

    if success:
        console.print("[green]✓ 通知发送成功[/green]")
    else:
        console.print("[red]✗ 通知发送失败[/red]")


@app.command()
def platforms():
    """列出支持的平台"""
    config = get_config()

    table = Table(title="支持的平台")
    table.add_column("平台", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("基础URL")

    for name, platform_config in config.platforms.items():
        status = "✓ 启用" if platform_config.get("enabled", False) else "✗ 禁用"
        table.add_row(name, status, platform_config.get("base_url", ""))

    console.print(table)


def main_entry():
    """CLI入口"""
    app()


if __name__ == "__main__":
    main_entry()
