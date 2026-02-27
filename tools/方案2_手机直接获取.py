"""
方案2：使用手机浏览器 + 电脑配合获取Cookie

这是最可靠的方法！

准备工作：
- 电脑和手机连接同一WiFi
- 或者使用USB数据线连接

步骤：

【方法A - 使用远程调试（推荐）】
-----------------------------------
1. 手机安装 Chrome 浏览器（Android）或使用 Safari（iPhone）

2. 安卓手机：
   - 打开 Chrome → 地址栏输入：chrome://inspect
   - 开启USB调试

3. iPhone：
   - 设置 → Safari → 高级 → Web检查器（开启）
   - 用数据线连接电脑

4. 电脑Chrome访问：chrome://inspect

5. 手机Chrome打开：https://h5.pinduoduo.com

6. 点击登录按钮（页面顶部或底部）

7. 微信扫码登录

8. 登录成功后，电脑Chrome的DevTools会自动连接到手机

9. 在DevTools中：
   - Application → Cookies → https://h5.pinduoduo.com
   - 复制 pdd_token 和 customer_id

【方法B - 使用网页版微信（简单）】
-----------------------------------
1. 电脑访问：https://wx.qq.com/

2. 手机微信扫码登录微信网页版

3. 在网页版微信中打开拼多多链接

4. 此时浏览器已经有了微信的登录态

5. 访问拼多多H5页面时会自动登录

6. F12 → Application → Cookies 复制

【方法C - 最简单 - 直接用手机分享】
-----------------------------------
1. 手机打开拼多多APP

2. 分享任意商品链接到微信

3. 微信中点击链接，选择"在浏览器中打开"

4. 系统浏览器（如小米浏览器）会打开链接

5. 此时会自动登录（因为从微信跳转）

6. 在地址栏输入：chrome://inspect 或查看Cookie
   - 安卓：使用Chrome远程调试查看
   - 或安装"Cookie查看器"类APP

7. 复制Cookie后运行：python 快速配置Cookie.py
"""