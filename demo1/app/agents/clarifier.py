"""
澄清者智能体 (Clarifier)
负责识别信息缺口并提出澄清问题
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import CLARIFIER_SYSTEM_MESSAGE


def create_clarifier(model_client) -> AssistantAgent:
    """创建澄清者智能体"""
    return AssistantAgent(
        name="Clarifier",
        model_client=model_client,
        system_message=CLARIFIER_SYSTEM_MESSAGE,
    )
