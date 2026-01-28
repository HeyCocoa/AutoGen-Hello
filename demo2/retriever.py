"""检索器：仅负责"关键词 -> 向量化 -> Chroma 查询" """
import chromadb
from chromadb.config import Settings

from config import CHROMADB_PATH, COLLECTION_NAME
from embedding_client import ZhipuAIEmbedding


class KnowledgeRetriever:
    """只做检索的轻量类"""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMADB_PATH),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedding_function = ZhipuAIEmbedding()

        try:
            self.collection = self.chroma_client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            print(f"[OK] 成功连接到知识库: {COLLECTION_NAME}")
        except Exception as e:
            print(f"[ERROR] 无法连接到知识库: {e}")
            print("请先运行: python init_db.py")
            raise

        print("[OK] 检索器初始化成功")

    def retrieve_knowledge(self, keyword: str, n_results: int = 5) -> str:
        """从知识库检索相关内容"""
        print(f"\n[SEARCH] 检索: {keyword}")

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
            return "[WARN] 未找到相关知识，建议补充该领域的背景信息。"

        knowledge_text = f"[INFO] 检索到 {len(results['ids'][0])} 条相关知识：\n\n"

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
            print(
                f"   [{i}] id={doc_id} 关键词={metadata.get('keyword')} "
                f"类别={metadata.get('category')} 相似度={similarity:.2%}"
            )
            knowledge_text += (
                f"[{i}] 关键词: {metadata['keyword']} | "
                f"类别: {metadata['category']} | 相似度: {similarity:.2%}\n"
            )
            knowledge_text += f"{doc}\n\n"

        print(f"[OK] 找到 {len(results['ids'][0])} 条结果")
        return knowledge_text


def create_retriever() -> KnowledgeRetriever:
    """创建检索器实例"""
    return KnowledgeRetriever()
