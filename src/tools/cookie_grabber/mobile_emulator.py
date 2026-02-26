"""
移动端模拟器
使用Playwright模拟真实手机浏览器环境
"""

from typing import Dict, Any, Optional
from playwright.async_api import BrowserContext, Page
from loguru import logger


class MobileEmulator:
    """
    移动端浏览器模拟器

    模拟真实手机设备的User-Agent、视口、触摸事件等
    """

    # 常用移动设备配置
    DEVICES = {
        "iPhone_13_Pro": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 390, "height": 844},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
        },
        "iPhone_14": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 393, "height": 852},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
        },
        "Samsung_Galaxy_S23": {
            "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            "viewport": {"width": 360, "height": 800},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
        },
        "Xiaomi_13": {
            "user_agent": "Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.47.2560",
            "viewport": {"width": 393, "height": 851},
            "device_scale_factor": 2.75,
            "is_mobile": True,
            "has_touch": True,
        },
        "Huawei_Mate_60": {
            "user_agent": "Mozilla/5.0 (Linux; Android 14; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.0.0 Mobile Safari/537.36",
            "viewport": {"width": 393, "height": 851},
            "device_scale_factor": 2.75,
            "is_mobile": True,
            "has_touch": True,
        },
    }

    def __init__(self, device: str = "Xiaomi_13"):
        """
        初始化移动端模拟器

        Args:
            device: 设备名称，从DEVICES中选择
        """
        if device not in self.DEVICES:
            logger.warning(f"未知设备: {device}, 使用默认设备 Xiaomi_13")
            device = "Xiaomi_13"

        self.device_config = self.DEVICES[device]
        self.device_name = device

    def get_context_params(self) -> Dict[str, Any]:
        """获取浏览器上下文参数"""
        return {
            "user_agent": self.device_config["user_agent"],
            "viewport": self.device_config["viewport"],
            "device_scale_factor": self.device_config["device_scale_factor"],
            "is_mobile": self.device_config["is_mobile"],
            "has_touch": self.device_config["has_touch"],
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "geolocation": {"latitude": 31.2304, "longitude": 121.4737},  # 上海
            "permissions": ["geolocation"],
        }

    async def setup_context(self, context: BrowserContext):
        """
        设置浏览器上下文

        Args:
            context: Playwright浏览器上下文
        """
        # 添加初始化脚本，进一步模拟真实浏览器
        await context.add_init_script("""
            // 覆盖navigator检测
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Linux armv8l'
            });

            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });

            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });

            // 覆盖screen检测
            Object.defineProperty(screen, 'availWidth', {
                get: () => window.screen.width
            });

            Object.defineProperty(screen, 'availHeight', {
                get: () => window.screen.height
            });

            // 覆盖chrome检测（移动端没有chrome对象）
            if (!window.chrome) {
                window.chrome = {};
            }

            // 覆盖webdriver检测
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 添加移动端特有属性
            window.isMobile = true;

            // 模拟触摸事件支持
            document.createTouch = function() {
                return {
                    target: event.target,
                    identifier: 0,
                    pageX: event.pageX,
                    pageY: event.pageY,
                    screenX: event.screenX,
                    screenY: event.screenY,
                    clientX: event.clientX,
                    clientY: event.clientY
                };
            };
        """)

        logger.info(f"已设置移动端模拟器: {self.device_name}")

    def get_user_agent(self) -> str:
        """获取User-Agent"""
        return self.device_config["user_agent"]

    @staticmethod
    def list_devices() -> Dict[str, str]:
        """列出所有支持的设备"""
        return {
            name: config["user_agent"][:50] + "..."
            for name, config in MobileEmulator.DEVICES.items()
        }
