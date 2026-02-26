"""
拼多多CLI命令
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...models.platform import Account
from ...core.config import get_config
from ...core.logger import Logger
from .adapter import PinduoduoAdapter
from .utils.parser import parse_coupon_url

app = typer.Typer(
    name="pdd",
    help="拼多多抢券命令",
    no_args_is_help=True,
)
console = Console()


def get_pdd_account(account_id: str = "default") -> Account:
    """获取PDD账号配置"""
    import yaml
    from pathlib import Path

    config_file = Path("config/accounts.yaml")

    if not config_file.exists():
        return Account(
            platform="pinduoduo",
            username=account_id,
            cookies="",
            user_agent="Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36",
            enabled=True,
        )

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    accounts = config.get("accounts", [])

    # 查找拼多多账号
    for acc in accounts:
        if acc.get("platform") == "pinduoduo" and acc.get("enabled", False):
            # 转换为Account对象
            return Account(
                platform=acc.get("platform", "pinduoduo"),
                username=acc.get("username", account_id),
                password=acc.get("password", ""),
                cookies=acc.get("cookies", ""),
                user_agent=acc.get("user_agent", "Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36"),
                enabled=acc.get("enabled", True),
                metadata=acc.get("metadata", {}),
            )

    # 未找到配置的账号
    return Account(
        platform="pinduoduo",
        username=account_id,
        cookies="",
        user_agent="Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36",
        enabled=True,
    )


@app.command()
def grab(
    coupon_url: str = typer.Option(..., "--url", "-u", help="优惠券链接"),
    time: str = typer.Option(..., "--time", "-t", help="抢券时间 (YYYY-MM-DD HH:MM:SS)"),
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
   提前秒数: float = typer.Option(0.1, "--advance", help="提前发起请求的秒数"),
):
    """
    准点抢券

    示例:
        pdd grab --url "https://h5.pinduoduo.com/coupon.html?coupon_id=xxx" \\
               --time "2024-03-01 10:00:00"
    """
    console.print(Panel.fit(
        f"[bold blue]拼多多准点抢券[/bold blue]\n"
        f"链接: {coupon_url}\n"
        f"时间: {time}\n"
        f"账号: {account}\n"
        f"提前: {提前秒数}秒"
    ))

    async def execute_grab():
        # 获取账号
        acc = get_pdd_account(account)

        # 检查Cookie
        if not acc.cookies:
            console.print("[red]错误: 未配置Cookie，请先在config/accounts.yaml中配置[/red]")
            console.print("\n[yellow]获取Cookie方法:[/yellow]")
            console.print("1. 使用浏览器打开 h5.pinduoduo.com")
            console.print("2. 登录账号")
            console.print("3. 按F12打开开发者工具")
            console.print("4. 在Network中找到请求头中的Cookie")
            console.print("5. 复制Cookie到配置文件")
            raise typer.Exit(1)

        # 解析时间
        try:
            grab_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            console.print("[red]错误: 时间格式不正确，应为 YYYY-MM-DD HH:MM:SS[/red]")
            raise typer.Exit(1)

        # 检查时间
        now = datetime.now()
        if grab_time < now:
            console.print(f"[red]错误: 抢券时间 {grab_time} 已经过去了[/red]")
            raise typer.Exit(1)

        # 解析优惠券链接
        coupon_info = parse_coupon_url(coupon_url)
        if not coupon_info:
            console.print("[red]错误: 无效的优惠券链接[/red]")
            raise typer.Exit(1)

        console.print(f"\n[green]✓[/green] 优惠券信息:")
        console.print(f"  优惠券ID: {coupon_info.get('coupon_id', 'N/A')}")
        console.print(f"  商品ID: {coupon_info.get('goods_id', 'N/A')}")
        console.print(f"  活动ID: {coupon_info.get('activity_id', 'N/A')}")

        # 等待倒计时
        wait_seconds = (grab_time - now).total_seconds()
        console.print(f"\n[yellow]等待抢券时间...[/yellow]")

        if wait_seconds > 10:
            # 显示倒计时
            while wait_seconds > 10:
                console.print(f"  距离抢券还有: {int(wait_seconds)} 秒", end="\r")
                await asyncio.sleep(1)
                wait_seconds -= 1
            console.print("")

        # 创建适配器并执行
        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            # 登录
            console.print("\n[cyan]登录中...[/cyan]")
            login_result = await adapter.login()

            if not login_result.success:
                console.print(f"[red]登录失败: {login_result.message}[/red]")
                raise typer.Exit(1)

            console.print("[green]✓[/green] 登录成功")

            # 执行准点抢券
            result = await adapter.precise_grab(
                coupon_url=coupon_url,
                grab_time=grab_time,
                提前秒数=提前秒数,
            )

            # 显示结果
            console.print("\n" + "="*50)
            if result.success:
                console.print("[bold green]🎉 抢券成功！[/bold green]")
                console.print(f"优惠券序列号: {result.coupon_sn or 'N/A'}")
                if result.valid_until:
                    console.print(f"有效期至: {result.valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                console.print(f"[bold red]❌ 抢券失败[/bold red]")
                console.print(f"原因: {result.message}")

            console.print(f"耗时: {result.elapsed_ms:.2f}ms")
            console.print("="*50)

    try:
        asyncio.run(execute_grab())
    except KeyboardInterrupt:
        console.print("\n[yellow]用户取消[/yellow]")
        raise typer.Exit(0)


@app.command()
def check(
    coupon_url: str = typer.Option(..., "--url", "-u", help="优惠券链接"),
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """检查优惠券状态"""
    console.print(f"[bold blue]检查优惠券状态[/bold blue]\n")

    async def execute_check():
        acc = get_pdd_account(account)

        if not acc.cookies:
            console.print("[red]错误: 未配置Cookie[/red]")
            raise typer.Exit(1)

        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            # 解析链接
            coupon_info = parse_coupon_url(coupon_url)
            if not coupon_info:
                console.print("[red]错误: 无效的优惠券链接[/red]")
                raise typer.Exit(1)

            console.print(f"优惠券ID: {coupon_info.get('coupon_id', 'N/A')}")

            # 登录
            login_result = await adapter.login()
            if not login_result.success:
                console.print(f"[red]登录失败: {login_result.message}[/red]")
                raise typer.Exit(1)

            # 创建临时优惠券对象
            from ..models.coupon import CouponModel
            coupon = CouponModel(
                id=coupon_info.get("coupon_id", ""),
                name="PDD优惠券",
                platform="pinduoduo",
                url=coupon_url,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30),
            )

            # 检查状态
            status = await adapter.check_coupon_status(coupon)

            # 显示结果
            console.print("\n" + "="*50)
            console.print(f"状态: {status.get('status', 'UNKNOWN')}")
            console.print(f"可抢: {'是' if status.get('can_grab') else '否'}")
            console.print(f"剩余: {status.get('remaining_quantity', 'N/A')}/{status.get('total_quantity', 'N/A')}")
            console.print("="*50)

    try:
        asyncio.run(execute_check())
    except KeyboardInterrupt:
        console.print("\n[yellow]用户取消[/yellow]")
        raise typer.Exit(0)


@app.command()
def login(
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """测试登录"""
    console.print(f"[bold blue]测试拼多多登录[/bold blue]\n")

    async def execute_login():
        acc = get_pdd_account(account)

        if not acc.cookies:
            console.print("[red]错误: 未配置Cookie[/red]")
            console.print("\n[yellow]请按以下步骤获取Cookie:[/yellow]")
            console.print("1. 使用浏览器打开 h5.pinduoduo.com")
            console.print("2. 登录账号")
            console.print("3. 按F12打开开发者工具")
            console.print("4. 刷新页面，找到任意请求")
            console.print("5. 复制请求头中的Cookie到配置文件")
            raise typer.Exit(1)

        console.print("Cookie已配置")
        console.print(f"Token: {acc.cookies[:50]}..." if len(acc.cookies) > 50 else f"Token: {acc.cookies}")

        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            console.print("\n[cyan]正在验证Cookie...[/cyan]")
            result = await adapter.login()

            if result.success:
                console.print("[bold green]✓ 登录成功！[/bold green]")
                console.print(f"用户名: {result.data.get('username', 'N/A')}")
                console.print(f"登录时间: {result.data.get('login_time', 'N/A')}")
            else:
                console.print(f"[bold red]✗ 登录失败[/bold red]")
                console.print(f"原因: {result.message}")

    try:
        asyncio.run(execute_login())
    except KeyboardInterrupt:
        console.print("\n[yellow]用户取消[/yellow]")
        raise typer.Exit(0)


@app.command()
def parse_url(
    url: str = typer.Argument(..., help="优惠券或商品链接"),
):
    """解析URL并显示信息"""
    console.print(f"[bold blue]解析URL[/bold blue]\n")
    console.print(f"URL: {url}\n")

    # 尝试解析为优惠券链接
    from .utils.parser import parse_coupon_url, parse_goods_url

    coupon_info = parse_coupon_url(url)
    if coupon_info:
        console.print("[green]✓[/green] 这是优惠券链接")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("字段", style="cyan")
        table.add_column("值", style="green")

        for key, value in coupon_info.items():
            if key != "original_url":
                table.add_row(key, str(value) or "N/A")

        console.print(table)
        return

    # 尝试解析为商品链接
    goods_info = parse_goods_url(url)
    if goods_info:
        console.print("[green]✓[/green] 这是商品链接")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("字段", style="cyan")
        table.add_column("值", style="green")

        for key, value in goods_info.items():
            if key != "original_url":
                table.add_row(key, str(value) or "N/A")

        console.print(table)
        return

    console.print("[red]✗[/red] 无法识别的链接格式")
