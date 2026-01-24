"""
配置管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # API 配置（支持 OpenAI、DeepSeek 等兼容服务）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

    # 输出配置
    OUTPUT_DIR = "output"

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "未找到 OPENAI_API_KEY！\n"
                "请创建 .env 文件并设置 OPENAI_API_KEY=your_key_here\n"
                "支持 OpenAI、DeepSeek 等兼容 OpenAI API 格式的服务"
            )

        # 确保输出目录存在
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

        return True
