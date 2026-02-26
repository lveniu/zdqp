"""
优惠券数据模型
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field


class CouponType(str, Enum):
    """优惠券类型"""
    FULL_REDUCTION = "full_reduction"  # 满减
    DISCOUNT = "discount"  # 折扣
    CASH = "cash"  # 现金
    SHIPPING = "shipping"  # 包邮


class CouponStatus(str, Enum):
    """优惠券状态"""
    PENDING = "pending"  # 待抢
    GRABBING = "grabbing"  # 抢取中
    SUCCESS = "success"  # 抢取成功
    FAILED = "failed"  # 抢取失败
    EXPIRED = "expired"  # 已过期


class CouponModel(BaseModel):
    """优惠券模型"""

    id: str = Field(..., description="优惠券ID")
    name: str = Field(..., description="优惠券名称")
    platform: str = Field(..., description="所属平台")
    type: CouponType = Field(..., description="优惠券类型")
    value: float = Field(..., description="面值")
    min_spend: float = Field(default=0.0, description="最低消费")
    status: CouponStatus = Field(default=CouponStatus.PENDING, description="状态")

    # 时间信息
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    grab_time: Optional[datetime] = Field(None, description="抢券时间")

    # 链接信息
    url: str = Field(..., description="优惠券链接")
    jump_url: Optional[str] = Field(None, description="跳转链接")

    # 数量限制
    total_quantity: Optional[int] = Field(None, description="总数量")
    remaining_quantity: Optional[int] = Field(None, description="剩余数量")
    limit_per_user: Optional[int] = Field(None, description="每人限领")

    # 其他信息
    description: Optional[str] = Field(None, description="描述")
    rules: Optional[str] = Field(None, description="使用规则")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        use_enum_values = True

    def is_available(self) -> bool:
        """是否可抢"""
        now = datetime.now()
        if self.start_time > now or self.end_time < now:
            return False
        if self.remaining_quantity is not None and self.remaining_quantity <= 0:
            return False
        return self.status == CouponStatus.PENDING

    def is_expired(self) -> bool:
        """是否已过期"""
        return datetime.now() > self.end_time
