"""
方法一：使用Chrome DevTools移动端模拟获取Cookie
最简单可靠的方法
"""

print("""
============================================================
    方法一：Chrome移动端模拟获取Cookie
============================================================

步骤：

1. 打开 Chrome 浏览器

2. 按 F12 打开开发者工具

3. 点击 DevTools 左上角的"设备图标"或按 Ctrl+Shift+M
   （切换到移动端模拟模式）

4. 在顶部设备选择栏中选择：
   - 选择 "iPhone 12 Pro" 或 "Samsung Galaxy S21"
   - 或者点击 "Edit..." 添加自定义设备

5. 在地址栏输入：https://h5.pinduoduo.com

6. 点击登录，选择"微信扫码登录"

7. 用手机微信扫描屏幕上的二维码

8. 登录成功后，在 DevTools 中：
   - 切换到 "Application" 标签
   - 左侧找到 "Cookies" → "https://h5.pinduoduo.com"
   - 找到以下关键Cookie：
     * pdd_token
     * customer_id
     * pdd_user_id (如果有)

9. 复制Cookie：
   方法A - 逐个复制：
     - 双击每个Cookie的Value值复制
     - 手动拼接成格式：pdd_token=xxx; customer_id=yyy

   方法B - 使用Console导出所有Cookie：
     - 在Console标签中输入并回车：
       document.cookie.split(';').forEach(c=>console.log(c))
     - 复制输出的所有内容

10. 运行手动输入工具：
    python manual_cookie_input.py

11. 粘贴Cookie字符串

============================================================
""")
