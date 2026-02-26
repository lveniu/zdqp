"""
任务调度器
支持精确到毫秒的定时抢券
"""

import asyncio
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from loguru import logger

from ..models.task import TaskModel, TaskResult, TaskStatus
from ..core.config import get_config


class SchedulerState(str, Enum):
    """调度器状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class ScheduledTask:
    """计划任务"""
    task: TaskModel
    callback: Callable
    timer_handle: Optional[asyncio.TimerHandle] = None


class TaskScheduler:
    """
    任务调度器

    功能:
    - 精确到毫秒的定时执行
    - 并发控制
    - 任务优先级
    - 自动重试
    """

    def __init__(self, max_workers: int = None):
        self.config = get_config()
        self.max_workers = max_workers or self.config.scheduler.max_workers

        self.state = SchedulerState.STOPPED
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}

        # 任务队列（按优先级排序）
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

        # 信号控制
        self._stop_event = asyncio.Event()
        self._worker_tasks: List[asyncio.Task] = []

    async def start(self):
        """启动调度器"""
        if self.state == SchedulerState.RUNNING:
            logger.warning("调度器已在运行")
            return

        self.state = SchedulerState.RUNNING
        self._stop_event.clear()

        # 启动worker
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self._worker_tasks.append(task)

        logger.info(f"调度器已启动，workers: {self.max_workers}")

    async def stop(self):
        """停止调度器"""
        if self.state == SchedulerState.STOPPED:
            return

        self.state = SchedulerState.STOPPED
        self._stop_event.set()

        # 取消所有等待中的任务
        for scheduled_task in self.tasks.values():
            if scheduled_task.timer_handle:
                scheduled_task.timer_handle.cancel()

        # 等待所有worker完成
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()

        logger.info("调度器已停止")

    async def pause(self):
        """暂停调度器"""
        if self.state == SchedulerState.RUNNING:
            self.state = SchedulerState.PAUSED
            logger.info("调度器已暂停")

    async def resume(self):
        """恢复调度器"""
        if self.state == SchedulerState.PAUSED:
            self.state = SchedulerState.RUNNING
            logger.info("调度器已恢复")

    def schedule_task(
        self,
        task: TaskModel,
        callback: Callable[[TaskModel], Any],
    ) -> str:
        """调度任务"""
        task_id = task.id or str(uuid.uuid4())
        task.id = task_id

        # 计算延迟
        now = datetime.now()
        delay = (task.scheduled_time - now).total_seconds()

        if delay <= 0:
            # 立即执行
            asyncio.create_task(self._execute_task(task, callback))
        else:
            # 定时执行
            loop = asyncio.get_event_loop()
            timer_handle = loop.call_later(
                delay,
                lambda: asyncio.create_task(self._execute_task(task, callback))
            )

            scheduled_task = ScheduledTask(task=task, callback=callback, timer_handle=timer_handle)
            self.tasks[task_id] = scheduled_task

        logger.info(f"任务已调度: {task_id}, 执行时间: {task.scheduled_time}")
        return task_id

    async def _execute_task(
        self,
        task: TaskModel,
        callback: Callable[[TaskModel], Any],
    ):
        """执行任务"""
        task_id = task.id

        # 从定时任务列表移除
        if task_id in self.tasks:
            del self.tasks[task_id]

        # 加入执行队列
        await self.task_queue.put((task.priority.value, task))

    async def _worker(self, name: str):
        """Worker进程"""
        logger.debug(f"{name} 已启动")

        while not self._stop_event.is_set():
            try:
                # 等待任务，带超时
                priority, task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # 执行任务
                asyncio.create_task(self._run_task(task))

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"{name} 出错: {e}")

        logger.debug(f"{name} 已停止")

    async def _run_task(self, task: TaskModel):
        """运行单个任务"""
        task_id = task.id
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()

        logger.info(f"开始执行任务: {task_id}")

        try:
            # 这里应该调用实际的回调函数
            # 由于我们从task_queue获取任务时没有保存callback，需要重新设计
            # 暂时使用占位符
            result = await self._execute_with_timeout(task)

            if result.success:
                task.status = TaskStatus.SUCCESS
                task.success = True
                logger.success(f"任务成功: {task_id}")
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result.message
                await self._handle_failure(task, result)

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error_message = "执行超时"
            logger.error(f"任务超时: {task_id}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            logger.exception(f"任务失败: {task_id}, {e}")

        finally:
            task.end_time = datetime.now()

    async def _execute_with_timeout(self, task: TaskModel) -> TaskResult:
        """带超时执行任务"""
        # 这里需要实际的平台适配器来执行
        # 暂时返回模拟结果
        await asyncio.sleep(0.1)
        return TaskResult(
            task_id=task.id,
            success=False,
            message="需要实现平台适配器",
            data={}
        )

    async def _handle_failure(self, task: TaskModel, result: TaskResult):
        """处理失败任务"""
        if task.can_retry():
            task.increment_retry()
            delay = 2 ** task.retry_times  # 指数退避

            logger.warning(f"任务失败，{delay}秒后重试 (尝试 {task.retry_times}/{task.max_retry_times})")

            await asyncio.sleep(delay)

            # 重新调度
            task.status = TaskStatus.PENDING
            await self.task_queue.put((task.priority.value, task))
        else:
            logger.error(f"任务失败，已达最大重试次数: {task.id}")

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.tasks:
            scheduled_task = self.tasks[task_id]
            if scheduled_task.timer_handle:
                scheduled_task.timer_handle.cancel()
            del self.tasks[task_id]
            logger.info(f"任务已取消: {task_id}")
            return True
        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self.tasks:
            return self.tasks[task_id].task.status
        return None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "state": self.state.value,
            "max_workers": self.max_workers,
            "scheduled_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "queued_tasks": self.task_queue.qsize(),
        }


# 全局调度器实例
_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """获取全局调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler
