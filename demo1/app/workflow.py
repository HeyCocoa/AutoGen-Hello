"""
工作流编排模块
负责协调多智能体的工作流程

架构：4 阶段单 Agent 执行（无 Coordinator）
1. 澄清阶段 - Clarifier
2. 分析阶段 - Analyst（强制联网）
3. 质检阶段 - Critic（可联网验证）
4. 撰写阶段 - Writer
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
    create_clarifier,
    create_analyst,
    create_critic,
    create_writer,
)
from .prompts import (
    get_clarification_prompt,
    get_search_outline_prompt,
    get_outline_review_prompt,
    get_analysis_prompt,
    get_critic_prompt,
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

    if fallback_warning:
        print(f"   {fallback_warning}")
    return str(result.messages[-1].content)


class TopicStrategyWorkflow:
    """选题策略生成工作流"""

    def __init__(self):
        """初始化工作流"""
        # 验证配置
        Config.validate()

        # 创建模型客户端
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

        # 创建智能体（无 Coordinator）
        self.clarifier = create_clarifier(self.model_client)
        self.analyst = create_analyst(self.model_client)
        self.critic = create_critic(self.model_client)
        self.writer = create_writer(self.model_client)

        # 智能体列表
        self.agents = [
            self.clarifier,
            self.analyst,
            self.critic,
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
        print("选题策略生成器启动")
        print("=" * 80 + "\n")

        # 阶段1：澄清阶段（单 Agent）
        print_phase_header("阶段1：信息确认", "bold yellow")

        clarification_prompt = get_clarification_prompt(user_input)

        # 单 Agent 执行，max_turns=1
        clarification_team = RoundRobinGroupChat(
            participants=[self.clarifier],
            max_turns=1,
        )

        clarification_loading = start_loading("确认中...")
        clarification_result = await stream_messages(
            clarification_team.run_stream(task=clarification_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=False,
                show_tools=False,
            ),
        )
        stop_loading(clarification_loading)
        print_success("澄清阶段完成")

        clarifier_message = _extract_agent_output(
            clarification_result, "Clarifier", ""
        )

        additional_info = ""
        if clarifier_message and "【需要澄清】" in clarifier_message:
            print("\n" + "=" * 80)
            print("需要补充一些信息：")
            print("=" * 80)
            print(clarifier_message)
            print("\n" + "=" * 80)
            print("提示：输入完成后单独一行输入 'END' 并回车\n")

            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)

            additional_info = "\n".join(lines).strip()
            print("=" * 80 + "\n")
        else:
            print("   信息充分，无需澄清\n")

        # 阶段2：搜索大纲（Analyst -> Critic 对齐）
        print_phase_header("阶段2：搜索大纲对齐", "bold cyan")

        approved_outline = ""
        critic_feedback = ""
        max_outline_rounds = 2

        for round_index in range(max_outline_rounds):
            outline_prompt = get_search_outline_prompt(user_input, additional_info, critic_feedback)

            outline_team = RoundRobinGroupChat(
                participants=[self.analyst],
                max_turns=1,
            )

            outline_loading = start_loading("生成搜索大纲...")
            outline_result = await stream_messages(
                outline_team.run_stream(task=outline_prompt),
                display=StreamDisplayConfig(
                    show_agent_headers=True,
                    show_content=True,
                    show_tools=False,
                    content_max_chars=400,
                ),
            )
            stop_loading(outline_loading)

            outline_output = _extract_agent_output(
                outline_result, "Analyst", "警告：未找到 Analyst 的搜索大纲"
            )

            # Critic 审核大纲
            review_prompt = get_outline_review_prompt(outline_output)
            review_team = RoundRobinGroupChat(
                participants=[self.critic],
                max_turns=1,
            )

            review_loading = start_loading("质检搜索大纲...")
            review_result = await stream_messages(
                review_team.run_stream(task=review_prompt),
                display=StreamDisplayConfig(
                    show_agent_headers=True,
                    show_content=True,
                    show_tools=False,
                    content_max_chars=300,
                ),
            )
            stop_loading(review_loading)

            review_output = _extract_agent_output(
                review_result, "Critic", "警告：未找到 Critic 的审核结果"
            )

            if "【通过】" in review_output:
                approved_outline = outline_output
                print_success("搜索大纲通过")
                break

            critic_feedback = review_output
            print("\n⚠️  搜索大纲被打回，需要修正后再提交。\n")

        if not approved_outline:
            approved_outline = outline_output
            print("\n⚠️  搜索大纲多次未通过质检，将在提示风险后继续进入分析。\n")
            print("   提醒：请在结果中重点核查“行业痛点/受众痛点/竞品做法”的数据来源。\n")

        # 阶段3：分析阶段（单 Agent，带工具调用）
        print_phase_header("阶段3：业务分析", "bold green")

        analysis_prompt = get_analysis_prompt(user_input, additional_info, approved_outline)

        # Analyst 需要多轮来完成工具调用
        analysis_team = RoundRobinGroupChat(
            participants=[self.analyst],
            max_turns=3,  # 工具调用可能需要多轮
        )

        analysis_loading = start_loading("分析中（联网搜索）...")
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
        print_success("分析阶段完成")

        analyst_output = _extract_agent_output(
            analysis_result, "Analyst", "警告：未找到 Analyst 的输出"
        )

        # 阶段4：质检阶段（单 Agent，可带工具）
        print_phase_header("阶段4：质量检查", "bold magenta")

        critic_prompt = get_critic_prompt(analyst_output)

        critic_team = RoundRobinGroupChat(
            participants=[self.critic],
            max_turns=3,  # 可能需要搜索验证
        )

        critic_loading = start_loading("质检中...")
        critic_result = await stream_messages(
            critic_team.run_stream(task=critic_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=True,
                show_tools=True,
                content_max_chars=200,
            ),
        )
        stop_loading(critic_loading)
        print_success("质检阶段完成")

        critic_output = _extract_agent_output(
            critic_result, "Critic", "警告：未找到 Critic 的输出"
        )

        # 阶段5：文档撰写阶段（单 Agent）
        print_phase_header("阶段5：文档生成", "bold blue")

        writing_prompt = get_writing_prompt(user_input, additional_info, analyst_output, critic_output)

        writing_team = RoundRobinGroupChat(
            participants=[self.writer],
            max_turns=1,
        )

        writing_loading = start_loading("文档生成中...")
        writing_result = await stream_messages(
            writing_team.run_stream(task=writing_prompt),
            display=StreamDisplayConfig(
                show_agent_headers=True,
                show_content=True,
                show_tools=False,
            ),
        )
        stop_loading(writing_loading)
        print_success("文档生成阶段完成")

        writer_output = _extract_agent_output(
            writing_result, "Writer", "警告：未找到 Writer 的输出"
        )

        # 保存文档
        output_path = self._save_document(writer_output)

        print("\n" + "=" * 80)
        print("策略文档生成完成！")
        print(f"文档已保存至：{output_path}")
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
        print("智能体团队")
        print("=" * 80)
        for agent in self.agents:
            print(f"  - {agent.name}")
        print("=" * 80 + "\n")
