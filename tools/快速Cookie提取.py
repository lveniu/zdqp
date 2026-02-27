"""
快速Cookie提取指南 - 从已打开的浏览器
"""

print("""
============================================================
    快速Cookie提取指南
============================================================

在已经打开的浏览器窗口中：

步骤1：查看开发者工具
- 如果没有打开，按 F12 打开

步骤2：提取Cookie（任选一种方法）

【方法A】使用Console（最快）
---------------------------
1. 切换到 "Console" 标签
2. 输入以下命令并回车：

   copy(document.cookie)

3. 这会复制所有Cookie到剪贴板
4. 然后运行：python manual_cookie_input.py
5. 粘贴Cookie

【方法B】使用Application标签
---------------------------
1. 切换到 "Application" 标签
2. 左侧找到 Cookies → https://h5.pinduoduo.com
3. 找到并复制这些Cookie的值：
   - pdd_token (最重要)
   - customer_id
   - pdd_user_id (如果有)

4. 手动拼接格式：
   pdd_token=你复制的值; customer_id=你复制的值

5. 运行：python manual_cookie_input.py
6. 粘贴Cookie字符串

【方法C】使用Network标签
---------------------------
1. 切换到 "Network" 标签
2. 刷新页面（F5）
3. 点击任意请求
4. 右侧找到 "Request Headers"
5. 找到 Cookie 字段
6. 复制整个Cookie值
7. 运行：python manual_cookie_input.py
8. 粘贴

============================================================
""")

print("\n现在你可以：")
print("1. 在已打开的浏览器中按F12")
print("2. 使用Console命令: copy(document.cookie)")
print("3. 运行此命令提取Cookie：\n")

import subprocess
subprocess.run(["python", "manual_cookie_input.py"])
