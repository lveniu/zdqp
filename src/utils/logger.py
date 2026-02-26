"""
日志配置模块
提供统一的日志配置和管理
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class LoggerConfig:
    """日志配置类"""

    @staticmethod
    def setup_logger(
        name: str = "baibuti",
        level: int = logging.INFO,
        console: bool = True,
        file: bool = True
    ) -> logging.Logger:
        """
        配置日志记录器

        Args:
            name: 日志记录器名称
            level: 日志级别
            console: 是否输出到控制台
            file: 是否输出到文件

        Returns:
            配置好的Logger实例
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 清除现有处理器
        logger.handlers.clear()

        # 禁止传播到根日志记录器，避免重复日志
        logger.propagate = False

        # 日志格式
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # 文件处理器
        if file:
            # 主日志文件
            main_log_file = LOG_DIR / "api.log"
            file_handler = RotatingFileHandler(
                main_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # 错误日志文件
            error_log_file = LOG_DIR / "error.log"
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)

        return logger

    @staticmethod
    def get_logger(name: str = "baibuti") -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            Logger实例
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            return LoggerConfig.setup_logger(name)
        return logger


# 创建默认日志记录器
logger = LoggerConfig.setup_logger()

# 导出便捷函数
def get_logger(name: str = "baibuti") -> logging.Logger:
    """获取日志记录器"""
    return LoggerConfig.get_logger(name)


def log_request(user_id: str, action: str, details: dict = None):
    """
    记录API请求日志

    Args:
        user_id: 用户ID
        action: 操作类型
        details: 详细信息
    """
    logger = get_logger("api")
    logger.info(f"[API请求] 用户: {user_id}, 操作: {action}, 详情: {details or {}}")


def log_error(user_id: str, action: str, error: Exception):
    """
    记录错误日志

    Args:
        user_id: 用户ID
        action: 操作类型
        error: 异常对象
    """
    logger = get_logger("api")
    logger.error(f"[API错误] 用户: {user_id}, 操作: {action}, 错误: {str(error)}", exc_info=True)


def log_success(user_id: str, action: str, result: dict = None):
    """
    记录成功日志

    Args:
        user_id: 用户ID
        action: 操作类型
        result: 结果信息
    """
    logger = get_logger("api")
    logger.info(f"[API成功] 用户: {user_id}, 操作: {action}, 结果: {result or {}}")


__all__ = [
    "LoggerConfig",
    "logger",
    "get_logger",
    "log_request",
    "log_error",
    "log_success"
]
