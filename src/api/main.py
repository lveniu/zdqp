"""
FastAPI后端服务 - 简化版
直接使用Cookie，无需注册登录
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .simple import router

# 创建FastAPI应用
app = FastAPI(
    title="百亿补贴自动化系统",
    description="拼多多百亿补贴自动化抢券系统 - 简化版",
    version="2.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含简化版路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "百亿补贴自动化系统 - 简化版",
        "version": "2.0.0",
        "description": "直接使用Cookie，无需注册登录",
        "endpoints": {
            "health": "GET /api/health",
            "status": "POST /api/status",
            "checkin": "POST /api/checkin",
            "grab": "POST /api/grab",
            "records": "POST /api/records/checkin or /api/records/grab",
            "stats": "POST /api/stats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
