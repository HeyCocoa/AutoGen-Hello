"""
工具函数模块
提供Agent可以调用的工具函数
"""
from datetime import datetime
from typing import Annotated

from .config import Config


def get_current_date() -> Annotated[str, "当前日期（YYYY-MM-DD格式）"]:
    """
    获取当前日期，用于时效性分析

    Returns:
        当前日期字符串，格式：YYYY-MM-DD
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> Annotated[str, "当前时间（HH:MM:SS格式）"]:
    """
    获取当前时间

    Returns:
        当前时间字符串，格式：HH:MM:SS
    """
    return datetime.now().strftime("%H:%M:%S")


def web_search(query: Annotated[str, "搜索关键词"]) -> Annotated[str, "搜索结果摘要"]:
    """
    搜索行业信息和市场数据

    Args:
        query: 搜索关键词，例如"B2B SaaS市场趋势"、"东南亚电商规模"

    Returns:
        搜索结果摘要

    Raises:
        SystemExit: 联网搜索未启用或调用失败时退出程序
    """
    if not Config.is_zhipu_api():
        print("\n[错误] web_search 调用失败：当前未使用智谱AI API，联网搜索不可用")
        print("请在 .env 中配置智谱AI API：")
        print("  OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4")
        print("  OPENAI_API_KEY=your-zhipu-api-key")
        raise SystemExit(1)

    if not Config.ZHIPU_WEB_SEARCH_ENABLED:
        print("\n[错误] web_search 调用失败：联网搜索未启用")
        print("请在 .env 中设置：ZHIPU_WEB_SEARCH_ENABLED=true")
        raise SystemExit(1)

    return _zhipu_web_search(query)


def _zhipu_web_search(query: str) -> str:
    """调用智谱AI联网搜索API（使用zai SDK）"""
    try:
        from zai import ZhipuAiClient
    except ImportError:
        print("\n[错误] web_search 调用失败：未安装 zai-sdk")
        print("请运行: pip install zai-sdk")
        raise SystemExit(1)

    today = datetime.now().strftime("%Y年%m月%d日")

    tools = [{
        "type": "web_search",
        "web_search": {
            "enable": "True",
            "search_engine": Config.ZHIPU_SEARCH_ENGINE,
            "search_result": "True",
            "search_prompt": f"请用简洁的语言总结搜索结果中的关键信息，按重要性排序。今天是{today}。",
            "count": "5",
        }
    }]

    messages = [{"role": "user", "content": query}]

    try:
        client = ZhipuAiClient(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="glm-4.7-flash",
            messages=messages,
            tools=tools,
            max_tokens=2048,
        )

        content = response.choices[0].message.content
        if content:
            return f"【联网搜索结果】关于'{query}'：\n{content}"

        print(f"\n[错误] web_search 调用失败：未获取到关于'{query}'的搜索结果")
        raise SystemExit(1)

    except SystemExit:
        raise
    except Exception as e:
        print(f"\n[错误] web_search 调用失败：搜索'{query}'时出错")
        print(f"错误详情：{str(e)}")
        raise SystemExit(1)


def calculate(expression: Annotated[str, "数学表达式"]) -> Annotated[str, "计算结果"]:
    """
    计算数学表达式，用于市场规模、增长率等数值分析

    Args:
        expression: 数学表达式，例如"3000*0.15"（计算市场份额）

    Returns:
        计算结果
    """
    try:
        # 安全的eval：只允许数学运算
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含非法字符"

        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


# 导出所有工具
__all__ = [
    "get_current_date",
    "get_current_time",
    "web_search",
    "calculate",
]
