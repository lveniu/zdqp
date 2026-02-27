"""
统一的数据模型
包含所有数据库表定义
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib
from pathlib import Path

# ==================== 数据库配置 ====================

DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "baibuti.db"

# 创建引擎和会话
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== 用户模型 ====================

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False)
    phone = Column(String(20), unique=True)
    pdd_cookies = Column(Text)  # 拼多多Cookie
    pdd_user_agent = Column(Text)  # 拼多多UA
    pdd_user_id = Column(String(50), unique=True, index=True)  # 拼多多用户ID

    # 用户状态
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime)

    @property
    def is_authenticated(self):
        return self.is_active

    def set_password(self, password: str):
        """设置密码（SHA256）"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class UserSession(Base):
    """用户会话表"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    @property
    def is_valid(self):
        """检查会话是否有效"""
        return datetime.now() < self.expires_at


# ==================== 业务模型 ====================

class CheckinRecord(Base):
    """签到记录表"""
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    checkin_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    points_gained = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    extra_data = Column(Text)  # JSON格式的额外信息


class GrabRecord(Base):
    """抢券记录表"""
    __tablename__ = "grab_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    grab_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    grab_week = Column(String(10), nullable=False, index=True)  # YYYY-Www
    coupon_id = Column(String(100))
    coupon_value = Column(Float, default=5.0)  # 券面值(元)
    points_used = Column(Integer, default=100)  # 消耗积分
    success = Column(Boolean, default=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    extra_data = Column(Text)  # JSON格式的额外信息


class PointsRecord(Base):
    """积分记录表"""
    __tablename__ = "points_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    record_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    points_change = Column(Integer, default=0)  # 积分变化(+获得, -消耗)
    points_balance = Column(Integer, default=0)  # 余额
    reason = Column(String(50))  # 原因: checkin, grab, 等
    created_at = Column(DateTime, default=datetime.now)


# ==================== 系统配置模型 ====================

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(200))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TaskSchedule(Base):
    """定时任务表"""
    __tablename__ = "task_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(100), nullable=False)
    task_type = Column(String(50))  # checkin, grab, workflow
    schedule_time = Column(String(10))  # HH:MM格式
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


# ==================== 辅助类 ====================

class CheckinStats:
    """签到统计"""
    def __init__(self, total_checkins: int, consecutive_days: int, total_points: int):
        self.total_checkins = total_checkins
        self.consecutive_days = consecutive_days
        self.total_points = total_points


class GrabStats:
    """抢券统计"""
    def __init__(self, today_count: int, week_count: int, total_count: int, total_value: float):
        self.today_count = today_count
        self.week_count = week_count
        self.total_count = total_count
        self.total_value = total_value


class UserProfile:
    """用户资料"""
    def __init__(self, id: int, username: str, phone: str = None,
                 is_active: bool = True, is_admin: bool = False,
                 pdd_user_id: str = None, created_at: datetime = None):
        self.id = id
        self.username = username
        self.phone = phone
        self.is_active = is_active
        self.is_admin = is_admin
        self.pdd_user_id = pdd_user_id
        self.created_at = created_at


# ==================== 导出 ====================

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "DB_PATH",
    "User",
    "UserSession",
    "CheckinRecord",
    "GrabRecord",
    "PointsRecord",
    "SystemConfig",
    "TaskSchedule",
    "CheckinStats",
    "GrabStats",
    "UserProfile",
]
