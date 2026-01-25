# Repository Guidelines

## 项目结构与模块组织
- `app/` 为核心包，入口在 `app/__main__.py`，流程编排在 `app/workflow.py`，智能体定义在 `app/agents/`，流式输出与 UI 在 `app/utils/`。
- `output/` 为运行期生成物（策略 Markdown 等），视为产物目录而非源码。
- 依赖在 `requirements.txt`，架构说明见 `CLAUDE.md` 与 `README.md`。

## 构建、测试与开发命令
- `pip install -r requirements.txt`：安装依赖。
- `python -m app`：本地运行 CLI 工作流。
- `cp .env.example .env`：初始化配置，设置 `OPENAI_API_KEY`，可选 `OPENAI_API_BASE`/`MODEL_NAME`。

## 编码风格与命名规范
- Python 3.10+，4 空格缩进，遵循 PEP 8。
- 模块/函数使用 `snake_case`，类使用 `PascalCase`。
- Prompt 只放在 `app/agents/*.py`，终端显示与流式控制集中在 `app/utils/`。

## 测试指引
- 目前无自动化测试框架。
- 建议每次修改流程或输出展示后进行一次手动冒烟：`python -m app`。
- 输出文件命名形如 `output/strategy_YYYYMMDD_HHMMSS.md`。

## 提交与 PR 指引
- 现有提交信息以简短中文动词短语为主，偶尔带范围前缀（例如 `demo1:`）。
- 建议提交信息描述清晰、单一意图（如“优化命令行输出”）。
- 若改动影响终端可见内容，PR 中请注明前后差异。

## 配置与运行注意事项
- 启动时 `Config.validate()` 会强制检查 `OPENAI_API_KEY`。
- 工作流为顺序阶段（Clarifier → Analyst → Strategist → Writer），每阶段独立对话上下文。
