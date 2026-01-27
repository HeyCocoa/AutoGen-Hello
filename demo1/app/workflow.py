"""
工作流编排模块
负责协调多智能体的工作流程
"""
import os
from datetime import datetime

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelCapabilities

from .config import Config
from .utils import stream_messages, StreamDisplayConfig
from .utils.rich_ui import print_phase_header, print_success, start_loading, stop_loading
from .agents import (
    create_coordinator,
    create_clarifier,
    create_analyst,
    create_strategist,
    create_writer,
)
from .prompts import (
    get_clarification_prompt,
    get_analysis_prompt,
    get_strategy_prompt,
    get_writing_prompt,
)


def _extract_agent_output(result, agent_name: str, fallback_warning: str) -> str:
    """
    从消息结果中提取指定智能体的最后一次输出

    Args:
        result: 团队运行结果
        agent_name: 智能体名称
        fallback_warning: 未找到输出时的警告信息

    Returns:
        智能体输出内容
    """
    for msg in reversed(result.messages):
        if hasattr(msg, 'source') and msg.source == agent_name:
            return str(msg.content)

    print(f"   {fallback_warning}")
    return str(result.messages[-1].content)


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
        print_phase_header("📝 阶段1：信息确认", "bold yellow")

        clarification_prompt = get_clarification_prompt(user_input)

        # 创建澄清阶段的团队
        clarification_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.clarifier],
            max_turns=2,  # 减少轮次：Coordinator启动 -> Clarifier输出
        )

        # 使用流式输出运行澄清阶段
        clarification_loading = start_loading("确认中，请稍候...")
        clarification_result = await stream_messages(
            clarification_team.run_stream(task=clarification_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=False,
                show_tools=True,
                content_max_chars=200,
            ),
        )
        stop_loading(clarification_loading)
        print_success("✓ 澄清阶段完成")

        # 检查是否需要用户回答
        clarifier_message = _extract_agent_output(
            clarification_result, "Clarifier", ""
        )

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
        print_phase_header("📊 阶段2：业务分析", "bold green")

        analysis_prompt = get_analysis_prompt(user_input, additional_info)

        analysis_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.analyst],
            max_turns=4,  # Coordinator启动 -> Analyst工具调用 -> Analyst输出
        )

        # 使用流式输出运行分析阶段
        analysis_loading = start_loading("分析中，请稍候...")
        analysis_result = await stream_messages(
            analysis_team.run_stream(task=analysis_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=True,
                show_tools=True,
                content_max_chars=200,
            ),
        )
        stop_loading(analysis_loading)
        print_success("✓ 分析阶段完成")

        analyst_output = _extract_agent_output(
            analysis_result, "Analyst", "⚠️  警告：未找到 Analyst 的输出，使用最后一条消息"
        )

        # 阶段3：策略生成阶段
        print_phase_header("🎯 阶段3：策略生成", "bold magenta")

        strategy_prompt = get_strategy_prompt(analyst_output)

        strategy_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.strategist],
            max_turns=2,  # Coordinator启动 -> Strategist输出
        )

        # 使用流式输出运行策略生成阶段
        strategy_loading = start_loading("策略生成中，请稍候...")
        strategy_result = await stream_messages(
            strategy_team.run_stream(task=strategy_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=True,
                show_tools=True,
                content_max_chars=200,
            ),
        )
        stop_loading(strategy_loading)
        print_success("✓ 策略生成阶段完成")

        strategist_output = _extract_agent_output(
            strategy_result, "Strategist", "⚠️  警告：未找到 Strategist 的输出，使用最后一条消息"
        )

        # 阶段4：文档撰写阶段
        print_phase_header("📄 阶段4：文档生成", "bold blue")

        writing_prompt = get_writing_prompt(user_input, additional_info, analyst_output, strategist_output)

        writing_team = RoundRobinGroupChat(
            participants=[self.coordinator, self.writer],
            max_turns=2,  # Coordinator启动 -> Writer输出完整文档
        )

        # 使用流式输出运行文档撰写阶段
        writing_loading = start_loading("文档生成中，请稍候...")
        writing_result = await stream_messages(
            writing_team.run_stream(task=writing_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=True,
                show_tools=True,
                content_max_chars=200,
            ),
        )
        stop_loading(writing_loading)
        print_success("✓ 文档生成阶段完成")

        writer_output = _extract_agent_output(
            writing_result, "Writer", "⚠️  警告：未找到 Writer 的输出，使用最后一条消息"
        )

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
