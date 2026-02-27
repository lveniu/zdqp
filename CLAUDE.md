# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

多平台抢券系统，专注于拼多多平台。该系统支持自动抢券、每日签到领积分，并包含 Web 管理界面。

**版本：** 2.0.0（多用户系统）

**核心组件：**
- Python 后端，采用 async/await 架构
- FastAPI Web 服务器 + Vue.js 前端
- 基于令牌的多用户身份认证
- 平台适配器模式，易于扩展
- SQLite 数据库记录保存
- Playwright/Selenium 浏览器自动化

## 常用命令

### 开发环境配置
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Web 前端依赖
cd web && npm install

# 初始化项目（创建目录）
python -m src.cli.main init

# 安装 Playwright 浏览器（用于获取 Cookie）
playwright install chromium
```

### 运行应用

**后端 API：**
```bash
# 启动 FastAPI 服务器
python start_web.py
# 运行在 http://localhost:8000
# API 文档位于 http://localhost:8000/docs
```

**前端：**
```bash
cd web
npm run dev
# 运行在 http://localhost:5173
```

**或使用 Windows 批处理文件：**
```bash
scripts/start.bat
```

### 测试
```bash
# 测试拼多多适配器功能
python test_pdd_adapter.py

# 测试 Cookie 认证
python test_login.py

# 测试 Web 系统
python test_web_system.py
```

### 命令行操作
```bash
# 查看系统信息
python -m src.cli.main info

# 列出支持的平台
python -m src.cli.main platforms

# 查看调度器状态
python -m src.cli.main status

# 拼多多特定命令
python -m src.cli pdd status      # 检查账户状态
python -m src.cli pdd check <URL> # 检查优惠券状态
python -m src.cli pdd grab <URL>  # 抢取优惠券

# Cookie 管理
python -m src.cli cookie --help   # Cookie 获取工具
```

### API 接口（v2.0 多用户）
```bash
# 认证接口
POST /api/auth/register     # 注册新用户（含 PDD Cookie）
POST /api/auth/login        # 登录并获取令牌
POST /api/auth/logout       # 登出
GET  /api/auth/me           # 获取当前用户信息
POST /api/auth/update-pdd-config  # 更新 PDD Cookie

# 主要接口（需要 Authorization 请求头）
GET  /api/status            # 获取用户状态
POST /api/checkin           # 每日签到
POST /api/grab              # 抢券
GET  /api/records/checkin   # 签到历史
GET  /api/records/grab      # 抢券历史
GET  /api/stats             # 统计数据
```

## 架构说明

### 目录结构
```
src/
├── core/           # 核心模块（配置、日志、调度器、通知器）
├── models/         # 数据模型（平台、优惠券、任务）
├── clients/        # HTTP 和浏览器客户端
├── platforms/      # 平台适配器
│   ├── base_adapter.py      # 抽象基类
│   └── pinduoduo/           # 拼多多实现
│       ├── adapter.py       # 主适配器
│       ├── baibuti.py       # 百亿补贴特定逻辑
│       ├── constants.py     # API 端点和配置
│       └── utils/           # 签名生成、解析工具
├── database/       # SQLAlchemy 模型和 CRUD 操作
│   ├── models.py          # 主数据库（签到、抢券、积分）
│   ├── user_models.py     # 用户数据库（用户、会话）
│   └── crud.py            # 所有表的 CRUD 操作
├── api/            # FastAPI 端点
│   ├── main.py            # 主要 API 端点（含认证）
│   └── auth.py            # 认证端点
├── tools/          # 实用工具（Cookie 获取器）
└── cli/            # 命令行界面
```

### 平台适配器模式

所有平台都继承自 `BaseAdapter` ([src/platforms/base_adapter.py](src/platforms/base_adapter.py))：

**必需方法：**
- `login()` - 平台身份认证
- `grab_coupon()` - 执行抢券操作
- `check_coupon_status()` - 查询优惠券可用性

**关键类：** `PinduoduoAdapter` ([src/platforms/pinduoduo/adapter.py](src/platforms/pinduoduo/adapter.py))
- 使用基于 Cookie 的认证
- 支持精确的定时抢券
- 实现反爬虫措施

### 百亿补贴系统

拼多多百亿补贴项目的专用系统：
- **管理器类：** `BaiButiManager` ([src/platforms/pinduoduo/baibuti.py](src/platforms/pinduoduo/baibuti.py))
- **功能：**
  - 每日打卡领积分
  - 使用 100 积分抢 5 元券
  - 限制：每天 1 次，每周 2 次

### 数据库模型

**主数据库** ([src/database/models.py](src/database/models.py))：
- `CheckinRecord` - 每日签到历史
- `GrabRecord` - 抢券历史
- `PointsRecord` - 积分余额变化
- `SystemConfig` - 系统配置
- `TaskSchedule` - 定时任务

**用户数据库** ([src/database/user_models.py](src/database/user_models.py))：
- `User` - 用户账户（含凭据和 PDD 配置）
- `UserSession` - 基于令牌的用户会话
- 密码通过 SHA256 哈希
- 会话过期处理

### 调度器 ([src/core/scheduler.py](src/core/scheduler.py))
- 基于 Asyncio 的任务调度器
- 毫秒级精度的定时抢券
- 工作池模式并发执行
- 指数退避自动重试

## 配置说明

### 主配置 ([config/config.yaml](config/config.yaml))
```yaml
app:
  env: development
  debug: true

