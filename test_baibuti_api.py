"""
百亿补贴API测试脚本
用于测试真实的打卡和抢券API
"""

import asyncio
import json
from src.platforms.pinduoduo.baibuti import BaiButiManager
from src.models.platform import Account


async def test_checkin():
    """测试打卡功能"""
    print("=" * 60)
    print("百亿补贴打卡测试")
    print("=" * 60)

    # 从配置文件或用户输入获取Cookie
    cookies = input("\n请输入拼多多Cookie: ").strip()

    if not cookies:
        print("Cookie不能为空！")
        return

    # 创建账户对象
    account = Account(
        platform="pinduoduo",
        username="test_user",
        cookies=cookies,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002F2F) NetType/WIFI Language/zh_CN",
        enabled=True
    )

    # 创建管理器
    manager = BaiButiManager(account)

    try:
        print("\n[1/2] 测试打卡功能...")
        result = await manager.daily_checkin()

        print("\n打卡结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  消息: {result.get('message')}")
        print(f"  获得积分: {result.get('points', 0)}")
        print(f"  总积分: {result.get('total_points', 0)}")

        if result.get('api_used'):
            print(f"  使用的API: {result.get('api_used')}")

        print("\n[2/2] 测试查询积分...")
        points_result = await manager.query_points()

        print("\n查询结果:")
        print(f"  成功: {points_result.get('success')}")
        print(f"  当前积分: {points_result.get('points', 0)}")
        print(f"  可抢券: {points_result.get('can_grab', False)}")

    finally:
        await manager.close()

    print("\n测试完成！")


async def test_with_api_config(api_url, api_method="POST", api_params=None):
    """
    使用指定API配置测试

    Args:
        api_url: API地址
        api_method: 请求方法 (GET/POST)
        api_params: 请求参数字典
    """
    print("=" * 60)
    print("测试指定API")
    print("=" * 60)
    print(f"\nAPI地址: {api_url}")
    print(f"请求方法: {api_method}")
    print(f"请求参数: {json.dumps(api_params, indent=2, ensure_ascii=False)}")

    cookies = input("\n请输入拼多多Cookie: ").strip()

    if not cookies:
        print("Cookie不能为空！")
        return

    account = Account(
        platform="pinduoduo",
        username="test_user",
        cookies=cookies,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        enabled=True
    )

    manager = BaiButiManager(account)

    try:
        client = await manager._get_client()

        print("\n发送请求...")

        if api_method.upper() == "GET":
            response = await client.get(api_url, params=api_params)
        else:
            response = await client.post(api_url, json=api_params)

        print(f"\n状态码: {response.status_code}")
        print(f"\n响应头: {dict(response.headers)}")
        print(f"\n响应内容:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)

    finally:
        await manager.close()


def interactive_test():
    """交互式测试"""
    print("\n" + "=" * 60)
    print("百亿补贴API测试工具")
    print("=" * 60)
    print("\n请选择测试模式:")
    print("1. 使用默认打卡API测试")
    print("2. 使用自定义API测试")
    print("3. 查看API抓取指南")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    if choice == "1":
        asyncio.run(test_checkin())
    elif choice == "2":
        print("\n请输入API信息:")
        api_url = input("API地址: ").strip()
        api_method = input("请求方法 (GET/POST，默认POST): ").strip() or "POST"
        api_params_str = input("请求参数 (JSON格式，可选): ").strip()

        api_params = None
        if api_params_str:
            try:
                api_params = json.loads(api_params_str)
            except json.JSONDecodeError:
                print("参数格式错误，使用空参数")
                api_params = {}

        asyncio.run(test_with_api_config(api_url, api_method, api_params))
    elif choice == "3":
        print("\n请查看文件: docs/百亿补贴API抓取指南.md")
        print("\n快速步骤:")
        print("1. 使用 Charles Proxy 或 mitmproxy 抓包")
        print("2. 在拼多多App中执行打卡操作")
        print("3. 查找包含 'sign_in' 或 'checkin' 的请求")
        print("4. 记录请求URL、方法和参数")
        print("5. 运行此脚本并选择选项2进行测试")
    else:
        print("无效选项！")


if __name__ == "__main__":
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
