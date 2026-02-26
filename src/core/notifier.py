"""
通知系统
支持多种通知渠道
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from loguru import logger

try:
    from notifiers import Notifier
    NOTIFIERS_AVAILABLE = True
except ImportError:
    NOTIFIERS_AVAILABLE = False

from ..core.config import get_config


@dataclass
class NotificationMessage:
    """通知消息"""
    title: str
    content: str
    level: str = "info"  # info, warning, error, success
    extra: Dict[str, Any] = None


class Notifier:
    """
    通知系统

    支持的通知渠道:
    - ServerChan (微信推送)
    - Telegram
    - 钉钉
    - 企业微信
    """

    def __init__(self):
        self.config = get_config().notification
        self._providers = self._init_providers()

    def _init_providers(self) -> Dict[str, Any]:
        """初始化通知提供者"""
        providers = {}

        if NOTIFIERS_AVAILABLE:
            # ServerChan
            if self.config.serverchan_key:
                providers["serverchan"] = Notifier("serverchan")
                providers["serverchan"].notify(
                    key=self.config.serverchan_key,
                )

            # Telegram
            if self.config.telegram_bot_token and self.config.telegram_chat_id:
                providers["telegram"] = Notifier("telegram")

            # 钉钉
            if self.config.dingtalk_webhook:
                providers["dingtalk"] = Notifier("dingtalk")

            # 企业微信
            if self.config.wechat_webhook:
                providers["wechat"] = Notifier("wechat")

        logger.info(f"已初始化通知提供者: {list(providers.keys())}")
        return providers

    async def send(
        self,
        title: str,
        content: str,
        level: str = "info",
        channels: Optional[List[str]] = None,
    ) -> bool:
        """
        发送通知

        Args:
            title: 标题
            content: 内容
            level: 级别 (info, warning, error, success)
            channels: 指定通知渠道，None表示所有

        Returns:
            bool: 是否发送成功
        """
        if not self._providers:
            logger.warning("没有可用的通知提供者")
            return False

        message = NotificationMessage(
            title=title,
            content=content,
            level=level,
        )

        # 确定要发送的渠道
        target_channels = channels or list(self._providers.keys())

        results = []
        for channel in target_channels:
            if channel in self._providers:
                result = await self._send_to_channel(channel, message)
                results.append(result)

        return any(results)

    async def _send_to_channel(self, channel: str, message: NotificationMessage) -> bool:
        """发送到指定渠道"""
        try:
            provider = self._providers[channel]

            if channel == "serverchan":
                return await self._send_serverchan(provider, message)
            elif channel == "telegram":
                return await self._send_telegram(provider, message)
            elif channel == "dingtalk":
                return await self._send_dingtalk(provider, message)
            elif channel == "wechat":
                return await self._send_wechat(provider, message)
            else:
                logger.warning(f"未知的通知渠道: {channel}")
                return False

        except Exception as e:
            logger.error(f"发送通知失败 ({channel}): {e}")
            return False

    async def _send_serverchan(self, provider, message: NotificationMessage) -> bool:
        """发送ServerChan通知"""
        try:
            result = provider.notify(
                key=self.config.serverchan_key,
                title=message.title,
                text=message.content,
            )
            return result
        except Exception as e:
            logger.error(f"ServerChan通知失败: {e}")
            return False

    async def _send_telegram(self, provider, message: NotificationMessage) -> bool:
        """发送Telegram通知"""
        try:
            # 构建消息
            text = f"*{message.title}*\n\n{message.content}"

            result = provider.notify(
                token=self.config.telegram_bot_token,
                chat_id=self.config.telegram_chat_id,
                message=text,
                parse_mode="Markdown",
            )
            return result
        except Exception as e:
            logger.error(f"Telegram通知失败: {e}")
            return False

    async def _send_dingtalk(self, provider, message: NotificationMessage) -> bool:
        """发送钉钉通知"""
        try:
            result = provider.notify(
                webhook=self.config.dingtalk_webhook,
                secret=self.config.dingtalk_secret,
                message={
                    "msgtype": "markdown",
                    "markdown": {
                        "title": message.title,
                        "text": f"## {message.title}\n\n{message.content}",
                    },
                },
            )
            return result
        except Exception as e:
            logger.error(f"钉钉通知失败: {e}")
            return False

    async def _send_wechat(self, provider, message: NotificationMessage) -> bool:
        """发送企业微信通知"""
        try:
            result = provider.notify(
                webhook=self.config.wechat_webhook,
                message={
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"## {message.title}\n\n{message.content}",
                    },
                },
            )
            return result
        except Exception as e:
            logger.error(f"企业微信通知失败: {e}")
            return False

    # 便捷方法
    async def success(self, title: str, content: str, **kwargs):
        """发送成功通知"""
        await self.send(title, content, level="success", **kwargs)

    async def error(self, title: str, content: str, **kwargs):
        """发送错误通知"""
        await self.send(title, content, level="error", **kwargs)

    async def warning(self, title: str, content: str, **kwargs):
        """发送警告通知"""
        await self.send(title, content, level="warning", **kwargs)

    async def info(self, title: str, content: str, **kwargs):
        """发送信息通知"""
        await self.send(title, content, level="info", **kwargs)


# 全局通知实例
_notifier: Optional[Notifier] = None


def get_notifier() -> Notifier:
    """获取全局通知实例"""
    global _notifier
    if _notifier is None:
        _notifier = Notifier()
    return _notifier
