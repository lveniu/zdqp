@echo off
chcp 65001 >nul
echo ============================================================
echo           拼多多Cookie手动输入工具
echo ============================================================
echo.
echo 请先按以下步骤获取Cookie:
echo.
echo 1. 在打开的浏览器中按F12
echo 2. 切换到 Application 标签
echo 3. 左侧找到 Cookies ^> https://h5.pinduoduo.com
echo 4. 找到 pdd_token 和 customer_id
echo 5. 复制这两个Cookie的值
echo.
echo 格式: pdd_token=值; customer_id=值
echo.
pause

python manual_cookie_input.py

pause
