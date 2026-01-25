"""
检索器：仅负责“关键词 -> 向量化 -> Chroma 查询”
"""
import chromadb
from chromadb.config import Settings

from config import CHROMADB_PATH, COLLECTION_NAME
from embedding_client import SiliconFlowEmbedding


class KnowledgeRetriever:
    """只做检索的轻量类"""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMADB_PATH),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedding_function = SiliconFlowEmbedding()

        try:
            self.collection = self.chroma_client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            print(f"✅ 成功连接到知识库: {COLLECTION_NAME}")
        except Exception as e:
            print(f"❌ 无法连接到知识库: {e}")
            print("请先运行: python init_db.py")
            raise

        print("✅ 检索器初始化成功")

    def retrieve_knowledge(self, keyword: str, n_results: int = 5) -> str:
        """
        从知识库检索相关内容

        Args:
            keyword: 查询关键词
            n_results: 返回结果数量

        Returns:
            格式化的检索结果
        """
        print(f"\n🔍 检索: {keyword}")

        try:
            # 显式计算 query_embedding，避免 Chroma 对 EmbeddingFunction 接口差异导致的类型错误
            query_embedding = self.embedding_function.embed_query(keyword)
            if not isinstance(query_embedding, list) or (
                query_embedding and not isinstance(query_embedding[0], (float, int))
            ):
                raise ValueError("Embedding 返回格式异常：期望 List[float]")

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )

            if not results["ids"][0]:
                return "⚠️ 未找到相关知识，建议补充该领域的背景信息。"

            # 格式化检索结果
            knowledge_text = f"📚 检索到 {len(results['ids'][0])} 条相关知识：\n\n"

            for i, (doc_id, doc, metadata, distance) in enumerate(
                zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ),
                1,
            ):
                similarity = 1 - distance
                # 控制台打印检索证据，便于验收
                print(
                    f"   • [{i}] id={doc_id} 关键词={metadata.get('keyword')} "
                    f"类别={metadata.get('category')} 相似度={similarity:.2%}"
                )
                knowledge_text += (
                    f"[{i}] 关键词: {metadata['keyword']} | "
                    f"类别: {metadata['category']} | 相似度: {similarity:.2%}\n"
                )
                knowledge_text += f"{doc}\n\n"

            print(f"✅ 找到 {len(results['ids'][0])} 条结果")
            return knowledge_text

        except Exception as e:
            print(f"❌ 检索失败: {e}")
            return f"❌ 检索失败: {str(e)}"


def create_retriever() -> KnowledgeRetriever:
    """创建检索器实例"""
    return KnowledgeRetriever()
