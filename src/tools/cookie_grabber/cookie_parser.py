"""
Cookie解析器
解析和提取拼多多Cookie中的关键信息
"""

from typing import Dict, Any, List, Optional
import json
import base64


class CookieParser:
    """Cookie解析器"""

    # 拼多多关键Cookie名称
    PDD_COOKIES = {
        "pdd_token": "用户令牌",
        "pdd_user_id": "用户ID",
        "customer_id": "客户ID",
        "user_id": "用户ID",
        "username": "用户名",
        "mobile": "手机号",
        "_o_auth_session": "OAuth会话",
        "pdd_vds": "设备标识",
        "pdd_stk": "会话令牌",
    }

    def parse_pdd_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        解析拼多多Cookie

        Args:
            cookies: Cookie列表

        Returns:
            Dict: 解析后的关键信息
        """
        result = {}

        for cookie in cookies:
            name = cookie["name"]
            value = cookie["value"]

            if name in self.PDD_COOKIES:
                result[name] = value

        return result

    def cookies_to_string(self, cookies: List[Dict[str, Any]]) -> str:
        """
        将Cookie列表转换为字符串格式

        Args:
            cookies: Cookie列表

        Returns:
            str: Cookie字符串 (name1=value1; name2=value2)
        """
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    def string_to_cookies(self, cookie_str: str, domain: str = ".pinduoduo.com") -> List[Dict[str, Any]]:
        """
        将Cookie字符串转换为Cookie列表

        Args:
            cookie_str: Cookie字符串
            domain: 域名

        Returns:
            List[Dict]: Cookie列表
        """
        cookies = []

        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                name, value = item.split("=", 1)
                cookies.append({
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": domain,
                    "path": "/",
                })

        return cookies

    def extract_pdd_token(self, cookies: List[Dict[str, Any]]) -> Optional[str]:
        """提取PDD Token"""
        for cookie in cookies:
            if cookie["name"] == "pdd_token":
                return cookie["value"]
        return None

    def extract_customer_id(self, cookies: List[Dict[str, Any]]) -> Optional[str]:
        """提取Customer ID"""
        for cookie in cookies:
            if cookie["name"] == "customer_id":
                return cookie["value"]
        return None

    def validate_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证Cookie完整性

        Args:
            cookies: Cookie列表

        Returns:
            Dict: 验证结果
        """
        result = {
            "valid": False,
            "missing": [],
            "warnings": [],
        }

        # 检查必需的Cookie
        required = ["pdd_token", "customer_id"]
        for name in required:
            found = any(c["name"] == name for c in cookies)
            if not found:
                result["missing"].append(name)

        # 检查可选但重要的Cookie
        important = ["pdd_user_id", "user_id"]
        for name in important:
            found = any(c["name"] == name for c in cookies)
            if not found:
                result["warnings"].append(f"建议包含: {name}")

        # 判断是否有效
        result["valid"] = len(result["missing"]) == 0

        return result

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        尝试解码Token（如果未加密）

        Args:
            token: Token字符串

        Returns:
            Dict: 解码后的信息，失败返回None
        """
        try:
            # 尝试Base64解码
            decoded = base64.b64decode(token).decode("utf-8")
            return json.loads(decoded)
        except:
            # Token可能是加密的，无法解码
            return None

    def get_cookie_expiration(self, cookies: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
        """
        获取Cookie过期时间

        Args:
            cookies: Cookie列表

        Returns:
            Dict: Cookie名称 -> 过期时间戳
        """
        result = {}

        for cookie in cookies:
            name = cookie["name"]
            expires = cookie.get("expires")

            if isinstance(expires, float) or isinstance(expires, int):
                result[name] = expires
            elif isinstance(expires, str):
                # 尝试解析日期字符串
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                    result[name] = dt.timestamp()
                except:
                    result[name] = None
            else:
                result[name] = None

        return result
