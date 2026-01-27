"""
分析师智能体 (Analyst)
负责深度分析业务场景，提取关键信息
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import ANALYST_SYSTEM_MESSAGE
from ..tools import get_current_date, web_search, calculate


def create_analyst(model_client) -> AssistantAgent:
    """创建分析师智能体（带工具）"""
    return AssistantAgent(
        name="Analyst",
        model_client=model_client,
        system_message=ANALYST_SYSTEM_MESSAGE,
        tools=[get_current_date, web_search, calculate],
    )
