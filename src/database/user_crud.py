"""
用户管理CRUD操作
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import and_, or_
import secrets
import hashlib

from .user_models import User, UserSession, SessionLocal


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

            # 创建用户
            user = User(
                username=username,
                phone=phone,
                pdd_cookies=pdd_cookies,
                pdd_user_agent=pdd_ua,
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
        return UserCRUD.update_user(
            user_id,
            pdd_cookies=cookies,
            pdd_user_agent=user_agent,
            pdd_user_id=pdd_user_id
        )

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
        from .crud import CheckinCRUD, GrabCRUD, PointsCRUD

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
