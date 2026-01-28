# Demo2: 向量检索

## 项目简介

基于 **Chromadb** 向量数据库与 **智谱AI Embedding** 的通用检索示例，实现"关键词 -> 向量化 -> RAG 查询"流程。

### 技术栈

- **Chromadb**: 向量数据库
- **智谱AI API**: Embedding 模型 (embedding-3)
- **Rich**: 终端 UI
- **python-dotenv**: 环境变量管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 中配置：

- `ZHIPUAI_API_KEY`
- `ZHIPUAI_EMBEDDING_MODEL`（可选，默认 embedding-3）

### 3. 准备数据

在 `data/` 目录下放置 JSON 文件，格式如下：

```json
[
  {
    "id": "1",
    "keyword": "关键词",
    "category": "分类",
    "content": "内容描述",
    "tags": ["标签1", "标签2"]
  }
]
```

### 4. 初始化知识库

```bash
python init_db.py
```

### 5. 运行主程序

```bash
python main.py
```

## 项目结构

```
demo2/
├── main.py                 # 主程序入口
├── retriever.py            # 检索器
├── init_db.py              # 知识库初始化
├── embedding_client.py     # 智谱AI Embedding 客户端
├── config.py               # 配置文件
├── requirements.txt        # 依赖
├── .env                    # 环境变量
├── data/                   # 知识库数据（JSON）
└── db/                     # Chromadb 数据库目录
```

## 核心组件

### Embedding Client

```python
from embedding_client import ZhipuAIEmbedding

embedding = ZhipuAIEmbedding()
vectors = embedding.embed_documents(["文本1", "文本2"])
```

### 检索器

```python
from retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()
result = retriever.retrieve_knowledge("关键词", n_results=5)
```

## 工作流程

```
用户输入关键词
    ↓
向量化 (智谱AI Embedding)
    ↓
Chromadb 检索 (Top-N 相似结果)
    ↓
格式化输出
```

## License

MIT License
