"""
Demo2 主程序
实现"关键词 -> 向量化 -> RAG 查询"的完整流程（仅检索）
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from retriever import create_retriever

# 设置 Windows 控制台为 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()


def print_banner():
    """打印简洁提示"""
    banner = """
# 🚀 科技媒体选题检索 Demo2
输入关键词开始检索；输入 `help` 查看命令；输入 `exit` 退出。
"""
    console.print(Panel(Markdown(banner), border_style="cyan"))


def print_help():
    """打印帮助信息（简版）"""
    help_text = """
命令：
- `help`: 显示帮助
- `exit` / `quit`: 退出
"""
    console.print(Markdown(help_text))


def main():
    """主函数"""
    print_banner()

    # 检查知识库是否已初始化
    db_path = Path("./db")
    if not db_path.exists() or not list(db_path.glob("*")):
        console.print("\n[yellow]⚠️  警告: 知识库尚未初始化！[/yellow]")
        console.print("[cyan]请先运行: python init_db.py[/cyan]\n")
        sys.exit(1)

    console.print("\n[cyan]🔧 初始化检索器...[/cyan]")

    try:
        retriever = create_retriever()
    except Exception as e:
        console.print(f"\n[red]❌ 初始化失败: {e}[/red]")
        sys.exit(1)

    console.print("[green]✅ 初始化完成！[/green]\n")
    print_help()

    # 主循环
    while True:
        console.print("\n" + "-"*40)

        # 获取用户输入
        user_input = Prompt.ask(
            "[bold cyan]🔍 请输入关键词[/bold cyan]",
            default="help"
        ).strip()

        # 处理特殊命令
        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit']:
            console.print("\n[yellow]👋 感谢使用，再见！[/yellow]")
            break

        if user_input.lower() == 'help':
            print_help()
            continue

        # 处理正常查询
        console.print(f"\n[cyan]🔎 关键词: {user_input}[/cyan]")

        try:
            # 检索知识
            result = retriever.retrieve_knowledge(user_input, n_results=5)

            # 显示结果
            console.print("\n" + "-"*40)
            console.print("[green]✅ 检索完成[/green]\n")

            # 使用 Markdown 渲染结果
            console.print(Panel(
                Markdown(result),
                title="📝 检索结果",
                border_style="green"
            ))

        except Exception as e:
            console.print(f"\n[red]❌ 查询失败: {str(e)}[/red]")
            console.print("[yellow]💡 提示: 请检查 API 配置和网络连接[/yellow]")


if __name__ == "__main__":
    main()
