"""
CRUD 基类
提供通用的数据库操作方法，减少重复代码
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import SessionLocal, Base as SQLAlchemyBase

# 类型变量
ModelType = TypeVar("ModelType", bound=SQLAlchemyBase)


class BaseCRUD(Generic[ModelType]):
    """
    CRUD 基类，提供通用的数据库操作

    使用方法:
        class UserCRUD(BaseCRUD[User]):
            def __init__(self):
                super().__init__(User)
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 CRUD

        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据 ID 获取记录"""
        db = SessionLocal()
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        finally:
            db.close()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        获取所有记录（支持分页和过滤）

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            filters: 过滤条件字典，如 {"username": "test", "is_active": True}
        """
        db = SessionLocal()
        try:
            query = db.query(self.model)

            # 应用过滤条件
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            return query.offset(skip).limit(limit).all()
        finally:
            db.close()

    def create(self, **kwargs) -> ModelType:
        """
        创建新记录

        Args:
            **kwargs: 模型字段值

        Returns:
            创建的模型实例
        """
        db = SessionLocal()
        try:
            obj = self.model(**kwargs)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        finally:
            db.close()

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        更新记录

        Args:
            id: 记录 ID
            **kwargs: 要更新的字段值

        Returns:
            更新后的模型实例，如果不存在返回 None
        """
        db = SessionLocal()
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if not obj:
                return None

            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            db.commit()
            db.refresh(obj)
            return obj
        finally:
            db.close()

    def delete(self, id: int) -> bool:
        """
        删除记录

        Args:
            id: 记录 ID

        Returns:
            是否删除成功
        """
        db = SessionLocal()
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if not obj:
                return False

            db.delete(obj)
            db.commit()
            return True
        finally:
            db.close()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数

        Args:
            filters: 过滤条件字典

        Returns:
            记录总数
        """
        db = SessionLocal()
        try:
            query = db.query(self.model)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            return query.count()
        finally:
            db.close()

    def exists(self, **kwargs) -> bool:
        """
        检查记录是否存在

        Args:
            **kwargs: 查询条件

        Returns:
            是否存在
        """
        db = SessionLocal()
        try:
            query = db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first() is not None
        finally:
            db.close()

    def get_by_fields(self, **kwargs) -> Optional[ModelType]:
        """
        根据字段值获取记录

        Args:
            **kwargs: 查询字段

        Returns:
            模型实例或 None
        """
        db = SessionLocal()
        try:
            query = db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first()
        finally:
            db.close()

    def get_many_by_fields(
        self,
        limit: int = 100,
        **kwargs
    ) -> List[ModelType]:
        """
        根据字段值获取多条记录

        Args:
            limit: 最大返回数量
            **kwargs: 查询字段

        Returns:
            模型实例列表
        """
        db = SessionLocal()
        try:
            query = db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.limit(limit).all()
        finally:
            db.close()


__all__ = ["BaseCRUD"]
