"""
Loguru 与 Rich 集成的日志系统
结合 Loguru 的强大日志功能和 Rich 的美观输出
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager

from loguru import logger as loguru_logger
from rich.console import Console
from rich.text import Text

from .rich_output import RichOutput, Icons, get_output
from .config import get_config


class RichLogHandler:
    """
    Rich 格式的日志处理器

    将 Loguru 日志转换为 Rich 彩色输出
    """

    # 日志级别到 Rich 样式的映射
    LEVEL_STYLES = {
        "TRACE": "dim white",
        "DEBUG": "dim cyan",
        "INFO": "bold blue",
        "SUCCESS": "bold green",
        "WARNING": "bold yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }

    # 日志级别图标映射
    LEVEL_ICONS = {
        "TRACE": "·",
        "DEBUG": "⚡",
        "INFO": Icons.INFO,
        "SUCCESS": Icons.SUCCESS,
        "WARNING": Icons.WARNING,
        "ERROR": Icons.ERROR,
        "CRITICAL": Icons.CRITICAL,
    }

    def __init__(self, console: Optional[Console] = None, level: str = "INFO"):
        """
        初始化 Rich 日志处理器

        Args:
            console: Rich Console 实例
            level: 最低日志级别
        """
        self.console = console or get_output().console
        self.level = level

    def write(self, message: str) -> None:
        """
        写入日志消息

        Args:
            message: 格式化后的日志消息
        """
        self.console.print(message, highlight=False)

    def format_message(
        self,
        level: str,
        message: str,
        category: str = "",
        user_id: str = "",
        timestamp: str = "",
        **extra
    ) -> str:
        """
        格式化日志消息为 Rich 格式

        Args:
            level: 日志级别
            message: 日志消息
            category: 日志分类
            user_id: 用户ID
            timestamp: 时间戳
            **extra: 额外信息

        Returns:
            格式化后的消息字符串
        """
        icon = self.LEVEL_ICONS.get(level, "•")
        style = self.LEVEL_STYLES.get(level, "")

        parts = []

        # 时间戳
        if timestamp:
            parts.append(f"<dim>{timestamp}</dim>")

        # 级别和图标
        parts.append(f"[{style}]{icon} {level}[/{style}]")

        # 分类
        if category:
            parts.append(f"<cyan>[[{category}]]</cyan>")

        # 用户ID
        if user_id:
            parts.append(f"<magenta>[{user_id}]</magenta>")

        # 消息
        parts.append(f"[{style}]{message}[/{style}]")

        return " | ".join(parts)


class RichLogger:
    """
    Rich 日志管理器

    功能:
    - 集成 Loguru 和 Rich
    - 美化的控制台输出
    - 文件日志存储
    - 结构化日志记录
    - 日志级别控制
    """

    def __init__(
        self,
        name: str = "app",
        log_dir: str = "logs",
        level: str = "INFO",
        rotation: str = "100 MB",
        retention: str = "30 days",
        console_output: bool = True,
        file_output: bool = True,
        json_output: bool = False,
    ):
        """
        初始化 Rich 日志器

        Args:
            name: 日志器名称
            log_dir: 日志目录
            level: 日志级别
            rotation: 日志轮转大小
            retention: 日志保留时间
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            json_output: 是否输出 JSON 格式
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.rich_output = get_output()
        self.level = level

        # 移除默认处理器
        loguru_logger.remove()

        # 配置日志系统
        self._setup_logger(
            console_output=console_output,
            file_output=file_output,
            json_output=json_output,
            rotation=rotation,
            retention=retention,
        )

    def _setup_logger(
        self,
        console_output: bool,
        file_output: bool,
        json_output: bool,
        rotation: str,
        retention: str,
    ):
        """配置 Loguru 日志系统"""

        # 1. Rich 格式的控制台输出
        if console_output:
            loguru_logger.add(
                sys.stderr,
                format=(
                    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>[{extra[category]}]</cyan> | "
                    "{extra[user_id]: <10} | "
                    "<level>{message}</level>"
                ),
                level=self.level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )

        # 2. 文件输出 - 普通日志
        if file_output:
            # 主日志文件
            loguru_logger.add(
                self.log_dir / f"{self.name}_{{time:YYYY-MM-DD}}.log",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
                level="INFO",
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                enqueue=True,
            )

            # 错误日志文件
            loguru_logger.add(
                self.log_dir / f"{self.name}_error_{{time:YYYY-MM-DD}}.log",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}\n{exception}",
                level="ERROR",
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                backtrace=True,
                diagnose=True,
            )

            # 成功日志文件
            loguru_logger.add(
                self.log_dir / f"{self.name}_success_{{time:YYYY-MM-DD}}.log",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[category]}] | {extra[user_id]} | {message}",
                level="SUCCESS",
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                enqueue=True,
            )

        # 3. JSON 格式日志 - 用于日志分析
        if json_output:
            loguru_logger.add(
                self.log_dir / f"{self.name}_{{time:YYYY-MM-DD}}.jsonl",
                format="{message}",
                level="INFO",
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                serialize=True,
            )

    # ==================== 绑定上下文 ====================

    def bind(self, **kwargs):
        """
        绑定上下文变量

        用法:
            logger.bind(user_id="123", category="api").info("处理请求")
        """
        return loguru_logger.bind(**kwargs)

    # ==================== 日志方法 ====================

    def trace(self, message: str, **kwargs):
        """跟踪日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).trace(message)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).debug(message)

    def info(self, message: str, **kwargs):
        """信息日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).info(message)

    def success(self, message: str, **kwargs):
        """成功日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).success(message)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).warning(message)

    def error(self, message: str, **kwargs):
        """错误日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).error(message)

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        loguru_logger.opt(depth=1).bind(**kwargs).critical(message)

    def exception(self, message: str, **kwargs):
        """异常日志（包含堆栈）"""
        loguru_logger.opt(depth=1, exception=True).bind(**kwargs).error(message)

    # ==================== 便捷方法 ====================

    def with_context(self, category: str = "", user_id: str = ""):
        """
        创建带上下文的日志器

        Args:
            category: 日志分类
            user_id: 用户ID

        Returns:
            绑定了上下文的日志器
        """
        return loguru_logger.bind(category=category, user_id=user_id)

    @contextmanager
    def context(self, **kwargs):
        """
        上下文管理器，临时绑定变量

        用法:
            with logger.context(user_id="123"):
                logger.info("这条日志会包含 user_id")
        """
        logger = loguru_logger.bind(**kwargs)
        try:
            yield logger
        finally:
            pass

    # ==================== 标准库兼容 ====================

    def getLogger(self, name: str) -> logging.Logger:
        """
        获取标准库风格的 Logger

        用于兼容使用标准库 logging 的代码
        """
        # 创建 InterceptHandler 来拦截标准库日志
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                # 获取对应的 Loguru 级别
                try:
                    level = loguru_logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # 查找调用者
                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage()
                )

        # 配置标准库日志
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

        return logging.getLogger(name)


