"""
Demo2 主程序（适配 autogen 0.4.2）
实现"关键词 -> 向量化 -> RAG 查询"的完整流程
"""
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from agents import create_rag_assistant

console = Console()


def print_banner():
    """打印欢迎横幅"""
    banner = """
# 🚀 科技媒体选题智能助手 Demo2

**功能**: 关键词 → 向量化 → RAG 查询 → 选题建议

**技术栈**: AutoGen 0.4.2 + Chromadb + SiliconFlow Embedding
"""
    console.print(Panel(Markdown(banner), border_style="cyan"))


def print_help():
    """打印帮助信息"""
    help_text = """
## 📖 使用说明

1. 输入行业关键词（如: AI大模型、区块链、云计算等）
2. 系统会自动检索相关的历史选题策略和行业背景知识
3. 生成专业的选题建议

## 💡 特殊命令

- `help`: 显示帮助信息
- `exit` / `quit`: 退出程序

## 🎯 示例关键词

- AI大模型
- 区块链技术
- 云原生
- 自动驾驶
- 元宇宙
- 量子计算
"""
    console.print(Markdown(help_text))


async def main_async():
    """异步主函数"""
    print_banner()

    # 检查知识库是否已初始化
    db_path = Path("./db")
    if not db_path.exists() or not list(db_path.glob("*")):
        console.print("\n[yellow]⚠️  警告: 知识库尚未初始化！[/yellow]")
        console.print("[cyan]请先运行: python init_db.py[/cyan]\n")
        sys.exit(1)

    console.print("\n[cyan]🔧 正在初始化 RAG Assistant...[/cyan]")

    try:
        assistant = create_rag_assistant()
    except Exception as e:
        console.print(f"\n[red]❌ 初始化失败: {e}[/red]")
        sys.exit(1)

    console.print("[green]✅ 初始化完成！[/green]\n")
    print_help()

    # 主循环
    while True:
        console.print("\n" + "="*60)

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
        console.print(f"\n[cyan]🔎 正在处理关键词: {user_input}[/cyan]")
        console.print("="*60)

        try:
            # 生成选题建议
            result = await assistant.generate_topic_suggestion(user_input)

            # 显示结果
            console.print("\n" + "="*60)
            console.print("[green]✅ 选题建议生成完成！[/green]")
            console.print("="*60 + "\n")

            # 使用 Markdown 渲染结果
            console.print(Panel(
                Markdown(result),
                title="📝 选题建议",
                border_style="green"
            ))

        except Exception as e:
            console.print(f"\n[red]❌ 查询失败: {str(e)}[/red]")
            console.print("[yellow]💡 提示: 请检查 API 配置和网络连接[/yellow]")


def main():
    """同步主函数入口"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 程序已中断，再见！[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ 程序错误: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
