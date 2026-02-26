"""数据库模块"""
from .models import (
    init_db, get_db,
    CheckinRecord, GrabRecord, PointsRecord,
    SystemConfig, TaskSchedule,
    CheckinStats, GrabStats
)
from .crud import CheckinCRUD, GrabCRUD, PointsCRUD, ConfigCRUD
from .user_models import User, UserSession, init_user_db, UserProfile
from .user_crud import UserCRUD, SessionCRUD

__all__ = [
    "init_db", "get_db",
    "CheckinRecord", "GrabRecord", "PointsRecord",
    "SystemConfig", "TaskSchedule",
    "CheckinStats", "GrabStats",
    "CheckinCRUD", "GrabCRUD", "PointsCRUD", "ConfigCRUD",
    "User", "UserSession", "UserProfile",
    "UserCRUD", "SessionCRUD",
    "init_user_db"
]

# 初始化数据库
init_db()
init_user_db()
