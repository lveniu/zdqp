"""
辅助工具函数
"""

import hashlib
import time
import json
from typing import Any, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs


def generate_unique_id(prefix: str = "") -> str:
    """生成唯一ID"""
    timestamp = str(int(time.time() * 1000))
    hash_str = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{hash_str}" if prefix else f"{timestamp}_{hash_str}"


def parse_url(url: str) -> Dict[str, Any]:
    """解析URL"""
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "params": parsed.params,
        "query": parse_qs(parsed.query),
        "fragment": parsed.fragment,
    }


def format_timestamp(timestamp: float, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳"""
    return datetime.fromtimestamp(timestamp).strftime(format)


def parse_datetime(datetime_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(datetime_str, format)


def to_json(obj: Any, indent: int = 2) -> str:
    """转换为JSON字符串"""
    return json.dumps(obj, ensure_ascii=False, indent=indent)


def from_json(json_str: str) -> Any:
    """从JSON字符串解析"""
    return json.loads(json_str)


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return dictionary.get(key, default)


def merge_dict(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunk_list(lst: list, size: int) -> list[list]:
    """将列表分块"""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def retry(
    func,
    max_times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        current_delay = delay
        for attempt in range(max_times):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if attempt == max_times - 1:
                    raise
                time.sleep(current_delay)
                current_delay *= backoff
    return wrapper


async def async_retry(
    func,
    max_times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """异步重试装饰器"""
    import asyncio

    async def wrapper(*args, **kwargs):
        current_delay = delay
        for attempt in range(max_times):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if attempt == max_times - 1:
                    raise
                await asyncio.sleep(current_delay)
                current_delay *= backoff
    return wrapper


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def mask_sensitive(text: str, visible_chars: int = 4) -> str:
    """掩码敏感信息"""
    if len(text) <= visible_chars:
        return "*" * len(text)
    return text[:visible_chars] + "*" * (len(text) - visible_chars)


def calculate_hash(data: Any, algorithm: str = "md5") -> str:
    """计算哈希值"""
    if isinstance(data, str):
        content = data.encode()
    elif isinstance(data, dict):
        content = json.dumps(data, sort_keys=True).encode()
    else:
        content = str(data).encode()

    if algorithm == "md5":
        return hashlib.md5(content).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(content).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
