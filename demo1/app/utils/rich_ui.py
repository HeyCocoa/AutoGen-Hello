"""
Rich UI组件模块
提供统一的Rich样式和组件配置
"""
import sys
import io

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# 全局Console实例（配置UTF-8编码）
if RICH_AVAILABLE:
    # 确保Windows终端使用UTF-8
    if sys.platform == "win32":
        try:
            # 重新包装stdout为UTF-8
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass
    console = Console()
else:
    console = None


# Agent样式配置
AGENT_STYLES = {
    "Coordinator": ("🎯", "bold cyan"),
    "Clarifier": ("🔍", "bold yellow"),
    "Analyst": ("📊", "bold green"),
    "Strategist": ("💡", "bold magenta"),
    "Writer": ("✍️", "bold blue"),
}


def print_agent_header(agent_name: str):
    """打印Agent标题（带颜色和图标）"""
    icon, style = AGENT_STYLES.get(agent_name, ("🤖", "bold white"))

    if RICH_AVAILABLE and console:
        console.print()
        console.rule(f"{icon} {agent_name}", style=style)
        console.print()
    else:
        print(f"\n{'='*80}")
        print(f"{icon} {agent_name}")
        print(f"{'='*80}\n")


def print_phase_header(phase_text: str, style: str = "bold yellow"):
    """打印阶段标题"""
    if RICH_AVAILABLE and console:
        console.print(Panel(phase_text, style=style, expand=False))
    else:
        print(phase_text)


def print_tool_call(tool_name: str, arguments: str):
    """打印工具调用"""
    if RICH_AVAILABLE and console:
        tool_panel = Panel(
            f"[bold cyan]{tool_name}[/bold cyan]\n"
            f"[dim]参数:[/dim] {arguments}",
            title="🔧 调用工具",
            border_style="cyan",
            padding=(0, 1)
        )
        console.print(tool_panel)
    else:
        print(f"\n🔧 调用工具: {tool_name}")
        print(f"   参数: {arguments}\n")


def print_tool_result(result_content: str):
    """打印工具返回结果"""
    if RICH_AVAILABLE and console:
        result_panel = Panel(
            result_content,
            title="📊 工具返回",
            border_style="green",
            padding=(0, 1)
        )
        console.print(result_panel)
    else:
        print(f"\n📊 工具返回:")
        try:
            print(f"   {result_content}\n")
        except UnicodeEncodeError:
            print(f"   {result_content.encode('utf-8', errors='replace').decode('utf-8')}\n")


def print_content(content: str):
    """打印内容（支持Markdown）"""
    if RICH_AVAILABLE and console:
        # 检测是否是Markdown格式
        if content.startswith("#") or "```" in content:
            try:
                console.print(Markdown(content))
                return
            except:
                pass
        console.print(content)
    else:
        # Fallback：普通打印
        try:
            print(content, flush=True)
        except UnicodeEncodeError:
            print(content.encode('utf-8', errors='replace').decode('utf-8'), flush=True)


def print_success(message: str):
    """打印成功消息"""
    if RICH_AVAILABLE and console:
        console.print(message, style="bold green")
    else:
        print(f"   {message}")
