"""智谱AI Embedding 客户端"""
from typing import List

from chromadb.api.types import Documents, EmbeddingFunction
from zai import ZhipuAiClient

from config import EMBEDDING_MODEL, ZHIPUAI_API_KEY


class ZhipuAIEmbedding(EmbeddingFunction):
    """智谱AI Embedding API 客户端"""

    def __init__(self):
        if not ZHIPUAI_API_KEY:
            raise ValueError("ZHIPUAI_API_KEY 未设置，请检查 .env 文件")
        self.client = ZhipuAiClient(api_key=ZHIPUAI_API_KEY)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文本"""
        response = self.client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        """向量化单个查询文本"""
        response = self.client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
        return response.data[0].embedding

    def __call__(self, input: Documents) -> List[List[float]]:
        """兼容 Chromadb 的 EmbeddingFunction 接口"""
        if isinstance(input, str):
            return [self.embed_query(input)]
        if isinstance(input, list):
            return self.embed_documents(input)
        raise ValueError(f"不支持的输入类型: {type(input)}")
