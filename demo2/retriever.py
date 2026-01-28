"""向量检索器：通过向量索引查找，再从 SQLite 取完整内容"""
import chromadb
from chromadb.config import Settings

from config import CHROMADB_PATH, COLLECTION_NAME
from embedding_client import ZhipuAIEmbedding
from knowledge_db import KnowledgeDB


class KnowledgeRetriever:
    """向量检索器（索引层 + 数据层）"""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMADB_PATH),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedding_function = ZhipuAIEmbedding()
        self.collection = self.chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_function,
        )
        self.knowledge_db = KnowledgeDB()
        print(f"[OK] 检索器初始化成功")

    def retrieve(self, keyword: str, n_results: int = 5, min_similarity: float = 0.3) -> list:
        """
        检索相关知识，返回结构化数据

        Returns:
            [{"keyword": str, "content": str, "similarity": float, "sqlite_id": int}, ...]
        """
        query_embedding = self.embedding_function.embed_query(keyword)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

        if not results["ids"][0]:
            return []

        items = []
        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = 1 - distance
            if similarity < min_similarity:
                continue

            sqlite_id = metadata.get("sqlite_id")
            matched_keyword = metadata.get("keyword", "")

            content = ""
            if sqlite_id:
                record = self.knowledge_db.get_by_id(sqlite_id)
                if record:
                    content = record["content"]

            items.append({
                "keyword": matched_keyword,
                "content": content,
                "similarity": similarity,
                "sqlite_id": sqlite_id,
            })

        return items

    def retrieve_knowledge(self, keyword: str, n_results: int = 5) -> str:
        """检索并格式化输出（用于 local 命令显示）"""
        print(f"\n[SEARCH] 检索: {keyword}")

        items = self.retrieve(keyword, n_results, min_similarity=0.0)

        if not items:
            return "[WARN] 未找到相关知识"

        lines = [f"检索到 {len(items)} 条相关知识：\n"]
        for i, item in enumerate(items, 1):
            print(f"  [{i}] 关键词={item['keyword']} 相似度={item['similarity']:.2%}")
            lines.append(f"**[{i}] {item['keyword']}** (相似度: {item['similarity']:.2%})")
            lines.append(f"{item['content']}\n")

        return "\n".join(lines)


def create_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever()
