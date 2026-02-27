"""
数据库CRUD操作
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func, and_
from .models import (
    CheckinRecord, GrabRecord, PointsRecord,
    SystemConfig, TaskSchedule, SessionLocal
)


class CheckinCRUD:
    """打卡记录CRUD"""

    @staticmethod
    def create(user_id: str, points_gained: int, total_points: int,
               success: bool = True, message: str = "", **metadata) -> CheckinRecord:
        """创建打卡记录"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            record = CheckinRecord(
                user_id=user_id,
                checkin_date=today,
                points_gained=points_gained,
                total_points=total_points,
                success=success,
                message=message,
                metadata=str(metadata) if metadata else None
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        finally:
            db.close()

    @staticmethod
    def get_today(user_id: str) -> Optional[CheckinRecord]:
        """获取今日打卡记录"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return db.query(CheckinRecord).filter(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.checkin_date == today
                )
            ).first()
        finally:
            db.close()

    @staticmethod
    def get_recent(user_id: str, days: int = 7) -> List[CheckinRecord]:
        """获取最近几天的打卡记录"""
        db = SessionLocal()
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            return db.query(CheckinRecord).filter(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.checkin_date >= start_date
                )
            ).order_by(CheckinRecord.checkin_date.desc()).all()
        finally:
            db.close()

    @staticmethod
    def count_today(user_id: str) -> int:
        """获取今日签到次数"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return db.query(func.count(CheckinRecord.id)).filter(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.checkin_date == today,
                    CheckinRecord.success == True
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_stats(user_id: str) -> Dict[str, Any]:
        """获取打卡统计"""
        db = SessionLocal()
        try:
            # 总打卡次数
            total = db.query(func.count(CheckinRecord.id)).filter(
                CheckinRecord.user_id == user_id
            ).scalar()

            # 总积分
            total_points = db.query(func.sum(CheckinRecord.points_gained)).filter(
                and_(
                    CheckinRecord.user_id == user_id,
                    CheckinRecord.success == True
                )
            ).scalar() or 0

            # 连续打卡天数
            records = db.query(CheckinRecord.checkin_date).filter(
                CheckinRecord.user_id == user_id
            ).order_by(CheckinRecord.checkin_date.desc()).limit(30).all()

            consecutive = 0
            today = datetime.now()
            for i, (date,) in enumerate(records):
                expected_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                if date == expected_date:
                    consecutive += 1
                else:
                    break

            return {
                "total_checkins": total,
                "consecutive_days": consecutive,
                "total_points": total_points
            }
        finally:
            db.close()


class GrabCRUD:
    """抢券记录CRUD"""

    @staticmethod
    def create(user_id: str, coupon_id: str, success: bool = True,
               message: str = "", **metadata) -> GrabRecord:
        """创建抢券记录"""
        db = SessionLocal()
        try:
            today = datetime.now()
            today_str = today.strftime("%Y-%m-%d")
            week_str = today.strftime("%Y-W%W")

            record = GrabRecord(
                user_id=user_id,
                grab_date=today_str,
                grab_week=week_str,
                coupon_id=coupon_id,
                success=success,
                message=message,
                metadata=str(metadata) if metadata else None
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        finally:
            db.close()

    @staticmethod
    def get_today_count(user_id: str) -> int:
        """获取今日抢券次数"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_date == today,
                    GrabRecord.success == True
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_week_count(user_id: str) -> int:
        """获取本周抢券次数"""
        db = SessionLocal()
        try:
            week = datetime.now().strftime("%Y-W%W")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_week == week,
                    GrabRecord.success == True
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_recent(user_id: str, days: int = 7) -> List[GrabRecord]:
        """获取最近抢券记录"""
        db = SessionLocal()
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            return db.query(GrabRecord).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_date >= start_date
                )
            ).order_by(GrabRecord.created_at.desc()).all()
        finally:
            db.close()

    @staticmethod
    def count_success_today(user_id: str) -> int:
        """获取今日成功抢券次数"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_date == today,
                    GrabRecord.success == True
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def count_success_this_week(user_id: str) -> int:
        """获取本周成功抢券次数"""
        db = SessionLocal()
        try:
            week = datetime.now().strftime("%Y-W%W")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_week == week,
                    GrabRecord.success == True
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def count_points_grab_today(user_id: str) -> int:
        """获取今日积分抢券次数"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_date == today,
                    GrabRecord.success == True,
                    GrabRecord.points_used > 0
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def count_points_grab_this_week(user_id: str) -> int:
        """获取本周积分抢券次数"""
        db = SessionLocal()
        try:
            week = datetime.now().strftime("%Y-W%W")
            return db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_week == week,
                    GrabRecord.success == True,
                    GrabRecord.points_used > 0
                )
            ).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_stats(user_id: str) -> Dict[str, Any]:
        """获取抢券统计"""
        db = SessionLocal()
        try:
            # 今日次数
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_date == today,
                    GrabRecord.success == True
                )
            ).scalar() or 0

            # 本周次数
            week = datetime.now().strftime("%Y-W%W")
            week_count = db.query(func.count(GrabRecord.id)).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.grab_week == week,
                    GrabRecord.success == True
                )
            ).scalar() or 0

            # 总次数和总价值
            result = db.query(
                func.count(GrabRecord.id).label('total'),
                func.sum(GrabRecord.coupon_value).label('value')
            ).filter(
                and_(
                    GrabRecord.user_id == user_id,
                    GrabRecord.success == True
                )
            ).first()

            return {
                "today_count": today_count,
                "week_count": week_count,
                "total_count": result.total or 0,
                "total_value": float(result.value or 0)
            }
        finally:
            db.close()


class PointsCRUD:
    """积分记录CRUD"""

    @staticmethod
    def create(user_id: str, points_change: int, points_balance: int,
               reason: str = "") -> PointsRecord:
        """创建积分记录"""
        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            record = PointsRecord(
                user_id=user_id,
                record_date=today,
                points_change=points_change,
                points_balance=points_balance,
                reason=reason
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        finally:
            db.close()

    @staticmethod
    def get_current_points(user_id: str) -> int:
        """获取当前积分"""
        db = SessionLocal()
        try:
            # 获取最新的积分记录
            record = db.query(PointsRecord).filter(
                PointsRecord.user_id == user_id
            ).order_by(PointsRecord.created_at.desc()).first()

            return record.points_balance if record else 0
        finally:
            db.close()


class ConfigCRUD:
    """配置CRUD"""

    @staticmethod
    def get(key: str, default: str = "") -> str:
        """获取配置"""
        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.key == key
            ).first()
            return config.value if config else default
        finally:
            db.close()

    @staticmethod
    def set(key: str, value: str, description: str = ""):
        """设置配置"""
        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.key == key
            ).first()

            if config:
                config.value = value
                config.updated_at = datetime.now()
                if description:
                    config.description = description
            else:
                config = SystemConfig(
                    key=key,
                    value=value,
                    description=description
                )
                db.add(config)

            db.commit()
        finally:
            db.close()


# 数据库访问类 - 提供统一的访问接口
class Database:
    """数据库访问类"""

    def __init__(self):
        self.checkin = CheckinCRUD()
        self.grab = GrabCRUD()
        self.points = PointsCRUD()
        self.config = ConfigCRUD()


# 全局数据库实例
_db: Optional[Database] = None


def get_db() -> Database:
    """获取全局数据库实例"""
    global _db
    if _db is None:
        _db = Database()
    return _db
