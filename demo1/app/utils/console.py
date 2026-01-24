"""
流式消息处理模块
负责处理AutoGen的流式输出
"""
from typing import AsyncGenerator
from autogen_agentchat.base import TaskResult
from .rich_ui import (
    print_agent_header,
    print_tool_call,
    print_tool_result,
    print_content,
)


async def stream_messages(stream: AsyncGenerator) -> TaskResult:
    """
    处理流式消息输出，支持工具调用显示

    Args:
        stream: AutoGen的消息流生成器

    Returns:
        最终的TaskResult
    """
    result = None
    current_agent = None

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
            # 跳过user消息的header
            if source != "user" and source != current_agent:
                current_agent = source
                print_agent_header(current_agent)

        # 处理不同类型的消息
        if message_type == "TextMessage":
            # 普通文本消息
            if hasattr(message, "content") and isinstance(message.content, str):
                # 跳过user消息的内容（已经在workflow中显示）
                if hasattr(message, "source") and message.source != "user":
                    print_content(message.content)

        elif message_type == "ToolCallRequestEvent":
            # 工具调用请求
            if hasattr(message, "content") and isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, 'name') and hasattr(item, 'arguments'):
                        print_tool_call(item.name, item.arguments)

        elif message_type == "ToolCallExecutionEvent":
            # 工具执行结果
            if hasattr(message, "content") and isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, 'content'):
                        print_tool_result(str(item.content))

        elif message_type == "ToolCallSummaryMessage":
            # 工具调用摘要（可选择是否显示）
            # 这个消息通常是工具结果的总结，可以选择不显示以避免重复
            pass

    return result
