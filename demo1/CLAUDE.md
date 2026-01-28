# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AutoGen-based multi-agent system that generates topic strategy documents. It uses 4 specialized agents working in sequence (with a search-outline alignment step) to analyze business scenarios and produce structured content strategies in Markdown format.

## Core Architecture

### Multi-Agent Workflow (Sequential Execution)

The system uses **5 phases** with single-agent execution (no Coordinator):

1. **Clarification Phase** (`Clarifier`)
   - Analyzes user input completeness
   - May pause for user Q&A if information is insufficient
   - Outputs `【需要澄清】` or `【信息充分】`

2. **Search Outline Alignment** (`Analyst` -> `Critic`)
   - Analyst outputs a **search outline only** (no tools)
   - Critic approves or rejects; **must include industry pain points**

3. **Analysis Phase** (`Analyst`)
   - Receives original input + any clarification responses + approved outline
   - **Mandatory web search** (at least 3 searches): market trends, audience pain points, competitor practices
   - Performs deep business analysis + strategy recommendations
   - Output style: direct, opinionated, data-backed (no hedging words like "maybe", "perhaps")

4. **Quality Check Phase** (`Critic`)
   - Reviews analyst's conclusions from 4 dimensions: data reliability, logic gaps, blind spots, feasibility
   - **Can use web search** to verify or refute claims
   - Outputs: acknowledged points, questioned points, supplementary findings, correction suggestions

5. **Writing Phase** (`Writer`)
   - Integrates: base info + analyst output + critic output
   - **Preserves evidence chain**: citations, reasoning logic (because X, so Y), critic's challenges
   - Produces final Markdown document with `⚠️` annotations for disputed points
   - Includes "Key Data Summary" appendix for traceability

**Key Implementation Detail**: Each phase creates a new `RoundRobinGroupChat` with a single agent. Results from previous phases are passed via prompt context.

### Prompt Management

All prompts are centralized in `app/prompts.py`:

**Agent System Messages (constants):**
- `CLARIFIER_SYSTEM_MESSAGE` - concise, max 3 questions
- `ANALYST_SYSTEM_MESSAGE` - forced tool usage, no hedging, cite search results
- `CRITIC_SYSTEM_MESSAGE` - challenge-oriented, can search to verify
- `WRITER_SYSTEM_MESSAGE` - preserve evidence chain, no markdown code blocks

**Workflow Task Prompts (functions):**
- `get_clarification_prompt(user_input)`
- `get_search_outline_prompt(user_input, additional_info, critic_feedback)`
- `get_outline_review_prompt(outline)`
- `get_analysis_prompt(user_input, additional_info, approved_outline)`
- `get_critic_prompt(analyst_output)`
- `get_writing_prompt(user_input, additional_info, analyst_output, critic_output)`

When modifying agent behavior, edit the prompts in `app/prompts.py`. Agent files in `app/agents/` only handle instance creation.

### Model Client Configuration

The system uses `OpenAIChatCompletionClient` from `autogen-ext[openai]`, which is **compatible with any OpenAI-format API**:
- Default: 智谱AI GLM-4.7-flashx (`https://open.bigmodel.cn/api/paas/v4`)
- Configuration via `.env`: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `MODEL_NAME`

### Web Search (联网搜索)

**REQUIRED** - The system requires 智谱AI web search to function:
- Must be enabled via `ZHIPU_WEB_SEARCH_ENABLED=true` in `.env`
- Uses `zai-sdk` to call the configured model with web_search tool
- Concurrency limited to 1 request at a time to avoid API rate limits (429 errors)
- Search failures return graceful error messages instead of crashing
- Search engine configurable: `ZHIPU_SEARCH_ENGINE=search_std` (or `search_pro`)

Agents with web search capability:
- `Analyst` - mandatory, at least 3 searches
- `Critic` - optional, for verification

### Stream Display

`app/utils/console.py` handles streaming output with deduplication:
- Tool calls and results are deduplicated to avoid repeated display
- Uses `Set` to track shown tool calls (by name+arguments) and results (by first 200 chars)

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
pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env - all fields below are REQUIRED:
# OPENAI_API_KEY=your-zhipu-api-key
# OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4
# MODEL_NAME=glm-4.7-flashx
# ZHIPU_WEB_SEARCH_ENABLED=true
```

**Note**: Other LLM providers (DeepSeek, OpenAI) are NOT supported because web search is mandatory.

### Output Directory

Generated documents are saved to `output/` (created automatically). Filename format: `strategy_YYYYMMDD_HHMMSS.md`.

## Important Implementation Notes

### User Input Flow

- User types multiple lines
- Types `END` on a separate line to finish
- Implemented in `app/__main__.py:get_user_input()`

### Error Handling

- `Config.validate()` raises `ValueError` if:
  - `OPENAI_API_KEY` is missing
  - Not using 智谱AI API (bigmodel.cn)
  - `ZHIPU_WEB_SEARCH_ENABLED` is false
- `web_search()` returns error message (not crash) if search fails or returns empty

### File Structure

```
app/
├── __main__.py          # Entry point
├── config.py            # Environment config (智谱AI only)
├── workflow.py          # 5-phase orchestration
├── prompts.py           # All agent prompts (edit here to change behavior)
├── tools.py             # web_search, get_current_date, calculate
├── agents/
│   ├── clarifier.py
│   ├── analyst.py       # Has tools: web_search, get_current_date, calculate
│   ├── critic.py        # Has tools: web_search, get_current_date
│   └── writer.py
└── utils/
    ├── console.py       # Stream display with deduplication
    └── rich_ui.py       # Rich formatting helpers
```

## Testing the System

```bash
python -m app
# Input:
业务场景：B2B SaaS产品出海，目标市场是东南亚
END
```

## Dependencies

- `autogen-agentchat==0.4.2` - Multi-agent framework
- `autogen-ext[openai]==0.4.2` - OpenAI-compatible model client
- `zai-sdk>=0.2.0` - 智谱AI SDK for web search (required)
