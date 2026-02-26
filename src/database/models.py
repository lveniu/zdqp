"""
数据库模型定义
使用SQLite存储百亿补贴相关数据
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from pathlib import Path

# 数据库文件路径
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "baibuti.db"

# 创建引擎
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class CheckinRecord(Base):
    """打卡记录表"""
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


# 创建所有表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 查询模型
class CheckinStats:
    """打卡统计"""
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
