"""测试 RichOutput 类"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing RichOutput class...")

try:
    from src.core.rich_output import get_business_output, Icons

    output = get_business_output()

    print("Testing basic messages...")
    output.success("Success message")
    output.error("Error message")
    output.warning("Warning message")
    output.info("Info message")

    print("\nTesting panels...")
    output.success_panel("Operation completed!", title="Success")
    output.error_panel("Operation failed!", title="Error")

    print("\nTesting tables...")
    output.print_key_value({"key1": "value1", "key2": "value2"}, title="Test Table")

    print("\nTesting headers...")
    output.print_header("Test Header", level=1)

    print("\nAll RichOutput tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
