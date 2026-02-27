"""
数据库基础配置
包含引擎、会话、Base 等核心组件
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# 数据库目录
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

# 数据库文件路径
DB_PATH = DB_DIR / "baibuti.db"

# 创建引擎
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,  # 生产环境设为 False
    connect_args={"check_same_thread": False}  # SQLite 特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基类
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


def get_db_session():
    """获取数据库会话（用于直接使用）"""
    return SessionLocal()


__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "init_db",
    "get_db",
    "get_db_session",
    "DB_PATH",
]
