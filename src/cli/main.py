"""
命令行接口
使用 Typer 和 Click 实现
"""

import asyncio
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import typer
import click

from ..core.config import get_config, reload_config
from ..core.click_output import get_output, Icons
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

# 使用统一的 Click 输出
output = get_output()

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
    click.secho("# 项目初始化", fg="cyan", bold=True)
    click.echo()

    # 创建必要的目录
    dirs = ["logs", "data", "data/cache"]
    click.secho("创建目录结构...", fg="blue")

    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        click.echo(f"  {Icons.CHECK} 创建目录: {d}")

    click.echo()
    click.secho("项目初始化完成！", fg="green", bold=True)
    click.echo()
    click.echo("下一步:")
    click.echo("  1. 编辑 config/config.yaml 配置系统")
    click.echo("  2. 编辑 config/accounts.yaml 添加账号")
    click.echo("  3. 运行 python -m src.cli.main grab 开始抢券")


@app.command()
def info():
    """显示系统信息"""
    config = get_config()

    # 构建系统信息字典
    info_data = {
        "应用名称": config.app_name,
        "版本": config.version,
        "环境": config.env,
        "调试模式": str(config.debug),
        "日志级别": config.log.level,
        "日志目录": config.log.dir,
        "数据库": config.database.url.split("///")[-1],
        "代理启用": f"{Icons.SUCCESS} 启用" if config.proxy.enabled else f"{Icons.ERROR} 禁用",
        "最大并发": str(config.scheduler.max_workers),
        "重试次数": str(config.scheduler.retry_times),
    }

    output.print_system_info(info_data)


@app.command()
def grab(
    platform: str = typer.Argument(..., help="平台名称 (taobao, jd, meituan, pinduoduo)"),
    coupon_url: str = typer.Option(..., "--url", "-u", help="优惠券链接"),
    time: str = typer.Option(..., "--time", "-t", help="抢券时间 (YYYY-MM-DD HH:MM:SS)"),
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """抢券命令"""
    output.print_grab_start(platform, "优惠券", time)

    # 解析时间
    try:
        scheduled_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        output.error("时间格式不正确，应为 YYYY-MM-DD HH:MM:SS")
        raise typer.Exit(1)

    # 创建优惠券模型
    coupon = CouponModel(
        id=f"{platform}_{int(datetime.now().timestamp())}",
        name=f"{platform}优惠券",
        platform=platform,
        type=CouponType.FULL_REDUCTION,
        value=0,
        start_time=scheduled_time,
        end_time=scheduled_time.replace(second=59),
        url=coupon_url,
        status=CouponStatus.PENDING,
    )

    click.echo(f"优惠券ID: {coupon.id}")
    click.echo(f"执行时间: {scheduled_time}")

    # TODO: 实际执行抢券逻辑
    click.secho("平台适配器尚未实现，请先实现具体的平台适配器", fg="yellow")


@app.command()
def test(
    platform: str = typer.Argument(..., help="平台名称"),
):
    """测试平台连接"""
    click.echo(f"测试平台连接: {platform}")
    click.secho("连接测试功能待实现", fg="yellow")


@app.command()
def status():
    """查看调度器状态"""
    scheduler = get_scheduler()
    stats = scheduler.get_stats()

    # 构建状态数据
    status_data = {
        "状态": stats["state"],
        "最大Workers": str(stats["max_workers"]),
        "已调度任务": str(stats["scheduled_tasks"]),
        "运行中任务": str(stats["running_tasks"]),
        "队列中任务": str(stats["queued_tasks"]),
    }

    output.print_scheduler_status(status_data)


@app.command()
def notify(
    title: str = typer.Option(..., "--title", "-t", help="通知标题"),
    content: str = typer.Option(..., "--content", "-c", help="通知内容"),
    level: str = typer.Option("info", "--level", "-l", help="通知级别"),
):
    """测试通知功能"""
    click.echo(f"发送通知: {title}")

    async def send():
        notifier = get_notifier()
        success = await notifier.send(title, content, level=level)
        return success

    success = asyncio.run(send())

    if success:
        output.success("通知发送成功")
    else:
        output.error("通知发送失败")


@app.command()
def platforms():
    """列出支持的平台"""
    config = get_config()

    click.secho("支持的平台", fg="cyan", bold=True)
    click.echo()

    # 构建平台数据列表
    platform_data = []
    for name, platform_config in config.platforms.items():
        enabled = platform_config.get("enabled", False)
        platform_data.append({
            "平台": name,
            "状态": f"{Icons.SUCCESS} 启用" if enabled else f"{Icons.ERROR} 禁用",
            "基础URL": platform_config.get("base_url", ""),
        })

    output.print_table(platform_data, columns=["平台", "状态", "基础URL"])


def main_entry():
    """CLI入口"""
    app()


if __name__ == "__main__":
    main_entry()
