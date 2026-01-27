"""
策略师智能体 (Strategist)
负责生成可执行的选题策略
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import STRATEGIST_SYSTEM_MESSAGE


def create_strategist(model_client) -> AssistantAgent:
    """创建策略师智能体"""
    return AssistantAgent(
        name="Strategist",
        model_client=model_client,
        system_message=STRATEGIST_SYSTEM_MESSAGE,
    )
