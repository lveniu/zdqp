"""
拼多多URL解析工具
"""

import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs


def parse_coupon_url(url: str) -> Optional[Dict[str, Any]]:
    """
    解析拼多多优惠券URL

    支持的URL格式:
    - https://h5.pinduoduo.com/coupon.html?coupon_id=xxx
    - https://mobile.yangkeduo.com/coupon.html?coupon_id=xxx
    - yangkeduo://coupon?coupon_id=xxx

    Args:
        url: 优惠券链接

    Returns:
        包含优惠券信息的字典
    """
    try:
        # 处理yangkeduo://协议
        if url.startswith("yangkeduo://"):
            return _parse_app_url(url)

        # 处理HTTP/HTTPS链接
        parsed = urlparse(url)

        # 提取查询参数
        params = parse_qs(parsed.query)

        # 从URL中提取信息
        result = {
            "original_url": url,
            "coupon_id": params.get("coupon_id", [""])[0],
            "goods_id": params.get("goods_id", [""])[0],
            "activity_id": params.get("activity_id", [""])[0],
            "coupon_type": params.get("coupon_type", ["NORMAL"])[0],
        }

        # 从路径中提取coupon_id
        if not result["coupon_id"]:
            # 尝试从路径中提取
            path_parts = parsed.path.split("/")
            if "coupon" in path_parts:
                idx = path_parts.index("coupon")
                if idx + 1 < len(path_parts):
                    result["coupon_id"] = path_parts[idx + 1]

        return result if result["coupon_id"] else None

    except Exception as e:
        return None


def parse_goods_url(url: str) -> Optional[Dict[str, Any]]:
    """
    解析拼多多商品URL

    Args:
        url: 商品链接

    Returns:
        包含商品信息的字典
    """
    try:
        # 处理yangkeduo://协议
        if url.startswith("yangkeduo://"):
            return _parse_app_goods_url(url)

        # 处理HTTP/HTTPS链接
        parsed = urlparse(url)

        # 提取查询参数
        params = parse_qs(parsed.query)

        # 从URL中提取信息
        result = {
            "original_url": url,
            "goods_id": params.get("goods_id", [""])[0],
            "page_id": params.get("page_id", [""])[0],
            "category_id": params.get("category_id", [""])[0],
        }

        # 从路径中提取goods_id
        if not result["goods_id"]:
            # 尝试从路径中提取
            # 例如: /goods.html?goods_id=123
            # 或: /goods2.html?goods_id=123
            match = re.search(r'/goods\d*\.html', parsed.path)
            if match:
                result["goods_id"] = params.get("goods_id", [""])[0]

            # 尝试从短链接提取
            match = re.search(r'/goods/(\d+)', parsed.path)
            if match:
                result["goods_id"] = match.group(1)

        return result if result["goods_id"] else None

    except Exception as e:
        return None


def _parse_app_url(url: str) -> Optional[Dict[str, Any]]:
    """解析拼多多APP协议URL"""
    try:
        # yangkeduo://coupon?coupon_id=xxx&goods_id=yyy
        parsed = urlparse(url)

        if parsed.scheme != "yangkeduo":
            return None

        # 提取路径（去掉/）
        path = parsed.path.lstrip("/")

        # 解析查询参数
        params = parse_qs(parsed.query)

        result = {
            "original_url": url,
            "type": path,
            "coupon_id": params.get("coupon_id", [""])[0],
            "goods_id": params.get("goods_id", [""])[0],
            "activity_id": params.get("activity_id", [""])[0],
        }

        return result

    except Exception as e:
        return None


def _parse_app_goods_url(url: str) -> Optional[Dict[str, Any]]:
    """解析拼多多APP商品URL"""
    try:
        # yangkeduo://goods.html?goods_id=xxx
        parsed = urlparse(url)

        if parsed.scheme != "yangkeduo":
            return None

        # 解析查询参数
        params = parse_qs(parsed.query)

        result = {
            "original_url": url,
            "goods_id": params.get("goods_id", [""])[0],
            "page_id": params.get("page_id", [""])[0],
        }

        return result

    except Exception as e:
        return None


def extract_coupon_id(text: str) -> Optional[str]:
    """
    从文本中提取优惠券ID

    Args:
        text: 包含优惠券ID的文本

    Returns:
        优惠券ID
    """
    # 匹配常见的优惠券ID格式
    patterns = [
        r"coupon_id[=:]\s*([a-zA-Z0-9_-]+)",
        r"优惠券ID[=:：]\s*([a-zA-Z0-9_-]+)",
        r"coupon/([a-zA-Z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None
