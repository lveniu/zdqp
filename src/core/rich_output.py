"""
统一 Rich 输出组件库
提供美观的终端输出、进度条、表格、面板等组件
"""

import sys
import os
import time
from typing import Optional, List, Dict, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager

from rich.console import Console, Group
from rich.theme import Theme

# Windows 编码处理
if sys.platform == "win32":
    # 设置 UTF-8 编码
    try:
        import locale
        import codecs
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass  # 忽略错误，使用系统默认
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    DownloadColumn,
    TransferSpeedColumn,
    track,
)
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.live import Live
from rich.layout import Layout
from rich.box import ROUNDED, DOUBLE, SQUARE, HEAVY
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.traceback import install
from rich.status import Status
from rich.prompt import Prompt, Confirm
from rich import print as rprint


# ==================== 主题配置 ====================

class RichTheme:
    """Rich 终端主题配置"""

    # 自定义主题
    CUSTOM_THEME = Theme({
        # 日志级别颜色
        "trace": "dim white",
        "debug": "dim cyan",
        "info": "bold blue",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "critical": "bold white on red",

        # 应用颜色
        "primary": "bright_blue",
        "secondary": "bright_magenta",
        "accent": "cyan",

        # 状态颜色
        "status.running": "yellow",
        "status.success": "green",
        "status.failed": "red",
        "status.pending": "dim white",

        # 平台颜色 (使用 Rich 支持的颜色)
        "platform.pinduoduo": "red",
        "platform.jd": "bright_red",
        "platform.taobao": "yellow",
        "platform.meituan": "yellow",

        # 数据颜色
        "data.coupon": "green",
        "data.points": "yellow",
        "data.money": "bright_yellow",

        # 其他
        "timestamp": "dim",
        "path": "cyan",
        "url": "blue underline",
        "code": "dim black on white",
    })


# ==================== 图标配置 ====================

class Icons:
    """Unicode 图标集"""

    # 状态图标
    SUCCESS = "✓"
    FAILED = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    ERROR = "✖"
    CRITICAL = "☠"
    PENDING = "○"
    RUNNING = "⟳"
    SKIP = "⊘"

    # 操作图标
    ADD = "+"
    REMOVE = "-"
    EDIT = "✎"
    SEARCH = "🔍"
    DOWNLOAD = "⬇"
    UPLOAD = "⬆"
    COPY = "⎘"
    SAVE = "💾"
    DELETE = "🗑"

    # 方向图标
    ARROW_RIGHT = "→"
    ARROW_LEFT = "←"
    ARROW_UP = "↑"
    ARROW_DOWN = "↓"

    # 符号图标
    BULLET = "•"
    STAR = "★"
    HEART = "♥"
    CHECK = "✔"
    CROSS = "✖"
    DOT = "●"

    # 业务图标
    COUPON = "🎫"
    MONEY = "💰"
    POINTS = "⭐"
    GIFT = "🎁"
    COOKIE = "🍪"
    USER = "👤"
    TIME = "⏰"
    BELL = "🔔"

    # 平台图标
    PINDUODUO = "拼多多"
    JD = "京东"
    TAOBAO = "淘宝"
    MEITUAN = "美团"


# ==================== 输出级别 ====================

