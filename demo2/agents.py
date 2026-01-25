"""
AutoGen Agents 定义（适配 autogen 0.4.2）
手动实现 RAG 检索逻辑
"""
import asyncio
import chromadb
from chromadb.config import Settings
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from config import LLM_CONFIG, CHROMADB_PATH, COLLECTION_NAME
from embedding_client import SiliconFlowEmbedding


class RAGAssistant:
    """带 RAG 能力的选题助手"""

    def __init__(self):
        # 初始化 Chromadb 客户端
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMADB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_function = SiliconFlowEmbedding()

        # 获取集合
        try:
            self.collection = self.chroma_client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"✅ 成功连接到知识库: {COLLECTION_NAME}")
        except Exception as e:
            print(f"❌ 无法连接到知识库: {e}")
            print("请先运行: python init_db.py")
            raise

        # 创建 LLM 客户端
        model_client = OpenAIChatCompletionClient(
            model=LLM_CONFIG["config_list"][0]["model"],
            api_key=LLM_CONFIG["config_list"][0]["api_key"],
            base_url=LLM_CONFIG["config_list"][0]["base_url"],
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": False,
            }
        )

        # 创建 AssistantAgent
        self.agent = AssistantAgent(
            name="选题策划师",
            model_client=model_client,
            system_message="""你是一位资深的科技媒体选题策划师。

你的职责是：
1. 根据用户输入的行业关键词，结合提供的历史选题策略和行业背景知识
2. 生成一份专业的选题建议，包括：
   - 选题方向（3-5个具体选题）
   - 内容要点（每个选题的核心内容）
   - 目标受众
   - 预期效果

请用专业、简洁的语言回复，突出实用性和可操作性。
如果提供的背景知识不足，请明确指出缺少哪方面的信息。""",
        )

        print("✅ RAG Assistant 初始化成功")

    def retrieve_knowledge(self, keyword: str, n_results: int = 5) -> str:
        """
        从知识库检索相关内容

        Args:
            keyword: 查询关键词
            n_results: 返回结果数量

        Returns:
            格式化的检索结果
        """
        print(f"\n🔍 正在检索关键词: {keyword}")

        try:
            results = self.collection.query(
                query_texts=[keyword],
                n_results=n_results
            )

            if not results['ids'][0]:
                return "⚠️ 未找到相关知识，建议补充该领域的背景信息。"

            # 格式化检索结果
            knowledge_text = f"📚 检索到 {len(results['ids'][0])} 条相关知识：\n\n"

            for i, (doc_id, doc, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                similarity = 1 - distance
                knowledge_text += f"[{i}] 关键词: {metadata['keyword']} | 类别: {metadata['category']} | 相似度: {similarity:.2%}\n"
                knowledge_text += f"{doc}\n\n"

            print(f"✅ 检索完成，找到 {len(results['ids'][0])} 条结果")
            return knowledge_text

        except Exception as e:
            print(f"❌ 检索失败: {e}")
            return f"❌ 检索失败: {str(e)}"

    async def generate_topic_suggestion(self, keyword: str) -> str:
        """
        生成选题建议

        Args:
            keyword: 用户输入的关键词

        Returns:
            选题建议文本
        """
        # 1. 检索相关知识
        knowledge = self.retrieve_knowledge(keyword, n_results=5)

        # 2. 构造提示词
        prompt = f"""请根据以下关键词和背景知识，生成专业的选题建议：

**关键词**: {keyword}

**背景知识**:
{knowledge}

请生成选题建议。"""

        # 3. 调用 Agent 生成回复
        print("\n💡 正在生成选题建议...")

        response = await self.agent.on_messages(
            [{"content": prompt, "source": "user"}],
            cancellation_token=None
        )

        return response.chat_message.content

    async def chat_interactive(self, keyword: str):
        """
        交互式对话（支持多轮）

        Args:
            keyword: 初始关键词
        """
        # 检索知识
        knowledge = self.retrieve_knowledge(keyword, n_results=5)

        # 构造初始消息
        initial_message = f"""请根据关键词"{keyword}"生成选题建议。

背景知识：
{knowledge}"""

        # 创建终止条件
        termination = TextMentionTermination("TERMINATE")

        # 创建单 Agent 团队
        team = RoundRobinGroupChat(
            [self.agent],
            termination_condition=termination,
        )

        # 运行对话
        await Console(team.run_stream(task=initial_message))


def create_rag_assistant():
    """创建 RAG Assistant 实例"""
    return RAGAssistant()


# 同步包装函数
def generate_topic_sync(keyword: str) -> str:
    """同步版本的选题生成"""
    assistant = create_rag_assistant()
    result = asyncio.run(assistant.generate_topic_suggestion(keyword))
    return result


if __name__ == "__main__":
    # 测试
    print("🧪 测试 RAG Assistant...")
    assistant = create_rag_assistant()
    result = asyncio.run(assistant.generate_topic_suggestion("AI大模型"))
    print("\n" + "="*60)
    print(result)
