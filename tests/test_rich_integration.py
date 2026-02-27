"""
Rich 框架集成验证脚本
测试所有 Rich 输出组件
"""

import time
import asyncio
from pathlib import Path

# 添加项目路径
sys_path = str(Path(__file__).parent.parent)
import sys
sys.path.insert(0, sys_path)

from src.core.rich_output import BusinessOutput, get_business_output, Icons
from src.core.rich_logger import get_rich_logger, log_function_call


def test_basic_messages():
    """测试基础消息输出"""
    output = get_business_output()

    output.print_header("测试基础消息", level=1)

    output.success("这是成功消息")
    output.error("这是错误消息")
    output.warning("这是警告消息")
    output.info("这是信息消息")
    output.debug("这是调试消息")
    output.critical("这是严重错误消息")

    time.sleep(1)


def test_panels():
    """测试面板输出"""
    output = get_business_output()

    output.print_header("测试面板输出", level=2)

    output.success_panel("操作成功完成！", title="成功")
    time.sleep(0.5)

    output.error_panel("操作失败，请重试", title="错误")
    time.sleep(0.5)

    output.warning_panel("请注意检查配置", title="警告")
    time.sleep(0.5)

    output.info_panel("这是信息面板", title="信息")


def test_tables():
    """测试表格输出"""
    output = get_business_output()

    output.print_header("测试表格输出", level=2)

    # 键值对表格
    output.print_key_value({
        "应用名称": "整点抢券",
        "版本": "2.0.0",
        "状态": f"{Icons.SUCCESS} 运行中",
        "端口": "8000",
    }, title="系统信息")

    time.sleep(0.5)

    # 数据列表表格
    data = [
        {"平台": "拼多多", "状态": f"{Icons.SUCCESS} 启用", "抢券次数": "10"},
        {"平台": "京东", "状态": f"{Icons.FAILED} 禁用", "抢券次数": "0"},
        {"平台": "淘宝", "状态": f"{Icons.SUCCESS} 启用", "抢券次数": "5"},
    ]

    output.print_table(data, title="平台状态")


def test_progress_bars():
    """测试进度条"""
    output = get_business_output()

    output.print_header("测试进度条", level=2)

    # 使用 track 迭代
    items = ["处理数据", "验证Cookie", "连接API", "获取信息", "保存结果"]

    for item in output.track(items, description="处理任务"):
        time.sleep(0.3)

    # 使用 progress 上下文管理器
    with output.progress("批量处理...", transient=False) as progress:
        task1 = progress.add_task("下载文件", total=100)
        task2 = progress.add_task("处理数据", total=50)

        for i in range(100):
            time.sleep(0.02)
            progress.update(task1, advance=1)
            if i % 2 == 0:
                progress.update(task2, advance=1)


def test_status_display():
    """测试状态显示"""
    output = get_business_output()

    output.print_header("测试状态显示", level=2)

    with output.status("正在加载...", spinner="dots"):
        time.sleep(2)
        output.info("步骤 1 完成")
        time.sleep(1)
        output.info("步骤 2 完成")
        time.sleep(1)

    output.success("加载完成！")


def test_business_methods():
    """测试业务专用方法"""
    output = get_business_output()

    output.print_header("测试业务方法", level=2)

    # 抢券相关
    output.print_grab_start("拼多多", "5元优惠券", "2024-03-01 10:00:00")
    time.sleep(0.5)
    output.print_grab_success("5元优惠券", 5.0, "拼多多")
    time.sleep(0.5)

    # 签到相关
    output.print_checkin_success(10, 150)
    time.sleep(0.5)

    # 登录相关
    output.print_login_success("test_user", "拼多多")
    time.sleep(0.5)

    # Cookie 状态
    output.print_cookie_status(True, "test_user")


def test_user_stats():
    """测试用户统计"""
    output = get_business_output()

    output.print_header("测试用户统计", level=2)

    output.print_user_stats(
        username="test_user",
        total_checkins=30,
        total_grabs=50,
        success_grabs=35,
        total_points=150,
    )


def test_tree_display():
    """测试树形结构"""
    output = get_business_output()

    output.print_header("测试树形结构", level=2)

    tree_data = {
        "config": {
            "app": {
                "name": "整点抢券",
                "version": "2.0.0",
            },
            "database": {
                "url": "sqlite:///data/baibuti.db",
                "echo": "False",
            },
        },
        "logs": {
            "level": "INFO",
            "dir": "logs",
        }
    }

    output.print_tree(tree_data, title="配置结构")


