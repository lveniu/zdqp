"""
拼多多CLI命令
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import typer

from ...models.platform import Account
from ...core.config import get_config
from ...core.click_output import get_output, Icons
from .adapter import PinduoduoAdapter
from .utils.parser import parse_coupon_url, parse_goods_url

app = typer.Typer(
    name="pdd",
    help="拼多多抢券命令",
    no_args_is_help=True,
)

# 使用统一的 Click 输出
output = get_output()


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
    # 显示抢券信息面板
    content = (
        f"优惠券链接: {coupon_url}\n"
        f"抢券时间: {time}\n"
        f"账号标识: {account}\n"
        f"提前秒数: {提前秒数}秒"
    )
    output.panel(content, title="拼多多准点抢券")

    async def execute_grab():
        # 获取账号
        acc = get_pdd_account(account)

        # 检查Cookie
        if not acc.cookies:
            output.error_panel(
                "未配置Cookie，请先在 config/accounts.yaml 中配置\n\n"
                f"{Icons.ARROW_RIGHT} 使用浏览器打开 h5.pinduoduo.com\n"
                f"{Icons.ARROW_RIGHT} 登录账号\n"
                f"{Icons.ARROW_RIGHT} 按F12打开开发者工具\n"
                f"{Icons.ARROW_RIGHT} 在Network中找到请求头中的Cookie\n"
                f"{Icons.ARROW_RIGHT} 复制Cookie到配置文件",
                title="Cookie未配置"
            )
            raise typer.Exit(1)

        # 解析时间
        try:
            grab_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            output.error("时间格式不正确，应为 YYYY-MM-DD HH:MM:SS")
            raise typer.Exit(1)

        # 检查时间
        now = datetime.now()
        if grab_time < now:
            output.error(f"抢券时间 {grab_time} 已经过去了")
            raise typer.Exit(1)

        # 解析优惠券链接
        coupon_info = parse_coupon_url(coupon_url)
        if not coupon_info:
            output.error("无效的优惠券链接")
            raise typer.Exit(1)

        # 显示优惠券信息
        output.print_key_value({
            "优惠券ID": coupon_info.get('coupon_id', 'N/A'),
            "商品ID": coupon_info.get('goods_id', 'N/A'),
            "活动ID": coupon_info.get('activity_id', 'N/A'),
        }, title="优惠券信息")

        # 等待倒计时
        wait_seconds = (grab_time - now).total_seconds()
        output.info(f"等待抢券时间... (还有 {int(wait_seconds)} 秒)")

        if wait_seconds > 10:
            # 显示倒计时
            with output.status(f"倒计时中...", spinner="dots"):
                while wait_seconds > 10:
                    await asyncio.sleep(1)
                    wait_seconds -= 1

        # 创建适配器并执行
        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            # 登录
            output.info("登录中...")
            login_result = await adapter.login()

            if not login_result.success:
                output.print_login_failed(login_result.message, "拼多多")
                raise typer.Exit(1)

            output.print_login_success(acc.username, "拼多多")

            # 执行准点抢券
            result = await adapter.precise_grab(
                coupon_url=coupon_url,
                grab_time=grab_time,
                提前秒数=提前秒数,
            )

            # 显示结果
            output.print_separator()
            if result.success:
                output.success_panel(
                    f"优惠券序列号: {result.coupon_sn or 'N/A'}\n"
                    f"有效期至: {result.valid_until.strftime('%Y-%m-%d %H:%M:%S') if result.valid_until else 'N/A'}\n"
                    f"耗时: {result.elapsed_ms:.2f}ms",
                    title="抢券成功！"
                )
            else:
                output.error_panel(
                    f"原因: {result.message}\n"
                    f"耗时: {result.elapsed_ms:.2f}ms",
                    title="抢券失败"
                )
            output.print_separator()

    try:
        asyncio.run(execute_grab())
    except KeyboardInterrupt:
        output.warning("用户取消")
        raise typer.Exit(0)


@app.command()
def check(
    coupon_url: str = typer.Option(..., "--url", "-u", help="优惠券链接"),
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """检查优惠券状态"""
    output.print_header("检查优惠券状态", level=2)

    async def execute_check():
        acc = get_pdd_account(account)

        if not acc.cookies:
            output.error_panel("未配置Cookie", title="错误")
            raise typer.Exit(1)

        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            # 解析链接
            coupon_info = parse_coupon_url(coupon_url)
            if not coupon_info:
                output.error("无效的优惠券链接")
                raise typer.Exit(1)

            output.info(f"优惠券ID: {coupon_info.get('coupon_id', 'N/A')}")

            # 登录
            login_result = await adapter.login()
            if not login_result.success:
                output.print_login_failed(login_result.message)
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
            output.print_key_value({
                "状态": status.get('status', 'UNKNOWN'),
                "可抢": "是" if status.get('can_grab') else "否",
                "剩余": f"{status.get('remaining_quantity', 'N/A')}/{status.get('total_quantity', 'N/A')}",
            }, title="检查结果")

    try:
        asyncio.run(execute_check())
    except KeyboardInterrupt:
        output.warning("用户取消")
        raise typer.Exit(0)


@app.command()
def login(
    account: str = typer.Option("default", "--account", "-a", help="账号标识"),
):
    """测试登录"""
    output.print_header("测试拼多多登录", level=2)

    async def execute_login():
        acc = get_pdd_account(account)

        if not acc.cookies:
            output.error_panel(
                "未配置Cookie\n\n"
                f"{Icons.ARROW_RIGHT} 使用浏览器打开 h5.pinduoduo.com\n"
                f"{Icons.ARROW_RIGHT} 登录账号\n"
                f"{Icons.ARROW_RIGHT} 按F12打开开发者工具\n"
                f"{Icons.ARROW_RIGHT} 刷新页面，找到任意请求\n"
                f"{Icons.ARROW_RIGHT} 复制请求头中的Cookie到配置文件",
                title="Cookie未配置"
            )
            raise typer.Exit(1)

        output.info("Cookie已配置")
        token_preview = acc.cookies[:50] + "..." if len(acc.cookies) > 50 else acc.cookies
        output.debug(f"Token: {token_preview}")

        async with PinduoduoAdapter(acc, get_config().platforms.get("pinduoduo", {})) as adapter:
            output.info("验证Cookie中...")

            with output.status("登录中...", spinner="dots"):
                result = await adapter.login()

            if result.success:
                output.print_login_success(
                    result.data.get('username', acc.username),
                    "拼多多"
                )
                output.print_key_value({
                    "用户名": result.data.get('username', 'N/A'),
                    "登录时间": result.data.get('login_time', 'N/A'),
                }, title="登录详情")
            else:
                output.print_login_failed(result.message, "拼多多")

    try:
        asyncio.run(execute_login())
    except KeyboardInterrupt:
        output.warning("用户取消")
        raise typer.Exit(0)


@app.command()
def parse_url(
    url: str = typer.Argument(..., help="优惠券或商品链接"),
):
    """解析URL并显示信息"""
    output.print_header("解析URL", level=2)
    output.info(f"URL: {url}")

    # 尝试解析为优惠券链接
    coupon_info = parse_coupon_url(url)
    if coupon_info:
        output.success("这是优惠券链接")

        # 过滤掉 original_url 字段
        display_data = {k: v for k, v in coupon_info.items() if k != "original_url"}
        output.print_key_value(display_data, title="优惠券信息")
        return

    # 尝试解析为商品链接
    goods_info = parse_goods_url(url)
    if goods_info:
        output.success("这是商品链接")

        # 过滤掉 original_url 字段
        display_data = {k: v for k, v in goods_info.items() if k != "original_url"}
        output.print_key_value(display_data, title="商品信息")
        return

    output.error("无法识别的链接格式")
