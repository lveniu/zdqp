"""
用户认证API
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from ..database import UserCRUD, SessionCRUD

router = APIRouter(prefix="/api/auth", tags=["认证"])


# Pydantic模型
class UserRegister(BaseModel):
    """用户注册"""
    username: str
    password: str
    phone: Optional[str] = None
    pdd_cookies: Optional[str] = None
    pdd_user_agent: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    phone: Optional[str]
    pdd_user_id: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: UserResponse


class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str
    new_password: str


class PddConfigUpdate(BaseModel):
    """拼多多配置更新"""
    cookies: str
    user_agent: str


# 依赖项：获取当前用户
async def get_current_user(authorization: str = Header(...)) -> dict:
    """从请求头获取当前用户"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]  # 去掉 "Bearer "
    user = SessionCRUD.get_user_by_session(token)

    if not user:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    return {
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }


# API路由
@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister):
    """用户注册"""
    try:
        user = UserCRUD.create_user(
            username=data.username,
            password=data.password,
            phone=data.phone,
            pdd_cookies=data.pdd_cookies,
            pdd_ua=data.pdd_user_agent
        )

        return UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            pdd_user_id=user.pdd_user_id,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin):
    """用户登录"""
    user = UserCRUD.authenticate(data.username, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建会话
    token = SessionCRUD.create_session(user.id)

    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            pdd_user_id=user.pdd_user_id,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    )


@router.post("/logout")
async def logout(authorization: str = Header(...)):
    """用户登出"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]
    SessionCRUD.delete_session(token)

    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    user = UserCRUD.get_user_by_id(current_user["id"])

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        pdd_user_id=user.pdd_user_id,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at
    )


@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """修改密码"""
    success = UserCRUD.change_password(
        current_user["id"],
        data.old_password,
        data.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail="旧密码错误")

    return {"message": "密码修改成功"}


@router.post("/update-pdd-config")
async def update_pdd_config(
    data: PddConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新拼多多配置"""
    user = UserCRUD.update_pdd_config(
        current_user["id"],
        data.cookies,
        data.user_agent
    )

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "配置更新成功"}


@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """获取用户统计信息"""
    stats = UserCRUD.get_user_stats(current_user["id"])

    if not stats:
        raise HTTPException(status_code=404, detail="用户不存在")

    return stats


# 管理员接口
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """获取用户列表（管理员）"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")

    users = UserCRUD.list_users(skip, limit)

    return [
        UserResponse(
            id=u.id,
            username=u.username,
            phone=u.phone,
            pdd_user_id=u.pdd_user_id,
            is_active=u.is_active,
            is_admin=u.is_admin,
            created_at=u.created_at
        )
        for u in users
    ]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除用户（管理员）"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")

    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="不能删除自己")

    success = UserCRUD.delete_user(user_id)

    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "用户删除成功"}
