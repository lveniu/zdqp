"""
测试调度器功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.core.scheduler_models import (
    SchedulerConfig, ScheduleConfig, ConditionConfig,
    ConditionType, LimitType, TaskPriority, RetryConfig
)
from src.core.condition_checker import ConditionChecker, check_conditions_for_schedule
from src.core.task_executor import TaskExecutor, get_task_executor
from src.core.schedule_manager import ScheduleManager, get_schedule_manager


def test_config_loading():
    """测试配置加载"""
    logger.info("=== 测试配置加载 ===")

    config_path = project_root / "config" / "scheduler.yaml"

    try:
        config = SchedulerConfig.load_from_file(str(config_path))

        logger.info(f"✓ 配置加载成功")
        logger.info(f"  - 时区: {config.global_config.timezone}")
        logger.info(f"  - 调度器启用: {config.global_config.enabled}")
        logger.info(f"  - 最大并发: {config.global_config.max_concurrent_tasks}")
        logger.info(f"  - 总任务数: {len(config.schedules)}")
        logger.info(f"  - 启用任务数: {len(config.get_enabled_schedules())}")

        # 打印每个调度任务
        for schedule in config.schedules:
            status = "启用" if schedule.enabled else "禁用"
            logger.info(f"  - [{status}] {schedule.name}: {schedule.times}")

        return config

    except Exception as e:
        logger.error(f"✗ 配置加载失败: {e}")
        return None


def test_condition_checker():
    """测试条件检查器"""
    logger.info("\n=== 测试条件检查器 ===")

    # 创建测试条件
    conditions = [
        ConditionConfig(
            type=ConditionType.DAILY_LIMIT,
            limit_type=LimitType.GRAB_SUCCESS,
            max_count=0
        ),
        ConditionConfig(
            type=ConditionType.WEEKLY_LIMIT,
            limit_type=LimitType.POINTS_GRAB,
            max_count=2
        )
    ]

    # 使用测试用户名
    test_username = "test_user_12345"

    try:
        checker = ConditionChecker(test_username)

        # 测试单个条件检查
        for condition in conditions:
            passed, message = asyncio.run(checker.check_condition(condition))
            status = "✓" if passed else "✗"
            logger.info(f"{status} {condition.type.value} ({condition.limit_type.value}): {message}")

        # 测试所有条件检查
        passed, message = asyncio.run(checker.check_all(conditions))
        status = "✓" if passed else "✗"
        logger.info(f"{status} 所有条件检查: {message}")

    except Exception as e:
        logger.error(f"✗ 条件检查失败: {e}")


def test_task_executor():
    """测试任务执行器"""
    logger.info("\n=== 测试任务执行器 ===")

    executor = get_task_executor()

    # 列出已注册的处理器
    logger.info("已注册的任务处理器:")
    for task_type in executor._task_handlers.keys():
        logger.info(f"  - {task_type}")


def test_schedule_manager():
    """测试定时任务管理器"""
    logger.info("\n=== 测试定时任务管理器 ===")

    manager = get_schedule_manager()

    # 测试配置加载
    if manager.load_config():
        logger.info("✓ 配置加载成功")

        # 获取统计信息
        stats = manager.get_stats()
        logger.info(f"  - 调度器启用: {stats['config_loaded']}")
        logger.info(f"  - 总任务数: {stats['total_schedules']}")
        logger.info(f"  - 启用任务数: {stats['enabled_schedules']}")

        # 列出所有调度任务
        logger.info("\n调度任务列表:")
        for schedule in manager.get_schedules():
            status = "启用" if schedule.enabled else "禁用"
            logger.info(f"  - [{status}] {schedule.name}")
            logger.info(f"    时间: {', '.join(schedule.times)}")
            logger.info(f"    条件数: {len(schedule.conditions)}")
    else:
        logger.error("✗ 配置加载失败")


async def test_schedule_execute_immediate():
    """测试立即执行调度任务"""
    logger.info("\n=== 测试立即执行调度任务 ===")

    manager = get_schedule_manager()

    if not manager.load_config():
        logger.error("✗ 配置加载失败")
        return

    # 获取百亿补贴签到任务
    schedule = manager.get_schedule_by_name("百亿补贴每日签到")

    if not schedule:
        logger.error("✗ 未找到调度任务: 百亿补贴每日签到")
        return

    logger.info(f"执行任务: {schedule.name}")

    # 使用测试用户名
    test_username = "test_user_12345"

    # 执行任务
    result = await manager._execute_for_user(
        schedule,
        test_username,
        datetime.now().strftime("%H:%M")
    )

    if result.success:
        logger.success(f"✓ 任务执行成功: {result.message}")
    else:
        if result.data.get("skipped"):
            logger.info(f"⊘ 任务跳过: {result.message}")
        else:
            logger.warning(f"✗ 任务执行失败: {result.message}")


def main():
    """主测试函数"""
    logger.info("开始测试调度器功能...")

    # 测试配置加载
    config = test_config_loading()
    if not config:
        logger.error("配置加载失败，终止测试")
        return

    # 测试条件检查器
    test_condition_checker()

    # 测试任务执行器
    test_task_executor()

    # 测试定时任务管理器
    test_schedule_manager()

    # 询问是否测试立即执行
    logger.info("\n是否测试立即执行任务? (需要有效的 Cookie)")
    logger.info("如需测试，请确保已配置有效的拼多多 Cookie")

    # 这里不立即执行，因为需要有效的 Cookie
    # asyncio.run(test_schedule_execute_immediate())

    logger.info("\n=== 测试完成 ===")


if __name__ == "__main__":
    from datetime import datetime
    main()
