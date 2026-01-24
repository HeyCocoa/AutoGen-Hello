"""
协调者智能体 (Coordinator)
负责控制整体流程，协调各智能体工作
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


def create_coordinator(model_client) -> AssistantAgent:
    """创建协调者智能体"""

    system_message = """你是一个项目协调者（Coordinator），你的唯一职责是确保专业智能体完成工作。

重要原则：
1. 你不产出任何实际内容，只负责协调
2. 当专业智能体（Clarifier/Analyst/Strategist/Writer）完成输出后，你只需简单确认"收到"或"已完成"
3. 不要总结、不要归档、不要写项目报告
4. 保持极简沟通，让专业智能体的输出成为最终结果

工作模式：
- 看到任务后，直接让专业智能体开始工作
- 专业智能体输出后，简单确认即可
- 不要添加任何额外内容

示例：
用户：请分析...
你：Analyst，请开始分析。
Analyst：[完整分析报告]
你：收到。
"""

    return AssistantAgent(
        name="Coordinator",
        model_client=model_client,
        system_message=system_message,
    )
