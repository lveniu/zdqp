# 整点抢券 - Web界面

## 🎯 简介

这是一个拼多多百亿补贴自动化抢券系统，具有现代化的Web界面，支持：

- ✅ **每日打卡** - 自动打卡领积分
- ✅ **积分管理** - 实时查询积分余额
- ✅ **自动抢券** - 准点抢5元无门槛券
- ✅ **智能限制** - 自动遵守1天1次、1周2次规则
- ✅ **数据持久化** - SQLite数据库存储
- ✅ **Web界面** - Vue3 + Element Plus现代化UI
- ✅ **实时更新** - 自动刷新状态

## 🚀 快速开始

### Windows用户

1. **一键启动** (推荐):
   ```bash
   双击运行 start.bat
   ```

2. **手动启动**:
   ```bash
   # 启动后端
   python start_web.py

   # 新终端启动前端
   cd web
   npm install  # 首次运行
   npm run dev
   ```

### 访问界面

打开浏览器访问: **http://localhost:5173**

## 📸 界面预览

### 主界面
- 🎯 顶部导航 - 显示用户信息
- 💰 积分卡片 - 实时积分余额
- ⚡ 快捷操作 - 打卡、抢券按钮
- 📊 统计信息 - 次数、价值统计
- 📅 记录查询 - 打卡、抢券历史

## 📁 项目结构

```
整点抢券/
├── 📁 src/                    # 源代码
│   ├── api/                   # FastAPI后端
│   ├── database/              # SQLite数据库
│   └── platforms/             # 百亿补贴逻辑
├── 📁 web/                    # Vue前端
│   ├── src/
│   │   ├── App.vue           # 主组件
│   │   ├── api.js            # API封装
│   │   └── main.js           # 入口
│   └── package.json
├── 📁 data/                   # 数据库文件(自动创建)
├── 📄 start_web.py            # 后端启动脚本
├── 📄 start.bat               # 一键启动脚本
└── 📄 WEB_GUIDE.md            # 详细使用指南
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代化Python Web框架
- **SQLite** - 轻量级数据库
- **SQLAlchemy** - ORM框架
- **Uvicorn** - ASGI服务器

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3 UI组件库
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP客户端

## 📖 使用说明

### 1. 打卡领积分
- 点击左侧"📅 每日打卡"按钮
- 成功后获得积分(通常+10)
- 每天只能打卡一次

### 2. 抢5元券
- 积分>=100时,"🎁 抢5元券"按钮可用
- 点击抢券,消耗100积分
- 自动遵守限制(1天1次,1周2次)

### 3. 查看记录
- 切换Tab查看打卡/抢券记录
- 显示最近7天的历史
- 实时更新

### 4. 刷新状态
- 点击"刷新状态"按钮
- 自动30秒刷新一次

## 🔧 配置

### 修改账号

编辑 `src/api/main.py`:

```python
ACCOUNT = Account(
    platform="pinduoduo",
    username="你的手机号",
    cookies="你的Cookie",
    user_agent="浏览器UA",
    enabled=True,
)
```

### 获取Cookie

1. 打开 https://mobile.yangkeduo.com/
2. 登录账号
3. F12打开开发者工具
4. Network → 找到请求 → 复制Cookie

## 📊 API接口

### 基础URL
```
http://localhost:8000/api
```

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/status` | GET | 获取状态 |
| `/checkin` | POST | 执行打卡 |
| `/grab` | POST | 执行抢券 |
| `/records/checkin` | GET | 打卡记录 |
| `/records/grab` | GET | 抢券记录 |
| `/stats` | GET | 统计信息 |

### API文档

访问: http://localhost:8000/docs

## 💾 数据库

### 位置
```
data/baibuti.db
```

### 表结构
- `checkin_records` - 打卡记录
- `grab_records` - 抢券记录
- `points_records` - 积分记录
- `system_config` - 系统配置

## ❓ 常见问题

### Q: 前端连接不上后端？
**A:** 确保后端已启动在 http://localhost:8000

### Q: 点击按钮没反应？
**A:** 打开浏览器控制台(F12)查看错误信息

### Q: 积分不够怎么办？
**A:** 先执行"每日打卡"累积积分

### Q: Cookie过期了？
**A:** 重新获取Cookie并更新到配置

### Q: 如何修改端口？
**A:**
- 后端: 修改 `start_web.py` 中的 `port=8000`
- 前端: 修改 `web/vite.config.js` 中的 `target`

## 📝 注意事项

1. **Cookie有效期** - Cookie会过期,需要定期更新
2. **网络连接** - 确保网络稳定
3. **浏览器兼容** - 推荐使用Chrome/Edge
4. **数据备份** - 定期备份 `data/baibuti.db`

## 🔒 安全建议

1. 不要将包含Cookie的代码上传到公开仓库
2. 定期更换Cookie
3. 使用强密码保护系统
4. 在生产环境使用HTTPS

## 📚 文档

- [详细使用指南](WEB_GUIDE.md) - 完整的使用文档
- [百亿补贴功能说明](BAIBUTI_GUIDE.md) - 命令行版本指南
- [项目状态](STATUS.md) - 整体项目状态

## 🎉 功能特性

- ✨ **现代化UI** - Element Plus组件库
- 🔄 **实时更新** - 自动刷新状态
- 💾 **数据持久化** - SQLite存储
- 📱 **响应式设计** - 适配各种屏幕
- 🚀 **快速启动** - 一键启动脚本
- 📊 **数据统计** - 完整的统计展示
- 🛡️ **智能限制** - 自动遵守规则

## 🚧 待开发

- [ ] 用户登录系统
- [ ] 多账号管理
- [ ] 定时任务配置
- [ ] 通知推送(微信/邮件)
- [ ] 数据导出功能
- [ ] 移动端适配优化

## 📄 许可证

MIT License

---

**版本**: v1.0.0
**更新时间**: 2026-02-25
**状态**: ✅ 可用