# ==================== 全局实例 ====================

_global_logger: Optional[RichLogger] = None


def get_rich_logger(
    name: str = "app",
    **kwargs
) -> RichLogger:
    """
    获取全局 Rich 日志器实例

    Args:
        name: 日志器名称
        **kwargs: 其他配置参数

    Returns:
        RichLogger 实例
    """
    global _global_logger

    if _global_logger is None:
        # 尝试从配置获取
        try:
            config = get_config()
            _global_logger = RichLogger(
                name=name,
                log_dir=config.log.dir,
                level=config.log.level,
                rotation=config.log.rotation,
                retention=config.log.retention,
            )
        except Exception:
            # 使用默认配置
            _global_logger = RichLogger(name=name, **kwargs)

    return _global_logger


def setup_rich_logging(
    name: str = "app",
    level: str = "INFO",
    log_dir: str = "logs",
    **kwargs
) -> RichLogger:
    """
    设置 Rich 日志系统

    Args:
        name: 日志器名称
        level: 日志级别
        log_dir: 日志目录
        **kwargs: 其他配置

    Returns:
        RichLogger 实例
    """
    global _global_logger
    _global_logger = RichLogger(
        name=name,
        log_dir=log_dir,
        level=level,
        **kwargs
    )
    return _global_logger


# ==================== 便捷装饰器 ====================

def log_function_call(category: str = "function"):
    """
    装饰器：记录函数调用

    用法:
        @log_function_call(category="api")
        def my_function():
            pass
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            logger = get_rich_logger()
            func_name = func.__name__

            logger.bind(category=category).debug(f"调用函数: {func_name}")

            try:
                result = func(*args, **kwargs)
                logger.bind(category=category).success(f"函数完成: {func_name}")
                return result
            except Exception as e:
                logger.bind(category=category).error(f"函数失败: {func_name} - {e}")
                raise

        return wrapper
    return decorator


def log_execution_time(category: str = "performance"):
    """
    装饰器：记录函数执行时间

    用法:
        @log_execution_time(category="performance")
        def slow_function():
            time.sleep(1)
    """
    import time

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            logger = get_rich_logger()
            func_name = func.__name__

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                logger.bind(category=category).info(
                    f"{func_name} 执行时间: {elapsed:.3f}秒"
                )

        return wrapper
    return decorator


# ==================== 导出 ====================

__all__ = [
    "RichLogger",
    "RichLogHandler",
    "get_rich_logger",
    "setup_rich_logging",
    "log_function_call",
    "log_execution_time",
]
