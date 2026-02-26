"""
拼多多Cookie获取工具
使用浏览器自动化模拟移动端登录
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .mobile_emulator import MobileEmulator
from .cookie_parser import CookieParser

console = Console()


class PddCookieGrabber:
    """
    拼多多Cookie获取器

    功能:
    - 模拟移动端浏览器
    - 打开拼多多H5页面
    - 等待用户手动登录
    - 提取并保存Cookie
    """

    def __init__(
        self,
        device: str = "Xiaomi_13",
        headless: bool = False,
        save_dir: str = "config/cookies",
    ):
        """
        初始化Cookie获取器

        Args:
            device: 模拟的设备名称
            headless: 是否无头模式（登录时建议设为False）
            save_dir: Cookie保存目录
        """
        self.device = device
        self.headless = headless
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.emulator = MobileEmulator(device)
        self.cookie_parser = CookieParser()

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def start(self):
        """启动浏览器"""
        console.print("[cyan]启动移动端模拟浏览器...[/cyan]")

        self._playwright = await async_playwright().start()

        # 浏览器启动参数
        launch_options = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                # 模拟真实浏览器
                "--disable-infobars",
                "--window-size=393,851",
            ],
        }

        self._browser = await self._playwright.chromium.launch(**launch_options)

        # 创建移动端上下文
        context_params = self.emulator.get_context_params()
        self._context = await self._browser.new_context(**context_params)

        # 设置移动端模拟脚本
        await self.emulator.setup_context(self._context)

        # 创建页面
        self._page = await self._context.new_page()

        console.print(f"[green]✓[/green] 已启动 {self.device} 模拟器")
        console.print(f"  User-Agent: {self.emulator.get_user_agent()[:60]}...")

    async def close(self):
        """关闭浏览器"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

        console.print("[yellow]浏览器已关闭[/yellow]")

    async def navigate_to_login(self) -> bool:
        """
        导航到登录页面

        Returns:
            bool: 是否成功到达登录页面
        """
        login_url = "https://h5.pinduoduo.com/"

        console.print(f"\n[cyan]正在打开拼多多...[/cyan]")
        console.print(f"  URL: {login_url}")

        try:
            await self._page.goto(login_url, wait_until="networkidle", timeout=30000)
            console.print("[green]✓[/green] 页面加载完成")

            # 检查是否需要登录
            await asyncio.sleep(2)

            # 检查页面是否显示登录按钮
            try:
                # 常见的登录按钮/链接文本
                login_selectors = [
                    "text=登录",
                    "text=立即登录",
                    "text=请登录",
                    ".login-btn",
                    "[class*='login']",
                ]

                login_found = False
                for selector in login_selectors:
                    try:
                        element = await self._page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                login_found = True
                                console.print("[yellow]检测到未登录状态[/yellow]")
                                break
                    except:
                        continue

                if not login_found:
                    console.print("[green]可能已经登录[/green]")

            except Exception as e:
                console.print(f"[yellow]检查登录状态时出错: {e}[/yellow]")

            return True

        except Exception as e:
            console.print(f"[red]✗[/red] 打开页面失败: {e}")
            return False

    async def wait_for_login(self, timeout: int = 300) -> bool:
        """
        等待用户完成登录

        Args:
            timeout: 超时时间（秒）

        Returns:
            bool: 是否登录成功
        """
        console.print(Panel.fit(
            "[bold yellow]请在浏览器中完成登录[/bold yellow]\n"
            "1. 点击登录按钮\n"
            "2. 选择登录方式（手机号/微信/支付宝等）\n"
            "3. 完成登录验证\n"
            "4. 登录成功后程序会自动继续\n"
            f"等待时间: {timeout}秒",
            title="登录提示",
            border_style="yellow"
        ))

        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time

            if elapsed > timeout:
                console.print(f"\n[red]等待超时 ({timeout}秒)[/red]")
                return False

            # 显示倒计时
            remaining = int(timeout - elapsed)
            console.print(f"  等待登录中... 剩余 {remaining} 秒", end="\r")

            # 检查是否登录成功
            is_logged_in = await self._check_login_status()

            if is_logged_in:
                console.print("\n[green]✓[/green] 检测到登录成功！")
                return True

            await asyncio.sleep(2)

    async def _check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 方法1: 检查关键Cookie
            cookies = await self._context.cookies()
            cookie_names = [c["name"] for c in cookies]

            # 拼多多登录后的关键Cookie
            if "pdd_user_id" in cookie_names or "pdd_token" in cookie_names:
                return True

            # 方法2: 检查URL变化
            current_url = self._page.url
            if "login" not in current_url.lower() and "auth" not in current_url.lower():
                # 可能已经登录，再检查页面元素
                try:
                    # 检查是否有用户头像、昵称等登录后的元素
                    user_selectors = [
                        ".user-info",
                        ".avatar",
                        "[class*='user']",
                        "text=个人中心",
                        "text=我的",
                    ]
                    for selector in user_selectors:
                        element = await self._page.query_selector(selector)
                        if element:
                            if await element.is_visible():
                                return True
                except:
                    pass

            return False

        except Exception as e:
            return False

    async def extract_cookies(self) -> Dict[str, Any]:
        """
        提取Cookie

        Returns:
            Dict: 包含Cookie信息的字典
        """
        console.print("\n[cyan]正在提取Cookie...[/cyan]")

        cookies = await self._context.cookies()

        # 解析Cookie
        parsed_data = self.cookie_parser.parse_pdd_cookies(cookies)

        # 获取User-Agent
        user_agent = await self._page.evaluate("() => navigator.userAgent")

        # 获取页面信息
        page_info = {
            "url": self._page.url,
            "title": await self._page.title(),
        }

        result = {
            "cookies": cookies,
            "parsed": parsed_data,
            "user_agent": user_agent,
            "device": self.device,
            "page_info": page_info,
            "extracted_at": datetime.now().isoformat(),
        }

        return result

    async def get_account_info(self) -> Dict[str, Any]:
        """
        获取账号信息

        Returns:
            Dict: 账号信息
        """
        console.print("[cyan]正在获取账号信息...[/cyan]")

        account_info = {
            "username": "",
            "user_id": "",
            "nickname": "",
            "avatar": "",
            "mobile": "",
        }

        try:
            # 尝试从Cookie中获取
            cookies = await self._context.cookies()
            for cookie in cookies:
                if cookie["name"] in ["pdd_user_id", "customer_id", "user_id"]:
                    account_info["user_id"] = cookie["value"]

                # 获取用户名/手机号（可能需要解码）
                if cookie["name"] in ["user_name", "username", "mobile"]:
                    account_info["mobile"] = cookie["value"]

            # 尝试从页面获取
            try:
                # 用户昵称
                nickname = await self._page.evaluate("""
                    () => {
                        // 尝试多种选择器
                        const selectors = [
                            '.user-name',
                            '.nickname',
                            '[class*="nickname"]',
                            '[class*="userName"]'
                        ];
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el) return el.textContent || el.value;
                        }
                        return '';
                    }
                """)
                if nickname:
                    account_info["nickname"] = nickname

                # 头像
                avatar = await self._page.evaluate("""
                    () => {
                        const selectors = [
                            '.user-avatar img',
                            '.avatar img',
                            '[class*="avatar"] img'
                        ];
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el) return el.src;
                        }
                        return '';
                    }
                """)
                if avatar:
                    account_info["avatar"] = avatar

            except Exception as e:
                console.print(f"[yellow]获取页面账号信息失败: {e}[/yellow]")

        except Exception as e:
            console.print(f"[yellow]获取账号信息时出错: {e}[/yellow]")

        return account_info

    def save_cookies(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        保存Cookie到文件

        Args:
            data: Cookie数据
            filename: 文件名，不指定则自动生成

        Returns:
            str: 保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_cookies_{timestamp}.json"

        save_path = self.save_dir / filename

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        console.print(f"[green]✓[/green] Cookie已保存到: {save_path}")
        return str(save_path)

    def save_to_accounts_yaml(self, cookie_data: Dict[str, Any], account_info: Dict[str, Any]):
        """
        保存到accounts.yaml格式

        Args:
            cookie_data: Cookie数据
            account_info: 账号信息
        """
        # 构建Cookie字符串
        cookies = cookie_data["cookies"]
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

        # 构建账号配置
        account_config = {
            "platform": "pinduoduo",
            "username": account_info.get("mobile") or account_info.get("user_id") or "pinduoduo_user",
            "password": "",
            "cookies": cookie_str,
            "user_agent": cookie_data["user_agent"],
            "enabled": True,
            "metadata": {
                "user_id": account_info.get("user_id", ""),
                "nickname": account_info.get("nickname", ""),
                "device": cookie_data["device"],
                "saved_at": datetime.now().isoformat(),
            }
        }

        # 保存到文件
        accounts_file = self.save_dir.parent / "accounts.yaml"

        # 读取现有配置
        existing_accounts = []
        if accounts_file.exists():
            with open(accounts_file, "r", encoding="utf-8") as f:
                import yaml
                try:
                    data = yaml.safe_load(f)
                    existing_accounts = data.get("accounts", [])
                except:
                    pass

        # 检查是否已存在
        username = account_config["username"]
        updated = False
        for i, acc in enumerate(existing_accounts):
            if acc.get("platform") == "pinduoduo" and acc.get("username") == username:
                existing_accounts[i] = account_config
                updated = True
                break

        if not updated:
            existing_accounts.append(account_config)

        # 保存
        import yaml
        with open(accounts_file, "w", encoding="utf-8") as f:
            yaml.dump({"accounts": existing_accounts}, f, allow_unicode=True, default_flow_style=False)

        console.print(f"[green]✓[/green] 已更新配置文件: {accounts_file}")

    def display_cookie_summary(self, data: Dict[str, Any], account_info: Dict[str, Any]):
        """显示Cookie摘要信息"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]Cookie提取成功[/bold cyan]")
        console.print("="*60)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="green")

        # 账号信息
        table.add_row("用户ID", account_info.get("user_id", "N/A"))
        table.add_row("昵称", account_info.get("nickname", "N/A"))
        table.add_row("手机号", account_info.get("mobile", "N/A"))

        # Cookie信息
        parsed = data["parsed"]
        table.add_row("PDD Token", parsed.get("pdd_token", "N/A")[:30] + "..." if parsed.get("pdd_token") else "N/A")
        table.add_row("Customer ID", parsed.get("customer_id", "N/A"))

        # 其他信息
        table.add_row("设备", data["device"])
        table.add_row("提取时间", data["extracted_at"])

        console.print(table)
        console.print("="*60)

    async def run(self) -> Dict[str, Any]:
        """
        执行完整的Cookie获取流程

        Returns:
            Dict: Cookie数据
        """
        # 1. 启动浏览器
        await self.start()

        try:
            # 2. 导航到登录页面
            if not await self.navigate_to_login():
                raise Exception("无法打开登录页面")

            # 3. 等待用户登录
            if not await self.wait_for_login():
                raise Exception("登录超时")

            # 4. 提取Cookie
            cookie_data = await self.extract_cookies()

            # 5. 获取账号信息
            account_info = await self.get_account_info()

            # 6. 显示结果
            self.display_cookie_summary(cookie_data, account_info)

            # 7. 保存Cookie
            self.save_cookies(cookie_data)
            self.save_to_accounts_yaml(cookie_data, account_info)

            return cookie_data

        except Exception as e:
            console.print(f"\n[red]✗ Cookie获取失败: {e}[/red]")
            raise