scheduler:
  max_workers: 10      # 并发任务限制
  retry_times: 3       # 失败重试次数

notification:
  serverchan_key: ""   # 微信推送通知
  telegram_bot_token: ""

platforms:
  pinduoduo:
    enabled: true
    base_url: "https://mobile.yangkeduo.com"
```

### 账户配置

**单用户（旧版）：** [config/accounts.yaml](config/accounts.yaml) - 存储 Cookie 和用户凭据。**切勿提交此文件。**

**多用户（v2.0）：** 用户账户存储在数据库中（`data/baibuti.db`）。每个用户拥有：
- PDD Cookie 和用户代理
- 认证凭据
- 隔离数据（签到、抢券、积分）

拼多多 Cookie 格式必须包含：
- `PDDAccessToken` - 主认证令牌
- `pdd_user_id` - 用户标识符
- 其他会话 Cookie

**API 认证：**
- 通过 `Authorization: Bearer <token>` 请求头进行基于令牌的认证
- 注册：`POST /api/auth/register`
- 登录：`POST /api/auth/login`
- 用户 CRUD：[src/database/crud.py](src/database/crud.py) - `UserCRUD`, `SessionCRUD`

### Cookie 管理工具

位于 [src/tools/cookie_grabber/](src/tools/cookie_grabber/)
- `mobile_emulator.py` - 模拟移动浏览器
- `pdd_login.py` - PDD 登录逻辑
- `cli.py` - 命令行界面

## 关键文件说明

1. **[src/platforms/pinduoduo/baibuti.py](src/platforms/pinduoduo/baibuti.py)** - 百亿补贴业务逻辑
2. **[src/api/main.py](src/api/main.py)** - REST API 端点（含用户认证）
3. **[src/api/auth.py](src/api/auth.py)** - 认证端点（注册、登录、会话管理）
4. **[src/platforms/pinduoduo/adapter.py](src/platforms/pinduoduo/adapter.py)** - PDD 平台实现
5. **[src/database/user_models.py](src/database/user_models.py)** - 用户和会话模型
6. **[src/database/crud.py](src/database/crud.py)** - 所有数据的 CRUD 操作
7. **[start_web.py](start_web.py)** - Web 服务器入口

## 重要提示

1. **Cookie 过期：** PDD Cookie 会定期过期。登录失败时使用 Cookie 获取工具刷新。

2. **请求限制：** 系统包含请求节流以避免反爬虫检测。谨慎调整 `scheduler.max_workers`。

3. **时间精度：** 对于定时抢券，调度器使用毫秒级精度。`precise_grab()` 方法允许通过可配置偏移量预先调度请求。

4. **账户安全：** 切勿提交 `config/accounts.yaml` 或 `.env` 文件。使用 `.env.example` 作为模板。

5. **Windows 环境：** 项目包含 `.bat` 文件以便 Windows 用户使用（如 `scripts/start.bat`、`scripts/手动输入Cookie.bat`）。

## 开发流程

添加功能时：
1. 在适配器中实现平台特定逻辑
2. 如需持久化则添加数据库模型（检查 `models.py` 或 `user_models.py`）
3. 在 [src/database/crud.py](src/database/crud.py) 中创建 CRUD 操作
4. 在 [src/api/main.py](src/api/main.py) 或 [src/api/auth.py](src/api/auth.py) 中添加 API 端点
5. 对需要认证的端点使用 `Depends(get_current_user)`
6. 在 [web/](web/) 目录中更新前端

### 多用户模式

所有受保护端点遵循此模式：
```python
@app.get("/api/protected-endpoint")
async def protected_function(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    # 使用 username 进行所有数据操作
```

用户账户获取：
```python
account = get_user_account(username)  # 返回含 Cookie 的 Account 对象
manager = BaiButiManager(account)
```

## 故障排除

- **登录失败：** 运行 `python test_pdd_adapter.py` 验证 Cookie
- **数据库错误：** 删除 `data/baibuti.db` 并重启以重新初始化
- **导入错误：** 确保虚拟环境已激活且依赖已安装
- **认证错误（401）：** 检查是否设置了 Authorization 请求头：`Authorization: Bearer <token>`
- **Cookie 错误：** 每个用户必须通过 `/api/auth/update-pdd-config` 或注册时配置自己的 PDD Cookie
