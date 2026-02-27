"""
方法二：使用真机 + Charles/Fiddler 抓包
获取最真实的APP Cookie
"""

print("""
============================================================
    方法二：真机抓包获取Cookie
============================================================

准备工作：
- 下载并安装 Charles Proxy (https://www.charlesproxy.com/)
  或 Fiddler (https://www.telerik.com/fiddler)

步骤（以Charles为例）：

1. 安装并启动 Charles

2. 配置端口：
   - Help → Local IP Address → 查看本机IP (如 192.168.1.100)
   - Proxy → Proxy Settings → Port: 8888

3. 手机连接同一WiFi

4. 手机配置代理：
   - iPhone: 设置 → 无线局域网 → 点击WiFi详情 → HTTP代理 → 手动
     服务器：电脑IP (192.168.1.100)
     端口：8888
   - Android: 长按WiFi → 修改网络 → 高级选项 → 代理 → 手动
     服务器：电脑IP
     端口：8888

5. 电脑安装SSL证书：
   - Charles 会弹窗提示手机请求连接
   - 点击 "Allow"
   - Help → SSL Proxying → Install Charles Root Certificate

6. 手机安装SSL证书：
   - iPhone: Safari访问 chls.pro/ssl → 下载并安装
     设置 → 通用 → 描述文件与设备管理 → 信任
   - Android: 浏览器访问 chls.pro/ssl → 下载
     设置 → 安全 → 安装证书 → 启用

7. 配置SSL代理：
   - Proxy → SSL Proxying Settings
   - 添加：*.pinduoduo.com:443 和 *.yangkeduo.com:443

8. 手机打开拼多多APP

9. Charles 中会显示所有请求

10. 找到包含 Cookie 的请求（如用户信息接口）

11. 查看请求头中的 Cookie，复制

12. 运行：python manual_cookie_input.py
    粘贴Cookie

============================================================
""")
