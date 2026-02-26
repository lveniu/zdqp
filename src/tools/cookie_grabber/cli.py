"""
Cookie获取工具CLI命令
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

from .pdd_login import PddCookieGrabber
from .mobile_emulator import MobileEmulator

app = typer.Typer(
    name="cookie",
    help="Cookie获取工具",
    no_args_is_help=True,
)
console = Console()


@app.command()
def pdd(
    device: str = typer.Option("Xiaomi_13", "--device", "-d", help="模拟设备名称"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="登录超时时间(秒)"),
    headless: bool = typer.Option(False, "--headless", help="无头模式（不推荐）"),
):
    """
    获取拼多多Cookie

    使用浏览器自动化模拟移动端登录，自动提取并保存Cookie。

    示例:
        cookie pdd
        cookie pdd --device iPhone_14
        cookie pdd --timeout 600
    """
    console.print(Panel.fit(
        "[bold cyan]拼多多Cookie获取工具[/bold cyan]\n\n"
        "本工具将:\n"
        "1. 启动移动端模拟浏览器\n"
        "2. 打开拼多多H5页面\n"
        "3. 等待您完成登录\n"
        "4. 自动提取Cookie\n"
        "5. 保存到配置文件",
        border_style="cyan"
    ))

    # 显示支持的设备列表
    console.print("\n[bold]支持的设备:[/bold]")
    devices = MobileEmulator.list_devices()
    table = Table(show_header=False)
    table.add_column("设备名", style="cyan")
    table.add_column("User-Agent", style="green")
    for name, ua in devices.items():
        table.add_row(name, ua)
    console.print(table)

    console.print(f"\n当前使用: [yellow]{device}[/yellow]")

    async def run():
        grabber = PddCookieGrabber(
            device=device,
            headless=headless,
            save_dir="config/cookies",
        )

        try:
            await grabber.run()

            console.print("\n[bold green]✓ Cookie获取完成！[/bold green]")
            console.print("\n下一步:")
            console.print("1. Cookie已保存到 config/accounts.yaml")
            console.print("2. 运行 [cyan]python -m src.cli.main pdd login[/cyan] 测试登录")
            console.print("3. 使用 [cyan]python -m src.cli.main pdd grab[/cyan] 开始抢券")

        except KeyboardInterrupt:
            console.print("\n[yellow]用户取消[/yellow]")
            raise typer.Exit(0)

        except Exception as e:
            console.print(f"\n[red]✗ 失败: {e}[/red]")
            raise typer.Exit(1)

        finally:
            await grabber.close()

    asyncio.run(run())


@app.command()
def list_devices():
    """列出所有支持的移动设备"""
    console.print("[bold cyan]支持的移动设备[/bold cyan]\n")

    devices = MobileEmulator.DEVICES

    table = Table(show_header=True)
    table.add_column("设备名", style="cyan")
    table.add_column("屏幕尺寸", style="green")
    table.add_column("User-Agent", style="yellow")

    for name, config in devices.items():
        width = config["viewport"]["width"]
        height = config["viewport"]["height"]
        ua = config["user_agent"][:60] + "..."
        table.add_row(name, f"{width}x{height}", ua)

    console.print(table)


@app.command()
def validate(
    file: str = typer.Option("config/accounts.yaml", "--file", "-f", help="Cookie文件路径"),
):
    """验证Cookie有效性"""
    import yaml
    from pathlib import Path

    file_path = Path(file)

    if not file_path.exists():
        console.print(f"[red]✗ 文件不存在: {file}[/red]")
        raise typer.Exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    accounts = config.get("accounts", [])

    if not accounts:
        console.print("[yellow]未找到账号配置[/yellow]")
        return

    console.print("[bold cyan]Cookie验证结果[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("平台", style="cyan")
    table.add_column("用户名", style="green")
    table.add_column("Cookie", style="yellow")
    table.add_column("状态", style="bold")

    from .cookie_parser import CookieParser

    parser = CookieParser()
    valid_count = 0

    for acc in accounts:
        platform = acc.get("platform", "N/A")
        username = acc.get("username", "N/A")
        cookies_str = acc.get("cookies", "")

        if not cookies_str:
            status = "[red]✗ 无Cookie[/red]"
        else:
            cookies = parser.string_to_cookies(cookies_str)
            validation = parser.validate_cookies(cookies)

            if validation["valid"]:
                status = "[green]✓ 有效[/green]"
                valid_count += 1
            else:
                missing = ", ".join(validation["missing"])
                status = f"[red]✗ 缺少: {missing}[/red]"

        # 截断Cookie显示
        cookie_display = cookies_str[:30] + "..." if len(cookies_str) > 30 else cookies_str
        if not cookie_display:
            cookie_display = "N/A"

        table.add_row(platform, username, cookie_display, status)

    console.print(table)
    console.print(f"\n总计: {len(accounts)} 个账号, {valid_count} 个有效")


@app.command()
def parse(
    cookie_string: str = typer.Argument(..., help="Cookie字符串"),
):
    """解析Cookie字符串"""
    from .cookie_parser import CookieParser

    parser = CookieParser()

    console.print("[bold cyan]Cookie解析结果[/bold cyan]\n")

    # 转换为Cookie列表
    cookies = parser.string_to_cookies(cookie_string)

    console.print(f"解析到 [green]{len(cookies)}[/green] 个Cookie\n")

    table = Table(show_header=True)
    table.add_column("名称", style="cyan")
    table.add_column("值", style="green")
    table.add_column("说明", style="yellow")

    for cookie in cookies:
        name = cookie["name"]
        value = cookie["value"]
        desc = CookieParser.PDD_COOKIES.get(name, "")

        # 截断长值
        if len(value) > 40:
            value = value[:40] + "..."

        table.add_row(name, value, desc)

    console.print(table)

    # 验证
    validation = parser.validate_cookies(cookies)
    console.print(f"\n状态: ", end="")

    if validation["valid"]:
        console.print("[green]✓ Cookie完整[/green]")
    else:
        console.print(f"[red]✗ 缺少必要Cookie: {', '.join(validation['missing'])}[/red]")

    if validation["warnings"]:
        console.print("\n[yellow]建议:[/yellow]")
        for warning in validation["warnings"]:
            console.print(f"  • {warning}")


@app.command()
def export(
    file: str = typer.Option(..., "--file", "-f", help="导出的JSON文件路径"),
    username: str = typer.Option("pinduoduo_user", "--username", "-u", help="用户名"),
):
    """
    从JSON文件导出Cookie到accounts.yaml

    使用 cookie pdd 命令会自动保存JSON文件，此命令用于手动导出。
    """
    from pathlib import Path
    import json

    file_path = Path(file)

    if not file_path.exists():
        console.print(f"[red]✗ 文件不存在: {file}[/red]")
        raise typer.Exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 提取信息
    cookies = data.get("cookies", [])
    user_agent = data.get("user_agent", "")
    device = data.get("device", "Xiaomi_13")

    # 构建Cookie字符串
    from .cookie_parser import CookieParser
    parser = CookieParser()
    cookie_str = parser.cookies_to_string(cookies)

    # 构建账号配置
    account_config = {
        "platform": "pinduoduo",
        "username": username,
        "password": "",
        "cookies": cookie_str,
        "user_agent": user_agent,
        "enabled": True,
        "metadata": {
            "device": device,
            "exported_from": str(file_path),
        }
    }

    # 保存到accounts.yaml
    import yaml
    accounts_file = Path("config/accounts.yaml")

    # 读取现有配置
    existing_accounts = []
    if accounts_file.exists():
        with open(accounts_file, "r", encoding="utf-8") as f:
            try:
                config_data = yaml.safe_load(f)
                existing_accounts = config_data.get("accounts", [])
            except:
                pass

    # 检查是否已存在
    updated = False
    for i, acc in enumerate(existing_accounts):
        if acc.get("platform") == "pinduoduo" and acc.get("username") == username:
            existing_accounts[i] = account_config
            updated = True
            break

    if not updated:
        existing_accounts.append(account_config)

    # 保存
    with open(accounts_file, "w", encoding="utf-8") as f:
        yaml.dump({"accounts": existing_accounts}, f, allow_unicode=True, default_flow_style=False)

    console.print(f"[green]✓[/green] 已导出到: {accounts_file}")
