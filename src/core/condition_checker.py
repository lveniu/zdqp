"""
条件检查器
用于检查任务执行条件是否满足
"""

from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from loguru import logger

from .scheduler_models import ConditionConfig, ConditionType, LimitType
from ..database.crud import get_db


class ConditionChecker:
    """条件检查器"""

    def __init__(self, username: str):
        self.username = username

    async def check_all(self, conditions: List[ConditionConfig]) -> Tuple[bool, str]:
        """
        检查所有条件是否都满足

        Returns:
            (passed, message): 是否通过及原因
        """
        for condition in conditions:
            passed, message = await self.check_condition(condition)
            if not passed:
                return False, message

        return True, "所有条件满足"

    async def check_condition(self, condition: ConditionConfig) -> Tuple[bool, str]:
        """
        检查单个条件

        Returns:
            (passed, message): 是否通过及原因
        """
        if condition.type == ConditionType.DAILY_LIMIT:
            return await self._check_daily_limit(condition)
        elif condition.type == ConditionType.WEEKLY_LIMIT:
            return await self._check_weekly_limit(condition)
        elif condition.type == ConditionType.CUSTOM_CONDITION:
            return await self._check_custom_condition(condition)
        else:
            logger.warning(f"未知的条件类型: {condition.type}")
            return True, "未知条件类型，默认通过"

    async def _check_daily_limit(self, condition: ConditionConfig) -> Tuple[bool, str]:
        """
        检查每日限制

        检查今天已执行的操作次数是否超过限制
        """
        if condition.limit_type is None:
            return True, "未指定限制类型"

        today = date.today()
        db = get_db()

        try:
            if condition.limit_type == LimitType.CHECKIN:
                # 检查今天是否已签到
                count = db.checkin.count_today(self.username)
                if count >= condition.max_count:
                    return False, f"今天已签到过（限制：{condition.max_count}次/天）"

            elif condition.limit_type == LimitType.GRAB_SUCCESS:
                # 检查今天是否成功抢到过券
                count = db.grab.count_success_today(self.username)
                if count >= condition.max_count:
                    return False, f"今天已成功抢到{count}次券（限制：{condition.max_count}次/天）"

            elif condition.limit_type == LimitType.POINTS_GRAB:
                # 检查今天是否使用积分抢过券
                # 这里需要查询百亿补贴特定的积分抢券记录
                count = db.grab.count_points_grab_today(self.username)
                if count >= condition.max_count:
                    return False, f"今天已积分抢券{count}次（限制：{condition.max_count}次/天）"

            return True, "每日限制检查通过"

        except Exception as e:
            logger.error(f"每日限制检查出错: {e}")
            return True, f"检查出错，默认通过: {e}"

    async def _check_weekly_limit(self, condition: ConditionConfig) -> Tuple[bool, str]:
        """
        检查每周限制

        检查本周已执行的操作次数是否超过限制
        """
        if condition.limit_type is None:
            return True, "未指定限制类型"

        db = get_db()

        try:
            if condition.limit_type == LimitType.POINTS_GRAB:
                # 检查本周积分抢券次数（百亿补贴限制：每周2次）
                count = db.grab.count_points_grab_this_week(self.username)
                if count >= condition.max_count:
                    return False, f"本周已积分抢券{count}次（限制：{condition.max_count}次/周）"

            elif condition.limit_type == LimitType.GRAB_SUCCESS:
                # 检查本周抢券成功次数
                count = db.grab.count_success_this_week(self.username)
                if count >= condition.max_count:
                    return False, f"本周已成功抢券{count}次（限制：{condition.max_count}次/周）"

            return True, "每周限制检查通过"

        except Exception as e:
            logger.error(f"每周限制检查出错: {e}")
            return True, f"检查出错，默认通过: {e}"

    async def _check_custom_condition(self, condition: ConditionConfig) -> Tuple[bool, str]:
        """
        检查自定义条件

        可以在这里添加自定义的业务逻辑
        """
        if condition.custom_check:
            # 这里可以扩展自定义条件检查
            # 例如：检查积分余额、检查特定商品库存等
            logger.info(f"执行自定义条件检查: {condition.custom_check}")
            return True, "自定义条件检查通过"

        return True, "未指定自定义条件"


# 便捷函数
async def check_conditions_for_schedule(
    username: str,
    conditions: List[ConditionConfig]
) -> Tuple[bool, str]:
    """
    为特定调度任务检查所有条件

    Args:
        username: 用户名
        conditions: 条件列表

    Returns:
        (passed, message): 是否通过及原因
    """
    checker = ConditionChecker(username)
    return await checker.check_all(conditions)