class OutputLevel(Enum):
    """输出级别枚举"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==================== 主输出类 ====================

class RichOutput:
    """
    统一的 Rich 输出管理器

    功能:
    - 统一的终端输出格式
    - 彩色日志消息
    - 表格、面板、树形结构
    - 进度条和状态显示
    - 交互式提示
    """

    _instance: Optional["RichOutput"] = None

    def __new__(cls, console: Optional[Console] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, console: Optional[Console] = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # 安装 Rich 异常处理
        install(show_locals=True)

        # 创建控制台
        if console is None:
            self.console = Console(theme=RichTheme.CUSTOM_THEME)
        else:
            self.console = console

        # 用于状态跟踪的 Live 显示
        self._live: Optional[Live] = None
        self._layout: Optional[Layout] = None

        self._initialized = True

    # ==================== 基础输出 ====================

    def print(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: Optional[str] = None,
        justify: Optional[str] = None,
        emoji: bool = True,
        markup: bool = True,
    ) -> None:
        """基础打印方法"""
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup)

    # ==================== 消息输出 ====================

    def success(self, message: str, icon: str = Icons.SUCCESS, **kwargs) -> None:
        """输出成功消息"""
        self.print(f"[bold green]{icon}[/bold green] {message}", **kwargs)

    def error(self, message: str, icon: str = Icons.ERROR, **kwargs) -> None:
        """输出错误消息"""
        self.print(f"[bold red]{icon}[/bold red] {message}", **kwargs)

    def warning(self, message: str, icon: str = Icons.WARNING, **kwargs) -> None:
        """输出警告消息"""
        self.print(f"[bold yellow]{icon}[/bold yellow] {message}", **kwargs)

    def info(self, message: str, icon: str = Icons.INFO, **kwargs) -> None:
        """输出信息消息"""
        self.print(f"[bold blue]{icon}[/bold blue] {message}", **kwargs)

    def debug(self, message: str, icon: str = None, **kwargs) -> None:
        """输出调试消息"""
        if icon is None:
            icon = Icons.BULLET
        self.print(f"[dim cyan]{icon}[/dim cyan] {message}", **kwargs)

    def critical(self, message: str, icon: str = Icons.CRITICAL, **kwargs) -> None:
        """输出严重错误消息"""
        self.print(f"[bold white on red]{icon}[/bold white on red] {message}", **kwargs)

    # ==================== 面板输出 ====================

    def panel(
        self,
        content: Any,
        title: str = "",
        subtitle: str = "",
        style: str = "primary",
        border_style: str = "blue",
        box: type = ROUNDED,
        expand: bool = True,
        **kwargs
    ) -> None:
        """输出面板"""
        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            style=style,
            border_style=border_style,
            box=box,
            expand=expand,
            **kwargs
        )
        self.print(panel)

    def success_panel(self, content: Any, title: str = "成功") -> None:
        """输出成功面板"""
        self.panel(content, title=title, style="success", border_style="green")

    def error_panel(self, content: Any, title: str = "错误") -> None:
        """输出错误面板"""
        self.panel(content, title=title, style="error", border_style="red")

    def warning_panel(self, content: Any, title: str = "警告") -> None:
        """输出警告面板"""
        self.panel(content, title=title, style="warning", border_style="yellow")

    def info_panel(self, content: Any, title: str = "信息") -> None:
        """输出信息面板"""
        self.panel(content, title=title, style="info", border_style="blue")

    # ==================== 表格输出 ====================

    def create_table(
        self,
        title: str = "",
        columns: Optional[List[str]] = None,
        box: type = ROUNDED,
        border_style: str = "blue",
        header_style: str = "bold magenta",
        title_style: str = "bold cyan",
        **kwargs
    ) -> Table:
        """创建表格"""
        table = Table(
            title=title,
            box=box,
            border_style=border_style,
            header_style=header_style,
            title_style=title_style,
            **kwargs
        )

        if columns:
            for col in columns:
                table.add_column(col)

        return table

    def print_table(
        self,
        data: List[Dict[str, Any]],
        title: str = "",
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        从数据列表打印表格

        Args:
            data: 数据列表，每个元素是一个字典
            title: 表格标题
            columns: 列名列表，如果为None则从数据中提取
        """
        if not data:
            self.warning("没有数据可显示")
            return

        if columns is None:
            columns = list(data[0].keys())

        table = self.create_table(title=title, columns=columns, **kwargs)

        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])

        self.print(table)

    def print_key_value(
        self,
        data: Dict[str, Any],
        title: str = "",
        key_column: str = "配置项",
        value_column: str = "值",
        **kwargs
    ) -> None:
        """打印键值对表格"""
        table = self.create_table(
            title=title,
            columns=[key_column, value_column],
            **kwargs
        )

        for key, value in data.items():
            table.add_row(str(key), str(value))

        self.print(table)

    # ==================== 树形结构 ====================

    def print_tree(
        self,
        data: Dict[str, Any],
        title: str = "",
        icon: str = Icons.BULLET
    ) -> None:
        """打印树形结构"""
        tree = Tree(f"[bold cyan]{title}[/bold cyan]" if title else "")

        def add_node(parent, data, icon):
            for key, value in data.items():
                if isinstance(value, dict):
                    node = parent.add(f"{icon} [blue]{key}[/blue]")
                    add_node(node, value, icon)
                elif isinstance(value, list):
                    node = parent.add(f"{icon} [blue]{key}[/blue]")
                    for item in value:
                        if isinstance(item, dict):
                            add_node(node, item, icon)
                        else:
                            node.add(f"  {Icons.BULLET} {item}")
                else:
                    parent.add(f"{icon} [blue]{key}[/blue]: [green]{value}[/green]")

        add_node(tree, data, icon)
        self.print(tree)

    # ==================== 进度条 ====================

    @contextmanager
    def progress(
        self,
        description: str = "处理中...",
        transient: bool = False,
        console: Optional[Console] = None
    ):
        """
        进度条上下文管理器

        用法:
            with rich_output.progress() as progress:
                task = progress.add_task("下载文件", total=100)
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.1)
        """
        console = console or self.console
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=transient,
        )

        with progress:
            yield progress

    def track(self, sequence: Any, description: str = "处理中"):
        """
        跟踪迭代进度

        用法:
            for item in rich_output.track(items, "处理项目"):
                process(item)
        """
        return track(sequence, description=description, console=self.console)

    # ==================== 状态显示 ====================

    @contextmanager
    def status(self, message: str, spinner: str = "dots", **kwargs):
        """
        状态显示上下文管理器

        用法:
            with rich_output.status("加载中..."):
                time.sleep(2)
                rich_output.success("加载完成!")
        """
        with self.console.status(message, spinner=spinner, **kwargs):
            yield

    # ==================== 规则线 ====================

    def rule(
        self,
        title: str = "",
        characters: str = "─",
        style: str = "primary"
    ) -> None:
        """输出规则线"""
        rule = Rule(title=title, characters=characters, style=style)
        self.print(rule)

    # ==================== Markdown 代码 ====================

    def print_markdown(self, content: str, **kwargs) -> None:
        """输出 Markdown 格式内容"""
        markdown = Markdown(content)
        self.print(markdown, **kwargs)

    def print_code(self, code: str, language: str = "python", **kwargs) -> None:
        """输出语法高亮的代码"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.print(syntax, **kwargs)

    # ==================== 交互式输入 ====================

    def prompt(
        self,
        message: str,
        default: Optional[str] = None,
        **kwargs
    ) -> str:
        """提示用户输入"""
        return Prompt.ask(message, default=default, console=self.console, **kwargs)

    def confirm(
        self,
        message: str,
        default: bool = False,
        **kwargs
    ) -> bool:
        """确认用户选择"""
        return Confirm.ask(message, default=default, console=self.console, **kwargs)

    def select(
        self,
        message: str,
        choices: List[str],
        default: Optional[str] = None
    ) -> str:
        """让用户选择一个选项"""
        return Prompt.ask(
            message,
            choices=choices,
            default=default,
            console=self.console
        )

    # ==================== 多列布局 ====================

    def print_columns(
        self,
        items: List[Any],
        title: str = "",
        equal: bool = True,
        expand: bool = True
    ) -> None:
        """打印多列布局"""
        columns = Columns(items, equal=equal, expand=expand)
        if title:
            self.print(Align.center(Text(title, style="bold cyan")))
            self.print()
        self.print(columns)

    # ==================== 分组输出 ====================

    def print_group(self, *renderables: Any, **kwargs) -> None:
        """打印分组内容"""
        group = Group(*renderables)
        self.print(group, **kwargs)

    # ==================== 清屏 ====================

    def clear(self) -> None:
        """清空控制台"""
        self.console.clear()

    # ==================== 实用方法 ====================

    def print_header(self, text: str, level: int = 1) -> None:
        """打印标题"""
        from rich.text import Text

        styles = {
            1: "bold bright_blue on black",
            2: "bold blue",
            3: "bold cyan",
            4: "bold white",
        }
        style = styles.get(level, "bold")
        prefix = "#" * level

        # 使用 Text 避免 markup 解析问题
        header_text = Text()
        header_text.append(f"\n", style=style)
        header_text.append(f"{prefix} {text}\n", style=style)
        self.print(header_text)

    def print_subheader(self, text: str) -> None:
        """打印子标题"""
        self.rule(text, style="cyan")

    def print_separator(self) -> None:
        """打印分隔线"""
        self.rule()

    def print_banner(
        self,
        title: str,
        subtitle: str = "",
        width: Optional[int] = None
    ) -> None:
        """打印横幅"""
        from rich.align import Align

        if subtitle:
            content = Align.center(
                Group(
                    Text(title, style="bold bright_blue"),
                    Text(subtitle, style="dim cyan")
                ),
                vertical="middle",
                width=width
            )
        else:
            content = Align.center(
                Text(title, style="bold bright_blue"),
                vertical="middle",
                width=width
            )

        panel = Panel(
            content,
            box=DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.print(panel)


# ==================== 业务专用输出类 ====================

class BusinessOutput(RichOutput):
    """业务场景专用的输出类"""

    # ==================== 抢券相关 ====================

    def print_grab_start(self, platform: str, coupon_name: str, time: str) -> None:
        """输出抢券开始信息"""
        self.print_header(f"🎫 开始抢券 - {platform}", level=2)
        self.print_key_value({
            "平台": platform,
            "优惠券": coupon_name,
            "抢券时间": time,
        })

    def print_grab_success(self, coupon_name: str, value: float, platform: str = "") -> None:
        """输出抢券成功"""
        prefix = f"[{platform}] " if platform else ""
        self.success(f"{prefix}抢券成功！获得 {coupon_name} (价值 {value} 元)")

    def print_grab_failed(self, reason: str, platform: str = "") -> None:
        """输出抢券失败"""
        prefix = f"[{platform}] " if platform else ""
        self.error(f"{prefix}抢券失败: {reason}")

    def print_grab_countdown(self, seconds: int, coupon_name: str = "") -> None:
        """输出抢券倒计时"""
        from rich.live import Live

        def generate_countdown():
            while seconds > 0:
                mins, secs = divmod(seconds, 60)
                text = f"⏰ [yellow]倒计时: {mins:02d}:{secs:02d}[/yellow]"
                if coupon_name:
                    text += f" | {coupon_name}"
                yield text
                seconds -= 1
                time.sleep(1)

        with Live(generate_countdown(), console=self.console, refresh_per_second=1) as live:
            for _ in generate_countdown():
                live.update(_)

    # ==================== 签到相关 ====================

    def print_checkin_success(self, points_gained: int, total_points: int) -> None:
        """输出签到成功"""
        self.success(f"签到成功！获得 {Icons.POINTS} {points_gained} 积分，当前总计: {total_points}")

    def print_checkin_failed(self, reason: str) -> None:
        """输出签到失败"""
        self.error(f"签到失败: {reason}")

    # ==================== 账户相关 ====================

    def print_login_success(self, username: str, platform: str = "") -> None:
        """输出登录成功"""
        prefix = f"[{platform}] " if platform else ""
        self.success(f"{prefix}欢迎回来，{Icons.USER} {username}")

    def print_login_failed(self, reason: str, platform: str = "") -> None:
        """输出登录失败"""
        prefix = f"[{platform}] " if platform else ""
        self.error(f"{prefix}登录失败: {reason}")

    def print_cookie_status(self, valid: bool, username: str = "") -> None:
        """输出 Cookie 状态"""
        if valid:
            self.success(f"{Icons.COOKIE} Cookie 状态正常{' - ' + username if username else ''}")
        else:
            self.error(f"{Icons.COOKIE} Cookie 已过期或无效，请重新获取")

    # ==================== 平台相关 ====================

    def print_platform_status(self, platform: str, enabled: bool, **info) -> None:
        """输出平台状态"""
        status_icon = Icons.SUCCESS if enabled else Icons.FAILED
        status_text = "启用" if enabled else "禁用"
        self.info(f"{platform}: {status_icon} {status_text}")

        if info:
            self.print_key_value(info, title="平台信息")

    # ==================== 系统信息 ====================

    def print_system_info(self, info: Dict[str, Any]) -> None:
        """输出系统信息"""
        self.print_header("系统信息", level=2)
        self.print_key_value(info)

    def print_scheduler_status(self, stats: Dict[str, Any]) -> None:
        """输出调度器状态"""
        self.print_header("调度器状态", level=2)
        self.print_key_value(stats)

    # ==================== 统计数据 ====================

    def print_statistics(
        self,
        title: str,
        stats: Dict[str, int],
        highlight_key: str = ""
    ) -> None:
        """输出统计数据"""
        table = self.create_table(title=title, columns=["项目", "数量"])

        for key, value in stats.items():
            style = "bold green" if key == highlight_key else ""
            table.add_row(key, str(value), style=style)

        self.print(table)

    def print_user_stats(
        self,
        username: str,
        total_checkins: int,
        total_grabs: int,
        success_grabs: int,
        total_points: int
    ) -> None:
        """输出用户统计"""
        success_rate = (success_grabs / total_grabs * 100) if total_grabs > 0 else 0

        stats = {
            "用户名": username,
            "签到次数": total_checkins,
            "抢券尝试": total_grabs,
            "抢券成功": success_grabs,
            "成功率": f"{success_rate:.1f}%",
            "当前积分": total_points,
        }

        self.print_header("用户统计", level=2)
        self.print_key_value(stats)

    # ==================== 历史记录 ====================

    def print_records(
        self,
        records: List[Dict[str, Any]],
        title: str = "历史记录"
    ) -> None:
        """输出历史记录"""
        if not records:
            self.warning("暂无记录")
            return

        self.print_header(title, level=2)

        # 获取所有可能的列
        all_columns = set()
        for record in records:
            all_columns.update(record.keys())

        columns = ["时间", "操作", "状态"] + [col for col in all_columns if col not in ["时间", "操作", "状态"]]

        self.print_table(records, columns=columns)


# ==================== 全局实例 ====================

# 默认输出实例
default_output = RichOutput()
business_output = BusinessOutput()

# 便捷访问函数
def get_output() -> RichOutput:
    """获取默认输出实例"""
    return default_output


def get_business_output() -> BusinessOutput:
    """获取业务输出实例"""
    return business_output


# ==================== 导出 ====================

__all__ = [
    # 类
    "RichOutput",
    "BusinessOutput",
    "RichTheme",
    "Icons",
    "OutputLevel",

    # 函数
    "get_output",
    "get_business_output",
]
