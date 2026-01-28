"""联网搜索模块：调用智谱AI联网搜索API + AI提取关键词"""
import json
from datetime import datetime

from zai import ZhipuAiClient

from config import WEB_SEARCH_ENABLED, WEB_SEARCH_ENGINE, WEB_SEARCH_MODEL, ZHIPUAI_API_KEY

_client = None


def _get_client() -> ZhipuAiClient:
    global _client
    if _client is None:
        if not ZHIPUAI_API_KEY:
            raise RuntimeError("ZHIPUAI_API_KEY 未设置")
        _client = ZhipuAiClient(api_key=ZHIPUAI_API_KEY)
    return _client


def web_search(query: str) -> str:
    """调用智谱AI联网搜索"""
    if not WEB_SEARCH_ENABLED:
        raise RuntimeError("联网搜索未启用，请在 .env 中设置 ZHIPU_WEB_SEARCH_ENABLED=true")

    today = datetime.now().strftime("%Y年%m月%d日")
    tools = [
        {
            "type": "web_search",
            "web_search": {
                "enable": "True",
                "search_engine": WEB_SEARCH_ENGINE,
                "search_result": "True",
                "search_prompt": f"请用简洁的语言总结搜索结果中的关键信息。今天是{today}。",
                "count": "5",
            },
        }
    ]

    client = _get_client()
    response = client.chat.completions.create(
        model=WEB_SEARCH_MODEL,
        messages=[{"role": "user", "content": query}],
        tools=tools,
        max_tokens=2048,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError(f"未获取到关于 '{query}' 的搜索结果")

    return content


def extract_knowledge_items(search_result: str) -> list:
    """
    用 AI 从搜索结果中提取结构化知识条目

    Returns:
        [{"keyword": "核心关键词", "content": "完整内容"}, ...]
    """
    prompt = f"""请从以下搜索结果中提取知识条目。

要求：
1. 每个独立的知识点作为一条
2. keyword: 该条内容的核心关键词（2-6个字，用于检索匹配）
3. content: 该条的完整内容

输出 JSON 数组格式：
[{{"keyword": "关键词1", "content": "内容1"}}, {{"keyword": "关键词2", "content": "内容2"}}]

搜索结果：
{search_result}

只输出 JSON，不要其他内容："""

    client = _get_client()
    response = client.chat.completions.create(
        model=WEB_SEARCH_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )

    content = response.choices[0].message.content
    if not content:
        return [{"keyword": "搜索结果", "content": search_result}]

    # 解析 JSON
    try:
        # 处理可能的 markdown 代码块
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        items = json.loads(content)
        if isinstance(items, list) and items:
            return items
    except (json.JSONDecodeError, IndexError):
        pass

    # 解析失败，返回整体
    return [{"keyword": "搜索结果", "content": search_result}]
