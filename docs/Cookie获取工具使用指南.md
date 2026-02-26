# Cookie获取工具使用指南

## 功能介绍

本工具使用Playwright浏览器自动化技术，在Windows上模拟真实手机浏览器环境，自动获取拼多多等平台的Cookie。

### 特性

- ✅ 真实移动端浏览器模拟
- ✅ 支持多种设备型号
- ✅ 自动提取和保存Cookie
- ✅ 自动更新配置文件
- ✅ Cookie完整性验证
- ✅ 可视化操作界面

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install playwright

# 安装浏览器
playwright install chromium
```

### 2. 获取拼多多Cookie

```bash
# 基本用法（推荐）
python -m src.cli.main cookie pdd

# 指定设备
python -m src.cli.main cookie pdd --device iPhone_14

# 设置超时时间（秒）
python -m src.cli.main cookie pdd --timeout 600
```

### 3. 操作步骤

程序启动后会：

1. **打开移动端浏览器** - 模拟真实手机设备
2. **显示拼多多页面** - 自动跳转到登录页面
3. **等待您登录** - 请在浏览器中完成登录
4. **自动提取Cookie** - 登录成功后自动提取
5. **保存到配置文件** - Cookie自动保存到 `config/accounts.yaml`

## 使用方法

### 命令列表

```bash
# 获取拼多多Cookie
python -m src.cli.main cookie pdd

# 列出支持的设备
python -m src.cli.main cookie list-devices

# 验证Cookie有效性
python -m src.cli.main cookie validate

# 解析Cookie字符串
python -m src.cli.main cookie parse "pdd_token=xxx; customer_id=yyy"

# 从JSON文件导出
python -m src.cli.main cookie export --file cookies.json
```

### 获取Cookie详细流程

```bash
# 运行命令
python -m src.cli.main cookie pdd

# 程序会:
1. 启动浏览器窗口（不要关闭！）
2. 打开拼多多H5页面
3. 显示登录提示面板

# 您需要:
1. 在浏览器窗口中点击"登录"
2. 选择登录方式（推荐微信扫码）
3. 完成人机验证（如有）
4. 登录成功后，程序会自动继续

# 程序自动:
1. 检测登录状态
2. 提取Cookie
3. 显示Cookie信息
4. 保存到 config/accounts.yaml
```

## 支持的设备

| 设备名 | 屏幕尺寸 | 说明 |
|--------|----------|------|
| `iPhone_13_Pro` | 390x844 | iPhone 13 Pro |
| `iPhone_14` | 393x852 | iPhone 14 |
| `Samsung_Galaxy_S23` | 360x800 | 三星 S23 |
| `Xiaomi_13` | 393x851 | 小米 13（默认） |
| `Huawei_Mate_60` | 393x851 | 华为 Mate 60 |

## Cookie格式

获取到的Cookie会自动保存到 `config/accounts.yaml`:

```yaml
accounts:
  - platform: pinduoduo
    username: "手机号或用户ID"
    password: ""
    cookies: "pdd_token=xxxxx; customer_id=xxxxx; ..."
    user_agent: "Mozilla/5.0 (Linux; Android 13; ...) AppleWebKit/537.36"
    enabled: true
    metadata:
      user_id: "xxxxx"
      nickname: "昵称"
      device: "Xiaomi_13"
      saved_at: "2024-03-01T10:00:00"
```

## 常见问题

### Q: 浏览器无法启动？
A: 确保已安装Playwright浏览器：
```bash
playwright install chromium
```

### Q: 登录后程序没有继续？
A: 程序会自动检测登录状态，如果30秒没有检测到，请：
1. 刷新页面
2. 检查是否真的登录成功
3. 查看浏览器控制台是否有错误

### Q: Cookie多久过期？
A: 拼多多Cookie通常7-30天，建议定期重新获取。

### Q: 可以使用其他浏览器吗？
A: 目前只支持Chromium，这是Playwright的限制。

### Q: 为什么需要模拟移动端？
A: 拼多多H5页面专门为移动端优化，使用移动端User-Agent可以避免很多问题。

## 验证Cookie

```bash
# 验证配置文件中的所有Cookie
python -m src.cli.main cookie validate

# 输出示例:
┌──────────┬──────────┬──────────────────┬─────────┐
│ 平台     │ 用户名   │ Cookie           │ 状态    │
├──────────┼──────────┼──────────────────┼─────────┤
│ pdd      │ 138****  │ pdd_token=abc... │ ✓ 有效  │
│ pdd      │ 139****  │ pdd_token=def... │ ✗ 缺少  │
└──────────┴──────────┴──────────────────┴─────────┘
```

## 手动解析Cookie

如果您从其他地方获取了Cookie字符串，可以使用此命令解析：

```bash
python -m src.cli.main cookie parse "pdd_token=abc123; customer_id=xyz789"

# 输出:
┌──────────────┬──────────────────┬────────────┐
│ 名称         │ 值               │ 说明       │
├──────────────┼──────────────────┼────────────┤
│ pdd_token    │ abc123           │ 用户令牌   │
│ customer_id  │ xyz789           │ 客户ID     │
└──────────────┴──────────────────┴────────────┘

状态: ✓ Cookie完整
```

## 从JSON导出

如果您有之前保存的JSON格式Cookie，可以导出到配置文件：

```bash
python -m src.cli.main cookie export \
  --file config/cookies/pdd_cookies_20240301.json \
  --username "my_account"
```

## 技术原理

```
启动Playwright → 配置移动端参数 → 打开PDD页面
                                           ↓
                                  用户手动登录
                                           ↓
                            检测登录状态（轮询）
                                           ↓
                            提取所有Cookie
                                           ↓
                            解析关键信息
                                           ↓
                            保存到配置文件
```

### 反检测技术

1. **真实User-Agent** - 使用真实设备的UA
2. **移动端特征** - 模拟触摸事件、设备像素比等
3. **浏览器指纹** - 覆盖webdriver、platform等检测点
4. **地理位置** - 设置为中国境内位置
5. **时区语言** - 使用Asia/Shanghai时区和简体中文

## 注意事项

1. **窗口大小** - 首次使用建议不要使用无头模式，方便操作
2. **网络环境** - 确保网络畅通，能够访问拼多多
3. **登录方式** - 推荐使用微信扫码登录，最快捷
4. **验证码** - 可能需要完成人机验证
5. **安全** - Cookie包含敏感信息，请妥善保管

## 下一步

Cookie获取成功后：

```bash
# 1. 测试登录
python -m src.cli.main pdd login

# 2. 检查优惠券状态
python -m src.cli.main pdd check --url "优惠券链接"

# 3. 准点抢券
python -m src.cli.main pdd grab \
  --url "优惠券链接" \
  --time "2024-03-01 10:00:00"
```

## 更新日志

- **v0.1.0** - 初始版本
  - 支持拼多多Cookie获取
  - 5种移动设备模拟
  - 自动保存到配置文件
