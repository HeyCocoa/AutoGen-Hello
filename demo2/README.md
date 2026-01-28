# Demo2: 向量检索 + 语义扩展

## 项目简介

基于 **Chromadb** 向量数据库与 **智谱AI** 的检索系统，支持：
- 向量语义检索
- 联网搜索扩展
- SQLite 数据沉淀

### 技术栈

- **Chromadb**: 向量数据库
- **智谱AI API**: Embedding (embedding-3) + 联网搜索 (glm-4.7-flash)
- **SQLite**: 知识持久化存储
- **Rich**: 终端 UI

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 中配置：

```env
ZHIPUAI_API_KEY=your_api_key
ZHIPUAI_EMBEDDING_MODEL=embedding-3
ZHIPUAI_CHAT_MODEL=glm-4.7-flash
ZHIPU_WEB_SEARCH_ENABLED=true
ZHIPU_SEARCH_ENGINE=search_std
```

### 3. 运行主程序

```bash
python main.py
```

## 使用方式

| 命令 | 说明 |
|------|------|
| `<关键词>` | 向量检索（需先初始化向量库） |
| `web <关键词>` | 语义扩展 + 联网搜索，结果存入 SQLite |
| `sync` | 同步 SQLite 数据到向量库 |
| `stats` | 查看 SQLite 统计 |
| `help` | 显示帮助 |
| `exit` | 退出 |

## 项目结构

```
demo2/
├── main.py                 # 主程序入口
├── retriever.py            # 向量检索器
├── semantic_searcher.py    # 语义扩展检索器
├── web_searcher.py         # 联网搜索模块
├── knowledge_db.py         # SQLite 知识库管理
├── sync_to_vector.py       # SQLite -> Chromadb 同步
├── embedding_client.py     # 智谱AI Embedding 客户端
├── init_db.py              # 向量库初始化（可选）
├── config.py               # 配置文件
├── requirements.txt        # 依赖
├── .env                    # 环境变量
├── data/                   # 初始知识库数据（JSON）
└── db/                     # 数据库目录
    ├── chromadb/           # Chromadb 向量数据库
    └── knowledge.db        # SQLite 知识库
```

## 工作流程

```
用户输入关键词
    ↓
向量库模糊匹配 → 扩展关键词
    ↓
智谱联网 LLM 搜索
    ↓
搜索结果 → 存入 SQLite
    ↓
（sync 命令）SQLite → 向量化 → Chromadb
```

## 数据双向增值

1. **SQLite → 向量库**：联网搜索的结果可同步到向量库，增强未来检索
2. **长期存储**：SQLite 作为持久化存储，数据可供后续其他用途

## License

MIT License
