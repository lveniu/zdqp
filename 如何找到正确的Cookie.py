"""
如何找到正确的拼多多请求和Cookie

步骤详解：
"""

print("""
============================================================
    找到拼多多正确的请求和Cookie
============================================================

方法一：使用Chrome DevTools Network标签
------------------------------------------------------------

1. 打开Chrome浏览器
2. 访问: https://mobile.yangkeduo.com/index.html
3. 按F12打开开发者工具
4. 切换到 "Network" 标签
5. 登录你的拼多多账号（微信扫码）
6. 登录成功后，在Network中找到以下请求：

   关键请求URL特征：
   - 包含 "user" 的请求 (用户信息)
   - 包含 "api" 的请求 (API接口)
   - 域名包含 "yangkeduo.com" 或 "pinduoduo.com"

7. 点击该请求
8. 右侧 "Headers" → "Request Headers"
9. 找到 "Cookie:" 字段
10. 复制整个Cookie值


方法二：使用Application标签直接查看
------------------------------------------------------------

1. 登录后，F12打开开发者工具
2. 切换到 "Application" 标签
3. 左侧展开: Cookies → https://mobile.yangkeduo.com
4. 找到以下关键Cookie:

   必需Cookie:
   - PDDAccessToken (最重要)
   - pdd_user_id
   - api_uid

   可选但重要:
   - customer_id
   - pdd_vds
   - _nano_fp

5. 点击每个Cookie，复制其Value值
6. 手动拼接成格式:
   PDDAccessToken=xxx; pdd_user_id=yyy; api_uid=zzz


方法三：使用Console快速导出（最快）
------------------------------------------------------------

1. 登录后，F12 → Console标签
2. 输入以下命令并回车:

   copy(document.cookie)

3. 这会复制所有Cookie到剪贴板
4. 粘贴出来查看


方法四：筛选特定域名的Cookie
------------------------------------------------------------

1. F12 → Application → Cookies
2. 在搜索框输入: "yangkeduo" 或 "pinduoduo"
3. 只显示相关域名的Cookie
4. 逐个复制关键Cookie


验证Cookie是否有效
------------------------------------------------------------

找到Cookie后，可以测试：

1. F12 → Console标签
2. 输入:

   fetch('https://mobile.yangkeduo.com/user', {
     headers: {
       'Cookie': document.cookie
     }
   }).then(r=>r.json()).then(console.log)

3. 如果返回用户信息，说明Cookie有效


拼多多主要Cookie说明
------------------------------------------------------------

- PDDAccessToken: 访问令牌，最重要
- pdd_user_id: 用户ID
- api_uid: API用户标识
- pdd_vds: 设备标识
- customer_id: 客户ID
- _nano_fp: 浏览器指纹


注意事项
------------------------------------------------------------

1. 必须在登录后的页面提取Cookie
2. Cookie通常有有效期（7-30天）
3. 不同域名可能需要不同的Cookie
4. HTTPS页面只能获取HTTPS的Cookie

============================================================
""")
