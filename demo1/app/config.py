"""配置管理模块"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """应用配置类"""

    # 智谱AI API 配置（本项目依赖智谱联网搜索，不支持其他 LLM）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
    MODEL_NAME = os.getenv("MODEL_NAME", "glm-4.7-flashx")

    # 智谱AI联网搜索配置
    ZHIPU_WEB_SEARCH_ENABLED = os.getenv("ZHIPU_WEB_SEARCH_ENABLED", "false").lower() == "true"
    ZHIPU_SEARCH_ENGINE = os.getenv("ZHIPU_SEARCH_ENGINE", "search_std")

    OUTPUT_DIR = "output"

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "未找到 OPENAI_API_KEY！\n"
                "请创建 .env 文件并设置智谱AI API Key：\n"
                "  OPENAI_API_KEY=your-zhipu-api-key\n"
                "  ZHIPU_WEB_SEARCH_ENABLED=true"
            )

        if not cls.is_zhipu_api():
            raise ValueError(
                "本项目依赖智谱AI联网搜索功能，不支持其他 LLM 服务。\n"
                "请在 .env 中配置：\n"
                "  OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4"
            )

        if not cls.ZHIPU_WEB_SEARCH_ENABLED:
            raise ValueError(
                "联网搜索未启用！\n"
                "请在 .env 中设置：ZHIPU_WEB_SEARCH_ENABLED=true"
            )

        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return True

    @classmethod
    def is_zhipu_api(cls) -> bool:
        """判断是否使用智谱AI API"""
        return "bigmodel.cn" in (cls.OPENAI_API_BASE or "")
