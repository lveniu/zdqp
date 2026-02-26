"""
拼多多签名工具
"""

import hashlib
import json
from typing import Dict, Any


def generate_signature(params: Dict[str, Any], token: str = "") -> str:
    """
    生成拼多多请求签名

    Args:
        params: 请求参数
        token: 用户token

    Returns:
        签名字符串
    """
    # 1. 参数排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])

    # 2. 拼接参数
    param_str = "&".join([f"{k}={v}" for k, v in sorted_params if v != ""])

    # 3. 添加token
    if token:
        sign_str = f"{param_str}&token={token}"
    else:
        sign_str = param_str

    # 4. MD5签名
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    return sign.upper()


def generate_pdd_sign(
    method: str,
    path: str,
    params: Dict[str, Any],
    secret: str,
) -> str:
    """
    生成PDD开放平台API签名

    Args:
        method: 请求方法
        path: 请求路径
        params: 请求参数
        secret: 应用密钥

    Returns:
        签名字符串
    """
    # 1. 参数排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])

    # 2. 拼接字符串
    sign_str = f"{method.upper()}&{path}&"
    param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += param_str

    # 3. 添加密钥
    sign_str += f"&{secret}"

    # 4. MD5签名
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    return sign.upper()
