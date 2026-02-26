# 拼多多(PDD)准点抢券使用指南

## 功能介绍

本模块实现了拼多多平台的准点自动抢券功能，支持:

- ✅ Cookie登录，无需密码
- ✅ 毫秒级准点抢券
- ✅ 优惠券状态查询
- ✅ 自动重试机制
- ✅ URL解析功能

## 快速开始

### 1. 获取Cookie

首次使用需要获取拼多多Cookie:

```bash
# 方法一: 使用浏览器
1. 打开浏览器访问 https://h5.pinduoduo.com
2. 登录你的拼多多账号
3. 按F12打开开发者工具
4. 切换到 Network 标签
5. 刷新页面
6. 点击任意请求，找到 Request Headers 中的 Cookie
7. 复制整个Cookie字符串

# 方法二: 使用抓包工具
1. 手机安装Charles/Fiddler等抓包工具
2. 打开拼多多APP
3. 登录账号
4. 在抓包工具中找到包含 pdd_token 的请求
5. 复制Cookie
```

### 2. 配置账号

编辑 `config/accounts.yaml`:

```yaml
accounts:
  - platform: pinduoduo
    username: "your_phone_number"  # 手机号
    password: ""  # 不需要密码
    cookies: "pdd_token=xxxxx; customer_id=xxxxx; ..."  # 粘贴Cookie
    user_agent: "Mozilla/5.0 (Linux; Android 13; ...) AppleWebKit/537.36"
    enabled: true
```

### 3. 测试登录

```bash
python -m src.cli.main pdd login
```

如果看到 `✓ 登录成功！` 说明配置正确。

## 使用命令

### 准点抢券

```bash
# 基本用法
python -m src.cli.main pdd grab \
  --url "优惠券链接" \
  --time "2024-03-01 10:00:00"

# 指定账号
python -m src.cli.main pdd grab \
  --url "优惠券链接" \
  --time "2024-03-01 10:00:00" \
  --account "账号标识"

# 设置提前发起请求的时间(秒)
python -m src.cli.main pdd grab \
  --url "优惠券链接" \
  --time "2024-03-01 10:00:00" \
  --advance 0.5
```

**参数说明:**
- `--url, -u`: 优惠券链接(必填)
- `--time, -t`: 抢券时间，格式 `YYYY-MM-DD HH:MM:SS`(必填)
- `--account, -a`: 账号标识，默认 `default`
- `--advance`: 提前发起请求的秒数，默认 `0.1` 秒

### 检查优惠券状态

```bash
python -m src.cli.main pdd check \
  --url "优惠券链接" \
  --account "账号标识"
```

### 解析URL

```bash
# 解析优惠券链接
python -m src.cli.main pdd parse-url "https://h5.pinduoduo.com/coupon.html?coupon_id=xxx"

# 解析商品链接
python -m src.cli.main pdd parse-url "https://mobile.yangkeduo.com/goods.html?goods_id=xxx"
```

## 优惠券链接格式

支持的优惠券链接格式:

```
# H5链接
https://h5.pinduoduo.com/coupon.html?coupon_id=xxx&goods_id=yyy
https://mobile.yangkeduo.com/coupon.html?coupon_id=xxx

# APP协议
yangkeduo://coupon?coupon_id=xxx&goods_id=yyy

# 短链接(自动解析)
https://p.pinduoduo.com/xxxxxx
```

## 使用示例

### 示例1: 抢取限时优惠券

```bash
# 假设优惠券在 2024-03-01 10:00:00 开抢
python -m src.cli.main pdd grab \
  --url "https://h5.pinduoduo.com/coupon.html?coupon_id=ABC123" \
  --time "2024-03-01 10:00:00"
```

程序会:
1. 验证Cookie有效性
2. 等待到指定时间前0.1秒
3. 立即发起抢券请求
4. 显示抢券结果

### 示例2: 提前0.5秒发起请求

```bash
python -m src.cli.main pdd grab \
  --url "优惠券链接" \
  --time "2024-03-01 10:00:00" \
  --advance 0.5
```

### 示例3: 先检查优惠券状态

```bash
python -m src.cli.main pdd check \
  --url "优惠券链接"
```

输出:
```
状态: AVAILABLE
可抢: 是
剩余: 50/100
```

## 常见问题

### Q: Cookie多久会过期?
A: 拼多多Cookie通常7-30天过期，建议定期更新。

### Q: 抢券失败怎么办?
A: 可能原因:
1. Cookie已过期 - 重新获取
2. 优惠券已抢完 - 使用 `pdd check` 检查
3. 时间未到 - 确认时间设置正确
4. 限流 - 稍后重试

### Q: 提前时间设置多少合适?
A: 建议 `0.1-0.5` 秒，根据网络情况调整:
- 网络好: 0.1 秒
- 网络一般: 0.3 秒
- 网络差: 0.5 秒

### Q: 支持多账号抢券吗?
A: 支持，在 `config/accounts.yaml` 配置多个账号，使用 `--account` 指定。

### Q: 如何提高抢券成功率?
A: 建议:
1. 使用稳定的网络环境
2. 提前测试Cookie有效性
2. 合理设置提前时间
3. 使用配置文件中的重试机制

## 技术原理

```
用户输入 → 解析优惠券URL → 等待抢券时间
                              ↓
                         提前N秒发起请求
                              ↓
                         发送抢券API请求
                              ↓
                         解析响应结果
                              ↓
                         返回抢券结果
```

## 注意事项

1. **合法使用** - 请遵守拼多多使用条款
2. **频率限制** - 避免频繁请求导致账号受限
3. **Cookie安全** - 不要泄露Cookie，建议定期更换
4. **时间同步** - 确保系统时间准确
5. **网络稳定** - 抢券时保持网络稳定

## 进阶功能

### 使用调度器批量抢券

```python
from src.core.scheduler import get_scheduler
from src.platforms.pinduoduo.adapter import PinduoduoAdapter
from src.models.coupon import CouponModel
from datetime import datetime

# 创建调度器
scheduler = get_scheduler()
await scheduler.start()

# 添加抢券任务
coupon = CouponModel(
    id="coupon_123",
    name="PDD优惠券",
    platform="pinduoduo",
    url="优惠券链接",
    start_time=datetime(2024, 3, 1, 10, 0, 0),
    end_time=datetime(2024, 3, 1, 10, 0, 59),
)

scheduler.schedule_task(
    task=task,
    callback=lambda t: adapter.grab_coupon(coupon),
)
```

### 自定义User-Agent

在 `config/accounts.yaml` 中设置:

```yaml
user_agent: "Mozilla/5.0 (Linux; Android 13; ...) AppleWebKit/537.36"
```

建议使用真实手机浏览器的User-Agent。

## 更新日志

- **v0.1.0** - 初始版本
  - 支持准点抢券
  - Cookie登录
  - 优惠券状态查询
