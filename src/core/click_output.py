"""
Click 输出组件库
使用 Click 框架提供美观的命令行输出
"""

import sys
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Windows UTF-8 支持
if sys.platform == "win32":
    try:
        import locale
        import codecs
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import click
from click import secho, echo, style


class Colors:
    """ANSI 颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # 明亮的前景色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class Icons:
    """Unicode 图标"""
    SUCCESS = '[OK]'
    ERROR = '[FAIL]'
    WARNING = '[WARN]'
    INFO = '[INFO]'
    RUNNING = '[RUN]'
    ARROW = '->'
    ARROW_RIGHT = '->'
    DOT = '*'
    CHECK = 'v'
    CROSS = 'x'
    STAR = '*'


class ClickOutput:
    """
    基于 Click 的输出管理器

    功能:
    - 彩色消息输出
    - 表格显示
    - 面板/边框
    - 进度条
    - 确认提示
    """

    def __init__(self, color: bool = True):
        self.color = color and self._supports_color()

    @staticmethod
    def _supports_color() -> bool:
        """检测终端是否支持颜色"""
        if sys.platform == "win32":
            # Windows 10+ 支持 ANSI 颜色
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(ctypes.c_ulong()))
                return True
            except:
                return False
        # 非Windows 系统通常支持
        return True

    # ==================== 基础输出 ====================

    def print(self, message: str = "", **kwargs):
        """基础打印"""
        click.echo(message, **kwargs)

    def newline(self, count: int = 1):
        """打印空行"""
        click.echo()

    # ==================== 消息输出 ====================

    def success(self, message: str, icon: str = Icons.SUCCESS):
        """输出成功消息"""
        if self.color:
            secho(f"{icon} {message}", fg="green", bold=True)
        else:
            click.echo(f"{icon} {message}")

    def error(self, message: str, icon: str = Icons.ERROR):
        """输出错误消息"""
        if self.color:
            secho(f"{icon} {message}", fg="red", bold=True)
        else:
            click.echo(f"{icon} {message}")

    def warning(self, message: str, icon: str = Icons.WARNING):
        """输出警告消息"""
        if self.color:
            secho(f"{icon} {message}", fg="yellow", bold=True)
        else:
            click.echo(f"{icon} {message}")

    def info(self, message: str, icon: str = Icons.INFO):
        """输出信息消息"""
        if self.color:
            secho(f"{icon} {message}", fg="blue", bold=True)
        else:
            click.echo(f"{icon} {message}")

    def debug(self, message: str, icon: str = Icons.DOT):
        """输出调试消息"""
        if self.color:
            secho(f"{icon} {message}", fg="cyan", dim=True)
        else:
            click.echo(f"{icon} {message}")

    def critical(self, message: str, icon: str = Icons.ERROR):
        """输出严重错误消息"""
        if self.color:
            secho(f"{icon} {message}", fg="white", bg="red", bold=True)
        else:
            click.echo(f"{icon} {message}")

    # ==================== 面板输出 ====================

    def panel(self, content: str, title: str = "", border_char: str = "=", width: int = 80):
        """输出面板"""
        lines = content.split('\n')
        max_len = max(len(line) for line in lines)
        max_len = min(max_len, width - 4)

        padding = 2
        total_width = max_len + padding * 2
        border = border_char * total_width

        self.newline()
        if title:
            title_line = f" {title} "
            if len(title_line) < total_width:
                title_line += border_char * (total_width - len(title_line))
            secho(title_line, fg="cyan", bold=True)
        else:
            secho(border, fg="cyan")

        for line in lines:
            # 截断过长的行
            display_line = line[:max_len]
            padded_line = f"  {display_line.ljust(max_len)}  "
            secho(padded_line)

        secho(border, fg="cyan")
        self.newline()

    def success_panel(self, content: str, title: str = "成功"):
        """输出成功面板"""
        if self.color:
            self._colored_panel(content, title, "green")
        else:
            self.panel(content, title)

    def error_panel(self, content: str, title: str = "错误"):
        """输出错误面板"""
        if self.color:
            self._colored_panel(content, title, "red")
        else:
            self.panel(content, title)

    def warning_panel(self, content: str, title: str = "警告"):
        """输出警告面板"""
        if self.color:
            self._colored_panel(content, title, "yellow")
        else:
            self.panel(content, title)

    def info_panel(self, content: str, title: str = "信息"):
        """输出信息面板"""
        if self.color:
            self._colored_panel(content, title, "blue")
        else:
            self.panel(content, title)

    def _colored_panel(self, content: str, title: str, color: str):
        """输出彩色面板"""
        lines = content.split('\n')
        max_len = max(len(line) for line in lines)
        max_len = min(max_len, 76)

        padding = 2
        total_width = max_len + padding * 2
        border = "=" * total_width

        self.newline()
        if title:
            title_line = f" {title} "
            if len(title_line) < total_width:
                title_line += "=" * (total_width - len(title_line))
            secho(title_line, fg=color, bold=True)
        else:
            secho(border, fg=color)

        for line in lines:
            display_line = line[:max_len]
            padded_line = f"  {display_line.ljust(max_len)}  "
            secho(padded_line, fg=color)

        secho(border, fg=color)
        self.newline()

    # ==================== 表格输出 ====================

    def print_table(self, data: List[Dict[str, Any]], title: str = "", columns: Optional[List[str]] = None):
        """打印表格"""
        if not data:
            self.warning("没有数据可显示")
            return

        if columns is None:
            columns = list(data[0].keys())

        # 计算每列宽度
        col_widths = {}
        for col in columns:
            col_widths[col] = max(len(col), max(len(str(row.get(col, ""))) for row in data))

        # 打印标题
        if title:
            self.newline()
            secho(title, fg="cyan", bold=True)
            self.newline()

        # 打印表头
        header_parts = []
        for col in columns:
            header_parts.append(col.ljust(col_widths[col]))
        secho("  ".join(header_parts), fg="cyan", bold=True)

        # 打印分隔线
        separator_parts = []
        for col in columns:
            separator_parts.append("-" * col_widths[col])
        secho("  ".join(separator_parts), fg="cyan")

        # 打印数据行
        for row in data:
            row_parts = []
            for col in columns:
                value = str(row.get(col, ""))
                row_parts.append(value.ljust(col_widths[col]))
            echo("  ".join(row_parts))

        self.newline()

    def print_key_value(self, data: Dict[str, Any], title: str = "", key_col: str = "配置项", val_col: str = "值"):
        """打印键值对表格"""
        table_data = [{key_col: k, val_col: str(v)} for k, v in data.items()]
        self.print_table(table_data, title=title, columns=[key_col, val_col])

    # ==================== 标题和分隔线 ====================

    def print_header(self, text: str, level: int = 1):
        """打印标题"""
        self.newline()
        prefix = "#" * level
        if self.color:
            secho(f"{prefix} {text}", fg="cyan", bold=True)
        else:
            click.echo(f"{prefix} {text}")
        self.newline()

    def print_subheader(self, text: str):
        """打印子标题"""
        self.print_header(text, level=2)

    def print_separator(self, char: str = "-", width: int = 80):
        """打印分隔线"""
        secho(char * width, fg="cyan")

    def print_rule(self, text: str = "", char: str = "-"):
        """打印规则线"""
        if text:
            line = f" {text} "
            remaining = 78 - len(line)
            line += char * max(0, remaining)
            secho(line, fg="cyan")
        else:
            secho(char * 80, fg="cyan")

    # ==================== 状态显示 ====================

    @contextmanager
    def status(self, message: str, spinner: str = "dots"):
        """显示状态（类似于 Rich 的 status）"""
        self.info(f"{message}...")
        try:
            yield
        finally:
            pass  # 可以添加完成后的输出

    # ==================== 进度条 ====================

    @contextmanager
    def progress(self, items: Optional[List] = None, label: str = "处理中"):
        """进度条上下文管理器"""
        if items:
            with click.progressbar(items, label=label) as bar:
                yield bar
        else:
            # 创建一个简单的文本进度显示
            class SimpleProgress:
                def __init__(self):
                    self.current = 0
                    self.total = 100

                def update(self, advance: int = 1):
                    self.current += advance
                    percent = int(self.current / self.total * 100)
                    click.echo(f"\r{label}: {percent}%", nl=False)

                def finish(self):
                    click.echo()  # 换行

            progress = SimpleProgress()
            yield progress
            progress.finish()

    # ==================== 确认和输入 ====================

    def confirm(self, message: str, default: bool = False) -> bool:
        """确认选择"""
        return click.confirm(message, default=default)

    def prompt(self, message: str, default: Optional[str] = None, **kwargs) -> str:
        """提示用户输入"""
        return click.prompt(message, default=default or "", **kwargs)

    # ==================== 横幅 ====================

    def print_banner(self, title: str, subtitle: str = "", width: int = 80):
        """打印横幅"""
        self.newline()

        if self.color:
            secho("=" * width, fg="cyan", bold=True)
        else:
            click.echo("=" * width)

        # 标题居中
        title_lines = self._center_text(title, width)
        for line in title_lines:
            secho(line, fg="cyan", bold=True)

        # 副标题居中
        if subtitle:
            subtitle_lines = self._center_text(subtitle, width)
            for line in subtitle_lines:
                secho(line, fg="blue")

        if self.color:
            secho("=" * width, fg="cyan", bold=True)
        else:
            click.echo("=" * width)

        self.newline()

    @staticmethod
    def _center_text(text: str, width: int) -> List[str]:
        """居中文本"""
        lines = []
        for line in text.split('\n'):
            # 处理中文字符（中文算2个字符宽度）
            display_width = 0
            for char in line:
                if '\u4e00' <= char <= '\u9fff':
                    display_width += 2
                else:
                    display_width += 1

            padding = max(0, width - display_width)
            left_padding = padding // 2
            lines.append(" " * left_padding + line)
        return lines

    # ==================== 业务专用方法 ====================

    def print_grab_start(self, platform: str, coupon_name: str, time: str):
        """输出抢券开始信息"""
        self.print_header(f"开始抢券 - {platform}", level=2)
        self.print_key_value({
            "平台": platform,
            "优惠券": coupon_name,
            "抢券时间": time,
        })

    def print_grab_success(self, coupon_name: str, value: float, platform: str = ""):
        """输出抢券成功"""
        prefix = f"[{platform}] " if platform else ""
        self.success(f"{prefix}抢券成功！获得 {coupon_name} (价值 {value} 元)")

    def print_grab_failed(self, reason: str, platform: str = ""):
        """输出抢券失败"""
        prefix = f"[{platform}] " if platform else ""
        self.error(f"{prefix}抢券失败: {reason}")

    def print_checkin_success(self, points_gained: int, total_points: int):
        """输出签到成功"""
        self.success(f"签到成功！获得 {Icons.STAR} {points_gained} 积分，当前总计: {total_points}")

    def print_login_success(self, username: str, platform: str = ""):
        """输出登录成功"""
        prefix = f"[{platform}] " if platform else ""
        self.success(f"{prefix}欢迎回来，{username}")

    def print_login_failed(self, reason: str, platform: str = ""):
        """输出登录失败"""
        prefix = f"[{platform}] " if platform else ""
        self.error(f"{prefix}登录失败: {reason}")

    def print_system_info(self, info: Dict[str, Any]):
        """输出系统信息"""
        self.print_header("系统信息", level=2)
        self.print_key_value(info)

    def print_scheduler_status(self, stats: Dict[str, Any]):
        """输出调度器状态"""
        self.print_header("调度器状态", level=2)
        self.print_key_value(stats)


# 全局输出实例
_output: Optional[ClickOutput] = None


def get_output(color: bool = True) -> ClickOutput:
    """获取全局输出实例"""
    global _output
    if _output is None:
        _output = ClickOutput(color=color)
    return _output


# 导出
__all__ = [
    "ClickOutput",
    "Colors",
    "Icons",
    "get_output",
]
