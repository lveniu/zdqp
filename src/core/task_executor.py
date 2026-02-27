"""
任务执行器
负责执行不同平台、不同类型的任务
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import asyncio

from .scheduler_models import ScheduleConfig, ScheduleExecutionResult, TaskPriority
from .condition_checker import check_conditions_for_schedule


class TaskExecutor:
    """任务执行器 - 解耦的任务执行逻辑"""

    def __init__(self):
        self._platform_handlers = {}  # 平台处理器注册表
        self._task_handlers = {}      # 任务类型处理器注册表

        # 注册默认处理器
        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认的处理器"""
        # 百亿补贴任务
        self._task_handlers["baibuti_checkin"] = self._execute_baibuti_checkin
        self._task_handlers["baibuti_grab"] = self._execute_baibuti_grab

        # 通用抢券任务
        self._task_handlers["grab_coupon"] = self._execute_grab_coupon

    def register_platform_handler(self, platform: str, handler):
        """注册平台处理器"""
        self._platform_handlers[platform] = handler
        logger.info(f"已注册平台处理器: {platform}")

    def register_task_handler(self, task_type: str, handler):
        """注册任务类型处理器"""
        self._task_handlers[task_type] = handler
        logger.info(f"已注册任务处理器: {task_type}")

    async def execute(
        self,
        schedule: ScheduleConfig,
        username: str,
        scheduled_time: str
    ) -> ScheduleExecutionResult:
        """
        执行调度任务

        Args:
            schedule: 调度配置
            username: 用户名
            scheduled_time: 计划执行时间

        Returns:
            ScheduleExecutionResult: 执行结果
        """
        executed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = datetime.now()

        logger.info(f"开始执行调度任务: {schedule.name}, 用户: {username}")

        # 1. 检查条件
        conditions_passed, condition_message = await check_conditions_for_schedule(
            username, schedule.conditions
        )

        if not conditions_passed:
            logger.info(f"条件不满足，跳过执行: {condition_message}")
            return ScheduleExecutionResult(
                schedule_name=schedule.name,
                platform=schedule.platform,
                task_type=schedule.task_type,
                executed_time=executed_time,
                scheduled_time=scheduled_time,
                success=False,
                message=condition_message,
                data={"skipped": True, "reason": condition_message}
            )

        # 2. 获取任务处理器
        handler = self._task_handlers.get(schedule.task_type)
        if not handler:
            logger.error(f"未找到任务处理器: {schedule.task_type}")
            return ScheduleExecutionResult(
                schedule_name=schedule.name,
                platform=schedule.platform,
                task_type=schedule.task_type,
                executed_time=executed_time,
                scheduled_time=scheduled_time,
                success=False,
                message=f"未找到任务处理器: {schedule.task_type}",
                error="No handler found"
            )

        # 3. 执行任务（带重试）
        retry_count = 0
        max_retries = schedule.retry.max_times if schedule.retry.enabled else 0

        while retry_count <= max_retries:
            try:
                result = await handler(username, schedule.params)
                elapsed = (datetime.now() - start_time).total_seconds()

                if result.get("success", False):
                    logger.success(f"任务执行成功: {schedule.name}, 耗时: {elapsed:.2f}秒")
                    return ScheduleExecutionResult(
                        schedule_name=schedule.name,
                        platform=schedule.platform,
                        task_type=schedule.task_type,
                        executed_time=executed_time,
                        scheduled_time=scheduled_time,
                        success=True,
                        message=result.get("message", "执行成功"),
                        data=result.get("data", {}),
                        retry_count=retry_count
                    )
                else:
                    # 执行失败
                    if retry_count < max_retries:
                        retry_count += 1
                        wait_time = schedule.retry.interval
                        logger.warning(f"任务执行失败，{wait_time}秒后重试 ({retry_count}/{max_retries}): {result.get('message')}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"任务执行失败，已达最大重试次数: {result.get('message')}")
                        return ScheduleExecutionResult(
                            schedule_name=schedule.name,
                            platform=schedule.platform,
                            task_type=schedule.task_type,
                            executed_time=executed_time,
                            scheduled_time=scheduled_time,
                            success=False,
                            message=result.get("message", "执行失败"),
                            error=result.get("error"),
                            data=result.get("data", {}),
                            retry_count=retry_count
                        )

            except Exception as e:
                if retry_count < max_retries:
                    retry_count += 1
                    wait_time = schedule.retry.interval
                    logger.error(f"任务执行出错，{wait_time}秒后重试 ({retry_count}/{max_retries}): {e}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.exception(f"任务执行出错，已达最大重试次数: {e}")
                    return ScheduleExecutionResult(
                        schedule_name=schedule.name,
                        platform=schedule.platform,
                        task_type=schedule.task_type,
                        executed_time=executed_time,
                        scheduled_time=scheduled_time,
                        success=False,
                        message=f"执行出错: {str(e)}",
                        error=str(e),
                        retry_count=retry_count
                    )

    # ========== 任务处理器 ==========

    async def _execute_baibuti_checkin(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行百亿补贴签到"""
        from ..database.crud import get_user_account
        from ..platforms.pinduoduo.baibuti import BaiButiManager

        account = get_user_account(username)
        if not account or not account.cookie:
            return {
                "success": False,
                "message": "未配置拼多多 Cookie",
                "error": "No cookie configured"
            }

        manager = BaiButiManager(account)
        result = await manager.daily_checkin()

        if result.get("success"):
            return {
                "success": True,
                "message": f"签到成功，获得 {result.get('points', 0)} 积分",
                "data": {
                    "points": result.get("points"),
                    "total_points": result.get("total_points")
                }
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "签到失败"),
                "error": result.get("error")
            }

    async def _execute_baibuti_grab(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行百亿补贴积分抢券"""
        from ..database.crud import get_user_account
        from ..platforms.pinduoduo.baibuti import BaiButiManager

        account = get_user_account(username)
        if not account or not account.cookie:
            return {
                "success": False,
                "message": "未配置拼多多 Cookie",
                "error": "No cookie configured"
            }

        manager = BaiButiManager(account)

        # 使用积分抢 5 元券
        result = await manager.grab_with_points()

        if result.get("success"):
            return {
                "success": True,
                "message": f"抢券成功: {result.get('coupon_name', '5元无门槛券')}",
                "data": {
                    "coupon_name": result.get("coupon_name", "5元无门槛券"),
                    "points_used": params.get("use_points", 100)
                }
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "抢券失败"),
                "error": result.get("error"),
                "data": result.get("data", {})
            }

    async def _execute_grab_coupon(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行通用抢券（用于其他平台）"""
        # 这里可以实现其他平台的抢券逻辑
        return {
            "success": False,
            "message": f"平台 {params.get('platform', 'unknown')} 的抢券功能尚未实现",
            "error": "Not implemented"
        }


# 全局执行器实例
_executor: Optional[TaskExecutor] = None


def get_task_executor() -> TaskExecutor:
    """获取全局任务执行器实例"""
    global _executor
    if _executor is None:
        _executor = TaskExecutor()
    return _executor
