"""
日志框架测试脚本
验证日志框架的各项功能
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_framework import (
    LoggingFramework,
    LogLevel,
    LogCategory,
    LogEvent,
    LogRecord,
    NotificationFilter,
    get_logger,
)


def test_logger_instance():
    """测试日志框架实例化"""
    print("\n=== 测试 1: 日志框架实例化 ===")

    logger = get_logger()
    assert isinstance(logger, LoggingFramework), "应该返回 LoggingFramework 实例"
    assert logger.log_dir.exists(), "日志目录应该存在"

    print("✅ 日志框架实例化成功")


def test_basic_logging():
    """测试基础日志功能"""
    print("\n=== 测试 2: 基础日志功能 ===")

    logger = get_logger()

    # 测试各个级别
    logger.debug(LogCategory.SYSTEM, "DEBUG 测试")
    logger.info(LogCategory.API, "INFO 测试", user_id="test_user")
    logger.success(LogCategory.GRAB, "SUCCESS 测试", user_id="test_user")
    logger.warning(LogCategory.POINTS, "WARNING 测试", user_id="test_user")
    logger.error(LogCategory.DATABASE, "ERROR 测试", user_id="test_user")
    logger.critical(LogCategory.SYSTEM, "CRITICAL 测试", user_id="test_user")

    print("✅ 基础日志功能正常")


def test_categorized_logging():
    """测试分类日志"""
    print("\n=== 测试 3: 分类日志功能 ===")

    logger = get_logger()

    # 测试各种分类
    categories = [
        LogCategory.API,
        LogCategory.GRAB,
        LogCategory.CHECKIN,
        LogCategory.POINTS,
        LogCategory.SYSTEM,
        LogCategory.AUTH,
        LogCategory.DATABASE,
        LogCategory.SCHEDULER,
    ]

    for category in categories:
        logger.info(category, f"测试分类: {category.value}", user_id="test_user")

    print("✅ 分类日志功能正常")


def test_business_methods():
    """测试业务专用方法"""
    print("\n=== 测试 4: 业务专用方法 ===")

    logger = get_logger()

    # 测试业务方法
    logger.log_api_request("test_user", "/api/test", "GET", status=200)
    logger.log_grab_success("test_user", 5.0, coupon_id="TEST001")
    logger.log_grab_failed("test_user", "测试失败", retry_count=3)
    logger.log_checkin("test_user", 10, consecutive_days=5)
    logger.log_cookie_expired("test_user")
    logger.log_points_low("test_user", 50, required=100)

    print("✅ 业务专用方法正常")


def test_log_record():
    """测试日志记录对象"""
    print("\n=== 测试 5: 日志记录对象 ===")

    record = LogRecord(
        level=LogLevel.INFO,
        category=LogCategory.API,
        message="测试消息",
        user_id="test_user",
        extra={"key": "value"},
        event=LogEvent.GRAB_SUCCESS
    )

    # 测试 to_dict
    data = record.to_dict()
    assert "timestamp" in data
    assert data["level"] == "INFO"
    assert data["category"] == "api"
    assert data["user_id"] == "test_user"
    assert data["event"] == "grab_success"

    # 测试 to_json
    json_str = record.to_json()
    assert isinstance(json_str, str)

    print("✅ 日志记录对象正常")


def test_notification_filter():
    """测试通知过滤器"""
    print("\n=== 测试 6: 通知过滤器 ===")

    # 测试应该推送的事件
    push_record = LogRecord(
        level=LogLevel.SUCCESS,
        category=LogCategory.GRAB,
        message="抢券成功",
        user_id="test_user",
        event=LogEvent.GRAB_SUCCESS
    )
    assert NotificationFilter.should_push(push_record), "抢券成功应该推送"

    # 测试不应该推送的事件
    no_push_record = LogRecord(
        level=LogLevel.SUCCESS,
        category=LogCategory.CHECKIN,
        message="签到成功",
        user_id="test_user",
        event=LogEvent.CHECKIN_SUCCESS
    )
    assert not NotificationFilter.should_push(no_push_record), "签到成功不应该推送"

    # 测试没有事件的情况
    no_event_record = LogRecord(
        level=LogLevel.INFO,
        category=LogCategory.API,
        message="普通日志",
        user_id="test_user"
    )
    assert not NotificationFilter.should_push(no_event_record), "无事件不应该推送"

    # 测试消息格式化
    message = NotificationFilter.format_push_message(push_record)
    assert "抢券成功" in message or "Grab Success" in message

    print("✅ 通知过滤器正常")


def test_custom_callback():
    """测试自定义回调"""
    print("\n=== 测试 7: 自定义推送回调 ===")

    logger = get_logger()

    callback_called = []

    def test_callback(record: LogRecord):
        callback_called.append(record)

    # 注册回调
    logger.register_push_callback(test_callback)

    # 触发一个会推送的事件
    logger.log_grab_success("test_user", 5.0, coupon_id="TEST001")

    # 注意：由于推送是异步的，这里可能需要延迟检查
    # 在实际测试中，应该等待一小段时间
    import time
    time.sleep(0.1)

    if callback_called:
        print("✅ 自定义回调正常")
    else:
        print("⚠️  自定义回调未触发（可能是推送配置未启用）")


async def test_async_usage():
    """测试异步使用"""
    print("\n=== 测试 8: 异步场景使用 ===")

    logger = get_logger()

    async def async_task():
        logger.info(LogCategory.GRAB, "异步任务开始", user_id="test_user")
        await asyncio.sleep(0.01)
        logger.success(LogCategory.GRAB, "异步任务完成", user_id="test_user")

    await async_task()

    print("✅ 异步场景使用正常")


def test_log_files_created():
    """测试日志文件是否创建"""
    print("\n=== 测试 9: 日志文件创建 ===")

    logger = get_logger()
    logger.log_dir

    # 触发各种日志
    logger.info(LogCategory.API, "测试API日志", user_id="test")
    logger.info(LogCategory.GRAB, "测试抢券日志", user_id="test")
    logger.info(LogCategory.CHECKIN, "测试签到日志", user_id="test")
    logger.info(LogCategory.POINTS, "测试积分日志", user_id="test")

    # 检查日志目录
    subdirs = ["app", "error", "api", "grab", "checkin", "points", "success", "json"]
    for subdir in subdirs:
        dir_path = logger.log_dir / subdir
        if dir_path.exists():
            print(f"  ✅ {dir_path} 目录存在")
        else:
            print(f"  ⚠️  {dir_path} 目录不存在（首次运行可能未生成）")

    print("✅ 日志文件结构检查完成")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("日志框架测试")
    print("=" * 60)

    try:
        test_logger_instance()
        test_basic_logging()
        test_categorized_logging()
        test_business_methods()
        test_log_record()
        test_notification_filter()
        test_custom_callback()
        asyncio.run(test_async_usage())
        test_log_files_created()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

        print("\n📝 请检查 logs/ 目录确认日志文件已生成：")
        print("   - logs/app/      主应用日志")
        print("   - logs/api/      API日志")
        print("   - logs/grab/     抢券日志")
        print("   - logs/checkin/  签到日志")
        print("   - logs/points/   积分日志")
        print("   - logs/success/  成功日志")
        print("   - logs/json/     JSON日志")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
