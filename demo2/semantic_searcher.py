"""语义扩展检索器：联网搜索 + AI提取 + 向量扩展 + 自动同步"""
from typing import Optional

from knowledge_db import KnowledgeDB
from retriever import KnowledgeRetriever
from sync_to_vector import sync_to_vector
from web_searcher import extract_knowledge_items, web_search


class SemanticSearcher:
    """语义扩展检索器"""

    def __init__(self, retriever: Optional[KnowledgeRetriever] = None):
        self.retriever = retriever
        self.knowledge_db = KnowledgeDB()

    def search(self, keyword: str, n_expand: int = 3, min_similarity: float = 0.3) -> dict:
        """
        语义扩展搜索

        流程：
        1. 向量库查找相关关键词（相似度 > min_similarity 才算有效扩展）
        2. 用原始关键词 + 扩展关键词联网搜索
        3. AI 提取知识条目，分条存入 SQLite
        4. 自动同步到向量库
        """
        expanded_keywords = []

        # 1. 向量扩展（只取相似度足够高的）
        if self.retriever:
            try:
                items = self.retriever.retrieve(keyword, n_results=n_expand, min_similarity=min_similarity)
                expanded_keywords = [item["keyword"] for item in items if item["keyword"]]
                if expanded_keywords:
                    print(f"[EXPAND] 扩展关键词: {', '.join(expanded_keywords)}")
            except Exception as e:
                print(f"[WARN] 向量检索失败: {e}")

        # 2. 联网搜索（原始关键词 + 有效扩展）
        search_terms = [keyword] + expanded_keywords[:3]
        search_query = " ".join(search_terms)
        print(f"[SEARCH] 联网搜索: {search_query}")
        web_results = web_search(search_query)

        # 3. AI 提取知识条目
        print("[EXTRACT] AI 提取知识条目...")
        items = extract_knowledge_items(web_results)
        print(f"[OK] 提取到 {len(items)} 条知识")

        # 4. 分条存入 SQLite
        saved_ids = []
        for item in items:
            saved_id = self.knowledge_db.save(
                keyword=item["keyword"],
                content=item["content"],
            )
            saved_ids.append(saved_id)
            print(f"  - [{saved_id}] {item['keyword']}")

        # 5. 自动同步到向量库
        print("[SYNC] 同步到向量库...")
        sync_to_vector()

        return {
            "keyword": keyword,
            "expanded_keywords": expanded_keywords,
            "web_results": web_results,
            "saved_count": len(saved_ids),
            "items": items,
        }


def create_semantic_searcher(retriever: Optional[KnowledgeRetriever] = None) -> SemanticSearcher:
    return SemanticSearcher(retriever)
