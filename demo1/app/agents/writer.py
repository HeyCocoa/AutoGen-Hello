"""
撰写者智能体 (Writer)
负责将策略整理成结构化Markdown文档
"""
from autogen_agentchat.agents import AssistantAgent

from ..prompts import WRITER_SYSTEM_MESSAGE


def create_writer(model_client) -> AssistantAgent:
    """创建撰写者智能体"""
    return AssistantAgent(
        name="Writer",
        model_client=model_client,
        system_message=WRITER_SYSTEM_MESSAGE,
    )
