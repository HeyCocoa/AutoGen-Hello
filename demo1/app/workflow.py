"""
工作流编排模块
负责协调多智能体的工作流程
"""
import os
from datetime import datetime
from typing import List, Dict, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelCapabilities

from .config import Config
from .agents import (
    create_coordinator,
    create_clarifier,
    create_analyst,
    create_strategist,
    create_writer,
)


class TopicStrategyWorkflow:
    """选题策略生成工作流"""

    def __init__(self):
        """初始化工作流"""
        # 验证配置
        Config.validate()

        # 创建模型客户端
        # 对于非 OpenAI 模型（如 DeepSeek），需要提供 model_info
        model_capabilities = ModelCapabilities(
            vision=False,
            function_calling=True,
            json_output=True,
        )

        self.model_client = OpenAIChatCompletionClient(
            model=Config.MODEL_NAME,
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE,
            model_info=model_capabilities,
        )

        # 创建智能体
        self.coordinator = create_coordinator(self.model_client)
        self.clarifier = create_clarifier(self.model_client)
        self.analyst = create_analyst(self.model_client)
        self.strategist = create_strategist(self.model_client)
        self.writer = create_writer(self.model_client)

        # 智能体列表
        self.agents = [
            self.coordinator,
            self.clarifier,
            self.analyst,
            self.strategist,
            self.writer,
        ]

    async def run(self, user_input: str) -> str:
        """
        运行工作流

        Args:
            user_input: 用户输入的业务场景描述

        Returns:
            生成的策略文档内容
        """
        print("\n" + "=" * 80)
        print("🚀 选题策略生成器启动")
        print("=" * 80 + "\n")

        # 阶段1：澄清阶段
        print("📝 阶段1：信息澄清")
        print("-" * 80)

        clarification_prompt = f"""
用户输入的业务场景：
{user_input}

请 Clarifier 分析这个场景描述，判断信息是否充分。
如果需要澄清，请提出问题；如果信息充分，请说明可以直接进入分析阶段。
"""

        # 创建澄清阶段的团队
        clarification_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.clarifier],
            max_turns=3,
        )

        # 运行澄清阶段
        clarification_result = await Console(
            clarification_team.run_stream(task=clarification_prompt)
        )

        # 检查是否需要用户回答
        last_message = str(clarification_result.messages[-1].content)

        additional_info = ""
        if "需要澄清" in last_message or "问题" in last_message:
            print("\n" + "=" * 80)
            print("💬 Clarifier 提出了一些问题，请回答：")
            print("=" * 80)
            print(last_message)
            print("\n" + "=" * 80)
            print("请输入您的回答（输入完成后按回车）：")
            additional_info = input("> ")
            print("=" * 80 + "\n")

        # 阶段2：分析阶段
        print("\n📊 阶段2：业务分析")
        print("-" * 80)

        analysis_prompt = f"""
业务场景信息：
原始输入：{user_input}
补充信息：{additional_info if additional_info else "无"}

请 Analyst 进行深度业务分析。
"""

        analysis_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.analyst],
            max_turns=3,
        )

        analysis_result = await Console(
            analysis_team.run_stream(task=analysis_prompt)
        )

        # 阶段3：策略生成阶段
        print("\n🎯 阶段3：策略生成")
        print("-" * 80)

        strategy_prompt = f"""
基于 Analyst 的分析结果，请 Strategist 生成详细的选题策略。

分析结果：
{analysis_result.messages[-1].content}
"""

        strategy_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.strategist],
            max_turns=3,
        )

        strategy_result = await Console(
            strategy_team.run_stream(task=strategy_prompt)
        )

        # 阶段4：文档撰写阶段
        print("\n📄 阶段4：文档生成")
        print("-" * 80)

        writing_prompt = f"""
请 Writer 将以下内容整理成完整的Markdown策略文档：

业务场景：{user_input}
补充信息：{additional_info if additional_info else "无"}

分析结果：
{analysis_result.messages[-1].content}

策略方案：
{strategy_result.messages[-1].content}

请输出完整的Markdown文档。
"""

        writing_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.writer],
            max_turns=3,
        )

        writing_result = await Console(
            writing_team.run_stream(task=writing_prompt)
        )

        # 提取最终文档
        final_document = str(writing_result.messages[-1].content)

        # 保存文档
        output_path = self._save_document(final_document)

        print("\n" + "=" * 80)
        print("✅ 策略文档生成完成！")
        print(f"📁 文档已保存至：{output_path}")
        print("=" * 80 + "\n")

        return final_document

    def _save_document(self, content: str) -> str:
        """
        保存文档到文件

        Args:
            content: 文档内容

        Returns:
            文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategy_{timestamp}.md"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def print_agent_info(self):
        """打印智能体信息"""
        print("\n" + "=" * 80)
        print("🤖 智能体团队")
        print("=" * 80)
        for agent in self.agents:
            print(f"  • {agent.name}")
        print("=" * 80 + "\n")
