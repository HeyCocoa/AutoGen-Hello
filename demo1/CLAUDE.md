# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AutoGen-based multi-agent system that generates topic strategy documents. It uses 5 specialized agents working in sequence to analyze business scenarios and produce structured content strategies in Markdown format.

## Core Architecture

### Multi-Agent Workflow (Sequential Execution)

The system uses **4 distinct phases** with `RoundRobinGroupChat` teams:

1. **Clarification Phase** (`Coordinator` + `Clarifier`)
   - Analyzes user input completeness
   - May pause for user Q&A if information is insufficient
   - Determines if ready to proceed to analysis

2. **Analysis Phase** (`Coordinator` + `Analyst`)
   - Receives original input + any clarification responses
   - Performs deep business analysis
   - Output feeds into strategy generation

3. **Strategy Phase** (`Coordinator` + `Strategist`)
   - Consumes analysis results
   - Generates structured topic strategy (keywords, priorities, templates, execution plan)

4. **Writing Phase** (`Coordinator` + `Writer`)
   - Integrates all previous outputs
   - Produces final Markdown document
   - Saved to `output/strategy_YYYYMMDD_HHMMSS.md`

**Key Implementation Detail**: Each phase creates a new `RoundRobinGroupChat` with `max_turns=3`. Results from previous phases are passed via prompt context, not through persistent conversation state.

### Prompt Management

All prompts are centralized in `app/prompts.py`:

**Agent System Messages (constants):**
- `COORDINATOR_SYSTEM_MESSAGE`
- `CLARIFIER_SYSTEM_MESSAGE`
- `ANALYST_SYSTEM_MESSAGE`
- `STRATEGIST_SYSTEM_MESSAGE`
- `WRITER_SYSTEM_MESSAGE`

**Workflow Task Prompts (functions):**
- `get_clarification_prompt(user_input)`
- `get_analysis_prompt(user_input, additional_info)`
- `get_strategy_prompt(analyst_output)`
- `get_writing_prompt(user_input, additional_info, analyst_output, strategist_output)`

When modifying agent behavior, edit the prompts in `app/prompts.py`. Agent files in `app/agents/` only handle instance creation.

### Model Client Configuration

The system uses `OpenAIChatCompletionClient` from `autogen-ext[openai]`, which is **compatible with any OpenAI-format API**:
- Default: 智谱AI GLM-4.7-flash (`https://open.bigmodel.cn/api/paas/v4`)
- Also supports: DeepSeek, OpenAI, Azure OpenAI, or any compatible service
- Configuration via `.env`: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `MODEL_NAME`

### Web Search (联网搜索)

The Analyst agent can perform real web searches using 智谱AI's web search API:
- Enabled via `ZHIPU_WEB_SEARCH_ENABLED=true` in `.env`
- Uses `zai-sdk` to call GLM-4.7-flash with web_search tool
- Falls back to mock results if disabled or using non-智谱 API
- Search engine configurable: `ZHIPU_SEARCH_ENGINE=search_std` (or `search_pro`)

## Development Commands

### Running the Application

```bash
# Primary method
python -m app

# Alternative (using Make)
make run
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using Make
make install
```

### Environment Setup

```bash
# Copy template
cp .env.example .env

# Edit .env with your API credentials
# Required: OPENAI_API_KEY
# Optional: OPENAI_API_BASE (defaults to DeepSeek)
# Optional: MODEL_NAME (defaults to deepseek-chat)
```

### Cleanup

```bash
make clean  # Removes __pycache__, *.pyc, *.log files
```

## Key Configuration Points

### Switching LLM Providers

Edit `.env`:
```env
# For 智谱AI GLM-4.7 (default, with web search support)
OPENAI_API_KEY=your-zhipu-api-key
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4
MODEL_NAME=glm-4.7-flash
ZHIPU_WEB_SEARCH_ENABLED=true
ZHIPU_SEARCH_ENGINE=search_std

# For DeepSeek
OPENAI_API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# For OpenAI
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

### Output Directory

Generated documents are saved to `output/` (created automatically by `Config.validate()`). Filename format: `strategy_YYYYMMDD_HHMMSS.md`.

## Important Implementation Notes

### User Input Flow

The application uses a special input pattern:
- User types multiple lines
- Types `END` on a separate line to finish
- Implemented in `app/__main__.py:get_user_input()`

### Async Execution

The workflow is fully async (`async def run()`). The main entry point uses `asyncio.run(main())`.

### Console Output

AutoGen's `Console` wrapper is used for streaming output: `await Console(team.run_stream(task=prompt))`. This displays agent interactions in real-time.

### Error Handling

`Config.validate()` is called at workflow initialization and will raise `ValueError` if `OPENAI_API_KEY` is missing.

### Structured Output (Reserved)

`app/models.py` defines a `StrategyDocument` Pydantic model for structured JSON output. Currently not used because glm-4.7-flash struggles with strict JSON generation. When switching to a more capable model (e.g., GPT-4, Claude), consider:
1. Update `WRITER_SYSTEM_MESSAGE` in `prompts.py` to require JSON output
2. Use `StrategyDocument.to_markdown()` to render the validated data

## Testing the System

Run with example inputs:
```bash
python -m app
# Then input:
业务场景：B2B SaaS产品出海，目标市场是东南亚
END
```

Check `examples/` directory for reference outputs showing expected document structure.

## Dependencies Version Note

The project uses AutoGen 0.4.2 (not 0.4.0, which had GPL dependency issues). If upgrading AutoGen, ensure compatibility with the `RoundRobinGroupChat` and `OpenAIChatCompletionClient` APIs.

Key dependencies:
- `autogen-agentchat==0.4.2` - Multi-agent framework
- `autogen-ext[openai]==0.4.2` - OpenAI-compatible model client
- `zai-sdk>=0.2.0` - 智谱AI SDK for web search
