"""数据模型"""
from .platform import PlatformType, PlatformStatus, PlatformModel, Account
from .coupon import CouponType, CouponStatus, CouponModel
from .task import TaskStatus, TaskPriority, TaskModel, TaskResult

__all__ = [
    "PlatformType", "PlatformStatus", "PlatformModel", "Account",
    "CouponType", "CouponStatus", "CouponModel",
    "TaskStatus", "TaskPriority", "TaskModel", "TaskResult"
]
