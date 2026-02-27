"""
通知系统模块
支持多种通知渠道的统一推送接口
"""

import asyncio
import httpx
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from loguru import logger
from enum import Enum

from .config import get_config


class NotificationLevel(Enum):
    """通知级别"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotificationMessage:
    """通知消息数据类"""
    title: str
    content: str
    level: NotificationLevel = NotificationLevel.INFO
    extra: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class NotificationChannel:
    """通知渠道基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = self._check_enabled()

    def _check_enabled(self) -> bool:
        """检查渠道是否启用"""
        return False

    def send(self, message: NotificationMessage) -> bool:
        """发送通知（同步方法）"""
        return False

    async def send_async(self, message: NotificationMessage) -> bool:
        """发送通知（异步方法）"""
        return False


class ServerChanChannel(NotificationChannel):
    """ServerChan 微信推送通道"""

    def _check_enabled(self) -> bool:
        return bool(self.config.get("serverchan_key"))

    def send(self, message: NotificationMessage) -> bool:
        """同步发送"""
        try:
            api_url = f"https://sctapi.ftqq.com/{self.config['serverchan_key']}.send"

            data = {
                "title": message.title,
                "desp": message.content
            }

            with httpx.Client(timeout=10) as client:
                response = client.post(api_url, json=data)
                result = response.json()

                if result.get("code") == 0:
                    logger.debug(f"ServerChan通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"ServerChan通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"ServerChan通知异常: {e}")
            return False

    async def send_async(self, message: NotificationMessage) -> bool:
        """异步发送"""
        try:
            api_url = f"https://sctapi.ftqq.com/{self.config['serverchan_key']}.send"

            data = {
                "title": message.title,
                "desp": message.content
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(api_url, json=data)
                result = response.json()

                if result.get("code") == 0:
                    logger.debug(f"ServerChan通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"ServerChan通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"ServerChan通知异常: {e}")
            return False


class TelegramChannel(NotificationChannel):
    """Telegram 推送通道"""

    def _check_enabled(self) -> bool:
        return bool(
            self.config.get("telegram_bot_token") and
            self.config.get("telegram_chat_id")
        )

    def _send_request(self, message: NotificationMessage) -> bool:
        """发送Telegram请求"""
        try:
            api_url = f"https://api.telegram.org/bot{self.config['telegram_bot_token']}/sendMessage"

            # 格式化消息
            emoji_map = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.SUCCESS: "✅",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = emoji_map.get(message.level, "")
            text = f"{emoji} *{message.title}*\n\n{message.content}"

            data = {
                "chat_id": self.config["telegram_chat_id"],
                "text": text,
                "parse_mode": "Markdown"
            }

            with httpx.Client(timeout=10) as client:
                response = client.post(api_url, json=data)
                result = response.json()

                if result.get("ok"):
                    logger.debug(f"Telegram通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"Telegram通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"Telegram通知异常: {e}")
            return False

    def send(self, message: NotificationMessage) -> bool:
        return self._send_request(message)

    async def send_async(self, message: NotificationMessage) -> bool:
        try:
            api_url = f"https://api.telegram.org/bot{self.config['telegram_bot_token']}/sendMessage"

            emoji_map = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.SUCCESS: "✅",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = emoji_map.get(message.level, "")
            text = f"{emoji} *{message.title}*\n\n{message.content}"

            data = {
                "chat_id": self.config["telegram_chat_id"],
                "text": text,
                "parse_mode": "Markdown"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(api_url, json=data)
                result = response.json()

                if result.get("ok"):
                    logger.debug(f"Telegram通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"Telegram通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"Telegram通知异常: {e}")
            return False


class DingTalkChannel(NotificationChannel):
    """钉钉推送通道"""

    def _check_enabled(self) -> bool:
        return bool(self.config.get("dingtalk_webhook"))

    def send(self, message: NotificationMessage) -> bool:
        try:
            emoji_map = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.SUCCESS: "✅",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = emoji_map.get(message.level, "")

            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": message.title,
                    "text": f"{emoji} ## {message.title}\n\n{message.content}"
                }
            }

            # 如果配置了加签密钥
            if self.config.get("dingtalk_secret"):
                import time
                import hmac
                import hashlib
                import base64
                import urllib.parse

                secret = self.config["dingtalk_secret"]
                timestamp = str(round(time.time() * 1000))
                secret_enc = secret.encode('utf-8')
                string_to_sign = f'{timestamp}\n{secret}'
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

                data["markdown"]["text"] = f"{emoji} ## {message.title}\n\n{message.content}\n\n> 时间: {timestamp}"

            with httpx.Client(timeout=10) as client:
                response = client.post(self.config["dingtalk_webhook"], json=data)
                result = response.json()

                if result.get("errcode") == 0:
                    logger.debug(f"钉钉通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"钉钉通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"钉钉通知异常: {e}")
            return False

    async def send_async(self, message: NotificationMessage) -> bool:
        # 异步实现类似同步版本
        return self.send(message)


