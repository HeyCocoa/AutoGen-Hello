"""
配置文件：管理 API keys 和存储配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# SiliconFlow Embedding 配置
EMBEDDING_CONFIG = {
    "api_key": os.getenv("EMBEDDING_API_KEY"),
    "api_base": os.getenv("EMBEDDING_API_BASE"),
    "model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5"),
}

# Chromadb 配置
CHROMADB_PATH = Path("./db")
COLLECTION_NAME = "tech_media_knowledge"

CHROMADB_CONFIG = {
    "persist_directory": str(CHROMADB_PATH),
    "collection_name": COLLECTION_NAME,
}
