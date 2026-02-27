"""数据库模块"""
from .models import (
    init_db, get_db,
    User, UserSession,
    CheckinRecord, GrabRecord, PointsRecord,
    SystemConfig, TaskSchedule,
    CheckinStats, GrabStats, UserProfile
)
from .crud import (
    UserCRUD, SessionCRUD,
    CheckinCRUD, GrabCRUD, PointsCRUD, ConfigCRUD,
    Database, get_db as get_crud_db
)

__all__ = [
    "init_db", "get_db",
    "User", "UserSession", "UserProfile",
    "CheckinRecord", "GrabRecord", "PointsRecord",
    "SystemConfig", "TaskSchedule",
    "CheckinStats", "GrabStats",
    "UserCRUD", "SessionCRUD",
    "CheckinCRUD", "GrabCRUD", "PointsCRUD", "ConfigCRUD",
    "Database", "get_crud_db",
]

# 初始化数据库
init_db()
