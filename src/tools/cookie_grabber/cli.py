"""
Cookie获取工具CLI命令
"""

import asyncio
import typer
from pathlib import Path
from typing import List, Dict

from ...core.click_output import get_output, Icons
from .pdd_login import PddCookieGrabber
from .mobile_emulator import MobileEmulator

app = typer.Typer(
    name="cookie",
    help="Cookie获取工具",
    no_args_is_help=True,
)

# 使用统一的 Click 输出
output = get_output()


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
    output.panel(
        f"{Icons.ARROW_RIGHT} 启动移动端模拟浏览器\n"
        f"{Icons.ARROW_RIGHT} 打开拼多多H5页面\n"
        f"{Icons.ARROW_RIGHT} 等待您完成登录\n"
        f"{Icons.ARROW_RIGHT} 自动提取Cookie\n"
        f"{Icons.ARROW_RIGHT} 保存到配置文件",
        title="拼多多Cookie获取工具"
    )

    # 显示支持的设备列表
    output.print_header("支持的设备", level=3)
    devices = MobileEmulator.list_devices()

    device_data = []
    for name, ua in devices.items():
        device_data.append({
            "设备名": name,
            "User-Agent": ua,
        })

    output.print_table(device_data, columns=["设备名", "User-Agent"])
    output.info(f"当前使用: {device}")

    async def run():
        grabber = PddCookieGrabber(
            device=device,
            headless=headless,
            save_dir="config/cookies",
        )

        try:
            await grabber.run()

            output.success_panel(
                f"{Icons.ARROW_RIGHT} Cookie已保存到 config/accounts.yaml\n"
                f"{Icons.ARROW_RIGHT} 运行 python -m src.cli.main pdd login 测试登录\n"
                f"{Icons.ARROW_RIGHT} 使用 python -m src.cli.main pdd grab 开始抢券",
                title="Cookie获取完成！"
            )

        except KeyboardInterrupt:
            output.warning("用户取消")
            raise typer.Exit(0)

        except Exception as e:
            output.error(f"失败: {e}")
            raise typer.Exit(1)

        finally:
            await grabber.close()

    asyncio.run(run())


@app.command()
def list_devices():
    """列出所有支持的移动设备"""
    output.print_header("支持的移动设备", level=2)

    devices = MobileEmulator.DEVICES

    device_data = []
    for name, config in devices.items():
        width = config["viewport"]["width"]
        height = config["viewport"]["height"]
        ua = config["user_agent"][:60] + "..."
        device_data.append({
            "设备名": name,
            "屏幕尺寸": f"{width}x{height}",
            "User-Agent": ua,
        })

    output.print_table(device_data, columns=["设备名", "屏幕尺寸", "User-Agent"])


@app.command()
def validate(
    file: str = typer.Option("config/accounts.yaml", "--file", "-f", help="Cookie文件路径"),
):
    """验证Cookie有效性"""
    import yaml

    file_path = Path(file)

    if not file_path.exists():
        output.error(f"文件不存在: {file}")
        raise typer.Exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    accounts = config.get("accounts", [])

    if not accounts:
        output.warning("未找到账号配置")
        return

    output.print_header("Cookie验证结果", level=2)

    from .cookie_parser import CookieParser

    parser = CookieParser()
    valid_count = 0

    account_data = []
    for acc in accounts:
        platform = acc.get("platform", "N/A")
        username = acc.get("username", "N/A")
        cookies_str = acc.get("cookies", "")

        if not cookies_str:
            status = f"{Icons.ERROR} 无Cookie"
            status_type = "error"
        else:
            cookies = parser.string_to_cookies(cookies_str)
            validation = parser.validate_cookies(cookies)

            if validation["valid"]:
                status = f"{Icons.SUCCESS} 有效"
                status_type = "success"
                valid_count += 1
            else:
                missing = ", ".join(validation["missing"])
                status = f"{Icons.ERROR} 缺少: {missing}"
                status_type = "error"

        # 截断Cookie显示
        cookie_display = cookies_str[:30] + "..." if len(cookies_str) > 30 else cookies_str
        if not cookie_display:
            cookie_display = "N/A"

        account_data.append({
            "平台": platform,
            "用户名": username,
            "Cookie": cookie_display,
            "状态": status,
        })

    output.print_table(account_data, columns=["平台", "用户名", "Cookie", "状态"])
    output.info(f"总计: {len(accounts)} 个账号, {valid_count} 个有效")


@app.command()
def parse(
    cookie_string: str = typer.Argument(..., help="Cookie字符串"),
):
    """解析Cookie字符串"""
    from .cookie_parser import CookieParser

    parser = CookieParser()

    output.print_header("Cookie解析结果", level=2)

    # 转换为Cookie列表
    cookies = parser.string_to_cookies(cookie_string)

    output.info(f"解析到 {len(cookies)} 个Cookie")

    cookie_data = []
    for cookie in cookies:
        name = cookie["name"]
        value = cookie["value"]
        desc = CookieParser.PDD_COOKIES.get(name, "")

        # 截断长值
        if len(value) > 40:
            value = value[:40] + "..."

        cookie_data.append({
            "名称": name,
            "值": value,
            "说明": desc,
        })

    output.print_table(cookie_data, columns=["名称", "值", "说明"])

    # 验证
    validation = parser.validate_cookies(cookies)

    if validation["valid"]:
        output.success("Cookie完整")
    else:
        missing = ", ".join(validation['missing'])
        output.error(f"缺少必要Cookie: {missing}")

    if validation["warnings"]:
        output.warning("建议:")
        for warning in validation["warnings"]:
            output.print(f"  {Icons.DOT} {warning}")


@app.command()
def export(
    file: str = typer.Option(..., "--file", "-f", help="导出的JSON文件路径"),
    username: str = typer.Option("pinduoduo_user", "--username", "-u", help="用户名"),
):
    """
    从JSON文件导出Cookie到accounts.yaml

    使用 cookie pdd 命令会自动保存JSON文件，此命令用于手动导出。
    """
    import json
    import yaml

    file_path = Path(file)

    if not file_path.exists():
        output.error(f"文件不存在: {file}")
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

    output.success(f"已导出到: {accounts_file}")
