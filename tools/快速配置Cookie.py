"""
快速配置Cookie到config/accounts.yaml
只需提供Cookie值，自动生成配置文件
"""

import yaml
from pathlib import Path
from datetime import datetime

def create_pdd_config(pdd_token, customer_id="", user_id=""):
    """
    创建拼多多配置

    参数:
        pdd_token:拼多多Token (必需)
        customer_id: 客户ID (可选)
        user_id: 用户ID (可选)
    """
    # 构建Cookie字符串
    cookies = f"pdd_token={pdd_token}"
    if customer_id:
        cookies += f"; customer_id={customer_id}"

    # 默认User-Agent (小米13)
    user_agent = "Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.47.2560"

    # 创建账号配置
    account = {
        "platform": "pinduoduo",
        "username": user_id or customer_id or "13750005447",
        "password": "",
        "cookies": cookies,
        "user_agent": user_agent,
        "enabled": True,
        "metadata": {
            "device": "Xiaomi_13",
            "saved_at": datetime.now().isoformat(),
        }
    }

    # 保存到accounts.yaml
    config_file = Path("config/accounts.yaml")
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有配置
    existing = {"accounts": []}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            try:
                existing = yaml.safe_load(f) or {"accounts": []}
            except:
                pass

    # 更新或添加
    username = account["username"]
    updated = False
    for i, acc in enumerate(existing.get("accounts", [])):
        if acc.get("platform") == "pinduoduo" and acc.get("username") == username:
            existing["accounts"][i] = account
            updated = True
            print(f"[更新] 已更新账号: {username}")
            break

    if not updated:
        existing["accounts"].append(account)
        print(f"[新增] 已添加账号: {username}")

    # 保存
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(existing, f, allow_unicode=True, default_flow_style=False)

    print(f"\n[保存] 配置已保存到: {config_file}")
    print("\n配置内容:")
    print(f"  平台: {account['platform']}")
    print(f"  用户名: {account['username']}")
    print(f"  Cookie: {account['cookies'][:50]}...")
    print(f"  User-Agent: {account['user_agent'][:50]}...")
    print("\n下一步:")
    print("  python -m src.cli.main pdd login")
    print("  # 测试登录是否成功")

if __name__ == "__main__":
    print("="*60)
    print("    拼多多Cookie快速配置工具")
    print("="*60)
    print("\n请提供Cookie信息:")
    print("(如果某项没有，直接回车跳过)\n")

    pdd_token = input("请输入 pdd_token (必需): ").strip()
    if not pdd_token:
        print("\n[错误] pdd_token 不能为空！")
        print("\n获取pdd_token的方法:")
        print("1. 用Chrome打开 https://h5.pinduoduo.com")
        print("2. 按F12 → Application → Cookies")
        print("3. 找到 pdd_token 并复制其值")
        exit(1)

    customer_id = input("请输入 customer_id (可选): ").strip()
    user_id = input("请输入 user_id (可选): ").strip()

    print("\n正在创建配置...")
    create_pdd_config(pdd_token, customer_id, user_id)
