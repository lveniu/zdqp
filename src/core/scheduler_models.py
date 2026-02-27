"""
调度器配置模型
用于解析和管理调度器配置
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import time
from enum import Enum
import yaml


class TaskPriority(str, Enum):
    """任务优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConditionType(str, Enum):
    """条件类型"""
    DAILY_LIMIT = "daily_limit"      # 每日限制
    WEEKLY_LIMIT = "weekly_limit"    # 每周限制
    CUSTOM_CONDITION = "custom_condition"  # 自定义条件


class LimitType(str, Enum):
    """限制类型"""
    CHECKIN = "checkin"              # 签到
    GRAB_SUCCESS = "grab_success"    # 抢券成功
    POINTS_GRAB = "points_grab"      # 积分抢券


@dataclass
class ConditionConfig:
    """条件配置"""
    type: ConditionType
    limit_type: Optional[LimitType] = None
    max_count: int = 0
    custom_check: Optional[str] = None  # 自定义检查函数名

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionConfig":
        """从字典创建条件配置"""
        return cls(
            type=ConditionType(data["type"]),
            limit_type=LimitType(data.get("limit_type")) if "limit_type" in data else None,
            max_count=data.get("max_count", 0),
            custom_check=data.get("custom_check")
        )


@dataclass
class RetryConfig:
    """重试配置"""
    enabled: bool = True
    max_times: int = 3
    interval: int = 5  # 秒

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RetryConfig":
        """从字典创建重试配置"""
        return cls(
            enabled=data.get("enabled", True),
            max_times=data.get("max_times", 3),
            interval=data.get("interval", 5)
        )


@dataclass
class ScheduleConfig:
    """定时任务配置"""
    name: str
    enabled: bool = True
    description: str = ""
    platform: str = "pinduoduo"
    task_type: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    times: List[str] = field(default_factory=list)  # 时间点列表，如 ["10:00", "14:00"]
    conditions: List[ConditionConfig] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    retry: RetryConfig = field(default_factory=RetryConfig)
    continue_on_failure: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduleConfig":
        """从字典创建调度配置"""
        conditions = []
        if "conditions" in data:
            conditions = [ConditionConfig.from_dict(c) for c in data["conditions"]]

        retry = RetryConfig.from_dict(data.get("retry", {}))

        return cls(
            name=data["name"],
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
            platform=data.get("platform", "pinduoduo"),
            task_type=data.get("task_type", ""),
            priority=TaskPriority(data.get("priority", "medium")),
            times=data.get("times", []),
            conditions=conditions,
            params=data.get("params", {}),
            retry=retry,
            continue_on_failure=data.get("continue_on_failure", True)
        )

    def get_time_objects(self) -> List[time]:
        """将时间字符串转换为 time 对象"""
        time_objects = []
        for time_str in self.times:
            hour, minute = map(int, time_str.split(":"))
            time_objects.append(time(hour, minute))
        return time_objects

    def should_execute_now(self) -> tuple[bool, str]:
        """
        检查是否应该在当前时间执行

        Returns:
            (should_execute, reason): 是否应该执行及原因
        """
        if not self.enabled:
            return False, "任务未启用"

        if not self.times:
            return False, "没有配置执行时间"

        return True, ""


@dataclass
class SchedulerGlobalConfig:
    """调度器全局配置"""
    timezone: str = "Asia/Shanghai"
    enabled: bool = True
    max_concurrent_tasks: int = 3

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchedulerGlobalConfig":
        """从字典创建全局配置"""
        return cls(
            timezone=data.get("timezone", "Asia/Shanghai"),
            enabled=data.get("enabled", True),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 3)
        )


@dataclass
class SchedulerConfig:
    """调度器完整配置"""
    global_config: SchedulerGlobalConfig
    schedules: List[ScheduleConfig] = field(default_factory=list)

    @classmethod
    def load_from_file(cls, file_path: str) -> "SchedulerConfig":
        """从 YAML 文件加载配置"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        global_config = SchedulerGlobalConfig.from_dict(data.get("global", {}))
        schedules = []
        if "schedules" in data:
            schedules = [ScheduleConfig.from_dict(s) for s in data["schedules"]]

        return cls(
            global_config=global_config,
            schedules=schedules
        )

    def get_enabled_schedules(self) -> List[ScheduleConfig]:
        """获取已启用的调度配置"""
        return [s for s in self.schedules if s.enabled]

    def get_schedule_by_name(self, name: str) -> Optional[ScheduleConfig]:
        """根据名称获取调度配置"""
        for schedule in self.schedules:
            if schedule.name == name:
                return schedule
        return None


# 执行结果记录
@dataclass
class ScheduleExecutionResult:
    """调度执行结果"""
    schedule_name: str
    platform: str
    task_type: str
    executed_time: str  # 实际执行时间
    scheduled_time: str  # 计划执行时间
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
