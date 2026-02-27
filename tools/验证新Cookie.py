"""
验证新的PDD Cookie
"""
import asyncio
import httpx

# 新的Cookie
cookies_str = "api_uid=CipZCWmeWZJl6wCJGxTOAg==; _nano_fp=Xpm8XpUJnpPblpT8XT_P6fQ4r4FbgHPoQhalFu_a; webp=1; jrpl=Jv7lDi76gcpiZCVj9YgGztYxIasMUlnv; njrpl=Jv7lDi76gcpiZCVj9YgGztYxIasMUlnv; dilx=TRb6lpcqv3ve0Jt6jauhi; PDDAccessToken=N5G7FBOWT7VLFOZVTZOQSWU6MB56H4E24J7RFABK265BNDMI6LUQ123ec37; pdd_user_id=4895903724; pdd_user_uin=NEQKYJJANGXJGWR4OO3MDNU6ZY_GEXDA; pdd_vds=gajLSyXOFygPkmqmZaJajnFaVbSyjnKOkmgnkPVyHGViXbqbpNHNXLpbngG"

# 解析Cookie
cookies = {}
for item in cookies_str.split(";"):
    item = item.strip()
    if "=" in item:
        key, value = item.split("=", 1)
        cookies[key.strip()] = value.strip()

print("="*60)
print("PDD Cookie 验证")
print("="*60)
print()
print(f"解析到 {len(cookies)} 个Cookie")
print()

# 显示关键Cookie
print("关键Cookie:")
print(f"  PDDAccessToken: {cookies.get('PDDAccessToken', 'N/A')[:40]}...")
print(f"  pdd_user_id: {cookies.get('pdd_user_id', 'N/A')}")
print(f"  api_uid: {cookies.get('api_uid', 'N/A')}")
print(f"  pdd_vds: {cookies.get('pdd_vds', 'N/A')[:40]}...")
print()

# 测试多个可能的API端点
test_urls = [
    ("用户信息", "https://mobile.yangkeduo.com/user"),
    ("用户信息2", "https://h5.pinduoduo.com/user"),
    ("个人中心", "https://mobile.yangkeduo.com/api/ubi/user"),
]

async def test_all_endpoints():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.47.2560",
        "Referer": "https://h5.pinduoduo.com/",
        "Accept": "application/json, text/plain, */*",
    }

    async with httpx.AsyncClient(cookies=cookies, headers=headers, timeout=15, follow_redirects=True) as client:
        for name, url in test_urls:
            print(f"测试 {name}: {url}")
            try:
                response = await client.get(url)
                print(f"  状态码: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") or data.get("code", -1) == 0 or "result" in data:
                            print(f"  [成功] API返回有效数据!")
                            if "user" in data:
                                print(f"  用户数据: {str(data['user'])[:100]}")
                            else:
                                print(f"  响应: {str(data)[:200]}")
                        else:
                            print(f"  响应: {str(data)[:200]}")
                    except:
                        content = response.text[:200]
                        print(f"  内容: {content}")
                        if "用户" in content or "nickname" in content:
                            print(f"  [可能有效] HTML中包含用户信息")
                elif response.status_code in [301, 302]:
                    print(f"  [重定向] 需要跟随重定向")
                else:
                    print(f"  响应: {response.text[:100]}")

            except Exception as e:
                print(f"  [错误] {e}")

            print()

print("="*60)
print("开始测试...")
print("="*60)
print()

asyncio.run(test_all_endpoints())

print()
print("="*60)
print("如果看到 '[成功]' 或 '[可能有效]'，说明Cookie有效")
print("="*60)
