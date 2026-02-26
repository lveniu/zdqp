"""
平台数据模型
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class PlatformType(str, Enum):
    """平台类型枚举"""
    TAOBAO = "taobao"
    JD = "jd"
    MEITUAN = "meituan"
    PINDUODUO = "pinduoduo"


class PlatformStatus(str, Enum):
    """平台状态"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class Account:
    """账号信息"""
    platform: str
    username: str
    password: str = ""
    cookies: str = ""
    user_agent: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformModel(BaseModel):
    """平台模型"""

    name: str = Field(..., description="平台名称")
    platform_type: PlatformType = Field(..., description="平台类型")
    base_url: str = Field(..., description="基础URL")
    grab_url: str = Field(..., description="抢券URL")
    enabled: bool = Field(default=True, description="是否启用")
    status: PlatformStatus = Field(default=PlatformStatus.ENABLED, description="平台状态")
    accounts: List[Account] = Field(default_factory=list, description="账号列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="平台配置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        use_enum_values = True
