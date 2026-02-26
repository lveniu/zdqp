"""
基础客户端抽象类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import httpx


class BaseClient(ABC):
    """客户端基类"""

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers or {}
        self._setup_default_headers()

    def _setup_default_headers(self):
        """设置默认请求头"""
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

    def _build_url(self, path: str) -> str:
        """构建完整URL"""
        if path.startswith("http"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    @abstractmethod
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """GET请求"""
        pass

    @abstractmethod
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """POST请求"""
        pass

    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """通用请求方法"""
        pass
