"""
工作流编排模块
负责协调多智能体的工作流程
"""
import os
from datetime import datetime
from typing import List, Dict, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelCapabilities

from .config import Config
from .utils import async_spinner
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

        clarification_prompt = f"""
用户输入的业务场景：
{user_input}

【任务分工】
- Coordinator：你负责协调流程，确保 Clarifier 完成任务后汇报结果
- Clarifier：你负责分析场景描述的完整性，判断信息是否充分

Clarifier，请按照你的 system_message 中的要求，分析这个场景描述。
如果需要澄清，请输出【需要澄清】标记和具体问题；
如果信息充分，请输出【信息充分】标记。
"""

        # 创建澄清阶段的团队
        clarification_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.clarifier],
            max_turns=2,  # 减少轮次：Coordinator启动 -> Clarifier输出
        )

        # 使用spinner运行澄清阶段
        async with async_spinner("Coordinator 和 Clarifier 正在分析场景", "✓ 澄清阶段完成"):
            clarification_result = await clarification_team.run(
                task=clarification_prompt
            )

        # 检查是否需要用户回答 - 查找Clarifier的消息
        clarifier_message = None
        for msg in reversed(clarification_result.messages):
            if hasattr(msg, 'source') and msg.source == "Clarifier":
                clarifier_message = str(msg.content)
                break

        additional_info = ""
        if clarifier_message and "【需要澄清】" in clarifier_message:
            print("\n" + "=" * 80)
            print("💬 需要补充一些信息：")
            print("=" * 80)
            print(clarifier_message)
            print("\n" + "=" * 80)
            print("💡 提示：可以输入多行回答，输入完成后单独一行输入 'END' 并回车\n")

            # 多行输入，支持END结束
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)

            additional_info = "\n".join(lines).strip()
            print("=" * 80 + "\n")
        else:
            print("   ✓ 信息充分，无需澄清\n")

        # 阶段2：分析阶段
        print("\n📊 阶段2：业务分析")

        analysis_prompt = f"""
业务场景信息：
原始输入：{user_input}
补充信息：{additional_info if additional_info else "无"}

【任务分工】
- Coordinator：你负责协调流程，确保 Analyst 完成深度分析
- Analyst：你负责进行深度业务分析

Analyst，请按照你的 system_message 进行深度业务分析，输出完整的分析报告。
"""

        analysis_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.analyst],
            max_turns=2,  # Coordinator启动 -> Analyst输出
        )

        # 使用spinner运行分析阶段
        async with async_spinner("Coordinator 和 Analyst 正在进行业务分析", "✓ 分析阶段完成"):
            analysis_result = await analysis_team.run(task=analysis_prompt)

        # 提取Analyst的分析结果（找Analyst的最后一次输出）
        analyst_output = None
        for msg in reversed(analysis_result.messages):
            if hasattr(msg, 'source') and msg.source == "Analyst":
                analyst_output = str(msg.content)
                break

        if not analyst_output:
            print("   ⚠️  警告：未找到 Analyst 的输出，使用最后一条消息")
            analyst_output = str(analysis_result.messages[-1].content)

        # 阶段3：策略生成阶段
        print("\n🎯 阶段3：策略生成")

        strategy_prompt = f"""
【任务分工】
- Coordinator：你负责协调流程，确保 Strategist 完成策略制定
- Strategist：你负责基于分析结果生成详细的选题策略

Strategist，请基于以下分析结果，按照你的 system_message 生成完整的选题策略方案。

分析结果：
{analyst_output}
"""

        strategy_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.strategist],
            max_turns=2,  # Coordinator启动 -> Strategist输出
        )

        # 使用spinner运行策略生成阶段
        async with async_spinner("Coordinator 和 Strategist 正在生成策略", "✓ 策略生成阶段完成"):
            strategy_result = await strategy_team.run(task=strategy_prompt)

        # 提取Strategist的策略方案（找Strategist的最后一次输出）
        strategist_output = None
        for msg in reversed(strategy_result.messages):
            if hasattr(msg, 'source') and msg.source == "Strategist":
                strategist_output = str(msg.content)
                break

        if not strategist_output:
            print("   ⚠️  警告：未找到 Strategist 的输出，使用最后一条消息")
            strategist_output = str(strategy_result.messages[-1].content)

        # 阶段4：文档撰写阶段
        print("\n📄 阶段4：文档生成")

        writing_prompt = f"""
【任务分工】
- Coordinator：你负责协调流程，确保 Writer 完成文档撰写
- Writer：你负责将所有内容整理成完整的 Markdown 策略文档

Writer，请将以下内容按照你的 system_message 要求，整理成完整的 Markdown 文档。

业务场景：{user_input}
补充信息：{additional_info if additional_info else "无"}

分析结果：
{analyst_output}

策略方案：
{strategist_output}

请输出完整的 Markdown 文档，包含所有必要的章节和内容。
"""

        writing_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.writer],
            max_turns=2,  # Coordinator启动 -> Writer输出完整文档
        )

        # 使用spinner运行文档撰写阶段
        async with async_spinner("Coordinator 和 Writer 正在生成文档", "✓ 文档生成阶段完成"):
            writing_result = await writing_team.run(task=writing_prompt)

        # 提取Writer的最终文档（找Writer的最后一次输出）
        writer_output = None
        for msg in reversed(writing_result.messages):
            if hasattr(msg, 'source') and msg.source == "Writer":
                writer_output = str(msg.content)
                break

        if not writer_output:
            print("   ⚠️  警告：未找到 Writer 的输出，使用最后一条消息")
            writer_output = str(writing_result.messages[-1].content)

        # 保存文档
        output_path = self._save_document(writer_output)

        print("\n" + "=" * 80)
        print("✅ 策略文档生成完成！")
        print(f"📁 文档已保存至：{output_path}")
        print("=" * 80 + "\n")

        return writer_output

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
