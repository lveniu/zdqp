"""
测试API日志输出
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import httpx

# 测试API
print("测试API日志输出...")
print()

try:
    # 测试状态接口
    print("[1/2] 测试 /api/status...")
    response = httpx.post(
        'http://localhost:9000/api/status',
        json={'cookies': 'pdd_user_id=test123456; api_uid=test_value'}
    )
    print(f"  状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  用户ID: {data.get('user_id')}")
        print(f"  积分: {data.get('current_points')}")
    else:
        print(f"  错误: {response.text}")

    print()
    print("[2/2] 检查日志文件...")
    with open('logs/api.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        recent_logs = lines[-10:] if len(lines) > 10 else lines
        print(f"  日志文件共 {len(lines)} 行")
        print("  最近10行:")
        for line in recent_logs:
            print(f"    {line.rstrip()}")

except Exception as e:
    print(f"  异常: {e}")
    import traceback
    traceback.print_exc()
