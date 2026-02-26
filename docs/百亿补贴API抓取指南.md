# 百亿补贴API抓取指南

## 方法一：使用 Charles Proxy 抓包（推荐）

### 1. 安装 Charles Proxy
- 下载地址：https://www.charlesproxy.com/download
- 安装并启动 Charles

### 2. 配置 iOS 设备
1. 确保 iOS 设备和电脑在同一 Wi-Fi 网络
2. 在 iOS 设备上打开 **设置 > Wi-Fi**
3. 点击当前连接的 Wi-Fi 右边的 **(i)** 图标
4. 滚动到底部，点击 **HTTP 代理 > 手动**
5. 服务器：输入您电脑的 IP 地址
6. 端口：8888

### 3. 安装 SSL 证书
1. 在 iOS 设备的 Safari 浏览器访问：`http://charles`
2. 点击 **Charles Certificate** 下载证书
3. 打开 **设置 > 已下载描述文件**，安装证书
4. 打开 **设置 > 通用 > 关于本机 > 证书信任设置**
5. 启用 **charlesproxy.com** 的完全信任

### 4. 在拼多多 App 中操作
1. 打开拼多多 App
2. 进入 **百亿补贴** 页面
3. 执行打卡操作
4. 在 Charles 中查看请求

### 5. 查找打卡 API
在 Charles 中查找包含以下关键词的请求：
- `sign_in` 或 `signin`
- `checkin` 或 `check_in`
- `daily`
- `points`
- `reward`

## 方法二：使用 mitmproxy 抓包

### 安装 mitmproxy
```bash
pip install mitmproxy
```

### 启动代理
```bash
mitmweb --listen-host 0.0.0.0 --listen-port 8080
```

### 配置 iOS 设备
同 Charles 方法，使用电脑 IP 和端口 8080

### 安装证书
1. 访问 `http://mitm.it`
2. 下载 iOS 证书
3. 安装并信任证书

## 方法三：使用 Flutter 抓包

如果您有 Flutter 项目的源代码：

### 1. 添加 HTTP 日志
在 `main.dart` 中添加：

```dart
import 'dart:developer' as developer;

void main() {
  // 开启 HTTP 请求日志
  HttpClient.enableTimelineLogging = true;

  runApp(MyApp());
}
```

### 2. 使用 Dio 添加拦截器
```dart
import 'package:dio/dio.dart';

final dio = Dio();

dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    developer.log('REQUEST: ${options.uri}');
    developer.log('HEADERS: ${options.headers}');
    developer.log('DATA: ${options.data}');
    return handler.next(options);
  },
  onResponse: (response, handler) {
    developer.log('RESPONSE: ${response.data}');
    return handler.next(response);
  },
  onError: (DioException error, handler) {
    developer.log('ERROR: ${error.message}');
    return handler.next(error);
  },
));
```

### 3. 查看日志
在 Xcode 或 VS Code 的调试控制台查看 HTTP 请求日志

## 需要收集的信息

### 打卡 API
- [ ] 请求方法 (GET/POST)
- [ ] 请求 URL
- [ ] 请求头 (Headers)
- [ ] 请求参数 (Query/Body)
- [ ] Cookie 格式和必需字段
- [ ] 响应数据格式

### 抢券 API
- [ ] 请求方法 (GET/POST)
- [ ] 请求 URL
- [ ] 请求头 (Headers)
- [ ] 请求参数 (Query/Body)
- [ ] Cookie 格式和必需字段
- [ ] 响应数据格式

## 示例格式

### 请求示例
```
POST https://mobile.yangkeduo.com/api/redflix/user_sign_in

Headers:
  User-Agent: Mozilla/5.0...
  Cookie: pdd_user_id=xxx; PDDAccessToken=xxx
  Content-Type: application/json

Body:
{
  "user_id": "xxx",
  "timestamp": 1234567890
}
```

### 响应示例
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "points": 10,
    "total_points": 100,
    "signed": true
  }
}
```

## 获取信息后

将收集到的 API 信息提供给我，我会更新 `src/platforms/pinduoduo/baibuti.py` 文件，接入真实的 API。

## 联系方式

如有问题，请随时反馈！
