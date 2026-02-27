"""
测试调度器 API
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

import uvicorn
from fastapi.testclient import TestClient

from src.api.main import app


def test_scheduler_api():
    """测试调度器 API"""
    logger.info("=== 测试调度器 API ===")

    # 手动初始化调度器配置（因为 TestClient 不会触发 startup 事件）
    from src.core.schedule_manager import get_schedule_manager
    manager = get_schedule_manager()
    manager.load_config()

    client = TestClient(app)

    # 1. 测试获取调度器状态
    logger.info("\n1. 测试获取调度器状态")
    response = client.get("/api/scheduler/status")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 运行中: {data['running']}")
        logger.info(f"  - 总任务数: {data['total_schedules']}")
        logger.info(f"  - 启用任务数: {data['enabled_schedules']}")
        logger.info(f"  - 用户列表: {data['users']}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 2. 测试获取所有调度配置
    logger.info("\n2. 测试获取所有调度配置")
    response = client.get("/api/scheduler/schedules")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        schedules = response.json()
        logger.info(f"  - 调度任务数量: {len(schedules)}")
        for schedule in schedules:
            status = "启用" if schedule['enabled'] else "禁用"
            logger.info(f"    [{status}] {schedule['name']}: {schedule['times']}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 3. 测试获取单个调度配置详情
    logger.info("\n3. 测试获取单个调度配置详情")
    response = client.get("/api/scheduler/schedules/百亿补贴5元券定时抢")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 名称: {data['name']}")
        logger.info(f"  - 描述: {data['description']}")
        logger.info(f"  - 时间: {data['times']}")
        logger.info(f"  - 条件: {len(data['conditions'])} 个")
        for cond in data['conditions']:
            logger.info(f"    - {cond['type']}: {cond['limit_type']} (max: {cond['max_count']})")
        logger.info(f"  - 参数: {data['params']}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 4. 测试获取执行历史
    logger.info("\n4. 测试获取执行历史")
    response = client.get("/api/scheduler/history?limit=10")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        history = response.json()
        logger.info(f"  - 历史记录数量: {len(history)}")
        for item in history[:3]:  # 只显示前3条
            status = "成功" if item['success'] else "失败"
            skipped = " (跳过)" if item.get('skipped') else ""
            logger.info(f"    [{status}]{skipped} {item['schedule_name']} at {item['executed_time']}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 5. 测试控制调度器（启动）
    logger.info("\n5. 测试启动调度器")
    response = client.post("/api/scheduler/control", json={
        "action": "start",
        "users": []
    })
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 状态: {data['status']}")
        logger.info(f"  - 用户: {data.get('users', [])}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 6. 等待一下再检查状态
    logger.info("\n6. 等待2秒后检查调度器状态")
    asyncio.sleep(2)
    response = client.get("/api/scheduler/status")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 运行中: {data['running']}")

    # 7. 测试停止调度器
    logger.info("\n7. 测试停止调度器")
    response = client.post("/api/scheduler/control", json={
        "action": "stop"
    })
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 状态: {data['status']}")
    else:
        logger.error(f"  - 错误: {response.text}")

    # 8. 测试切换调度启用状态
    logger.info("\n8. 测试切换调度启用状态")
    response = client.post("/api/scheduler/schedules/百亿补贴每日签到/toggle")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 任务名: {data['schedule_name']}")
        logger.info(f"  - 新状态: {'启用' if data['enabled'] else '禁用'}")
        # 切换回来
        client.post("/api/scheduler/schedules/百亿补贴每日签到/toggle")
    else:
        logger.error(f"  - 错误: {response.text}")

    logger.info("\n=== API 测试完成 ===")


def test_health_check():
    """测试健康检查"""
    logger.info("\n=== 测试健康检查 ===")

    client = TestClient(app)

    response = client.get("/api/health")
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"  - 状态: {data['status']}")
        logger.info(f"  - 时间戳: {data['timestamp']}")


if __name__ == "__main__":
    test_health_check()
    test_scheduler_api()
