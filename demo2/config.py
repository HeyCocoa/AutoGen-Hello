"""配置文件：管理 API keys 和存储配置"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

EMBEDDING_CONFIG = {
    "api_key": os.getenv("ZHIPUAI_API_KEY"),
    "model": os.getenv("ZHIPUAI_EMBEDDING_MODEL", "embedding-3"),
}

CHROMADB_PATH = Path("./db")
COLLECTION_NAME = "knowledge_base"

CHROMADB_CONFIG = {
    "persist_directory": str(CHROMADB_PATH),
    "collection_name": COLLECTION_NAME,
}
