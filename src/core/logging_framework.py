"""
统一日志框架层
实现分级日志、重要日志推送、按时间命名的日志文件
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from loguru import logger as loguru_logger

from .config import get_config
from .notifier import NotificationManager


class LogLevel(Enum):
    """日志级别枚举"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """日志分类枚举"""
    # 业务日志
    API = "api"           # API请求日志
    GRAB = "grab"         # 抢券日志
    CHECKIN = "checkin"   # 签到日志
    POINTS = "points"     # 积分日志

    # 系统日志
    SYSTEM = "system"     # 系统运行日志
    AUTH = "auth"         # 认证日志
    DATABASE = "database" # 数据库操作日志
    SCHEDULER = "scheduler" # 调度器日志

    # 平台日志
    PLATFORM_PDD = "pinduoduo"  # 拼多多平台日志
    PLATFORM_JD = "jd"          # 京东平台日志
    PLATFORM_TB = "taobao"      # 淘宝平台日志
    PLATFORM_MT = "meituan"     # 美团平台日志


class LogEvent(Enum):
    """重要日志事件（需要推送）"""
    # 抢券事件
    GRAB_SUCCESS = "grab_success"       # 抢券成功
    GRAB_FAILED = "grab_failed"         # 抢券失败
    GRAB_TIMEOUT = "grab_timeout"       # 抢券超时

    # 签到事件
    CHECKIN_SUCCESS = "checkin_success" # 签到成功
    CHECKIN_FAILED = "checkin_failed"   # 签到失败

    # 系统事件
    SYSTEM_ERROR = "system_error"       # 系统错误
    SYSTEM_START = "system_start"       # 系统启动
    SYSTEM_STOP = "system_stop"         # 系统停止

    # 认证事件
    LOGIN_SUCCESS = "login_success"     # 登录成功
    LOGIN_FAILED = "login_failed"       # 登录失败
    COOKIE_EXPIRED = "cookie_expired"   # Cookie过期

    # 积分事件
    POINTS_LOW = "points_low"           # 积分不足警告


class LogRecord:
    """日志记录数据类"""

    def __init__(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        event: Optional[LogEvent] = None
    ):
        self.level = level
        self.category = category
        self.message = message
        self.user_id = user_id
        self.extra = extra or {}
        self.event = event
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "category": self.category.value,
            "message": self.message,
            "user_id": self.user_id,
            "event": self.event.value if self.event else None,
            "extra": self.extra
        }

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class NotificationFilter:
    """通知过滤器 - 决定哪些日志需要推送"""

    # 默认需要推送的日志事件配置
    PUSH_EVENTS = {
        # 抢券相关 - 总是推送
        LogEvent.GRAB_SUCCESS: {"level": LogLevel.SUCCESS, "push": True},
        LogEvent.GRAB_FAILED: {"level": LogLevel.ERROR, "push": True},
        LogEvent.GRAB_TIMEOUT: {"level": LogLevel.WARNING, "push": True},

        # 签到相关 - 成功不推送，失败推送
        LogEvent.CHECKIN_SUCCESS: {"level": LogLevel.SUCCESS, "push": False},
        LogEvent.CHECKIN_FAILED: {"level": LogLevel.ERROR, "push": True},

        # 系统事件 - 严重错误推送
        LogEvent.SYSTEM_ERROR: {"level": LogLevel.CRITICAL, "push": True},
        LogEvent.SYSTEM_START: {"level": LogLevel.INFO, "push": False},
        LogEvent.SYSTEM_STOP: {"level": LogLevel.INFO, "push": False},

        # 认证事件
        LogEvent.LOGIN_SUCCESS: {"level": LogLevel.INFO, "push": False},
        LogEvent.LOGIN_FAILED: {"level": LogLevel.WARNING, "push": True},
        LogEvent.COOKIE_EXPIRED: {"level": LogLevel.ERROR, "push": True},

        # 积分事件
        LogEvent.POINTS_LOW: {"level": LogLevel.WARNING, "push": True},
    }

    @classmethod
    def should_push(cls, record: LogRecord) -> bool:
        """判断是否应该推送此日志"""
        if record.event is None:
            return False

        event_config = cls.PUSH_EVENTS.get(record.event)
        if event_config:
            return event_config.get("push", False)

        return False

    @classmethod
    def format_push_message(cls, record: LogRecord) -> str:
        """格式化推送消息"""
        event_emoji = {
            LogEvent.GRAB_SUCCESS: "🎉",
            LogEvent.GRAB_FAILED: "❌",
            LogEvent.GRAB_TIMEOUT: "⏰",
            LogEvent.CHECKIN_SUCCESS: "✅",
            LogEvent.CHECKIN_FAILED: "❌",
            LogEvent.SYSTEM_ERROR: "🚨",
            LogEvent.SYSTEM_START: "🚀",
            LogEvent.SYSTEM_STOP: "🛑",
            LogEvent.LOGIN_SUCCESS: "👤",
            LogEvent.LOGIN_FAILED: "🔒",
            LogEvent.COOKIE_EXPIRED: "🍪",
            LogEvent.POINTS_LOW: "💰",
        }

        emoji = event_emoji.get(record.event, "📌")

        parts = [
            f"{emoji} {record.event.value.replace('_', ' ').title()}",
        ]

        if record.user_id:
            parts.append(f"用户: {record.user_id}")

        parts.append(f"{record.message}")

        if record.extra:
            extra_str = ", ".join(f"{k}={v}" for k, v in record.extra.items())
            parts.append(f"详情: {extra_str}")

        return " | ".join(parts)


class LoggingFramework:
    """
    统一日志框架

    功能:
    1. 日志分级 (TRACE/DEBUG/INFO/SUCCESS/WARNING/ERROR/CRITICAL)
    2. 按级别和类型输出日志文件
    3. 按天自动切割日志文件（格式: level_年_月_日.log）
    4. 重要日志事件自动推送
    5. 结构化日志记录

    日志文件命名:
    - trace_2024_01_15.log
    - debug_2024_01_15.log
    - info_2024_01_15.log
    - success_2024_01_15.log
    - warning_2024_01_15.log
    - error_2024_01_15.log
    - critical_2024_01_15.log
    """
    _instance: Optional["LoggingFramework"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config = get_config()
        self.log_dir = Path(self.config.log.dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 通知管理器
        self.notifier = NotificationManager()

        # 推送回调列表（允许注册自定义推送处理器）
        self.push_callbacks: List[Callable[[LogRecord], None]] = []

        # 初始化日志系统
        self._setup_logger()
        self._initialized = True

    def _get_log_filename(self, level: str) -> str:
        """
        获取日志文件名
        格式: level_年_月_日.log
        例如: info_2024_01_15.log
        """
        return f"{level.lower()}_{{time:YYYY_MM_DD}}.log"

    def _setup_logger(self):
        """配置loguru日志系统"""
        # 移除默认处理器
        loguru_logger.remove()

        # 1. 控制台输出 - 带颜色
        loguru_logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>[{extra[category]}]</cyan> | "
                "{extra[user_id]: <10} | "
                "<level>{message}</level>"
            ),
            level=self.config.log.level,
            colorize=True,
        )

        # 2. 按级别分文件 - 格式: level_年_月_日.log

        # TRACE 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("TRACE"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
            level="TRACE",
            rotation="00:00",  # 每天午夜切割
            retention="7 days",  # TRACE 日志保留时间短
            compression="zip",
            encoding="utf-8",
            enqueue=True,  # 异步写入
        )

        # DEBUG 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("DEBUG"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
            level="DEBUG",
            rotation="00:00",
            retention="15 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )

        # INFO 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("INFO"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
            level="INFO",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )

        # SUCCESS 日志（成功操作单独记录）
        loguru_logger.add(
            self.log_dir / self._get_log_filename("SUCCESS"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
            level="SUCCESS",
            rotation="00:00",
            retention="90 days",  # 成功日志保留更久
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )

        # WARNING 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("WARNING"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
            level="WARNING",
            rotation="00:00",
            retention="60 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )

        # ERROR 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("ERROR"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}\n{exception}",
            level="ERROR",
            rotation="00:00",
            retention="90 days",  # 错误日志保留更久
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,  # 包含回溯信息
            diagnose=True,   # 包含诊断信息
        )

        # CRITICAL 日志
        loguru_logger.add(
            self.log_dir / self._get_log_filename("CRITICAL"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}\n{exception}",
            level="CRITICAL",
            rotation="00:00",
            retention="180 days",  # 严重错误日志保留最久
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        # 3. JSON格式日志 - 用于日志分析（可选）
        loguru_logger.add(
            self.log_dir / "json_{time:YYYY_MM_DD}.jsonl",
            format="{message}",
            level="INFO",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            serialize=True,  # JSON格式
        )

    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        event: Optional[LogEvent] = None
    ) -> LogRecord:
        """
        记录日志

        Args:
            level: 日志级别
            category: 日志分类
            message: 日志消息
            user_id: 用户ID
            extra: 额外信息
            event: 日志事件（用于推送）

        Returns:
            LogRecord: 日志记录对象
        """
        # 创建日志记录
        record = LogRecord(
            level=level,
            category=category,
            message=message,
            user_id=user_id,
            extra=extra,
            event=event
        )

        # 绑定上下文并输出
        loguru_logger.bind(
            category=category.value,
            user_id=user_id or "system"
        ).log(
            level.value,
            message,
            **(extra or {})
        )

        # 检查是否需要推送
        if NotificationFilter.should_push(record):
            self._push_notification(record)

        return record

    def _push_notification(self, record: LogRecord):
        """推送重要日志通知"""
        try:
            message = NotificationFilter.format_push_message(record)

            # 通过通知管理器发送
            # 根据日志级别决定通知方式
            if record.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                self.notifier.send_error(message)
            elif record.level == LogLevel.WARNING:
                self.notifier.send_warning(message)
            elif record.level == LogLevel.SUCCESS:
                self.notifier.send_success(message)
            else:
                self.notifier.send_info(message)

            # 调用自定义推送回调
            for callback in self.push_callbacks:
                try:
                    callback(record)
                except Exception as e:
                    loguru_logger.error(f"推送回调执行失败: {e}")

        except Exception as e:
            loguru_logger.error(f"发送通知失败: {e}")

    def register_push_callback(self, callback: Callable[[LogRecord], None]):
        """注册自定义推送回调"""
        self.push_callbacks.append(callback)

    # ============ 便捷方法 ============

    def trace(self, category: LogCategory, message: str, user_id: str = None, **kwargs):
        """跟踪日志"""
        return self.log(LogLevel.TRACE, category, message, user_id, kwargs)

    def debug(self, category: LogCategory, message: str, user_id: str = None, **kwargs):
        """调试日志"""
        return self.log(LogLevel.DEBUG, category, message, user_id, kwargs)

    def info(self, category: LogCategory, message: str, user_id: str = None, **kwargs):
        """信息日志"""
        return self.log(LogLevel.INFO, category, message, user_id, kwargs)

    def success(self, category: LogCategory, message: str, user_id: str = None, event: LogEvent = None, **kwargs):
        """成功日志"""
        return self.log(LogLevel.SUCCESS, category, message, user_id, kwargs, event)

    def warning(self, category: LogCategory, message: str, user_id: str = None, event: LogEvent = None, **kwargs):
        """警告日志"""
        return self.log(LogLevel.WARNING, category, message, user_id, kwargs, event)

    def error(self, category: LogCategory, message: str, user_id: str = None, event: LogEvent = None, **kwargs):
        """错误日志"""
        return self.log(LogLevel.ERROR, category, message, user_id, kwargs, event)

    def critical(self, category: LogCategory, message: str, user_id: str = None, event: LogEvent = None, **kwargs):
        """严重错误日志"""
        return self.log(LogLevel.CRITICAL, category, message, user_id, kwargs, event)

    # ============ 业务专用方法 ============

    def log_api_request(self, user_id: str, endpoint: str, method: str, **kwargs):
        """记录API请求"""
        return self.info(
            LogCategory.API,
            f"{method} {endpoint}",
            user_id,
            endpoint=endpoint,
            method=method,
            **kwargs
        )

    def log_grab_success(self, user_id: str, coupon_value: float, **kwargs):
        """记录抢券成功"""
        return self.success(
            LogCategory.GRAB,
            f"抢券成功，获得 {coupon_value} 元优惠券",
            user_id,
            event=LogEvent.GRAB_SUCCESS,
            coupon_value=coupon_value,
            **kwargs
        )

    def log_grab_failed(self, user_id: str, reason: str, **kwargs):
        """记录抢券失败"""
        return self.error(
            LogCategory.GRAB,
            f"抢券失败: {reason}",
            user_id,
            event=LogEvent.GRAB_FAILED,
            reason=reason,
            **kwargs
        )

    def log_checkin(self, user_id: str, points_gained: int, **kwargs):
        """记录签到"""
        return self.success(
            LogCategory.CHECKIN,
            f"签到成功，获得 {points_gained} 积分",
            user_id,
            event=LogEvent.CHECKIN_SUCCESS,
            points=points_gained,
            **kwargs
        )

    def log_cookie_expired(self, user_id: str, **kwargs):
        """记录Cookie过期"""
        return self.error(
            LogCategory.AUTH,
            "Cookie已过期，请重新获取",
            user_id,
            event=LogEvent.COOKIE_EXPIRED,
            **kwargs
        )

    def log_points_low(self, user_id: str, current_points: int, **kwargs):
        """记录积分不足"""
        return self.warning(
            LogCategory.POINTS,
            f"积分不足，当前: {current_points}",
            user_id,
            event=LogEvent.POINTS_LOW,
            points=current_points,
            **kwargs
        )


# 全局日志框架实例
_framework: Optional[LoggingFramework] = None


def get_logging_framework() -> LoggingFramework:
    """获取日志框架实例"""
    global _framework
    if _framework is None:
        _framework = LoggingFramework()
    return _framework


# 便捷访问
def get_logger() -> LoggingFramework:
    """获取日志实例（别名）"""
    return get_logging_framework()


# 导出
__all__ = [
    "LogLevel",
    "LogCategory",
    "LogEvent",
    "LogRecord",
    "NotificationFilter",
    "LoggingFramework",
    "get_logging_framework",
    "get_logger",
]
