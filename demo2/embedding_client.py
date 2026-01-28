"""自定义 Embedding Client：封装智谱AI Embedding API 调用"""
from typing import List

from chromadb.api.types import Documents, EmbeddingFunction
from zai import ZhipuAiClient

from config import EMBEDDING_CONFIG


class ZhipuAIEmbedding(EmbeddingFunction):
    """智谱AI Embedding API 客户端"""

    def __init__(self):
        self.api_key = EMBEDDING_CONFIG["api_key"]
        self.model = EMBEDDING_CONFIG["model"]

        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY 未设置，请检查 .env 文件")

        self.client = ZhipuAiClient(api_key=self.api_key)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文本"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str = None, input: str = None) -> List[float]:
        """向量化单个查询文本（兼容 Chromadb 的 input 参数）"""
        query_text = input if input is not None else text
        if query_text is None:
            raise ValueError("必须提供 text 或 input 参数")

        response = self.client.embeddings.create(
            model=self.model,
            input=[query_text],
        )
        return response.data[0].embedding

    def __call__(self, input: Documents) -> List[List[float]]:
        """兼容 Chromadb 的 EmbeddingFunction 接口"""
        if isinstance(input, str):
            return [self.embed_query(input)]
        if isinstance(input, list):
            return self.embed_documents(input)
        raise ValueError(f"不支持的输入类型: {type(input)}")
