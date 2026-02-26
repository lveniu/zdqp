"""
HTTP客户端实现
支持代理、会话管理、重试机制
"""

import asyncio
from typing import Optional, Dict, Any, Union
from fake_useragent import UserAgent
import httpx
from loguru import logger

from .base_client import BaseClient
from ..core.config import get_config


class HttpClient(BaseClient):
    """
    HTTP客户端

    功能:
    - 支持HTTP/2
    - 自动重试
    - 代理支持
    - Cookie/Session管理
    - 随机User-Agent
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        enable_retry: bool = True,
        max_retries: int = 3,
        random_ua: bool = True,
    ):
        super().__init__(base_url, timeout, proxy, headers)
        self.cookies = cookies or {}
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.random_ua = random_ua

        # User-Agent生成器
        self.ua_generator = UserAgent() if random_ua else None

        # HTTP客户端
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def init_client(self):
        """初始化HTTP客户端"""
        if self._client is None or self._client.is_closed:
            # 设置代理
            proxy = None
            if self.proxy:
                proxy = self.proxy
            elif get_config().proxy.enabled and get_config().proxy.pool_url:
                proxy = get_config().proxy.pool_url

            # 初始化客户端
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
                proxy=proxy,
                follow_redirects=True,
                http2=True,
            )

            logger.debug(f"HTTP客户端已初始化: {self.base_url}")

    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("HTTP客户端已关闭")

    def _get_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """获取请求头"""
        final_headers = self.headers.copy()
        if headers:
            final_headers.update(headers)

        # 随机User-Agent
        if self.random_ua and self.ua_generator:
            final_headers["User-Agent"] = self.ua_generator.random

        return final_headers

    async def _retry_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """带重试的请求"""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                return response
            except httpx.HTTPError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"请求失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"请求失败，已达最大重试次数: {e}")

        raise last_error

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """GET请求"""
        await self.init_client()
        full_url = self._build_url(url)
        final_headers = self._get_headers(headers)

        if self.enable_retry:
            return await self._retry_request("GET", full_url, params=params, headers=final_headers, **kwargs)

        return await self._client.get(full_url, params=params, headers=final_headers, **kwargs)

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """POST请求"""
        await self.init_client()
        full_url = self._build_url(url)
        final_headers = self._get_headers(headers)

        if self.enable_retry:
            return await self._retry_request(
                "POST", full_url, data=data, json=json, headers=final_headers, **kwargs
            )

        return await self._client.post(full_url, data=data, json=json, headers=final_headers, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """通用请求方法"""
        await self.init_client()
        full_url = self._build_url(url)
        final_headers = self._get_headers(kwargs.pop("headers", None))

        if self.enable_retry:
            return await self._retry_request(method, full_url, headers=final_headers, **kwargs)

        return await self._client.request(method, full_url, headers=final_headers, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求并返回JSON"""
        response = await self.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def post_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST请求并返回JSON"""
        response = await self.post(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def update_cookies(self, cookies: Dict[str, str]):
        """更新Cookies"""
        self.cookies.update(cookies)
        if self._client:
            self._client.cookies.update(cookies)

    def update_headers(self, headers: Dict[str, str]):
        """更新请求头"""
        self.headers.update(headers)
