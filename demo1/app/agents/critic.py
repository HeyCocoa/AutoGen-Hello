"""
批评者/质检员智能体 (Critic)
负责挑战分析师的结论，找出漏洞和盲点
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import CRITIC_SYSTEM_MESSAGE
from ..tools import get_current_date, web_search


def create_critic(model_client) -> AssistantAgent:
    """创建批评者智能体（带工具，可联网验证）"""
    return AssistantAgent(
        name="Critic",
        model_client=model_client,
        system_message=CRITIC_SYSTEM_MESSAGE,
        tools=[get_current_date, web_search],
    )
