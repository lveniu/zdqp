# 多平台抢券系统

基于 Python 实现的多平台自动抢券系统，采用插件化架构，轻松扩展新平台。目前已实现拼多多平台适配器，支持百亿补贴自动打卡、积分抢券等功能。包含 Web 管理界面，支持多用户管理。

## 版本

**v2.0.0** - 多用户系统

## 特性

- **多平台支持** - 插件化架构，轻松扩展淘宝、京东、美团等新平台
- **Web 管理界面** - Vue.js 前端 + FastAPI 后端，现代化管理体验
- **多用户系统** - 基于令牌的身份认证，每个用户独立数据隔离
- **百亿补贴** - 拼多多平台自动每日打卡领积分，使用积分抢 5 元券
- **精确计时** - 毫秒级定时任务调度，精确抢券
- **异步高性能** - 基于 asyncio 实现高并发抢券
- **自动重试** - 失败自动重试，指数退避策略
- **通知推送** - 支持微信推送通知
- **数据持久化** - SQLite 数据库记录所有操作历史

## 技术栈

**后端：**
- Python 3.12+
- FastAPI - Web 框架
- SQLAlchemy - ORM
- Pydantic - 数据验证
- asyncio - 异步编程
- httpx - HTTP 客户端
- Playwright - 浏览器自动化

**前端：**
- Vue.js 3
- Vite
- Element Plus

**Claude Code 技能：**
- python-lib-finder - Python 库快速查找
- skill-creator - 技能创建工具

## 项目结构

```
coupon-grabber/
├── src/
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── logger.py      # 日志系统
│   │   ├── scheduler.py   # 任务调度器
│   │   └── notifier.py    # 通知系统
│   ├── models/            # 数据模型
│   │   ├── platform.py    # 平台模型
│   │   ├── coupon.py      # 优惠券模型
│   │   └── task.py        # 任务模型
│   ├── clients/           # HTTP 和浏览器客户端
│   ├── platforms/         # 平台适配器
│   │   ├── base_adapter.py        # 抽象基类
│   │   ├── taobao/                # 淘宝（待实现）
│   │   ├── jd/                    # 京东（待实现）
│   │   ├── meituan/               # 美团（待实现）
│   │   └── pinduoduo/             # 拼多多实现
│   │       ├── adapter.py         # 主适配器
│   │       ├── baibuti.py         # 百亿补贴逻辑
│   │       ├── constants.py       # API 端点
│   │       └── utils/             # 签名、解析工具
│   ├── database/          # 数据库模型和 CRUD
│   │   ├── base.py                # 数据库基类
│   │   ├── models.py              # 数据模型（签到、抢券、积分、用户）
│   │   └── crud.py                # 所有表的 CRUD 操作
│   ├── api/               # FastAPI 端点
│   │   ├── main.py        # 主要 API（含认证）
│   │   └── auth.py        # 认证端点
│   ├── tools/             # 实用工具（Cookie 获取器）
│   └── cli/               # 命令行界面
├── web/                   # Vue.js 前端
│   ├── src/
│   │   ├── Login.vue      # 登录页
│   │   ├── Dashboard.vue  # 仪表盘
│   │   └── api.js         # API 调用
│   └── package.json
├── config/                # 配置文件
│   └── config.yaml        # 主配置
├── data/                  # 数据目录
│   └── baibuti.db         # SQLite 数据库
├── logs/                  # 日志目录
├── scripts/               # 启动脚本
│   ├── 启动.bat            # 一键启动（后端，端口自动分配）
│   ├── stop.bat            # 停止所有服务
│   ├── start_backend.bat  # 启动后端服务
│   ├── start_frontend.bat # 启动前端服务
│   ├── run_test.bat       # 运行测试
│   └── 手动输入Cookie.bat # Cookie 输入工具
├── tools/                 # 工具脚本
│   ├── 快速Cookie提取.py  # Cookie 提取工具
│   ├── 快速配置Cookie.py  # Cookie 配置工具
│   ├── 方案1_商品页面登录.py
│   ├── 方案2_手机直接获取.py
│   ├── 方案3_扫码登录.py
│   ├── 如何找到正确的Cookie.py
│   └── 验证新Cookie.py    # Cookie 验证工具
├── tests/                 # 测试文件
│   ├── test_api_logging.py
│   └── test_baibuti_api.py
├── .claude/               # Claude Code 配置
│   └── skills/            # 技能包
│       ├── python-lib-finder.skill  # Python 库查找技能
│       └── skill_creator/          # 技能创建工具
├── docs/                  # 文档目录
│   ├── 启动指南.md
│   ├── WEB_GUIDE.md
│   ├── API配置指南.md
│   └── REFACTORING_PLAN.md  # 重构计划文档
├── start_web.py           # Web 服务器入口
└── requirements.txt       # Python 依赖
```

