"""
日志框架使用示例
展示如何使用统一日志框架
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_framework import (
    get_logger,
    LogLevel,
    LogCategory,
    LogEvent,
)


def demo_basic_logging():
    """演示基础日志功能"""
    print("\n=== 1. 基础日志功能 ===\n")

    logger = get_logger()

    # 不同级别的日志
    logger.debug(LogCategory.SYSTEM, "这是一条调试日志", user_id="demo")
    logger.info(LogCategory.API, "API请求开始", user_id="user001", endpoint="/api/status")
    logger.success(LogCategory.GRAB, "抢券成功！", user_id="user001", coupon_value=5)
    logger.warning(LogCategory.POINTS, "积分不足警告", user_id="user001", points=50)
    logger.error(LogCategory.DATABASE, "数据库连接失败", user_id="system")


def demo_categorized_logging():
    """演示分类日志"""
    print("\n=== 2. 分类日志功能 ===\n")

    logger = get_logger()

    # API 日志
    logger.log(
        level=LogLevel.INFO,
        category=LogCategory.API,
        message="POST /api/grab - 抢券请求",
        user_id="user001",
        extra={"coupon_id": "12345", "timestamp": "2024-01-01 10:00:00"}
    )

    # 抢券日志
    logger.log(
        level=LogLevel.SUCCESS,
        category=LogCategory.GRAB,
        message="成功抢到5元优惠券",
        user_id="user001",
        event=LogEvent.GRAB_SUCCESS,
        extra={"coupon_value": 5, "points_used": 100}
    )

    # 签到日志
    logger.log(
        level=LogLevel.SUCCESS,
        category=LogCategory.CHECKIN,
        message="每日签到成功",
        user_id="user001",
        event=LogEvent.CHECKIN_SUCCESS,
        extra={"points_gained": 10, "total_points": 1000}
    )


def demo_event_logging():
    """演示事件日志（会触发推送）"""
    print("\n=== 3. 事件日志（推送功能） ===\n")

    logger = get_logger()

    # 抢券成功事件 - 会触发推送
    logger.log(
        level=LogLevel.SUCCESS,
        category=LogCategory.GRAB,
        message="恭喜！成功抢到5元无门槛优惠券",
        user_id="user001",
        event=LogEvent.GRAB_SUCCESS,
        extra={"coupon_value": 5, "coupon_id": "PDD20240101"}
    )

    # 抢券失败事件 - 会触发推送
    logger.log(
        level=LogLevel.ERROR,
        category=LogCategory.GRAB,
        message="抢券失败：优惠券已抢完",
        user_id="user001",
        event=LogEvent.GRAB_FAILED,
        extra={"reason": "stock_out", "retry_count": 3}
    )

    # Cookie过期事件 - 会触发推送
    logger.log(
        level=LogLevel.ERROR,
        category=LogCategory.AUTH,
        message="Cookie已过期，请重新登录获取",
        user_id="user001",
        event=LogEvent.COOKIE_EXPIRED
    )


def demo_business_methods():
    """演示业务专用方法"""
    print("\n=== 4. 业务专用方法 ===\n")

    logger = get_logger()

    # API请求日志
    logger.log_api_request("user001", "/api/grab", "POST", status=200)

    # 抢券成功日志
    logger.log_grab_success("user001", 5.0, coupon_id="PDD12345")

    # 抢券失败日志
    logger.log_grab_failed("user001", "库存不足", retry_available=True)

    # 签到日志
    logger.log_checkin("user001", 10, consecutive_days=7)

    # Cookie过期日志
    logger.log_cookie_expired("user001", last_refresh="2024-01-01")

    # 积分不足日志
    logger.log_points_low("user001", 50, required=100)


def demo_custom_push_callback():
    """演示自定义推送回调"""
    print("\n=== 5. 自定义推送回调 ===\n")

    logger = get_logger()

    # 注册自定义推送回调
    def custom_callback(record):
        print(f"[自定义回调] 捕获到重要事件: {record.event.value if record.event else 'N/A'}")
        print(f"  消息: {record.message}")
        print(f"  用户: {record.user_id}")

    logger.register_push_callback(custom_callback)

    # 触发一个会推送的事件
    logger.log_grab_success("user001", 5.0, coupon_id="CUSTOM123")


async def demo_async_usage():
    """演示异步场景使用"""
    print("\n=== 6. 异步场景使用 ===\n")

    logger = get_logger()

    async def simulate_grab_task(user_id: str, coupon_id: str):
        """模拟异步抢券任务"""
        logger.info(LogCategory.GRAB, f"开始抢券 {coupon_id}", user_id=user_id)

        await asyncio.sleep(0.1)

        logger.success(
            LogCategory.GRAB,
            f"抢券成功 {coupon_id}",
            user_id=user_id,
            event=LogEvent.GRAB_SUCCESS,
            extra={"coupon_value": 5}
        )

    # 并发执行多个抢券任务
    tasks = [
        simulate_grab_task("user001", "PDD001"),
        simulate_grab_task("user002", "PDD002"),
        simulate_grab_task("user003", "PDD003"),
    ]

    await asyncio.gather(*tasks)


def demo_all_log_categories():
    """演示所有日志分类"""
    print("\n=== 7. 所有日志分类 ===\n")

    logger = get_logger()

    categories = [
        (LogCategory.API, "API请求日志"),
        (LogCategory.GRAB, "抢券业务日志"),
        (LogCategory.CHECKIN, "签到业务日志"),
        (LogCategory.POINTS, "积分业务日志"),
        (LogCategory.SYSTEM, "系统运行日志"),
        (LogCategory.AUTH, "认证授权日志"),
        (LogCategory.DATABASE, "数据库操作日志"),
        (LogCategory.SCHEDULER, "调度器日志"),
        (LogCategory.PLATFORM_PDD, "拼多多平台日志"),
    ]

    for category, description in categories:
        logger.info(category, f"这是 {description}", user_id="demo")


def main():
    """主函数"""
    print("=" * 60)
    print("日志框架使用示例")
    print("=" * 60)

    # 运行各个示例
    demo_basic_logging()
    demo_categorized_logging()
    demo_event_logging()
    demo_business_methods()
    demo_custom_push_callback()

    # 运行异步示例
    asyncio.run(demo_async_usage())

    demo_all_log_categories()

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)
    print("\n请查看 logs/ 目录下的日志文件：")
    print("  - logs/app/           - 主应用日志")
    print("  - logs/error/         - 错误日志")
    print("  - logs/api/           - API日志")
    print("  - logs/grab/          - 抢券日志")
    print("  - logs/checkin/       - 签到日志")
    print("  - logs/points/        - 积分日志")
    print("  - logs/success/       - 成功日志")
    print("  - logs/json/          - JSON格式日志")
    print("=" * 60)


if __name__ == "__main__":
    main()
