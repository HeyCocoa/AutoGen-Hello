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
    """
    if Config.is_zhipu_api() and Config.ZHIPU_WEB_SEARCH_ENABLED:
        return _zhipu_web_search(query)
    return _mock_web_search(query)


def _zhipu_web_search(query: str) -> str:
    """调用智谱AI联网搜索API（使用zai SDK）"""
    try:
        from zai import ZhipuAiClient
    except ImportError:
        return f"【搜索失败】未安装 zai-sdk，请运行: pip install zai-sdk"

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
        return f"【搜索失败】未获取到关于'{query}'的搜索结果"

    except Exception as e:
        return f"【搜索错误】搜索'{query}'时出错：{str(e)}"


def _mock_web_search(query: str) -> str:
    """模拟搜索结果（备用）"""
    mock_results = {
        "B2B SaaS": "B2B SaaS市场在2024年持续增长，全球市场规模预计达到3000亿美元。主要趋势：AI集成、垂直化解决方案、订阅模式优化。",
        "东南亚": "东南亚数字经济快速发展，2025年预计达到3000亿美元规模。主要市场：印尼、越南、泰国、菲律宾。",
        "IVD": "体外诊断（IVD）市场规模持续扩大，2024年全球市场约900亿美元。中国市场占比约15%，年增长率12%。",
        "电商": "电商市场竞争激烈，2024年中国网络零售额超15万亿。获客成本持续上升。",
        "内容营销": "内容营销ROI持续提升，2024年企业平均投入占比达25%。有效形式：短视频、长文深度内容、互动直播。",
        "出海": "中国企业出海加速，2024年跨境电商交易额超2万亿。热门市场：东南亚、中东、拉美。",
        "AI": "AI技术快速发展，2024年全球AI市场规模超5000亿美元。主要应用：大语言模型、计算机视觉、智能客服。",
    }

    query_lower = query.lower()
    for key, result in mock_results.items():
        if key.lower() in query_lower or key in query:
            return f"【搜索结果】关于'{query}'：\n{result}"

    return f"【搜索结果】关于'{query}'：建议关注行业最新动态、竞品分析、用户需求变化等维度进行深入研究。"


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
