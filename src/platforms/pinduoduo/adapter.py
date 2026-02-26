"""
拼多多平台适配器
支持准点抢券功能
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlencode, urlparse
import hashlib
from loguru import logger

from ..base_adapter import BaseAdapter
from ...models.task import TaskResult
from ...models.coupon import CouponModel
from ...models.platform import Account
from .constants import (
    PDD_BASE_URL,
    PDD_H5_URL,
    PDD_API_ENDPOINTS,
    PDD_HEADERS_TEMPLATE,
    PDD_RESPONSE_CODE,
    PDD_GRAB_CONFIG,
)
from .models import PddAccount, PddCouponModel, PddGrabResult
from .utils.signature import generate_signature
from .utils.parser import parse_coupon_url


class PinduoduoAdapter(BaseAdapter):
    """
    拼多多平台适配器

    功能:
    - Cookie登录
    - 准点抢券
    - 优惠券状态检查
    - 反爬虫对抗
    """

    platform_name = "pinduoduo"
    platform_type = "pinduoduo"

    def __init__(self, account: Account, config: Dict[str, Any] = None):
        super().__init__(account, config)

        # PDD专用账号信息
        self.pdd_account = self._init_pdd_account()

        # 抢券配置
        self.grab_config = PDD_GRAB_CONFIG

        # 请求计数器（用于限流）
        self._request_count = 0
        self._last_request_time = 0

    def _init_pdd_account(self) -> PddAccount:
        """初始化PDD账号信息"""
        # 解析Cookie获取token
        cookies = self._parse_cookies(self.account.cookies)
        # PDD实际使用的cookie名称是PDDAccessToken
        token = cookies.get("PDDAccessToken", "") or cookies.get("pdd_token", "")
        customer_id = cookies.get("pdd_user_id", "") or cookies.get("customer_id", "")

        return PddAccount(
            username=self.account.username,
            password=self.account.password,
            cookies=self.account.cookies,
            user_agent=self.account.user_agent,
            token=token,
            customer_id=customer_id,
        )

    def _build_headers(self) -> Dict[str, str]:
        """构建PDD专用请求头"""
        headers = PDD_HEADERS_TEMPLATE.copy()
        headers["User-Agent"] = self.account.user_agent or headers["User-Agent"]

        # 添加认证信息 - 使用完整的Cookie字符串
        if self.account.cookies:
            headers["Cookie"] = self.account.cookies

        return headers

    async def login(self) -> TaskResult:
        """
        登录拼多多

        使用Cookie登录，无需密码
        """
        try:
            logger.info(f"PDD登录: {self.account.username}")

            # 检查Cookie是否有效
            if not self.pdd_account.token and not self.account.cookies:
                return TaskResult(
                    task_id=f"login_{self.account.username}",
                    success=False,
                    message="Cookie为空，请先登录网页获取Cookie",
                    data={},
                )

            # 验证Cookie有效性
            is_valid = await self._verify_cookies()

            if is_valid:
                self._logged_in = True
                self.pdd_account.is_logged_in = True
                self.pdd_account.login_time = datetime.now()

                logger.success(f"PDD登录成功: {self.account.username}")

                return TaskResult(
                    task_id=f"login_{self.account.username}",
                    success=True,
                    message="登录成功",
                    data={
                        "username": self.account.username,
                        "login_time": self.pdd_account.login_time.isoformat(),
                    },
                )
            else:
                return TaskResult(
                    task_id=f"login_{self.account.username}",
                    success=False,
                    message="Cookie已失效，请重新获取",
                    data={},
                )

        except Exception as e:
            logger.exception(f"PDD登录异常: {e}")
            return TaskResult(
                task_id=f"login_{self.account.username}",
                success=False,
                message=f"登录异常: {str(e)}",
                data={},
            )

    async def _verify_cookies(self) -> bool:
        """验证Cookie是否有效"""
        try:
            # 通过访问需要登录的页面验证
            # 尝试多个可能的端点
            test_urls = [
                f"{PDD_H5_URL}/user",
                f"{PDD_BASE_URL}/user",
            ]

            headers = self._build_headers()

            for url in test_urls:
                try:
                    response = await self.http_client.get(url, headers=headers)

                    if response.status_code == 200:
                        content = response.text

                        # 检查是否包含登录用户的标识
                        # 注意: login关键词可能出现在前端代码中,所以只有在明确看到登录按钮时才算未登录
                        login_indicators = ["我的", "个人中心", "nickname", "avatar"]
                        not_login_indicators = ["立即登录", "请先登录", "登录注册"]

                        has_login = any(kw in content for kw in login_indicators)
                        has_not_login = any(kw in content for kw in not_login_indicators)

                        if has_login:
                            logger.info(f"Cookie验证成功: {url} - 找到登录标识")
                            return True
                        elif has_not_login:
                            logger.debug(f"Cookie可能失效: {url} - 显示未登录页面")
                            continue
                        else:
                            # 如果没有明确的登录或未登录标识,检查其他特征
                            # 检查是否包含用户ID相关的cookie响应
                            if "pdd_user_id" in self.account.cookies:
                                logger.info(f"Cookie验证通过: {url} - 包含用户ID")
                                return True

                except Exception as e:
                    logger.debug(f"测试端点失败: {url}, 错误: {e}")
                    continue

            # 如果所有端点都失败但有cookie,保守地认为可能有效
            if self.account.cookies and "PDDAccessToken" in self.account.cookies:
                logger.warning("Cookie验证无法确认,但包含token,将尝试使用")
                return True

            return False

        except Exception as e:
            logger.warning(f"验证Cookie异常: {e}")
            return False

    async def grab_coupon(self, coupon: CouponModel) -> TaskResult:
        """
        抢取优惠券

        Args:
            coupon: 优惠券信息

        Returns:
            TaskResult: 抢券结果
        """
        grab_start_time = time.time()

        try:
            logger.info(f"开始抢券: {coupon.id}, URL: {coupon.url}")

            # 解析优惠券URL
            coupon_info = parse_coupon_url(coupon.url)
            if not coupon_info:
                return TaskResult(
                    task_id=coupon.id,
                    success=False,
                    message="无效的优惠券链接",
                    data={},
                )

            # 构建抢券请求
            grab_data = await self._build_grab_request(coupon_info)

            # 发起抢券请求
            result = await self._send_grab_request(grab_data)

            # 记录结果
            elapsed_ms = (time.time() - grab_start_time) * 1000
            logger.info(f"抢券完成: {coupon.id}, 耗时: {elapsed_ms:.2f}ms, 结果: {result.success}")

            return TaskResult(
                task_id=coupon.id,
                success=result.success,
                message=result.message,
                data={
                    "coupon_id": coupon.id,
                    "elapsed_ms": elapsed_ms,
                    "coupon_sn": result.coupon_sn,
                    "valid_until": result.valid_until.isoformat() if result.valid_until else None,
                },
            )

        except Exception as e:
            logger.exception(f"抢券异常: {e}")
            return TaskResult(
                task_id=coupon.id,
                success=False,
                message=f"抢券异常: {str(e)}",
                data={},
            )

    async def _build_grab_request(self, coupon_info: Dict[str, Any]) -> Dict[str, Any]:
        """构建抢券请求参数"""
        # 基础参数
        params = {
            "coupon_id": coupon_info.get("coupon_id", ""),
            "coupon_type": coupon_info.get("coupon_type", "NORMAL"),
            "goods_id": coupon_info.get("goods_id", ""),
            "activity_id": coupon_info.get("activity_id", ""),
            "timestamp": int(time.time() * 1000),
        }

        # 添加签名
        params["sign"] = generate_signature(params, self.pdd_account.token)

        return params

    async def _send_grab_request(self, grab_data: Dict[str, Any]) -> PddGrabResult:
        """发送抢券请求"""
        request_time = datetime.now()

        try:
            # 构建URL
            url = f"{PDD_H5_URL}/coupon_grab"
            headers = self._build_headers()

            # 发送请求
            response = await self.http_client.post(
                url,
                json=grab_data,
                headers=headers,
                timeout=self.grab_config["request_timeout"],
            )

            response_time = datetime.now()
            elapsed_ms = (response_time - request_time).total_seconds() * 1000

            # 解析响应
            if response.status_code == 200:
                data = response.json()
                return self._parse_grab_response(data, request_time, response_time, elapsed_ms)
            else:
                return PddGrabResult(
                    success=False,
                    coupon_id=grab_data.get("coupon_id", ""),
                    message=f"HTTP错误: {response.status_code}",
                    code=response.status_code,
                    request_time=request_time,
                    response_time=response_time,
                    elapsed_ms=elapsed_ms,
                )

        except Exception as e:
            logger.exception(f"发送抢券请求异常: {e}")
            return PddGrabResult(
                success=False,
                coupon_id=grab_data.get("coupon_id", ""),
                message=f"请求异常: {str(e)}",
                code=-1,
                request_time=request_time,
                elapsed_ms=0,
            )

    def _parse_grab_response(
        self,
        data: Dict[str, Any],
        request_time: datetime,
        response_time: datetime,
        elapsed_ms: float,
    ) -> PddGrabResult:
        """解析抢券响应"""
        code = data.get("code", -1)
        message = data.get("msg", data.get("message", ""))

        # 判断是否成功
        success = code == PDD_RESPONSE_CODE["SUCCESS"]

        # 提取优惠券信息
        coupon_sn = data.get("coupon_sn", "")
        coupon_batch = data.get("coupon_batch", "")
        valid_until_str = data.get("valid_until", "")
        valid_until = None

        if valid_until_str:
            try:
                valid_until = datetime.fromisoformat(valid_until_str)
            except:
                pass

        return PddGrabResult(
            success=success,
            coupon_id=data.get("coupon_id", ""),
            message=message,
            code=code,
            coupon_sn=coupon_sn,
            coupon_batch=coupon_batch,
            valid_until=valid_until,
            request_time=request_time,
            response_time=response_time,
            elapsed_ms=elapsed_ms,
            raw_response=data,
        )

    async def check_coupon_status(self, coupon: CouponModel) -> Dict[str, Any]:
        """
        检查优惠券状态

        Args:
            coupon: 优惠券信息

        Returns:
            Dict: 优惠券状态信息
        """
        try:
            # 解析优惠券URL
            coupon_info = parse_coupon_url(coupon.url)
            if not coupon_info:
                return {
                    "valid": False,
                    "message": "无效的优惠券链接",
                }

            # 查询优惠券状态
            url = f"{PDD_H5_URL}/coupon_detail"
            headers = self._build_headers()

            params = {
                "coupon_id": coupon_info.get("coupon_id", ""),
                "timestamp": int(time.time() * 1000),
            }

            response = await self.http_client.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": True,
                    "status": data.get("status", "UNKNOWN"),
                    "remaining_quantity": data.get("remaining_quantity", 0),
                    "total_quantity": data.get("total_quantity", 0),
                    "can_grab": data.get("can_grab", False),
                }
            else:
                return {
                    "valid": False,
                    "message": f"查询失败: {response.status_code}",
                }

        except Exception as e:
            logger.exception(f"检查优惠券状态异常: {e}")
            return {
                "valid": False,
                "message": f"检查异常: {str(e)}",
            }

    async def precise_grab(
        self,
        coupon_url: str,
        grab_time: datetime,
       提前秒数: float = 0.1,
    ) -> PddGrabResult:
        """
        准点抢券

        Args:
            coupon_url: 优惠券链接
            grab_time: 目标抢券时间
            提前秒数: 提前发起请求的时间(秒)

        Returns:
            PddGrabResult: 抢券结果
        """
        logger.info(f"准点抢券: 目标时间 {grab_time}, 提前 {提前秒数} 秒")

        # 创建优惠券模型
        coupon = CouponModel(
            id=f"pdd_{int(time.time())}",
            name="PDD优惠券",
            platform="pinduoduo",
            url=coupon_url,
            start_time=grab_time,
            end_time=grab_time.replace(second=59),
        )

        # 计算等待时间
        now = datetime.now()
        target_timestamp = grab_time.timestamp()
        current_timestamp = now.timestamp()
        wait_seconds = target_timestamp - current_timestamp - 提前秒数

        if wait_seconds > 0:
            logger.info(f"等待抢券时间: {wait_seconds:.3f} 秒")
            await asyncio.sleep(wait_seconds)

        # 执行抢券
        result = await self.execute_grab(coupon)

        # 转换结果
        return PddGrabResult(
            success=result.success,
            coupon_id=coupon.id,
            message=result.message,
            code=0 if result.success else -1,
            request_time=datetime.now(),
        )
