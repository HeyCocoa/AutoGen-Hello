"""
工具函数模块
提供Agent可以调用的工具函数
"""
from datetime import datetime
from typing import Annotated


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
    搜索行业信息和市场数据（模拟实现）

    Args:
        query: 搜索关键词，例如"B2B SaaS市场趋势"、"东南亚电商规模"

    Returns:
        搜索结果摘要

    Note:
        这是一个模拟实现。如果需要真实搜索，可以集成：
        - DuckDuckGo API (pip install duckduckgo-search)
        - Google Custom Search API
        - Bing Search API
        - Tavily AI (专为AI设计)
    """
    # 模拟搜索结果库
    mock_results = {
        "B2B SaaS": "B2B SaaS市场在2024年持续增长，全球市场规模预计达到3000亿美元。主要趋势：AI集成、垂直化解决方案、订阅模式优化。关键增长领域：销售自动化、客户成功管理、数据分析平台。",
        "东南亚": "东南亚数字经济快速发展，2025年预计达到3000亿美元规模。主要市场：印尼、越南、泰国、菲律宾。增长点：电商（年增长25%）、金融科技、在线教育。用户特征：移动优先、社交驱动、价格敏感。",
        "IVD": "体外诊断（IVD）市场规模持续扩大，2024年全球市场约900亿美元。中国市场占比约15%，年增长率12%。主要趋势：POCT快速增长、分子诊断普及、AI辅助诊断。政策支持：集采常态化、国产替代加速。",
        "电商": "电商市场竞争激烈，2024年中国网络零售额超15万亿。获客成本持续上升（CAC增长30%）。有效策略：私域流量运营、内容电商、直播带货、社交裂变。关键指标：ROI、复购率、LTV。",
        "内容营销": "内容营销ROI持续提升，2024年企业平均投入占比达25%。有效形式：短视频（抖音、视频号）、长文深度内容、互动直播、用户UGC。关键：价值输出、情感共鸣、持续更新。",
        "出海": "中国企业出海加速，2024年跨境电商交易额超2万亿。热门市场：东南亚、中东、拉美。成功要素：本地化运营、合规管理、支付物流、文化适配。挑战：政策风险、品牌认知、竞争加剧。",
        "AI": "AI技术快速发展，2024年全球AI市场规模超5000亿美元。主要应用：大语言模型、计算机视觉、自动驾驶、智能客服。企业应用：提效降本、个性化推荐、智能决策。关注：数据安全、伦理问题。",
    }

    # 关键词匹配
    query_lower = query.lower()
    for key, result in mock_results.items():
        if key.lower() in query_lower or key in query:
            return f"【搜索结果】关于'{query}'：\n{result}"

    return f"【搜索结果】关于'{query}'：建议关注行业最新动态、竞品分析、用户需求变化、政策环境等维度进行深入研究。"


def calculate(expression: Annotated[str, "数学表达式"]) -> Annotated[str, "计算结果"]:
    """
    计算数学表达式，用于市场规模、增长率等数值分析

    Args:
        expression: 数学表达式，例如"3000*0.15"（计算市场份额）

    Returns:
        计算结果

    Examples:
        >>> calculate("2+2")
        "计算结果：4"
        >>> calculate("3000*0.15")
        "计算结果：450.0"
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
