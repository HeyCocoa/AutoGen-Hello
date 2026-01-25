# Demo2: 科技媒体选题智能助手

## 📖 项目简介

这是一个基于 **AutoGen 0.4.2** 框架和 **Chromadb** 向量数据库的智能选题系统，实现了"关键词 -> 向量化 -> RAG 查询"的完整流程。

### 核心功能

1. **向量化检索**: 将用户输入的关键词向量化，在知识库中检索相关内容
2. **智能选题**: 结合检索到的历史策略和行业知识，生成专业选题建议
3. **手动 RAG 实现**: 直接调用 Chromadb API，无需依赖旧版 AutoGen 的 RAG 组件

### 技术栈

- **AutoGen 0.4.2**: 新版 Agent 框架（与 demo1 版本一致）
- **Chromadb**: 向量数据库，存储和检索知识
- **SiliconFlow API**: 中文 Embedding 模型 (BAAI/bge-large-zh-v1.5)
- **DeepSeek API**: LLM 推理服务
- **Rich**: 终端 UI 美化

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

已在 `.env` 文件中配置好 API Keys，无需修改。

### 3. 初始化知识库

```bash
python init_db.py
```

这将：
- 加载 60 条科技媒体选题知识（AI、区块链、云计算等领域）
- 向量化并存入 Chromadb
- 验证数据插入成功

### 4. 运行主程序

```bash
python main.py
```

## 💡 使用示例

### 基本查询

```
🔍 请输入关键词: AI大模型

系统会：
1. 向量化关键词 "AI大模型"
2. 在知识库中检索 Top-5 相关内容
3. 生成选题建议，包括：
   - 选题方向
   - 内容要点
   - 目标受众
   - 预期效果
```

## 📁 项目结构

```
demo2/
├── main.py                 # 主程序入口
├── agents.py               # AutoGen agents 定义
├── init_db.py              # 知识库初始化脚本
├── embedding_client.py     # SiliconFlow Embedding 客户端
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
├── .env                    # 环境变量
├── README.md               # 项目文档
├── data/                   # 知识库数据
│   ├── knowledge_base_part1.json  # 知识数据 (1-20)
│   ├── knowledge_base_part2.json  # 知识数据 (21-40)
│   └── knowledge_base_part3.json  # 知识数据 (41-60)
├── db/                     # Chromadb 数据库目录
└── README.md               # 项目文档
```

## 🔧 核心组件

### 1. Embedding Client

`embedding_client.py` 封装了 SiliconFlow API 调用，实现了 Chromadb 的 `EmbeddingFunction` 接口。

```python
embedding_function = SiliconFlowEmbedding()
embeddings = embedding_function.embed_documents(["AI大模型", "区块链"])
```

### 2. RAG Assistant

`agents.py` 中的 `RAGAssistant` 类手动实现了 RAG 逻辑：

```python
class RAGAssistant:
    def retrieve_knowledge(self, keyword: str) -> str:
        """从 Chromadb 检索相关知识"""
        results = self.collection.query(
            query_texts=[keyword],
            n_results=5
        )
        return formatted_knowledge

    async def generate_topic_suggestion(self, keyword: str) -> str:
        """生成选题建议"""
        knowledge = self.retrieve_knowledge(keyword)
        response = await self.agent.on_messages([...])
        return response.chat_message.content
```

### 3. AutoGen 0.4.2 Agent

使用新版 API 创建 AssistantAgent：

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    api_key="...",
    base_url="https://api.deepseek.com/v1",
)

agent = AssistantAgent(
    name="选题策划师",
    model_client=model_client,
    system_message="..."
)
```

## 📊 知识库内容

知识库包含 **60 条** 科技媒体选题知识，覆盖以下领域：

- **人工智能**: AI大模型、AIGC、机器学习、计算机视觉、NLP
- **区块链**: 区块链、智能合约、Web3、NFT、DeFi
- **云计算**: 云计算、容器技术、Kubernetes、微服务、Serverless
- **物联网**: 物联网、智能家居、工业互联网、车联网
- **前沿技术**: 5G、自动驾驶、芯片设计、量子计算、元宇宙
- **数据技术**: 大数据、数据湖、实时计算、数据中台
- **工程实践**: DevOps、云原生、API网关、消息队列、分布式系统

每条知识包含：
- **关键词**: 核心技术名称
- **类别**: 所属领域
- **内容**: 选题策略和行业背景
- **标签**: 相关技术标签

## 🎯 工作流程

```
用户输入关键词
    ↓
向量化 (SiliconFlow Embedding)
    ↓
Chromadb 检索 (Top-5 相似结果)
    ↓
RAGAssistant 格式化知识
    ↓
AssistantAgent 生成选题建议
    ↓
Rich 终端美化输出
```

## ⚙️ 配置说明

### LLM 配置 (DeepSeek)

```python
LLM_CONFIG = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_key": "sk-c43d04eb7c014c70a7a493cd4e2675ee",
        "base_url": "https://api.deepseek.com/v1",
    }],
    "temperature": 0.7,
}
```

### Embedding 配置 (SiliconFlow)

```python
EMBEDDING_API_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBEDDING_API_KEY = "sk-rpdclwdlhqaizqcygggqfzflkqdarcasgqgwxjrxqwkjpxhq"
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
```

## 🐛 常见问题

### 1. 知识库未初始化

```
⚠️  警告: 知识库尚未初始化！
请先运行: python init_db.py
```

**解决**: 运行 `python init_db.py` 初始化知识库。

### 2. API 调用失败

检查 `.env` 文件中的 API Keys 是否正确。

### 3. 检索结果不准确

- 调整 `n_results` 参数（在 `agents.py` 中增加检索数量）
- 添加更多相关知识到 `data/` 目录，重新运行 `init_db.py`

## 📝 版本说明

**与 demo1 的区别**：
- demo1: 使用 autogen 0.4.2 的多 Agent 协作
- demo2: 使用 autogen 0.4.2 + 手动实现 RAG 检索

**为什么不使用 pyautogen 0.2.x**：
- autogen 0.4.2 是新架构，与 demo1 保持一致
- 手动实现 RAG 更灵活，可以自定义检索逻辑
- 避免版本冲突，无需单独的虚拟环境

## 📝 扩展建议

1. **增加知识库**: 在 `data/` 目录添加更多 JSON 文件
2. **优化检索**: 调整 `chunk_token_size` 和 `n_results` 参数
3. **多轮对话**: 修改 `human_input_mode` 支持交互式对话
4. **Web 界面**: 使用 Gradio/Streamlit 构建 Web UI

## 📄 License

MIT License

## 👥 作者

AutoGen + Chromadb Demo Project
