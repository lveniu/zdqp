"""
定时任务管理器
负责加载配置、管理定时任务、在指定时间触发执行
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, time, timedelta
from loguru import logger
from pathlib import Path

from .scheduler_models import SchedulerConfig, ScheduleConfig, ScheduleExecutionResult
from .task_executor import get_task_executor


class ScheduleManager:
    """
    定时任务管理器

    功能:
    - 加载调度器配置
    - 在指定时间点触发任务
    - 检查执行条件
    - 记录执行结果
    """

    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config" / "scheduler.yaml"
        self.config: Optional[SchedulerConfig] = None
        self.executor = get_task_executor()

        # 运行状态
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

        # 用户列表（需要为每个用户执行任务）
        self._users: List[str] = []

        # 执行历史记录
        self._execution_history: Dict[str, List[ScheduleExecutionResult]] = {}

    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            self.config = SchedulerConfig.load_from_file(str(self.config_path))
            logger.info(f"已加载调度器配置: {len(self.config.schedules)} 个任务")
            return True
        except Exception as e:
            logger.error(f"加载调度器配置失败: {e}")
            return False

    def reload_config(self) -> bool:
        """重新加载配置"""
        logger.info("重新加载调度器配置...")
        return self.load_config()

    def set_users(self, users: List[str]):
        """设置需要执行任务的用户列表"""
        self._users = users
        logger.info(f"设置用户列表: {users}")

    def add_user(self, username: str):
        """添加用户"""
        if username not in self._users:
            self._users.append(username)
            logger.info(f"添加用户: {username}")

    def remove_user(self, username: str):
        """移除用户"""
        if username in self._users:
            self._users.remove(username)
            logger.info(f"移除用户: {username}")

    async def start(self):
        """启动定时任务管理器"""
        if self._running:
            logger.warning("定时任务管理器已在运行")
            return

        if not self.load_config():
            logger.error("加载配置失败，无法启动")
            return

        if not self.config.global_config.enabled:
            logger.info("调度器未启用，不启动定时任务管理器")
            return

        self._running = True
        self._stop_event.clear()

        # 启动监控任务
        self._task = asyncio.create_task(self._monitor_loop())

        logger.info("定时任务管理器已启动")

    async def stop(self):
        """停止定时任务管理器"""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("定时任务管理器已停止")

    async def _monitor_loop(self):
        """监控循环 - 检查并执行到期的任务"""
        logger.info("启动定时任务监控循环")

        # 记录已经执行过的任务 {schedule_name: {date: [times]}}
        executed_today: Dict[str, Dict[str, List[str]]] = {}

        while self._running and not self._stop_event.is_set():
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_date = now.strftime("%Y-%m-%d")

                # 检查每个已启用的调度任务
                for schedule in self.config.get_enabled_schedules():
                    # 检查是否在执行时间点
                    if current_time in schedule.times:
                        # 检查今天这个时间点是否已经执行过
                        if schedule.name not in executed_today:
                            executed_today[schedule.name] = {}

                        if current_date not in executed_today[schedule.name]:
                            executed_today[schedule.name][current_date] = []

                        if current_time in executed_today[schedule.name][current_date]:
                            continue  # 今天这个时间点已经执行过了

                        # 执行任务
                        logger.info(f"触发定时任务: {schedule.name} at {current_time}")
                        await self._execute_schedule(schedule, current_time)

                        # 记录已执行
                        executed_today[schedule.name][current_date].append(current_time)

                # 每分钟检查一次
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                await asyncio.sleep(60)

    async def _execute_schedule(self, schedule: ScheduleConfig, scheduled_time: str):
        """执行调度任务（为所有用户）"""
        if not self._users:
            logger.warning("没有配置用户，跳过执行")
            return

        logger.info(f"为 {len(self._users)} 个用户执行任务: {schedule.name}")

        # 并发执行（受全局配置的并发数限制）
        max_concurrent = self.config.global_config.max_concurrent_tasks

        for i in range(0, len(self._users), max_concurrent):
            batch = self._users[i:i + max_concurrent]
            tasks = [self._execute_for_user(schedule, username, scheduled_time) for username in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 记录结果
            for j, result in enumerate(results):
                if isinstance(result, ScheduleExecutionResult):
                    self._add_execution_history(result)

            # 等待一下再执行下一批
            if i + max_concurrent < len(self._users):
                await asyncio.sleep(1)

    async def _execute_for_user(
        self,
        schedule: ScheduleConfig,
        username: str,
        scheduled_time: str
    ) -> ScheduleExecutionResult:
        """为单个用户执行调度任务"""
        logger.info(f"执行任务: {schedule.name}, 用户: {username}")

        try:
            result = await self.executor.execute(schedule, username, scheduled_time)

            if result.success:
                logger.success(f"任务成功: {schedule.name} - {username}: {result.message}")
            else:
                if not result.data.get("skipped"):
                    logger.warning(f"任务失败: {schedule.name} - {username}: {result.message}")
                else:
                    logger.info(f"任务跳过: {schedule.name} - {username}: {result.message}")

            return result

        except Exception as e:
            logger.exception(f"执行任务出错: {schedule.name} - {username}: {e}")
            return ScheduleExecutionResult(
                schedule_name=schedule.name,
                platform=schedule.platform,
                task_type=schedule.task_type,
                executed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                scheduled_time=scheduled_time,
                success=False,
                message=f"执行出错: {str(e)}",
                error=str(e)
            )

    def _add_execution_history(self, result: ScheduleExecutionResult):
        """添加执行历史记录"""
        if result.schedule_name not in self._execution_history:
            self._execution_history[result.schedule_name] = []

        self._execution_history[result.schedule_name].append(result)

        # 只保留最近100条记录
        if len(self._execution_history[result.schedule_name]) > 100:
            self._execution_history[result.schedule_name] = \
                self._execution_history[result.schedule_name][-100:]

    def get_execution_history(self, schedule_name: str = None, limit: int = 50) -> List[ScheduleExecutionResult]:
        """获取执行历史"""
        if schedule_name:
            history = self._execution_history.get(schedule_name, [])
        else:
            # 合并所有任务的历史
            history = []
            for results in self._execution_history.values():
                history.extend(results)

        # 按时间倒序排序
        history = sorted(history, key=lambda x: x.executed_time, reverse=True)
        return history[:limit]

    def get_schedules(self) -> List[ScheduleConfig]:
        """获取所有调度配置"""
        if self.config:
            return self.config.schedules
        return []

    def get_schedule_by_name(self, name: str) -> Optional[ScheduleConfig]:
        """根据名称获取调度配置"""
        if self.config:
            return self.config.get_schedule_by_name(name)
        return None

    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "running": self._running,
            "config_loaded": self.config is not None,
            "total_schedules": len(self.config.schedules) if self.config else 0,
            "enabled_schedules": len(self.config.get_enabled_schedules()) if self.config else 0,
            "users": self._users,
            "execution_history_size": sum(len(h) for h in self._execution_history.values())
        }


# 全局实例
_schedule_manager: Optional[ScheduleManager] = None


def get_schedule_manager() -> ScheduleManager:
    """获取全局定时任务管理器实例"""
    global _schedule_manager
    if _schedule_manager is None:
        _schedule_manager = ScheduleManager()
    return _schedule_manager
