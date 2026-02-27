"""核心模块"""

# 配置管理
from .config import Config, get_config, reload_config

# 日志系统 - 新的统一日志框架（推荐）
from .logging_framework import (
    LogLevel,
    LogCategory,
    LogEvent,
    LogRecord,
    NotificationFilter,
    LoggingFramework,
    get_logging_framework,
)

# 通知系统
from .notifier import (
    NotificationLevel,
    NotificationMessage,
    NotificationManager,
    get_notification_manager,
)

# 调度器
from .scheduler import TaskScheduler, SchedulerState, get_scheduler

# ============ 向后兼容 ============
# 旧的日志接口（保留以兼容现有代码）
from .logger import Logger as OldLogger

__all__ = [
    # 配置
    "Config", "get_config", "reload_config",

    # 新日志框架（推荐使用）
    "LogLevel",
    "LogCategory",
    "LogEvent",
    "LogRecord",
    "NotificationFilter",
    "LoggingFramework",
    "get_logging_framework",

    # 通知系统
    "NotificationLevel",
    "NotificationMessage",
    "NotificationManager",
    "get_notification_manager",

    # 调度器
    "TaskScheduler", "SchedulerState", "get_scheduler",

    # 向后兼容
    "OldLogger",
]


# 便捷函数：获取日志实例
def get_logger():
    """
    获取日志实例

    返回新的统一日志框架实例
    """
    return get_logging_framework()
