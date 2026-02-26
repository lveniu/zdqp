"""
平台适配器基类
所有平台适配器都应继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from loguru import logger

from ..clients.http_client import HttpClient
from ..clients.browser_client import BrowserClient
from ..models.platform import PlatformModel, Account
from ..models.coupon import CouponModel
from ..models.task import TaskResult


class BaseAdapter(ABC):
    """
    平台适配器基类

    所有平台适配器必须实现的方法:
    - login: 登录
    - grab_coupon: 抢券
    - check_coupon: 检查优惠券状态
    """

    # 平台标识
    platform_name: str = ""
    platform_type: str = ""

    def __init__(self, account: Account, config: Dict[str, Any] = None):
        self.account = account
        self.config = config or {}

        # HTTP客户端
        self.http_client: Optional[HttpClient] = None

        # 浏览器客户端
        self.browser_client: Optional[BrowserClient] = None

        # 登录状态
        self._logged_in = False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()

    async def init(self):
        """初始化客户端"""
        # 初始化HTTP客户端
        self.http_client = HttpClient(
            base_url=self.config.get("base_url", ""),
            headers=self._build_headers(),
            cookies=self._parse_cookies(self.account.cookies),
        )
        await self.http_client.init_client()

        logger.debug(f"{self.platform_name} 适配器已初始化")

    async def cleanup(self):
        """清理资源"""
        if self.http_client:
            await self.http_client.close()
        if self.browser_client:
            await self.browser_client.close()

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "User-Agent": self.account.user_agent or self._get_default_user_agent(),
            "Referer": self.config.get("base_url", ""),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def _get_default_user_agent(self) -> str:
        """获取默认User-Agent"""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _parse_cookies(self, cookies_str: str) -> Dict[str, str]:
        """解析Cookie字符串为字典"""
        cookies = {}
        if cookies_str:
            for item in cookies_str.split(";"):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    cookies[key.strip()] = value.strip()
        return cookies

    @abstractmethod
    async def login(self) -> TaskResult:
        """
        登录平台

        Returns:
            TaskResult: 登录结果
        """
        pass

    @abstractmethod
    async def grab_coupon(self, coupon: CouponModel) -> TaskResult:
        """
        抢取优惠券

        Args:
            coupon: 优惠券信息

        Returns:
            TaskResult: 抢券结果
        """
        pass

    @abstractmethod
    async def check_coupon_status(self, coupon: CouponModel) -> Dict[str, Any]:
        """
        检查优惠券状态

        Args:
            coupon: 优惠券信息

        Returns:
            Dict: 包含优惠券状态信息
        """
        pass

    async def pre_grab_check(self, coupon: CouponModel) -> bool:
        """
        抢券前检查

        Args:
            coupon: 优惠券信息

        Returns:
            bool: 是否可以抢券
        """
        # 检查登录状态
        if not self._logged_in:
            result = await self.login()
            if not result.success:
                logger.error(f"登录失败: {result.message}")
                return False
            self._logged_in = True

        # 检查优惠券是否可抢
        if not coupon.is_available():
            logger.warning(f"优惠券不可抢: {coupon.id}")
            return False

        return True

    async def execute_grab(self, coupon: CouponModel) -> TaskResult:
        """
        执行抢券流程（包含前置检查）

        Args:
            coupon: 优惠券信息

        Returns:
            TaskResult: 抢券结果
        """
        try:
            # 前置检查
            if not await self.pre_grab_check(coupon):
                return TaskResult(
                    task_id=coupon.id,
                    success=False,
                    message="前置检查失败",
                    data={}
                )

            # 执行抢券
            result = await self.grab_coupon(coupon)

            return result

        except Exception as e:
            logger.exception(f"抢券异常: {e}")
            return TaskResult(
                task_id=coupon.id,
                success=False,
                message=f"抢券异常: {str(e)}",
                data={}
            )

    # 可选方法（子类可以重写）
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账号信息"""
        return {}

    async def get_my_coupons(self) -> List[CouponModel]:
        """获取我的优惠券列表"""
        return []

    @classmethod
    def from_config(cls, platform_config: Dict[str, Any], account: Account) -> "BaseAdapter":
        """
        从配置创建适配器实例

        Args:
            platform_config: 平台配置
            account: 账号信息

        Returns:
            BaseAdapter: 适配器实例
        """
        return cls(account, platform_config)
