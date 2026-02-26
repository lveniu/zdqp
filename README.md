# 多平台抢券系统

基于Python实现的多平台自动抢券系统，支持淘宝、京东、美团、拼多多等主流电商平台。

## 特性

- **多平台支持** - 插件化架构，轻松扩展新平台
- **精确计时** - 毫秒级定时任务调度
- **异步高性能** - 基于asyncio实现高并发抢券
- **反爬虫对抗** - 支持代理池、随机User-Agent、浏览器模拟
- **自动重试** - 失败自动重试，指数退避策略
- **多渠道通知** - 支持微信、Telegram、钉钉、企业微信通知
- **日志完善** - 结构化日志，便于问题排查

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
│   ├── clients/           # 客户端
│   │   ├── http_client.py         # HTTP客户端
│   │   └── browser_client.py      # 浏览器客户端
│   ├── platforms/         # 平台适配器
│   │   ├── base_adapter.py        # 基类
│   │   ├── taobao/                # 淘宝
│   │   ├── jd/                    # 京东
│   │   ├── meituan/               # 美团
│   │   └── pinduoduo/             # 拼多多
│   ├── utils/             # 工具类
│   └── cli/               # 命令行接口
├── config/                # 配置文件
│   ├── config.yaml        # 主配置
│   └── accounts.yaml      # 账号配置
├── logs/                  # 日志目录
├── data/                  # 数据目录
└── requirements.txt       # 依赖
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

### 2. 初始化项目

```bash
python -m src.cli.main init
```

### 3. 配置系统

编辑 `config/config.yaml`:

```yaml
# 应用配置
app:
  env: development
  debug: true

# 代理配置（可选）
proxy:
  enabled: false
  pool_url: ""

# 通知配置（可选）
notification:
  serverchan_key: ""
  telegram_bot_token: ""
  telegram_chat_id: ""

# 调度器配置
scheduler:
  max_workers: 10  # 最大并发数
  retry_times: 3   # 重试次数
```

编辑 `config/accounts.yaml` 添加账号:

```yaml
accounts:
  - platform: taobao
    username: "your_username"
    password: "your_password"
    cookies: "your_cookies"
    enabled: true
```

### 4. 使用CLI

```bash
# 查看系统信息
python -m src.cli.main info

# 列出支持的平台
python -m src.cli.main platforms

# 抢券
python -m src.cli.main grab taobao \
  --url "https://xxx" \
  --time "2024-03-01 10:00:00" \
  --account "default"

# 查看调度器状态
python -m src.cli.main status

# 测试通知
python -m src.cli.main notify \
  --title "测试" \
  --content "这是一条测试消息"
```

## 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并配置:

```bash
# 应用配置
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO

# 代理配置
PROXY_ENABLED=false
PROXY_POOL_URL=

# 通知配置
NOTIFY_SERVERCHAN_KEY=
NOTIFY_TELEGRAM_BOT_TOKEN=
NOTIFY_TELEGRAM_CHAT_ID=

# 验证码服务
CAPTCHA_2CAPTCHA_API_KEY=
```

### 通知渠道配置

#### ServerChan (微信推送)

1. 访问 https://sct.ftqq.com/
2. 获取SendKey
3. 填入 `config.yaml` 的 `notification.serverchan_key`

#### Telegram

1. 创建Bot，获取Bot Token
2. 获取Chat ID
3. 填入配置文件

#### 钉钉

1. 创建群机器人
2. 获取Webhook地址
3. 填入配置文件

## 开发指南

### 添加新平台适配器

1. 在 `src/platforms/` 创建平台目录
2. 继承 `BaseAdapter` 类:

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

## 注意事项

1. **合法使用** - 请遵守各平台的使用条款，合理使用
2. **频率限制** - 建议设置合理的并发数和重试间隔
3. **账号安全** - 妥善保管账号信息，不要提交到版本控制
4. **Cookie有效期** - 定期更新Cookie，避免失效

## 待实现功能

- [ ] 完善各平台适配器
- [ ] 代理池自动获取
- [ ] 验证码自动识别
- [ ] Web管理界面
- [ ] 数据持久化
- [ ] 分布式抢券

## 技术栈

- **Python 3.12+**
- **asyncio** - 异步编程
- **httpx** - HTTP客户端
- **Playwright** - 浏览器自动化
- **APScheduler** - 任务调度
- **Pydantic** - 数据验证
- **Typer** - CLI框架
- **Loguru** - 日志系统

## 许可证

MIT License

## 免责声明

本项目仅供学习交流使用，使用者需自行承担使用本工具产生的所有风险和责任。开发者不对使用本工具造成的任何损失负责。
