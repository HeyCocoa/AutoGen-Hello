# 选题策略生成器 (Topic Strategy Generator)

基于 AutoGen 的多智能体选题策略生成系统，能够根据用户输入的业务场景自动生成可执行的选题策略。

## 功能特性

- 🤖 **多智能体协作**：4个专业角色协同工作
- 💬 **智能澄清**：自动识别信息缺口并提问
- 📊 **策略生成**：输出结构化、可执行的选题策略
- 📝 **Markdown输出**：生成专业的策略文档
- 🔄 **灵活配置**：支持 DeepSeek、OpenAI 等多种 LLM 服务
- 👁️ **过程可见**：实时显示每个智能体的工作过程

## 快速开始

### 1. 安装依赖

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
```

### 3. 运行程序

```bash
# 方式1：使用 Python 模块
python -m app
```

### 4. 输入业务场景

程序启动后，输入你的业务场景，例如：

```
业务场景：B2B SaaS产品出海，目标市场是东南亚，
产品是企业协作工具，目标客户是50-500人的中小企业。
END
```

**重要提示**：输入完成后，单独一行输入 `END` 并回车结束输入。

### 5. 查看结果

生成的策略文档会保存在 `output/` 目录下，文件名格式为 `strategy_YYYYMMDD_HHMMSS.md`。

## 系统架构

系统包含4个智能体角色，采用顺序协作模式：

1. **Clarifier（澄清者）**
   - 识别信息缺口
   - 提出3个最关键问题
   - 自动判断是否需要澄清

2. **Analyst（分析师）**
   - 深度业务分析
   - 受众画像
   - 市场环境分析
   - 关键洞察提取

3. **Critic（质检员）**
   - 质疑分析结论
   - 找出逻辑漏洞与盲点
   - 必要时进行验证搜索

4. **Writer（撰写者）**
   - 整合所有输出
   - 生成结构化Markdown
   - 专业文档格式

## 环境要求

- Python 3.10+
- API Key（支持以下任一服务）：
  - **DeepSeek**（推荐，性价比高）
  - OpenAI
  - Azure OpenAI
  - 其他兼容 OpenAI API 格式的服务

## 项目结构

```
demo1/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # 程序入口
│   ├── agents/              # 智能体定义
│   │   ├── __init__.py
│   │   ├── coordinator.py
│   │   ├── clarifier.py
│   │   ├── analyst.py
│   │   ├── critic.py
│   │   └── writer.py
│   ├── config.py            # 配置管理
│   └── workflow.py          # 工作流编排
├── output/                  # 运行时输出目录
├── .env.example             # 环境变量模板
├── .gitignore
├── requirements.txt
├── Makefile
└── README.md
```

## 技术栈

- **AutoGen 0.4+**：多智能体框架（使用 autogen-agentchat）
- **Python 3.10+**：主要开发语言
- **python-dotenv**：环境变量管理
- **LLM API**：支持 DeepSeek、OpenAI 等兼容服务
