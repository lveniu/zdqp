"""
统一的后端 API 服务
支持可选认证，兼容两种模式：
1. 认证模式：使用用户 token
2. 简化模式：直接使用 Cookie
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from .simple import router as simple_router
from .auth import router as auth_router
from .scheduler import router as scheduler_router
from ..core.schedule_manager import get_schedule_manager

# 创建 FastAPI 应用
app = FastAPI(
    title="整点抢券",
    description="拼多多自动化抢券系统 - 统一版",
    version="2.1.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth_router)       # /api/auth/* - 认证相关
app.include_router(simple_router)      # /api/* - 业务接口（简化模式）
app.include_router(scheduler_router)   # /api/scheduler/* - 调度器


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化调度器"""
    manager = get_schedule_manager()
    manager.load_config()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "整点抢券 API",
        "version": "2.1.0",
        "description": "支持认证模式和简化模式",
        "endpoints": {
            "health": "GET /api/health",
            "auth": "POST /api/auth/* (认证模式)",
            "business": "POST /api/* (简化模式)",
            "scheduler": "GET /api/scheduler/*"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
