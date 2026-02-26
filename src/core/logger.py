"""
日志系统模块
基于loguru实现结构化日志
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional

from .config import get_config


class Logger:
    """日志管理器"""

    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config = get_config()
        self._setup_logger()
        self._initialized = True

    def _setup_logger(self):
        """配置日志系统"""
        # 移除默认处理器
        logger.remove()

        # 控制台输出 - 带颜色和格式
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level=self.config.log.level,
            colorize=True,
        )

        # 文件输出 - 所有日志
        log_dir = Path(self.config.log.dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation=self.config.log.rotation,
            retention=self.config.log.retention,
            compression="zip",
            encoding="utf-8",
        )

        # 文件输出 - 错误日志
        logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation=self.config.log.rotation,
            retention=self.config.log.retention,
            compression="zip",
            encoding="utf-8",
        )

        # 文件输出 - 抢券成功日志
        logger.add(
            log_dir / "success_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}",
            level="SUCCESS",
            rotation=self.config.log.rotation,
            retention=self.config.log.retention,
            compression="zip",
            encoding="utf-8",
            filter=lambda record: record["level"].name == "SUCCESS"
        )

    @staticmethod
    def debug(msg: str, **kwargs):
        """调试日志"""
        logger.debug(msg, **kwargs)

    @staticmethod
    def info(msg: str, **kwargs):
        """信息日志"""
        logger.info(msg, **kwargs)

    @staticmethod
    def warning(msg: str, **kwargs):
        """警告日志"""
        logger.warning(msg, **kwargs)

    @staticmethod
    def error(msg: str, **kwargs):
        """错误日志"""
        logger.error(msg, **kwargs)

    @staticmethod
    def critical(msg: str, **kwargs):
        """严重错误日志"""
        logger.critical(msg, **kwargs)

    @staticmethod
    def success(msg: str, **kwargs):
        """成功日志"""
        logger.success(msg, **kwargs)

    @staticmethod
    def exception(msg: str, **kwargs):
        """异常日志"""
        logger.exception(msg, **kwargs)


# 便捷函数
def get_logger() -> Logger:
    """获取日志实例"""
    return Logger()


# 导出logger实例供直接使用
__logger_instance = None

def log():
    """获取日志实例（单例）"""
    global __logger_instance
    if __logger_instance is None:
        __logger_instance = get_logger()
    return __logger_instance