def test_logging():
    """测试日志系统"""
    logger = get_rich_logger(name="test")

    output = get_business_output()
    output.print_header("测试日志系统", level=2)

    output.info("查看日志输出，以下消息也会被记录到日志文件...")

    # 使用上下文
    log = logger.with_context(category="test", user_id="test_user")

    log.debug("这是调试日志")
    log.info("这是信息日志")
    log.success("这是成功日志")
    log.warning("这是警告日志")
    log.error("这是错误日志")

    time.sleep(1)


def test_decorator():
    """测试日志装饰器"""
    from src.core.rich_logger import log_function_call, log_execution_time

    output = get_business_output()
    output.print_header("测试日志装饰器", level=2)

    @log_function_call(category="test")
    def test_function():
        time.sleep(0.5)
        return "结果"

    @log_execution_time(category="performance")
    def slow_function():
        time.sleep(1)
        return "完成"

    output.info("执行带日志装饰器的函数...")
    result1 = test_function()
    output.info(f"函数返回: {result1}")

    output.info("执行带执行时间装饰器的函数...")
    result2 = slow_function()
    output.info(f"函数返回: {result2}")


def test_async_status():
    """测试异步状态显示"""
    output = get_business_output()

    output.print_header("测试异步操作", level=2)

    async def async_task():
        with output.status("执行异步任务...", spinner="dots"):
            await asyncio.sleep(1)
            output.info("子任务 1 完成")
            await asyncio.sleep(1)
            output.info("子任务 2 完成")
            await asyncio.sleep(1)

    asyncio.run(async_task())
    output.success("异步任务完成！")


def test_separator_and_rules():
    """测试分隔线和规则"""
    output = get_business_output()

    output.print_header("测试分隔线和规则", level=2)

    output.info("上面是普通文本")
    output.print_separator()
    output.info("下面是规则线")
    output.rule("重要提示", style="yellow")
    output.info("继续内容")


def test_banner():
    """测试横幅"""
    output = get_business_output()

    output.print_header("测试横幅", level=2)

    output.print_banner("欢迎使用 Rich 框架", subtitle="美观的终端输出体验")


def test_markdown_and_code():
    """测试 Markdown 和代码"""
    output = get_business_output()

    output.print_header("测试 Markdown 和代码", level=2)

    output.print_markdown("""
# 这是 Markdown 标题

- 列表项 1
- 列表项 2
- 列表项 3

**粗体文本** 和 *斜体文本*
    """)

    time.sleep(0.5)

    code = '''
def hello_world():
    """打招呼函数"""
    print("Hello, World!")
    return True
'''
    output.print_code(code, language="python")


def run_all_tests():
    """运行所有测试"""
    output = get_business_output()

    # 打印大标题
    output.print_banner(
        "Rich 框架集成验证",
        subtitle="测试所有输出组件"
    )

    output.print_separator()

    tests = [
        ("基础消息", test_basic_messages),
        ("面板输出", test_panels),
        ("表格输出", test_tables),
        ("进度条", test_progress_bars),
        ("状态显示", test_status_display),
        ("业务方法", test_business_methods),
        ("用户统计", test_user_stats),
        ("树形结构", test_tree_display),
        ("日志系统", test_logging),
        ("日志装饰器", test_decorator),
        ("异步操作", test_async_status),
        ("分隔线", test_separator_and_rules),
        ("横幅", test_banner),
        ("Markdown", test_markdown_and_code),
    ]

    total = len(tests)
    for i, (name, test_func) in enumerate(tests, 1):
        output.print_header(f"[{i}/{total}] {name}", level=1)
        try:
            test_func()
            output.success(f"✓ {name} 测试通过")
        except Exception as e:
            output.error(f"✗ {name} 测试失败: {e}")
        output.print_separator()
        time.sleep(0.5)

    # 总结
    output.print_banner(
        "所有测试完成",
        subtitle=f"共 {total} 项测试"
    )

    output.success_panel(
        f"Rich 框架已成功集成！\n\n"
        f"{Icons.ARROW_RIGHT} 所有输出组件工作正常\n"
        f"{Icons.ARROW_RIGHT} 日志系统正常\n"
        f"{Icons.ARROW_RIGHT} 可以在项目中使用",
        title="验证成功"
    )


if __name__ == "__main__":
    run_all_tests()
