"""
拼多多适配器测试
"""

import pytest
from datetime import datetime, timedelta
from src.platforms.pinduoduo.adapter import PinduoduoAdapter
from src.platforms.pinduoduo.utils.parser import (
    parse_coupon_url,
    parse_goods_url,
    extract_coupon_id,
)
from src.platforms.pinduoduo.utils.signature import generate_signature
from src.models.platform import Account


class TestPddParser:
    """测试URL解析"""

    def test_parse_h5_coupon_url(self):
        """测试解析H5优惠券链接"""
        url = "https://h5.pinduoduo.com/coupon.html?coupon_id=ABC123&goods_id=XYZ456"
        result = parse_coupon_url(url)

        assert result is not None
        assert result["coupon_id"] == "ABC123"
        assert result["goods_id"] == "XYZ456"

    def test_parse_mobile_coupon_url(self):
        """测试解析移动端优惠券链接"""
        url = "https://mobile.yangkeduo.com/coupon.html?coupon_id=TEST123"
        result = parse_coupon_url(url)

        assert result is not None
        assert result["coupon_id"] == "TEST123"

    def test_parse_app_coupon_url(self):
        """测试解析APP协议链接"""
        url = "yangkeduo://coupon?coupon_id=APP123&goods_id=GOODS456"
        result = parse_coupon_url(url)

        assert result is not None
        assert result["coupon_id"] == "APP123"
        assert result["goods_id"] == "GOODS456"

    def test_parse_invalid_url(self):
        """测试解析无效链接"""
        url = "https://example.com/invalid"
        result = parse_coupon_url(url)

        assert result is None

    def test_extract_coupon_id(self):
        """测试从文本提取优惠券ID"""
        text = "优惠券ID: ABC123, 快来抢"
        coupon_id = extract_coupon_id(text)

        assert coupon_id == "ABC123"


class TestPddSignature:
    """测试签名生成"""

    def test_generate_signature_with_token(self):
        """测试生成带Token的签名"""
        params = {
            "coupon_id": "ABC123",
            "timestamp": "1234567890",
        }
        token = "test_token"

        signature = generate_signature(params, token)

        assert signature is not None
        assert len(signature) == 32  # MD5长度
        assert signature.isupper()

    def test_generate_signature_without_token(self):
        """测试生成不带Token的签名"""
        params = {
            "coupon_id": "ABC123",
            "timestamp": "1234567890",
        }

        signature = generate_signature(params, "")

        assert signature is not None
        assert len(signature) == 32

    def test_signature_consistency(self):
        """测试签名一致性"""
        params = {
            "coupon_id": "ABC123",
            "timestamp": "1234567890",
        }
        token = "test_token"

        sig1 = generate_signature(params, token)
        sig2 = generate_signature(params, token)

        assert sig1 == sig2


class TestPddAdapter:
    """测试PDD适配器"""

    @pytest.fixture
    def test_account(self):
        """测试账号"""
        return Account(
            platform="pinduoduo",
            username="test_user",
            cookies="pdd_token=test_token; customer_id=123456",
            user_agent="Mozilla/5.0 Test",
            enabled=True,
        )

    @pytest.fixture
    def adapter(self, test_account):
        """创建适配器实例"""
        return PinduoduoAdapter(test_account, {})

    def test_adapter_initialization(self, adapter):
        """测试适配器初始化"""
        assert adapter.platform_name == "pinduoduo"
        assert adapter.platform_type == "pinduoduo"
        assert adapter.pdd_account.username == "test_user"

    def test_pdd_account_initialization(self, adapter):
        """测试PDD账号初始化"""
        assert adapter.pdd_account.token == "test_token"
        assert adapter.pdd_account.customer_id == "123456"

    def test_build_headers(self, adapter):
        """测试构建请求头"""
        headers = adapter._build_headers()

        assert "User-Agent" in headers
        assert "Cookie" in headers
        assert "pdd_token=test_token" in headers["Cookie"]


@pytest.mark.asyncio
class TestPddAdapterAsync:
    """测试PDD适配器异步方法"""

    @pytest.fixture
    def test_account(self):
        return Account(
            platform="pinduoduo",
            username="test_user",
            cookies="pdd_token=invalid_token",
            user_agent="Mozilla/5.0 Test",
            enabled=True,
        )

    @pytest.fixture
    def adapter(self, test_account):
        return PinduoduoAdapter(test_account, {})

    async def test_login_with_invalid_cookie(self, adapter):
        """测试使用无效Cookie登录"""
        result = await adapter.login()

        assert result is not None
        assert "success" in result.__dict__
        assert "message" in result.__dict__


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
