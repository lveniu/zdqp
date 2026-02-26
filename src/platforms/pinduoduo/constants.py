"""
拼多多常量配置
"""

# 平台基础配置
PDD_BASE_URL = "https://mobile.yangkeduo.com"
PDD_H5_URL = "https://h5.pinduoduo.com"
PDD_WEB_URL = "https://www.pinduoduo.com"

# API端点
PDD_API_ENDPOINTS = {
    # 用户相关
    "user_info": "/user_info",
    "login": "/login",

    # 优惠券相关
    "coupon_list": "/coupon_list",
    "coupon_detail": "/coupon_detail",
    "grab_coupon": "/coupon_grab",
    "my_coupons": "/my_coupons",
    "coupon_status": "/coupon_status",

    # 商品相关
    "goods_detail": "/goods_detail",
}

# 请求头模板
PDD_HEADERS_TEMPLATE = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2211133C Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160065 MMWEBSDK/20231202 MMWEBID/2873 MicroMessenger/8.0.47.2560(0x28002F30) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 appVersion/24070143 appBrand/Wechat appType/LANGUAGE_WAPP pixels/1080x2400",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://h5.pinduoduo.com/",
    "Origin": "https://h5.pinduoduo.com",
}

# 优惠券类型
PDD_COUPON_TYPE = {
    "FULL_REDUCTION": "满减券",
    "DISCOUNT": "折扣券",
    "CASH": "现金券",
    "SHIPPING": "免邮券",
    "NEW_USER": "新人券",
}

# 优惠券状态
PDD_COUPON_STATUS = {
    "PENDING": "待领取",
    "AVAILABLE": "可使用",
    "USED": "已使用",
    "EXPIRED": "已过期",
    "OUT_OF_STOCK": "已抢完",
}

# 响应码
PDD_RESPONSE_CODE = {
    "SUCCESS": 0,
    "FAILED": -1,
    "NOT_LOGIN": 1001,
    "COUPON_EXPIRED": 2001,
    "COUPON_OUT_OF_STOCK": 2002,
    "ALREADY_RECEIVED": 2003,
    "RATE_LIMIT": 3001,
}

# 抢券相关常量
PDD_GRAB_CONFIG = {
    "max_retry": 3,
    "retry_delay": 0.5,  # 秒
    "request_timeout": 10,  # 秒
    "grab_before_seconds": 0.1,  # 提前0.1秒发起请求
}

# PDD特有的请求参数签名算法需要的参数
PDD_SIGNATURE_CONFIG = {
    "version": "1.0",
    "client_type": "mobile",  # mobile, web, h5
}
