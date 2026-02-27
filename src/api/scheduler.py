"""
调度器 API 端点
用于管理定时任务配置
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.schedule_manager import get_schedule_manager
from ..core.scheduler_models import ScheduleConfig
from ..database import UserCRUD
from ..utils import get_logger

logger = get_logger("scheduler_api")

router = APIRouter(prefix="/api/scheduler", tags=["调度器"])


# Pydantic 模型
class ScheduleInfo(BaseModel):
    """调度信息"""
    name: str
    enabled: bool
    description: str
    platform: str
    task_type: str
    priority: str
    times: List[str]
    has_conditions: bool


class ScheduleStatus(BaseModel):
    """调度器状态"""
    running: bool
    total_schedules: int
    enabled_schedules: int
    users: List[str]


class ScheduleHistoryItem(BaseModel):
    """调度执行历史项"""
    schedule_name: str
    platform: str
    task_type: str
    executed_time: str
    scheduled_time: str
    success: bool
    message: str
    retry_count: int
    skipped: bool = False


class ScheduleControlRequest(BaseModel):
    """调度控制请求"""
    action: str  # start, stop, reload
    users: Optional[List[str]] = None


# API 端点


@router.get("/status", response_model=ScheduleStatus)
async def get_scheduler_status():
    """获取调度器状态"""
    manager = get_schedule_manager()

    try:
        stats = manager.get_stats()

        # 获取所有活跃用户
        users = UserCRUD.get_all_active_usernames()

        return ScheduleStatus(
            running=stats["running"],
            total_schedules=stats["total_schedules"],
            enabled_schedules=stats["enabled_schedules"],
            users=stats.get("users", users)
        )
    except Exception as e:
        logger.error(f"获取调度器状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules", response_model=List[ScheduleInfo])
async def get_schedules():
    """获取所有调度配置"""
    manager = get_schedule_manager()

    try:
        schedules = manager.get_schedules()

        result = []
        for schedule in schedules:
            result.append(ScheduleInfo(
                name=schedule.name,
                enabled=schedule.enabled,
                description=schedule.description,
                platform=schedule.platform,
                task_type=schedule.task_type,
                priority=schedule.priority.value,
                times=schedule.times,
                has_conditions=len(schedule.conditions) > 0
            ))

        return result
    except Exception as e:
        logger.error(f"获取调度配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules/{schedule_name}")
async def get_schedule_detail(schedule_name: str):
    """获取单个调度配置详情"""
    manager = get_schedule_manager()

    try:
        schedule = manager.get_schedule_by_name(schedule_name)
        if not schedule:
            raise HTTPException(status_code=404, detail=f"未找到调度配置: {schedule_name}")

        return {
            "name": schedule.name,
            "enabled": schedule.enabled,
            "description": schedule.description,
            "platform": schedule.platform,
            "task_type": schedule.task_type,
            "priority": schedule.priority.value,
            "times": schedule.times,
            "conditions": [
                {
                    "type": c.type.value,
                    "limit_type": c.limit_type.value if c.limit_type else None,
                    "max_count": c.max_count
                }
                for c in schedule.conditions
            ],
            "params": schedule.params,
            "retry": {
                "enabled": schedule.retry.enabled,
                "max_times": schedule.retry.max_times,
                "interval": schedule.retry.interval
            },
            "continue_on_failure": schedule.continue_on_failure
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取调度配置详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_execution_history(
    schedule_name: Optional[str] = None,
    limit: int = 50
):
    """获取执行历史"""
    manager = get_schedule_manager()

    try:
        history = manager.get_execution_history(schedule_name, limit)

        result = []
        for item in history:
            result.append(ScheduleHistoryItem(
                schedule_name=item.schedule_name,
                platform=item.platform,
                task_type=item.task_type,
                executed_time=item.executed_time,
                scheduled_time=item.scheduled_time,
                success=item.success,
                message=item.message,
                retry_count=item.retry_count,
                skipped=item.data.get("skipped", False)
            ))

        return result
    except Exception as e:
        logger.error(f"获取执行历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control")
async def control_scheduler(request: ScheduleControlRequest):
    """控制调度器（启动/停止/重载）"""
    manager = get_schedule_manager()

    try:
        if request.action == "start":
            # 设置用户列表
            if request.users:
                manager.set_users(request.users)
            else:
                # 如果没有指定用户，使用所有活跃用户
                users = UserCRUD.get_all_active_usernames()
                manager.set_users(users)

            await manager.start()
            return {"status": "started", "users": manager._users}

        elif request.action == "stop":
            await manager.stop()
            return {"status": "stopped"}

        elif request.action == "reload":
            manager.reload_config()
            return {"status": "reloaded"}

        else:
            raise HTTPException(status_code=400, detail=f"未知的操作: {request.action}")

    except Exception as e:
        logger.error(f"控制调度器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{schedule_name}/toggle")
async def toggle_schedule(schedule_name: str):
    """切换调度配置的启用状态"""
    manager = get_schedule_manager()

    try:
        schedule = manager.get_schedule_by_name(schedule_name)
        if not schedule:
            raise HTTPException(status_code=404, detail=f"未找到调度配置: {schedule_name}")

        # 切换启用状态
        schedule.enabled = not schedule.enabled

        # 重新加载配置
        manager.reload_config()

        return {
            "status": "toggled",
            "schedule_name": schedule_name,
            "enabled": schedule.enabled
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换调度配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{schedule_name}/execute")
async def execute_schedule_now(schedule_name: str, users: Optional[List[str]] = None):
    """立即执行指定的调度任务"""
    manager = get_schedule_manager()

    try:
        schedule = manager.get_schedule_by_name(schedule_name)
        if not schedule:
            raise HTTPException(status_code=404, detail=f"未找到调度配置: {schedule_name}")

        # 获取用户列表
        if users:
            user_list = users
        else:
            user_list = UserCRUD.get_all_active_usernames()

        if not user_list:
            raise HTTPException(status_code=400, detail="没有可用的用户")

        # 立即执行
        current_time = datetime.now().strftime("%H:%M")
        results = []

        for username in user_list:
            result = await manager._execute_for_user(schedule, username, current_time)
            results.append({
                "user": username,
                "success": result.success,
                "message": result.message,
                "skipped": result.data.get("skipped", False)
            })

        return {
            "schedule_name": schedule_name,
            "executed_at": datetime.now().isoformat(),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行调度任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
