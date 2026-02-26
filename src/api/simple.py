"""
简化的API - 直接使用Cookie，无需注册登录
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib

from ..database import CheckinCRUD, GrabCRUD, PointsCRUD
from ..platforms.pinduoduo.baibuti import BaiButiManager
from ..models.platform import Account
from ..utils import get_logger

# 配置日志
logger = get_logger("api")

router = APIRouter(prefix="/api", tags=["业务"])


# Pydantic模型
class CookieInput(BaseModel):
    """Cookie输入"""
    cookies: str
    user_agent: Optional[str] = "Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36"


class StatusResponse(BaseModel):
    """状态响应"""
    user_id: str
    current_points: int
    can_grab_today: bool
    can_grab_week: bool
    today_grab_count: int
    week_grab_count: int
    total_grab_count: int
    total_grab_value: float
    today_checkin: bool
    consecutive_days: int
    total_checkins: int


# 辅助函数
def get_user_id_from_cookie(cookies: str) -> str:
    """从Cookie中提取用户ID"""
    # 尝试提取 pdd_user_id
    for item in cookies.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            if key.strip() == 'pdd_user_id':
                return value.strip()

    # 如果没有pdd_user_id，使用Cookie的hash作为用户ID
    return hashlib.md5(cookies.encode()).hexdigest()[:8]


def create_account_from_cookies(cookies: str, user_agent: str) -> Account:
    """从Cookie创建账号"""
    user_id = get_user_id_from_cookie(cookies)

    return Account(
        platform="pinduoduo",
        username=user_id,
        cookies=cookies,
        user_agent=user_agent,
        enabled=True,
    )


# API路由
@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.post("/status", response_model=StatusResponse)
async def get_status(data: CookieInput):
    """获取状态 - 仅在异常时记录日志"""
    user_id = get_user_id_from_cookie(data.cookies)

    try:
        # 获取积分
        current_points = PointsCRUD.get_current_points(user_id)

        # 获取抢券统计
        grab_stats = GrabCRUD.get_stats(user_id)

        # 获取打卡统计
        checkin_stats = CheckinCRUD.get_stats(user_id)

        # 今日是否已打卡
        today_checkin = CheckinCRUD.get_today(user_id) is not None

        return StatusResponse(
            user_id=user_id,
            current_points=current_points,
            can_grab_today=grab_stats["today_count"] < 1,
            can_grab_week=grab_stats["week_count"] < 2,
            today_grab_count=grab_stats["today_count"],
            week_grab_count=grab_stats["week_count"],
            total_grab_count=grab_stats["total_count"],
            total_grab_value=grab_stats["total_value"],
            today_checkin=today_checkin,
            consecutive_days=checkin_stats["consecutive_days"],
            total_checkins=checkin_stats["total_checkins"]
        )
    except Exception as e:
        logger.error(f"[状态查询异常] 用户: {user_id}, 错误: {str(e)}")
        raise


@router.post("/checkin")
async def do_checkin(data: CookieInput):
    """执行打卡"""
    user_id = get_user_id_from_cookie(data.cookies)

    # 检查今日是否已打卡
    if CheckinCRUD.get_today(user_id):
        return {
            "success": False,
            "message": "今日已打卡",
            "points_gained": 0,
            "total_points": PointsCRUD.get_current_points(user_id)
        }

    logger.info(f"[打卡] 开始执行 - 用户: {user_id}")

    # 创建账号
    account = create_account_from_cookies(data.cookies, data.user_agent)

    # 执行打卡
    manager = BaiButiManager(account)
    try:
        result = await manager.daily_checkin()

        points_gained = result.get("points", 10)

        # 保存记录
        current_points = PointsCRUD.get_current_points(user_id) + points_gained

        CheckinCRUD.create(
            user_id=user_id,
            points_gained=points_gained,
            total_points=current_points,
            success=result.get("success", True),
            message=result.get("message", "")
        )

        # 更新积分记录
        PointsCRUD.create(
            user_id=user_id,
            points_change=points_gained,
            points_balance=current_points,
            reason="checkin"
        )

        if result.get("success", True):
            logger.success(f"[打卡成功] 用户: {user_id}, 获得: {points_gained}积分, 总积分: {current_points}")
        else:
            logger.warning(f"[打卡失败] 用户: {user_id}, 原因: {result.get('message')}")

        return {
            "success": result.get("success", True),
            "message": result.get("message", "打卡成功"),
            "points_gained": points_gained,
            "total_points": current_points
        }

    except Exception as e:
        logger.error(f"[打卡异常] 用户: {user_id}, 错误: {str(e)}")
        return {
            "success": False,
            "message": f"打卡异常: {str(e)}",
            "points_gained": 0,
            "total_points": PointsCRUD.get_current_points(user_id)
        }
    finally:
        await manager.close()


@router.post("/grab")
async def do_grab(data: CookieInput):
    """执行抢券"""
    user_id = get_user_id_from_cookie(data.cookies)

    # 检查今日抢券次数
    today_count = GrabCRUD.get_today_count(user_id)
    if today_count >= 1:
        return {
            "success": False,
            "message": "今天已抢1次，达到上限",
            "coupon_id": None,
            "daily_count": today_count,
            "weekly_count": GrabCRUD.get_week_count(user_id)
        }

    # 检查本周抢券次数
    week_count = GrabCRUD.get_week_count(user_id)
    if week_count >= 2:
        return {
            "success": False,
            "message": "本周已抢2次，达到上限",
            "coupon_id": None,
            "daily_count": today_count,
            "weekly_count": week_count
        }

    # 检查积分
    current_points = PointsCRUD.get_current_points(user_id)
    if current_points < 100:
        return {
            "success": False,
            "message": f"积分不足，需要100积分，当前{current_points}",
            "coupon_id": None,
            "daily_count": today_count,
            "weekly_count": week_count
        }

    logger.info(f"[抢券] 开始执行 - 用户: {user_id}, 当前积分: {current_points}")

    # 创建账号
    account = create_account_from_cookies(data.cookies, data.user_agent)

    # 执行抢券
    manager = BaiButiManager(account)
    try:
        result = await manager.grab_coupon()

        # 保存记录
        coupon_id = result.get("coupon_id", "")
        if result.get("success"):
            GrabCRUD.create(
                user_id=user_id,
                coupon_id=coupon_id,
                success=True,
                message=result.get("message", "抢券成功")
            )

            # 扣除积分
            PointsCRUD.create(
                user_id=user_id,
                points_change=-100,
                points_balance=current_points - 100,
                reason="grab"
            )

            logger.success(f"[抢券成功] 用户: {user_id}, 券ID: {coupon_id}")
        else:
            logger.warning(f"[抢券失败] 用户: {user_id}, 原因: {result.get('message')}")

        return {
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "coupon_id": coupon_id if result.get("success") else None,
            "daily_count": today_count + (1 if result.get("success") else 0),
            "weekly_count": week_count + (1 if result.get("success") else 0)
        }

    except Exception as e:
        logger.error(f"[抢券异常] 用户: {user_id}, 错误: {str(e)}")
        return {
            "success": False,
            "message": f"抢券异常: {str(e)}",
            "coupon_id": None,
            "daily_count": today_count,
            "weekly_count": week_count
        }
    finally:
        await manager.close()


@router.post("/records/checkin")
async def get_checkin_records(data: CookieInput, days: int = 7):
    """获取打卡记录"""
    user_id = get_user_id_from_cookie(data.cookies)

    try:
        records = CheckinCRUD.get_recent(user_id, days)
        return [
            {
                "id": r.id,
                "date": r.checkin_date,
                "points": r.points_gained,
                "success": r.success,
                "message": r.message,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]
    except Exception as e:
        logger.error(f"[记录查询异常] 用户: {user_id}, 类型: 打卡, 错误: {str(e)}")
        raise


@router.post("/records/grab")
async def get_grab_records(data: CookieInput, days: int = 7):
    """获取抢券记录"""
    user_id = get_user_id_from_cookie(data.cookies)

    try:
        records = GrabCRUD.get_recent(user_id, days)
        return [
            {
                "id": r.id,
                "date": r.grab_date,
                "coupon_id": r.coupon_id,
                "value": r.coupon_value,
                "success": r.success,
                "message": r.message,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]
    except Exception as e:
        logger.error(f"[记录查询异常] 用户: {user_id}, 类型: 抢券, 错误: {str(e)}")
        raise


@router.post("/stats")
async def get_stats(data: CookieInput):
    """获取统计信息"""
    user_id = get_user_id_from_cookie(data.cookies)

    try:
        checkin_stats = CheckinCRUD.get_stats(user_id)
        grab_stats = GrabCRUD.get_stats(user_id)
        current_points = PointsCRUD.get_current_points(user_id)

        return {
            "user_id": user_id,
            "points": {
                "current": current_points,
                "total_gained": checkin_stats["total_points"]
            },
            "checkin": {
                "total": checkin_stats["total_checkins"],
                "consecutive": checkin_stats["consecutive_days"]
            },
            "grab": {
                "today": grab_stats["today_count"],
                "week": grab_stats["week_count"],
                "total": grab_stats["total_count"],
                "total_value": grab_stats["total_value"]
            }
        }
    except Exception as e:
        logger.error(f"[统计查询异常] 用户: {user_id}, 错误: {str(e)}")
        raise
