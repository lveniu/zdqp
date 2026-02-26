"""
任务数据模型
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时


class TaskPriority(int, Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskModel(BaseModel):
    """抢券任务模型"""

    id: str = Field(..., description="任务ID")
    coupon_id: str = Field(..., description="优惠券ID")
    platform: str = Field(..., description="平台")
    account_id: str = Field(..., description="账号ID")

    # 任务配置
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="优先级")

    # 时间配置
    scheduled_time: datetime = Field(..., description="计划执行时间")
    start_time: Optional[datetime] = Field(None, description="实际开始时间")
    end_time: Optional[datetime] = Field(None, description="实际结束时间")

    # 重试配置
    retry_times: int = Field(default=0, description="已重试次数")
    max_retry_times: int = Field(default=3, description="最大重试次数")

    # 结果信息
    success: bool = Field(default=False, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="结果数据")

    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        use_enum_values = True

    def is_ready(self) -> bool:
        """是否准备好执行"""
        if self.status != TaskStatus.PENDING:
            return False
        return datetime.now() >= self.scheduled_time

    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.retry_times < self.max_retry_times

    def increment_retry(self):
        """增加重试次数"""
        self.retry_times += 1
        self.updated_at = datetime.now()


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    success: bool
    message: str
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