## 快速开始

### 1. 安装依赖

**Python 依赖：**
```bash
pip install -r requirements.txt
```

**前端依赖：**
```bash
cd web
npm install
```

**安装 Playwright 浏览器（用于获取 Cookie）：**
```bash
playwright install chromium
```

### 2. 初始化项目

```bash
python -m src.cli.main init
```

### 3. 启动服务

**方式一：使用 Windows 批处理文件（推荐）**
```bash
scripts/启动.bat
```

**方式二：分别启动**

后端 API（端口自动分配）：
```bash
python start_web.py
# 端口从 9000 开始自动分配
# 启动后会显示实际端口号和 API 文档地址
```

前端：
```bash
cd web
npm run dev
# 运行在 http://localhost:5173
```

### 4. 停止服务

**使用停止脚本**
```bash
scripts/stop.bat
```

**手动停止**
- 后端：按 `Ctrl+C`
- 前端：按 `Ctrl+C`

### 4. 使用系统

1. 访问 http://localhost:5173 打开 Web 界面
2. 注册新用户（需要提供拼多多 Cookie）
3. 登录后使用功能

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册新用户（含 PDD Cookie） |
| POST | `/api/auth/login` | 登录并获取令牌 |
| POST | `/api/auth/logout` | 登出 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/auth/update-pdd-config` | 更新 PDD Cookie |

### 主要接口（需要认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 获取用户状态 |
| POST | `/api/checkin` | 每日签到领积分 |
| POST | `/api/grab` | 使用积分抢券 |
| GET | `/api/records/checkin` | 签到历史 |
| GET | `/api/records/grab` | 抢券历史 |
| GET | `/api/stats` | 统计数据 |

### 调度器接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/scheduler/status` | 获取调度器状态 |
| GET | `/api/scheduler/schedules` | 获取所有调度配置 |
| GET | `/api/scheduler/schedules/{name}` | 获取调度配置详情 |
| GET | `/api/scheduler/history` | 获取执行历史 |
| POST | `/api/scheduler/control` | 控制调度器（启动/停止/重载） |
| POST | `/api/scheduler/schedules/{name}/toggle` | 切换调度启用状态 |
| POST | `/api/scheduler/schedules/{name}/execute` | 立即执行指定任务 |

**认证方式：** 在请求头中添加 `Authorization: Bearer <token>`

## 百亿补贴系统

拼多多百亿补贴项目的专用系统：

- **每日打卡** - 每天自动打卡领积分
- **积分抢券** - 使用 100 积分抢 5 元优惠券
- **限制规则**：
  - 每天可打卡 1 次
  - 每周可使用积分抢券 2 次

## 命令行工具

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

## 配置说明

### 调度器配置 (config/scheduler.yaml)

调度器配置文件用于设置定时抢券任务，支持多平台、多时间点、多条件判断：

```yaml
# 定时抢券示例
schedules:
  - name: "百亿补贴5元券定时抢"
    enabled: true
    platform: "pinduoduo"
    task_type: "baibuti_grab"
    times:
      - "10:00"
      - "14:00"
      - "21:00"
    conditions:
      # 今天没抢到过券
      - type: "daily_limit"
        limit_type: "grab_success"
        max_count: 0
      # 本周积分抢券未超限（最多2次/周）
      - type: "weekly_limit"
        limit_type: "points_grab"
        max_count: 2
    params:
      coupon_type: "5元无门槛券"
      use_points: 100
```

**配置说明：**
- `times`: 执行时间点列表（24小时制）
- `conditions`: 执行条件（所有条件都满足才执行）
  - `daily_limit`: 每日限制
  - `weekly_limit`: 每周限制
- `params`: 任务参数

### 主配置 (config/config.yaml)

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

### 拼多多 Cookie 格式

每个用户需要配置自己的拼多多 Cookie，必须包含：

