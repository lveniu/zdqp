"""
拼多多数据模型
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field


@dataclass
class PddAccount:
    """拼多多账号信息"""
    user_id: str = ""
    username: str = ""
    password: str = ""
    cookies: str = ""
    user_agent: str = ""
    token: str = ""  # pdd_token
    customer_id: str = ""  # customer_id

    # 登录状态
    is_logged_in: bool = False
    login_time: Optional[datetime] = None

    # 用户信息
    nickname: str = ""
    avatar: str = ""
    mobile: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "token": self.token,
            "customer_id": self.customer_id,
            "is_logged_in": self.is_logged_in,
        }


class PddCouponModel(BaseModel):
    """拼多多优惠券模型"""

    # 基础信息
    coupon_id: str = Field(..., description="优惠券ID")
    coupon_type: str = Field(default="FULL_REDUCTION", description="优惠券类型")

    # 优惠信息
    discount_value: float = Field(..., description="优惠金额")
    min_spend: float = Field(default=0.0, description="最低消费")
    max_discount: float = Field(default=0.0, description="最大优惠金额")

    # 时间信息
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    valid_days: int = Field(default=0, description="有效天数")

    # 数量限制
    total_quantity: int = Field(default=0, description="总数量")
    remaining_quantity: int = Field(default=0, description="剩余数量")
    limit_per_user: int = Field(default=1, description="每人限领")

    # 适用范围
    goods_list: List[str] = Field(default_factory=list, description="适用商品ID列表")
    category_list: List[str] = Field(default_factory=list, description="适用分类")

    # 链接信息
    url: str = Field(..., description="优惠券链接")
    share_url: str = Field(default="", description="分享链接")

    # 状态
    status: str = Field(default="PENDING", description="状态")
    is_grabbed: bool = Field(default=False, description="是否已抢")
    grab_time: Optional[datetime] = Field(None, description="抢券时间")

    # 其他信息
    description: str = Field(default="", description="描述")
    rules: str = Field(default="", description="使用规则")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    class Config:
        use_enum_values = True

    def is_available(self) -> bool:
        """是否可抢"""
        if self.status != "PENDING":
            return False
        if self.remaining_quantity <= 0:
            return False
        return True


class PddGrabResult(BaseModel):
    """抢券结果"""
    success: bool = Field(..., description="是否成功")
    coupon_id: str = Field(..., description="优惠券ID")
    message: str = Field(default="", description="结果消息")
    code: int = Field(default=0, description="响应码")

    # 抢到的优惠券信息
    coupon_sn: str = Field(default="", description="优惠券序列号")
    coupon_batch: str = Field(default="", description="优惠券批次")
    valid_until: Optional[datetime] = Field(None, description="有效期至")

    # 请求信息
    request_time: datetime = Field(default_factory=datetime.now, description="请求时间")
    response_time: Optional[datetime] = Field(None, description="响应时间")
    elapsed_ms: float = Field(default=0.0, description="耗时(毫秒)")

    # 其他信息
    raw_response: Dict[str, Any] = Field(default_factory=dict, description="原始响应")


class PddGoodsModel(BaseModel):
    """拼多多商品模型"""
    goods_id: str = Field(..., description="商品ID")
    goods_name: str = Field(..., description="商品名称")
    price: float = Field(..., description="价格")
    original_price: float = Field(default=0.0, description="原价")
    sales: int = Field(default=0, description="销量")
    thumbnail: str = Field(default="", description="缩略图")
    url: str = Field(..., description="商品链接")
