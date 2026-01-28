"""配置文件：管理 API keys 和存储配置"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 智谱AI API Key (共用)
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")

# Embedding 配置
EMBEDDING_MODEL = os.getenv("ZHIPUAI_EMBEDDING_MODEL", "embedding-3")

# 联网搜索配置
WEB_SEARCH_ENABLED = os.getenv("ZHIPU_WEB_SEARCH_ENABLED", "false").lower() == "true"
WEB_SEARCH_MODEL = os.getenv("ZHIPUAI_CHAT_MODEL", "glm-4.7-flash")
WEB_SEARCH_ENGINE = os.getenv("ZHIPU_SEARCH_ENGINE", "search_std")

# 数据库路径
DB_DIR = Path("./db")
CHROMADB_PATH = DB_DIR / "chromadb"
SQLITE_DB_PATH = DB_DIR / "knowledge.db"
COLLECTION_NAME = "knowledge_base"