- `PDDAccessToken` - 主认证令牌
- `pdd_user_id` - 用户标识符
- 其他会话 Cookie

**获取 Cookie 的方式：**
1. 使用项目提供的 Cookie 获取工具：`scripts/手动输入Cookie.bat`
2. 使用浏览器开发者工具手动获取

## Cookie 管理工具

项目提供了多种 Cookie 获取方式，位于 `tools/` 目录：

| 文件 | 说明 |
|------|------|
| `tools/快速Cookie提取.py` | 快速提取 Cookie |
| `tools/快速配置Cookie.py` | Cookie 配置工具 |
| `tools/方案1_商品页面登录.py` | 通过商品页面登录 |
| `tools/方案2_手机直接获取.py` | 手机直接获取 |
| `tools/方案3_扫码登录.py` | 扫码登录 |
| `tools/如何找到正确的Cookie.py` | Cookie 获取指南 |
| `tools/验证新Cookie.py` | 验证 Cookie 有效性 |
| `scripts/手动输入Cookie.bat` | 交互式 Cookie 输入工具 |

## 测试

```bash
# 测试拼多多适配器功能
python test_pdd_adapter.py

# 测试 Cookie 认证
python test_login.py

# 测试 Web 系统
python test_web_system.py

# 测试百亿补贴 API
python tests/test_baibuti_api.py
```

## 开发指南

### 添加新平台适配器

1. 在 `src/platforms/` 创建平台目录
2. 继承 `BaseAdapter` 类：

```python
from ..base_adapter import BaseAdapter
from ...models.task import TaskResult

class MyPlatformAdapter(BaseAdapter):
    platform_name = "myplatform"
    platform_type = "myplatform"

    async def login(self) -> TaskResult:
        # 实现登录逻辑
        pass

    async def grab_coupon(self, coupon) -> TaskResult:
        # 实现抢券逻辑
        pass

    async def check_coupon_status(self, coupon) -> dict:
        # 实现状态检查
        pass
```

3. 在 `config/config.yaml` 添加平台配置

### 数据库扩展

所有数据模型继承自 `Base` 类 ([src/database/base.py](src/database/base.py)):

```python
from sqlalchemy import Column, Integer, String
from .base import Base

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # 自动生成 created_at, updated_at
```

CRUD 操作使用统一的 CRUD 类 ([src/database/crud.py](src/database/crud.py)):

```python
from .crud import GenericCRUD

class MyCRUD(GenericCRUD[MyModel, int]):
    pass
```

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

## 注意事项

1. **Cookie 过期** - PDD Cookie 会定期过期，登录失败时使用 Cookie 获取工具刷新
2. **请求限制** - 系统包含请求节流以避免反爬虫检测，谨慎调整 `scheduler.max_workers`
3. **时间精度** - 调度器使用毫秒级精度，`precise_grab()` 方法允许预先调度请求
4. **账号安全** - 切勿提交 `config/accounts.yaml` 或 `.env` 文件到版本控制
5. **认证令牌** - API 认证令牌会过期，需要重新登录

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 登录失败 | 运行 `python test_pdd_adapter.py` 验证 Cookie |
| 数据库错误 | 删除 `data/baibuti.db` 并重启以重新初始化 |
| 导入错误 | 确保虚拟环境已激活且依赖已安装 |
| 认证错误（401） | 检查是否设置了 `Authorization: Bearer <token>` 请求头 |
| Cookie 错误 | 每个用户必须配置自己的 PDD Cookie |

## Claude Code 技能

项目包含 Claude Code 技能包，用于辅助开发：

### python-lib-finder

快速查找 Python 开发库的技能，按分类组织常用库：

- Web 框架和 API
- 数据科学和机器学习
- 测试框架
- 数据库 ORM
- 异步编程
- CLI 和终端工具
- 文件格式处理
- 网页爬取
- DevOps 工具

### skill-creator

用于创建新的 Claude Code 技能的工具，包含：
- 技能初始化脚本
- 技能打包脚本
- 最佳实践指南

技能文件位于 [`.claude/skills/`](.claude/skills/) 目录。

## 许可证

MIT License

## 免责声明

本项目仅供学习交流使用，使用者需自行承担使用本工具产生的所有风险和责任。开发者不对使用本工具造成的任何损失负责。
