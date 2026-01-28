"""
Demo2 主程序
输入关键词 -> 向量扩展 -> 联网搜索 -> 存入SQLite
"""
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from config import CHROMADB_PATH
from retriever import create_retriever

console = Console()


def print_banner():
    console.print(Panel(Markdown("""
# 语义扩展搜索 Demo
输入关键词进行联网搜索；输入 `help` 查看命令。
"""), border_style="cyan"))


def print_help():
    console.print(Markdown("""
**命令：**
- `<关键词>`: 联网搜索（自动使用向量库扩展关键词）
- `local <关键词>`: 仅向量检索（不联网）
- `sync`: 同步 SQLite 数据到向量库
- `stats`: 查看 SQLite 统计
- `help`: 显示帮助
- `exit` / `quit`: 退出
"""))


def do_web_search(retriever, keyword: str):
    """联网搜索（默认行为）"""
    from semantic_searcher import create_semantic_searcher

    console.print(f"\n[cyan]搜索: {keyword}[/cyan]")
    searcher = create_semantic_searcher(retriever)
    result = searcher.search(keyword, n_expand=3)

    if result["expanded_keywords"]:
        console.print(f"[dim]扩展关键词: {', '.join(result['expanded_keywords'])}[/dim]")

    console.print(Panel(
        Markdown(result["web_results"]),
        title="搜索结果",
        border_style="blue",
    ))
    console.print(f"[green]已保存 {result['saved_count']} 条到 SQLite[/green]")


def do_local_search(retriever, keyword: str):
    """仅向量检索"""
    if not retriever:
        console.print("[yellow]向量库未初始化，请先执行 sync[/yellow]")
        return
    console.print(f"\n[cyan]本地检索: {keyword}[/cyan]")
    result = retriever.retrieve_knowledge(keyword, n_results=5)
    console.print(Panel(Markdown(result), title="本地检索结果", border_style="green"))


def do_sync():
    from sync_to_vector import sync_to_vector
    console.print("\n[cyan]同步 SQLite -> Chromadb...[/cyan]")
    count = sync_to_vector()
    console.print(f"[green]同步完成，共 {count} 条[/green]")


def do_stats():
    from knowledge_db import KnowledgeDB
    db = KnowledgeDB()
    console.print(Markdown(f"""
**SQLite 知识库统计：**
- 总记录数: {db.count()}
- 未同步到向量库: {len(db.get_unsynced())}
"""))


def init_retriever():
    """尝试初始化向量检索器（可选）"""
    if not CHROMADB_PATH.exists() or not list(CHROMADB_PATH.glob("*")):
        return None
    try:
        retriever = create_retriever()
        console.print("[dim]向量库已加载，将用于关键词扩展[/dim]")
        return retriever
    except Exception:
        return None


def handle_command(retriever, user_input: str) -> bool:
    cmd = user_input.lower()

    if cmd in ["exit", "quit"]:
        console.print("\n[yellow]再见！[/yellow]")
        return False

    if cmd == "help":
        print_help()
        return True

    if cmd == "sync":
        try:
            do_sync()
        except Exception as e:
            console.print(f"[red]同步失败: {e}[/red]")
        return True

    if cmd == "stats":
        try:
            do_stats()
        except Exception as e:
            console.print(f"[red]统计失败: {e}[/red]")
        return True

    # local <关键词> - 仅本地向量检索
    if cmd.startswith("local "):
        keyword = user_input[6:].strip()
        if keyword:
            try:
                do_local_search(retriever, keyword)
            except Exception as e:
                console.print(f"[red]检索失败: {e}[/red]")
        return True

    # 默认：联网搜索
    try:
        do_web_search(retriever, user_input)
    except Exception as e:
        console.print(f"[red]搜索失败: {e}[/red]")

    return True


def main():
    print_banner()
    retriever = init_retriever()
    print_help()

    while True:
        console.print("\n" + "-" * 40)
        user_input = Prompt.ask("[bold cyan]请输入关键词[/bold cyan]").strip()
        if not user_input:
            continue
        if not handle_command(retriever, user_input):
            break


if __name__ == "__main__":
    main()
