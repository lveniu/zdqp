# 百亿补贴API配置指南

## 概述

系统已更新为支持自定义API配置。您可以通过修改配置文件来接入真实的百亿补贴打卡和抢券API。

## 配置文件位置

```
config/baibuti_api.json
```

## 配置文件格式

```json
{
  "checkin_apis": [
    {
      "method": "POST",
      "path": "/api/xxx/sign_in",
      "enabled": true,
      "params": {
        "user_id": "",
        "timestamp": 0
      }
    }
  ],
  "points_api": {
    "method": "GET",
    "path": "/api/xxx/assets",
    "params": {}
  },
  "grab_api": {
    "method": "POST",
    "path": "/api/xxx/grab",
    "params": {
      "coupon_type": "no_threshold_5"
    }
  }
}
```

## 配置项说明

### checkin_apis (打卡API列表)

支持配置多个打卡API端点，系统会依次尝试：

```json
{
  "checkin_apis": [
    {
      "method": "POST",           // 请求方法: GET/POST
      "path": "/api/xxx/sign_in", // API路径
      "enabled": true,            // 是否启用
      "params": {                 // 请求参数
        "user_id": "",
        "timestamp": 0
      }
    }
  ]
}
```

### points_api (积分查询API)

```json
{
  "points_api": {
    "method": "GET",
    "path": "/api/xxx/assets",
    "params": {}
  }
}
```

### grab_api (抢券API)

```json
{
  "grab_api": {
    "method": "POST",
    "path": "/api/xxx/grab",
    "params": {
      "coupon_type": "no_threshold_5"
    }
  }
}
```

## 获取真实API的方法

### 方法1: 使用Charles Proxy抓包（推荐）

1. **下载安装 Charles**
   - 官网: https://www.charlesproxy.com/download/

2. **配置iOS设备代理**
   - iOS设置 > Wi-Fi > 点击当前网络 > HTTP代理 > 手动
   - 服务器: 电脑IP地址
   - 端口: 8888

3. **安装SSL证书**
   - Safari访问: `http://charles`
   - 下载并安装证书
   - 设置 > 通用 > 关于本机 > 证书信任设置 > 启用完全信任

4. **在拼多多App中操作**
   - 打开拼多多App
   - 进入百亿补贴页面
   - 执行打卡操作
   - 在Charles中查找请求

5. **查找API请求**
   在Charles中搜索关键词:
   - `sign_in` / `signin`
   - `checkin` / `check_in`
   - `daily`
   - `points`
   - `bailbuti` / `百亿补贴`

### 方法2: 使用mitmproxy

```bash
pip install mitmproxy
mitmweb --listen-host 0.0.0.0 --listen-port 8080
```

配置同Charles，端口改为8080。

### 方法3: Flutter抓包

如果您有Flutter源码，添加日志拦截器：

```dart
import 'package:dio/dio.dart';

final dio = Dio();

dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    print('REQUEST: ${options.uri}');
    print('HEADERS: ${options.headers}');
    print('DATA: ${options.data}');
    return handler.next(options);
  },
  onResponse: (response, handler) {
    print('RESPONSE: ${response.data}');
    return handler.next(response);
  },
));
```

## 配置真实API的步骤

1. **获取API信息**
   - 使用抓包工具获取真实API
   - 记录请求方法和路径
   - 记录请求参数和响应格式

2. **修改配置文件**
   ```bash
   # 编辑配置文件
   notepad config/baibuti_api.json
   ```

3. **更新API路径**
   将抓包获取的真实API路径填入配置文件

4. **测试API**
   ```bash
   python test_baibuti_api.py
   ```

5. **重启服务**
   配置会自动加载，无需重启

## 示例配置

### 示例1: 真实API（假设）

假设通过抓包获取到以下信息:

**打卡API:**
- URL: `https://mobile.yangkeduo.com/promotions/api/ddweb-daily-sign-in/sign-in/v3`
- 方法: POST
- 参数: `{"user_id": "xxx", "timestamp": 1234567890}`

配置:
```json
{
  "checkin_apis": [
    {
      "method": "POST",
      "path": "/promotions/api/ddweb-daily-sign-in/sign-in/v3",
      "enabled": true,
      "params": {
        "user_id": "",
        "timestamp": 0
      }
    }
  ]
}
```

### 示例2: 多个备用API

```json
{
  "checkin_apis": [
    {
      "method": "POST",
      "path": "/promotions/api/ddweb-daily-sign-in/sign-in/v3",
      "enabled": true
    },
    {
      "method": "POST",
      "path": "/api/redflix/user_sign_in",
      "enabled": true
    },
    {
      "method": "GET",
      "path": "/api/backup/signin",
      "enabled": false
    }
  ]
}
```

## 测试工具

### 运行测试脚本

```bash
python test_baibuti_api.py
```

选项:
1. 使用默认打卡API测试
2. 使用自定义API测试
3. 查看API抓取指南

### 在Web界面测试

1. 打开 http://localhost:5179
2. 添加账号并输入Cookie
3. 点击"每日打卡"按钮
4. 查看日志文件 `logs/api.log`

## 日志查看

### 查看实时日志

```bash
tail -f logs/api.log
```

### 日志位置

- API请求日志: `logs/api.log`
- 错误日志: `logs/error.log`

## 常见问题

### Q1: API返回401或403

**原因**: Cookie已过期或无效

**解决**: 重新获取Cookie并更新

### Q2: 所有API都失败

**原因**: API路径不正确或需要特殊参数

**解决**:
1. 使用抓包工具确认真实API路径
2. 检查是否需要签名或特殊参数
3. 查看日志了解详细错误

### Q3: 打卡成功但没有积分

**原因**: 响应格式解析失败

**解决**:
1. 查看日志中的响应内容
2. 根据实际响应格式调整代码

## 下一步

1. 使用抓包工具获取真实API
2. 更新 `config/baibuti_api.json`
3. 运行 `python test_baibuti_api.py` 测试
4. 在Web界面验证功能