class WeChatChannel(NotificationChannel):
    """企业微信推送通道"""

    def _check_enabled(self) -> bool:
        return bool(self.config.get("wechat_webhook"))

    def send(self, message: NotificationMessage) -> bool:
        try:
            emoji_map = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.SUCCESS: "✅",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = emoji_map.get(message.level, "")

            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"{emoji} ## {message.title}\n\n{message.content}"
                }
            }

            with httpx.Client(timeout=10) as client:
                response = client.post(self.config["wechat_webhook"], json=data)
                result = response.json()

                if result.get("errcode") == 0:
                    logger.debug(f"企业微信通知发送成功: {message.title}")
                    return True
                else:
                    logger.warning(f"企业微信通知失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"企业微信通知异常: {e}")
            return False

    async def send_async(self, message: NotificationMessage) -> bool:
        return self.send(message)


class NotificationManager:
    """
    通知管理器

    支持的通知渠道:
    - ServerChan (微信推送)
    - Telegram
    - 钉钉
    - 企业微信
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化通知管理器

        Args:
            config: 通知配置，如果为None则从全局配置获取
        """
        if config is None:
            config_dict = get_config().notification.__dict__
        else:
            config_dict = config

        self.channels: List[NotificationChannel] = []
        self._init_channels(config_dict)

    def _init_channels(self, config: Dict[str, Any]):
        """初始化通知渠道"""
        # ServerChan
        channel = ServerChanChannel(config)
        if channel.enabled:
            self.channels.append(channel)

        # Telegram
        channel = TelegramChannel(config)
        if channel.enabled:
            self.channels.append(channel)

        # 钉钉
        channel = DingTalkChannel(config)
        if channel.enabled:
            self.channels.append(channel)

        # 企业微信
        channel = WeChatChannel(config)
        if channel.enabled:
            self.channels.append(channel)

        logger.info(f"已初始化通知渠道: {[c.__class__.__name__ for c in self.channels]}")

    def send(
        self,
        title: str,
        content: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[str]] = None
    ) -> bool:
        """
        发送通知（同步方法）

        Args:
            title: 通知标题
            content: 通知内容
            level: 通知级别
            channels: 指定发送的渠道类型列表，None表示发送到所有渠道

        Returns:
            bool: 是否至少有一个渠道发送成功
        """
        if not self.channels:
            logger.debug("没有可用的通知渠道")
            return False

        message = NotificationMessage(
            title=title,
            content=content,
            level=level
        )

        # 过滤渠道
        target_channels = self.channels
        if channels:
            channel_map = {
                "serverchan": ServerChanChannel,
                "telegram": TelegramChannel,
                "dingtalk": DingTalkChannel,
                "wechat": WeChatChannel,
            }
            target_channels = [
                c for c in self.channels
                if c.__class__.__name__ in [channel_map.get(ch).__name__ for ch in channels if ch in channel_map]
            ]

        # 发送到所有目标渠道
        success_count = 0
        for channel in target_channels:
            try:
                if channel.send(message):
                    success_count += 1
            except Exception as e:
                logger.error(f"发送通知失败 ({channel.__class__.__name__}): {e}")

        return success_count > 0

    async def send_async(
        self,
        title: str,
        content: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[str]] = None
    ) -> bool:
        """异步发送通知"""
        if not self.channels:
            logger.debug("没有可用的通知渠道")
            return False

        message = NotificationMessage(
            title=title,
            content=content,
            level=level
        )

        # 过滤渠道
        target_channels = self.channels
        if channels:
            channel_map = {
                "serverchan": ServerChanChannel,
                "telegram": TelegramChannel,
                "dingtalk": DingTalkChannel,
                "wechat": WeChatChannel,
            }
            target_channels = [
                c for c in self.channels
                if c.__class__.__name__ in [channel_map.get(ch).__name__ for ch in channels if ch in channel_map]
            ]

        # 并发发送
        tasks = [channel.send_async(message) for channel in target_channels]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        return success_count > 0

    # ============ 便捷方法 ============

    def send_info(self, content: str, title: str = "信息通知") -> bool:
        """发送信息通知"""
        return self.send(title, content, NotificationLevel.INFO)

    def send_success(self, content: str, title: str = "操作成功") -> bool:
        """发送成功通知"""
        return self.send(title, content, NotificationLevel.SUCCESS)

    def send_warning(self, content: str, title: str = "警告通知") -> bool:
        """发送警告通知"""
        return self.send(title, content, NotificationLevel.WARNING)

    def send_error(self, content: str, title: str = "错误通知") -> bool:
        """发送错误通知"""
        return self.send(title, content, NotificationLevel.ERROR)

    def send_critical(self, content: str, title: str = "严重错误") -> bool:
        """发送严重错误通知"""
        return self.send(title, content, NotificationLevel.CRITICAL)


# 全局通知管理器实例
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """获取全局通知管理器实例"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# 向后兼容的别名
NotificationManagerOld = NotificationManager
get_notifier = get_notification_manager  # 向后兼容别名


# 导出
__all__ = [
    "NotificationLevel",
    "NotificationMessage",
    "NotificationChannel",
    "ServerChanChannel",
    "TelegramChannel",
    "DingTalkChannel",
    "WeChatChannel",
    "NotificationManager",
    "get_notification_manager",
]
