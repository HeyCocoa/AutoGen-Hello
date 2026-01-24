"""
Spinner工具模块
提供终端进度指示器，支持rich库和fallback实现
"""
import sys
import time
import asyncio
import threading
from contextlib import asynccontextmanager
from typing import Optional


class SimpleSpinner:
    """简单的自定义Spinner（fallback实现）"""

    def __init__(self, text: str = "处理中"):
        self.text = text
        self.spinning = False
        self.thread: Optional[threading.Thread] = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_index = 0

    def _spin(self):
        """Spinner动画循环"""
        while self.spinning:
            frame = self.frames[self.frame_index % len(self.frames)]
            sys.stdout.write(f"\r   {frame} {self.text}")
            sys.stdout.flush()
            self.frame_index += 1
            time.sleep(0.1)

    def start(self):
        """启动spinner"""
        self.spinning = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self, final_text: Optional[str] = None):
        """停止spinner"""
        self.spinning = False
        if self.thread:
            self.thread.join()
        # 清除spinner行
        sys.stdout.write("\r" + " " * (len(self.text) + 10) + "\r")
        sys.stdout.flush()
        if final_text:
            print(f"   {final_text}")


@asynccontextmanager
async def async_spinner(text: str, success_text: str = "✓ 完成"):
    """
    异步Spinner上下文管理器
    在等待异步任务时显示转圈动画

    Args:
        text: 处理中显示的文本
        success_text: 完成后显示的文本

    Example:
        async with async_spinner("正在分析", "✓ 分析完成"):
            result = await some_async_task()
    """
    try:
        # 尝试使用rich库
        from rich.console import Console

        console = Console()

        # 启动spinner任务
        stop_event = asyncio.Event()

        async def spin():
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            frame_index = 0
            while not stop_event.is_set():
                frame = frames[frame_index % len(frames)]
                console.print(
                    f"   {frame} [bold cyan]{text}[/bold cyan]",
                    end="\r"
                )
                frame_index += 1
                await asyncio.sleep(0.1)
            # 清除spinner行
            console.print(" " * 80, end="\r")

        spinner_task = asyncio.create_task(spin())

        try:
            yield
        finally:
            stop_event.set()
            await spinner_task
            console.print(f"   {success_text}", style="bold green")

    except ImportError:
        # Fallback到简单实现
        simple_spinner = SimpleSpinner(text)
        simple_spinner.start()
        try:
            yield
        finally:
            simple_spinner.stop(success_text)



