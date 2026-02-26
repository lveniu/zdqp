"""
配置管理模块
支持YAML配置文件和环境变量
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import yaml
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    pool_url: str = ""
    api_key: str = ""
    max_retries: int = 3
    timeout: int = 10


@dataclass
class NotificationConfig:
    """通知配置"""
    serverchan_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    dingtalk_webhook: str = ""
    dingtalk_secret: str = ""
    wechat_webhook: str = ""


@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = True
    timeout: int = 30000
    user_data_dir: Optional[str] = None
    proxy: Optional[str] = None


@dataclass
class SchedulerConfig:
    """调度器配置"""
    max_workers: int = 10
    task_timeout: int = 60
    retry_times: int = 3
    retry_delay: int = 1


@dataclass
class CaptchaConfig:
    """验证码服务配置"""
    two_captcha_api_key: str = ""
    anti_captcha_api_key: str = ""
    timeout: int = 120


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    dir: str = "logs"
    rotation: str = "100 MB"
    retention: str = "30 days"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str = "sqlite:///./data/coupons.db"
    echo: bool = False


@dataclass
class Config:
    """主配置类"""

    # 应用配置
    app_name: str = "CouponGrabber"
    version: str = "0.1.0"
    env: str = "development"
    debug: bool = False

    # 子配置
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    captcha: CaptchaConfig = field(default_factory=CaptchaConfig)
    log: LogConfig = field(default_factory=LogConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    # 平台配置
    platforms: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        self._load_from_env()

    @classmethod
    def from_yaml(cls, config_path: str = "config/config.yaml") -> "Config":
        """从YAML文件加载配置"""
        config_file = Path(config_path)

        if not config_file.exists():
            print(f"配置文件不存在: {config_path}, 使用默认配置")
            return cls()

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """从字典创建配置对象"""
        config = cls()

        # 应用配置
        if "app" in data:
            app = data["app"]
            config.env = app.get("env", config.env)
            config.debug = app.get("debug", config.debug)

        # 代理配置
        if "proxy" in data:
            proxy = data["proxy"]
            config.proxy = ProxyConfig(
                enabled=proxy.get("enabled", False),
                pool_url=proxy.get("pool_url", ""),
                api_key=proxy.get("api_key", ""),
                max_retries=proxy.get("max_retries", 3),
                timeout=proxy.get("timeout", 10),
            )

        # 通知配置
        if "notification" in data:
            notification = data["notification"]
            config.notification = NotificationConfig(**notification)

        # 浏览器配置
        if "browser" in data:
            browser = data["browser"]
            config.browser = BrowserConfig(**browser)

        # 调度器配置
        if "scheduler" in data:
            scheduler = data["scheduler"]
            config.scheduler = SchedulerConfig(**scheduler)

        # 验证码配置
        if "captcha" in data:
            captcha = data["captcha"]
            config.captcha = CaptchaConfig(**captcha)

        # 日志配置
        if "log" in data:
            log = data["log"]
            config.log = LogConfig(**log)

        # 数据库配置
        if "database" in data:
            database = data["database"]
            config.database = DatabaseConfig(**database)

        # 平台配置
        if "platforms" in data:
            config.platforms = data["platforms"]

        return config

    def _load_from_env(self):
        """从环境变量加载配置"""
        self.env = os.getenv("APP_ENV", self.env)
        self.debug = os.getenv("APP_DEBUG", "false").lower() == "true"

        # 日志
        self.log.level = os.getenv("LOG_LEVEL", self.log.level)

        # 数据库
        self.database.url = os.getenv("DATABASE_URL", self.database.url)

        # 代理
        self.proxy.enabled = os.getenv("PROXY_ENABLED", "false").lower() == "true"
        self.proxy.pool_url = os.getenv("PROXY_POOL_URL", self.proxy.pool_url)
        self.proxy.api_key = os.getenv("PROXY_API_KEY", self.proxy.api_key)

        # 通知
        self.notification.serverchan_key = os.getenv("NOTIFY_SERVERCHAN_KEY", "")
        self.notification.telegram_bot_token = os.getenv("NOTIFY_TELEGRAM_BOT_TOKEN", "")
        self.notification.telegram_chat_id = os.getenv("NOTIFY_TELEGRAM_CHAT_ID", "")
        self.notification.dingtalk_webhook = os.getenv("NOTIFY_DINGTALK_WEBHOOK", "")
        self.notification.dingtalk_secret = os.getenv("NOTIFY_DINGTALK_SECRET", "")
        self.notification.wechat_webhook = os.getenv("NOTIFY_WECHAT_WEBHOOK", "")

        # 浏览器
        self.browser.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.browser.timeout = int(os.getenv("BROWSER_TIMEOUT", str(self.browser.timeout)))

        # 验证码
        self.captcha.two_captcha_api_key = os.getenv("CAPTCHA_2CAPTCHA_API_KEY", "")
        self.captcha.anti_captcha_api_key = os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY", "")


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config.from_yaml()
    return _config


def reload_config(config_path: str = "config/config.yaml") -> Config:
    """重新加载配置"""
    global _config
    _config = Config.from_yaml(config_path)
    return _config
