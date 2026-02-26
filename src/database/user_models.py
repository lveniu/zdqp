"""
用户管理数据模型
支持多用户系统
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import hashlib

# 数据库文件路径
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "baibuti.db"

# 创建引擎
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False)
    phone = Column(String(20), unique=True)
    pdd_cookies = Column(Text)  # 拼多多Cookie
    pdd_user_agent = Column(Text)  # 拼多多UA
    pdd_user_id = Column(String(50))  # 拼多多用户ID

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
        """设置密码"""
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


# 创建所有表
def init_user_db():
    """初始化用户数据库"""
    Base.metadata.create_all(engine)


def get_user_db():
    """获取用户数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 查询模型
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
