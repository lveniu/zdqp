"""
启动Web服务器
运行后端API和前端界面
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置基础日志（仅控制台，避免与API日志重复）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    from src.api.main import app

    print("="*70)
    print("百亿补贴自动化系统 - Web界面 (多用户版)")
    print("="*70)
    print()
    print(f"[启动时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("[服务地址]")
    print("  后端API:    http://localhost:9000")
    print("  API文档:    http://localhost:9000/docs")
    print("  前端界面:   http://localhost:5173")
    print()
    print("[前端启动]")
    print("  1. cd web")
    print("  2. npm install (首次运行)")
    print("  3. npm run dev")
    print()
    print("[数据库]")
    print("  位置: data/baibuti.db")
    print("  支持: 多用户、打卡记录、抢券记录、积分管理")
    print()
    print("[主要功能]")
    print("  - 用户注册/登录")
    print("  - 多用户独立数据")
    print("  - 每日打卡领积分")
    print("  - 积分查询")
    print("  - 自动抢5元券")
    print("  - 历史记录查询")
    print()
    print("="*70)
    print("按 Ctrl+C 停止服务")
    print("="*70)
    print()

    logger.info("正在启动FastAPI服务器...")

    # 使用字符串格式启用reload，端口9000避免冲突
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
