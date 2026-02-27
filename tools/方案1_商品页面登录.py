"""
方案1：通过拼多多商品页面获取Cookie

步骤：
1. Chrome浏览器按F12
2. Ctrl+Shift+M 切换到移动端模式
3. 访问任意拼多多商品页面（例如）
   https://mobile.yangkeduo.com/goods.html?goods_id=xxxxx
   或打开手机拼多多，分享链接到电脑

4. 页面顶部或底部会有"登录"按钮

5. 点击登录，选择微信扫码

6. 登录成功后，F12 → Application → Cookies → https://h5.pinduoduo.com

7. 找到并复制：
   - pdd_token (必需)
   - customer_id (必需)

8. 运行: python 快速配置Cookie.py
"""