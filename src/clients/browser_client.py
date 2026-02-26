"""
浏览器自动化客户端
基于Playwright实现，支持反检测
"""

from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from loguru import logger

from ..core.config import get_config


class BrowserClient:
    """
    浏览器自动化客户端

    功能:
    - 反爬虫检测
    - Cookie管理
    - 截图/PDF
    - JavaScript执行
    """

    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_data_dir: Optional[str] = None,
    ):
        self.headless = headless or get_config().browser.headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.user_data_dir = user_data_dir

        self._playwright: Optional[Playwright] = None
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
        if self._browser is None:
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
                ],
            }

            # 代理配置
            if self.proxy:
                launch_options["proxy"] = {"server": self.proxy}
            elif get_config().proxy.enabled:
                launch_options["proxy"] = {"server": get_config().proxy.pool_url}

            self._browser = await self._playwright.chromium.launch(**launch_options)
            logger.info("浏览器已启动")

            # 创建上下文
            await self.create_context()

    async def create_context(self):
        """创建浏览器上下文"""
        if self._browser is None:
            await self.start()

        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "user_agent": self.user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        self._context = await self._browser.new_context(**context_options)

        # 添加初始化脚本（反检测）
        await self._context.add_init_script("""
            // 覆盖navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖chrome对象
            window.chrome = {
                runtime: {}
            };

            // 覆盖permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        logger.debug("浏览器上下文已创建")

    async def new_page(self) -> Page:
        """创建新页面"""
        if self._context is None:
            await self.create_context()

        self._page = await self._context.new_page()
        return self._page

    async def get_page(self) -> Page:
        """获取当前页面"""
        if self._page is None:
            return await self.new_page()
        return self._page

    async def goto(
        self,
        url: str,
        wait_until: str = "networkidle",
        timeout: int = None,
    ) -> Page:
        """导航到URL"""
        page = await self.get_page()
        timeout = timeout or get_config().browser.timeout

        await page.goto(url, wait_until=wait_until, timeout=timeout)
        logger.debug(f"导航到: {url}")
        return page

    async def screenshot(self, path: str = None, full_page: bool = True) -> bytes:
        """截图"""
        page = await self.get_page()
        return await page.screenshot(path=path, full_page=full_page)

    async def pdf(self, path: str = None) -> bytes:
        """导出PDF"""
        page = await self.get_page()
        return await page.pdf(path=path)

    async def execute_script(self, script: str) -> Any:
        """执行JavaScript"""
        page = await self.get_page()
        return await page.evaluate(script)

    async def get_cookies(self) -> List[Dict[str, Any]]:
        """获取所有Cookies"""
        if self._context is None:
            return []
        return await self._context.cookies()

    async def set_cookies(self, cookies: List[Dict[str, Any]]):
        """设置Cookies"""
        if self._context is None:
            await self.create_context()
        await self._context.add_cookies(cookies)

    async def close(self):
        """关闭浏览器"""
        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        logger.info("浏览器已关闭")

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 30000,
    ) -> Any:
        """等待选择器出现"""
        page = await self.get_page()
        return await page.wait_for_selector(selector, timeout=timeout)

    async def click(self, selector: str, **kwargs):
        """点击元素"""
        page = await self.get_page()
        await page.click(selector, **kwargs)
        logger.debug(f"点击元素: {selector}")

    async def fill(self, selector: str, value: str, **kwargs):
        """填写表单"""
        page = await self.get_page()
        await page.fill(selector, value, **kwargs)
        logger.debug(f"填写表单: {selector} = {value}")

    async def get_text(self, selector: str) -> str:
        """获取元素文本"""
        page = await self.get_page()
        element = await page.query_selector(selector)
        if element:
            return await element.inner_text()
        return ""

    async def get_attribute(self, selector: str, attribute: str) -> str:
        """获取元素属性"""
        page = await self.get_page()
        element = await page.query_selector(selector)
        if element:
            return await element.get_attribute(attribute)
        return ""
