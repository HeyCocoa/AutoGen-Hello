"""
配置文件：管理 API keys 和模型配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek LLM 配置
LLM_CONFIG = {
    "config_list": [
        {
            "model": os.getenv("MODEL_NAME", "deepseek-chat"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_API_BASE"),
            "api_type": "openai",
        }
    ],
    "temperature": 0.7,
    "timeout": 120,
}

# 非 OpenAI 模型需要提供 model_info
MODEL_INFO = {
    "deepseek-chat": {
        "max_tokens": 4096,
        "context_window": 32768,
        "supports_function_calling": True,
        "supports_vision": False,
    }
}

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

# 系统提示词
SYSTEM_PROMPTS = {
    "assistant": """你是一位资深的科技媒体编辑，擅长分析行业趋势并提供选题建议。
你的任务是：
1. 根据用户输入的行业关键词，从知识库中检索相关的历史选题策略和行业背景
2. 结合检索到的信息，生成具有洞察力的选题建议
3. 如果知识库中没有相关信息，请明确告知用户，并建议补充相关知识

请用专业、简洁的语言回答，重点突出可操作性。""",

    "user_proxy": """你是用户的代理，负责与助手交互并管理知识库。
当助手需要更多信息时，你会提示用户补充知识。""",
}
