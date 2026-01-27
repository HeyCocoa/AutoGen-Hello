"""
流式消息处理模块
负责处理AutoGen的流式输出
"""
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional, Set

from autogen_agentchat.base import TaskResult

from .rich_ui import (
    print_agent_header,
    print_tool_call,
    print_tool_result,
    print_content,
)


@dataclass
class StreamDisplayConfig:
    """流式输出显示配置"""
    show_agent_headers: bool = True
    show_content: bool = True
    show_tools: bool = False
    content_max_chars: Optional[int] = None
    allowed_sources: Optional[Set[str]] = None
    suppressed_sources: Set[str] = field(default_factory=set)


def _truncate_text(text: str, max_chars: Optional[int]) -> str:
    if not max_chars or len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rstrip()
    omitted = len(text) - len(truncated)
    return f"{truncated}... (truncated {omitted} chars)"


def _make_tool_call_key(name: str, arguments: str) -> str:
    """生成工具调用的唯一标识"""
    return f"{name}:{arguments}"


async def stream_messages(
    stream: AsyncGenerator,
    display: Optional[StreamDisplayConfig] = None,
) -> TaskResult:
    """
    处理流式消息输出，支持工具调用显示

    Args:
        stream: AutoGen的消息流生成器
        display: 显示配置

    Returns:
        最终的TaskResult
    """
    result = None
    current_agent = None
    display = display or StreamDisplayConfig()

    # 去重：记录已显示的工具调用和结果
    shown_tool_calls: Set[str] = set()
    shown_tool_results: Set[str] = set()

    async for message in stream:
        # 最终结果
        if isinstance(message, TaskResult):
            result = message
            continue

        # 获取消息类型名称
        message_type = type(message).__name__

        # 显示Agent名称切换
        if hasattr(message, "source"):
            source = message.source
            if source in display.suppressed_sources:
                source = None
            if display.show_agent_headers and source and source != "user" and source != current_agent:
                current_agent = source
                print_agent_header(current_agent)

        # 处理不同类型的消息
        if message_type == "TextMessage":
            # 普通文本消息
            if hasattr(message, "content") and isinstance(message.content, str):
                # 跳过user消息的内容（已经在workflow中显示）
                if hasattr(message, "source") and message.source != "user":
                    source = message.source
                    if source in display.suppressed_sources:
                        continue
                    if display.allowed_sources is not None and source not in display.allowed_sources:
                        continue
                    if display.show_content:
                        content = _truncate_text(message.content, display.content_max_chars)
                        print_content(content)

        elif message_type == "ToolCallRequestEvent":
            # 工具调用请求（去重）
            if display.show_tools and hasattr(message, "content") and isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, 'name') and hasattr(item, 'arguments'):
                        key = _make_tool_call_key(item.name, item.arguments)
                        if key not in shown_tool_calls:
                            shown_tool_calls.add(key)
                            print_tool_call(item.name, item.arguments)

        elif message_type == "ToolCallExecutionEvent":
            # 工具执行结果（去重）
            if display.show_tools and hasattr(message, "content") and isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, 'content'):
                        result_str = str(item.content)
                        # 用内容的前200字符作为去重key（避免完全相同的结果重复显示）
                        result_key = result_str[:200]
                        if result_key not in shown_tool_results:
                            shown_tool_results.add(result_key)
                            print_tool_result(result_str)

        elif message_type == "ToolCallSummaryMessage":
            # 工具调用摘要 - 完全忽略，避免重复
            pass

    return result
