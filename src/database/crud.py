"""
统一的数据库CRUD操作
包含所有业务数据的增删改查操作
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func, and_, or_
import secrets
import hashlib

from .models import (
    User, UserSession,
    CheckinRecord, GrabRecord, PointsRecord,
    SystemConfig, TaskSchedule
)
from .base import SessionLocal


# ==================== 辅助函数 ====================

def extract_pdd_user_id_from_cookie(cookie_str: str) -> Optional[str]:
    """
    从 Cookie 字符串中提取拼多多用户ID

    Args:
        cookie_str: Cookie 字符串，格式为 "key1=value1; key2=value2"

    Returns:
        拼多多用户ID，如果未找到则返回 None
    """
    if not cookie_str:
        return None

    # 尝试多种可能的 Cookie 名称
    possible_keys = ["pdd_user_id", "user_id", "customer_id"]

    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key in possible_keys and value:
                return value

    return None


# ==================== 用户 CRUD ====================

class UserCRUD:
    """用户CRUD操作"""

    @staticmethod
    def create_user(username: str, password: str, phone: str = None,
                    pdd_cookies: str = None, pdd_ua: str = None,
                    is_admin: bool = False) -> User:
        """创建新用户"""
        db = SessionLocal()
        try:
            # 检查用户名是否已存在
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                raise ValueError(f"用户名 '{username}' 已存在")

            # 检查手机号是否已存在
            if phone:
                existing_phone = db.query(User).filter(User.phone == phone).first()
                if existing_phone:
                    raise ValueError(f"手机号 '{phone}' 已被注册")

            # 从 Cookie 中提取 pdd_user_id 并检查是否已存在
            pdd_user_id = extract_pdd_user_id_from_cookie(pdd_cookies)
            if pdd_user_id:
                existing_pdd_user = db.query(User).filter(User.pdd_user_id == pdd_user_id).first()
                if existing_pdd_user:
                    raise ValueError(f"该拼多多账号（用户ID: {pdd_user_id}）已被用户 '{existing_pdd_user.username}' 使用")

            # 创建用户
            user = User(
                username=username,
                phone=phone,
                pdd_cookies=pdd_cookies,
                pdd_user_agent=pdd_ua,
                pdd_user_id=pdd_user_id,
                is_admin=is_admin
            )
            user.set_password(password)

            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            db.close()

    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.phone == phone).first()
        finally:
            db.close()

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                and_(
                    User.username == username,
                    User.is_active == True
                )
            ).first()

            if user and user.check_password(password):
                # 更新最后登录时间
                user.last_login = datetime.now()
                db.commit()
                db.refresh(user)
                return user

            return None
        finally:
            db.close()

    @staticmethod
    def list_users(skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        db = SessionLocal()
        try:
            return db.query(User).offset(skip).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def get_all_active_usernames() -> List[str]:
        """获取所有活跃用户的用户名列表"""
        db = SessionLocal()
        try:
            users = db.query(User.username).filter(
                and_(
                    User.is_active == True,
                    User.pdd_cookies.isnot(None),
                    User.pdd_cookies != ""
                )
            ).all()
            return [u[0] for u in users]
        finally:
            db.close()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional[User]:
        """更新用户信息"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # 可更新的字段
            updatable_fields = [
                'phone', 'pdd_cookies', 'pdd_user_agent',
                'pdd_user_id', 'is_active', 'is_admin'
            ]

            for field in updatable_fields:
                if field in kwargs:
                    setattr(user, field, kwargs[field])

            user.updated_at = datetime.now()
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def update_pdd_config(user_id: int, cookies: str, user_agent: str, pdd_user_id: str = None):
        """更新拼多多配置"""
        db = SessionLocal()
        try:
            # 从 Cookie 中提取 pdd_user_id（如果未显式提供）
            if not pdd_user_id:
                pdd_user_id = extract_pdd_user_id_from_cookie(cookies)

            # 检查 pdd_user_id 是否被其他用户使用
            if pdd_user_id:
                existing_user = db.query(User).filter(
                    and_(
                        User.pdd_user_id == pdd_user_id,
                        User.id != user_id
                    )
                ).first()
                if existing_user:
                    raise ValueError(f"该拼多多账号（用户ID: {pdd_user_id}）已被用户 '{existing_user.username}' 使用")

            # 更新配置
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            user.pdd_cookies = cookies
            user.pdd_user_agent = user_agent
            user.pdd_user_id = pdd_user_id
            user.updated_at = datetime.now()

            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            if not user.check_password(old_password):
                return False

            user.set_password(new_password)
            user.updated_at = datetime.now()
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            db.delete(user)
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def get_user_stats(user_id: int) -> dict:
        """获取用户统计信息"""
        user = UserCRUD.get_user_by_id(user_id)
        if not user:
            return None

        # 获取用户名用于查询记录
        username = user.username

        return {
            "user_id": user_id,
            "username": username,
            "phone": user.phone,
            "pdd_user_id": user.pdd_user_id,
            "is_active": user.is_active,
            "checkin_stats": CheckinCRUD.get_stats(username),
            "grab_stats": GrabCRUD.get_stats(username),
            "current_points": PointsCRUD.get_current_points(username)
        }


class SessionCRUD:
    """会话管理"""

    @staticmethod
    def create_session(user_id: int, expires_hours: int = 24) -> str:
        """创建用户会话"""
        db = SessionLocal()
        try:
            # 生成随机token
            token = secrets.token_hex(32)
            expires_at = datetime.now() + timedelta(hours=expires_hours)

            session = UserSession(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )

            db.add(session)
            db.commit()
            return token
        finally:
            db.close()

    @staticmethod
    def get_session(token: str) -> Optional[UserSession]:
        """获取会话"""
        db = SessionLocal()
        try:
            return db.query(UserSession).filter(
                and_(
                    UserSession.token == token,
                    UserSession.expires_at > datetime.now()
                )
            ).first()
        finally:
            db.close()

    @staticmethod
    def get_user_by_session(token: str) -> Optional[User]:
        """根据会话token获取用户"""
        session = SessionCRUD.get_session(token)
        if not session:
            return None
        return UserCRUD.get_user_by_id(session.user_id)

    @staticmethod
    def delete_session(token: str) -> bool:
        """删除会话（登出）"""
        db = SessionLocal()
        try:
            session = db.query(UserSession).filter(
                UserSession.token == token
            ).first()

            if session:
                db.delete(session)
                db.commit()
                return True

            return False
        finally:
            db.close()

    @staticmethod
    def cleanup_expired_sessions():
        """清理过期会话"""
        db = SessionLocal()
        try:
            db.query(UserSession).filter(
                UserSession.expires_at < datetime.now()
            ).delete()
            db.commit()
        finally:
            db.close()


# ==================== 业务 CRUD ====================

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
                extra_data=str(metadata) if metadata else None
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
                extra_data=str(metadata) if metadata else None
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


# ==================== 数据库访问类 ====================

class Database:
    """数据库访问类"""

    def __init__(self):
        self.user = UserCRUD()
        self.session = SessionCRUD()
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


# ==================== 导出 ====================

__all__ = [
    "UserCRUD",
    "SessionCRUD",
    "CheckinCRUD",
    "GrabCRUD",
    "PointsCRUD",
    "ConfigCRUD",
    "Database",
    "get_db",
]
