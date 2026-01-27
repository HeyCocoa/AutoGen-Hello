"""
协调者智能体 (Coordinator)
负责控制整体流程，协调各智能体工作
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import COORDINATOR_SYSTEM_MESSAGE


def create_coordinator(model_client) -> AssistantAgent:
    """创建协调者智能体"""
    return AssistantAgent(
        name="Coordinator",
        model_client=model_client,
        system_message=COORDINATOR_SYSTEM_MESSAGE,
    )
