"""简单的 Rich 测试"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

console = Console()

# 测试基本输出
console.print("[bold green]Success![/bold green] Hello World")
console.print("[bold red]Error![/bold red] Something went wrong")
console.print("[bold blue]Info![/bold blue] This is a message")

# 测试面板
from rich.panel import Panel
console.print(Panel("Hello, World!", title="Test"))

# 测试表格
from rich.table import Table
table = Table(title="Test Table")
table.add_column("Name", style="cyan")
table.add_column("Value", style="green")
table.add_row("Item 1", "Value 1")
table.add_row("Item 2", "Value 2")
console.print(table)

print("Rich basic test passed!")
