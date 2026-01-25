"""
自定义 Embedding Client：封装 SiliconFlow API 调用
"""
import requests
from typing import List, Union
from config import EMBEDDING_CONFIG


class SiliconFlowEmbedding:
    """SiliconFlow Embedding API 客户端"""

    def __init__(self):
        self.api_key = EMBEDDING_CONFIG["api_key"]
        self.api_base = EMBEDDING_CONFIG["api_base"]
        self.model = EMBEDDING_CONFIG["model"]

        if not self.api_key:
            raise ValueError("EMBEDDING_API_KEY 未设置，请检查 .env 文件")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量向量化文本

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        embeddings = []
        for text in texts:
            embedding = self._embed_single(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str = None, input: str = None) -> List[float]:
        """
        向量化单个查询文本（兼容 Chromadb 的 input 参数）

        Args:
            text: 查询文本
            input: 查询文本（Chromadb 使用此参数名）

        Returns:
            向量
        """
        query_text = input if input is not None else text
        if query_text is None:
            raise ValueError("必须提供 text 或 input 参数")
        return self._embed_single(query_text)

    def _embed_single(self, text: str) -> List[float]:
        """
        调用 SiliconFlow API 进行向量化

        Args:
            text: 输入文本

        Returns:
            向量（List[float]）
        """
        payload = {
            "model": self.model,
            "input": text
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_base, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            # SiliconFlow API 返回格式: {"data": [{"embedding": [...]}]}
            embedding = result["data"][0]["embedding"]
            return embedding

        except requests.exceptions.RequestException as e:
            print(f"❌ Embedding API 调用失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            print(f"❌ 解析 Embedding 响应失败: {e}")
            print(f"响应内容: {response.text}")
            raise

    def __call__(self, input: Union[str, List[str]]) -> List[List[float]]:
        """
        兼容 Chromadb 的 EmbeddingFunction 接口
        注意：Chromadb 总是期望返回 List[List[float]]，即使输入是单个字符串

        Args:
            input: 单个文本或文本列表

        Returns:
            向量列表（二维列表）
        """
        if isinstance(input, str):
            # 单个文本也返回二维列表
            return [self.embed_query(input)]
        elif isinstance(input, list):
            return self.embed_documents(input)
        else:
            raise ValueError(f"不支持的输入类型: {type(input)}")
