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

### Agent System Messages

Each agent in `app/agents/` has a detailed `system_message` that defines:
- Role and responsibilities
- Output format requirements (especially for Clarifier, Analyst, Strategist)
- Specific instructions (e.g., Clarifier outputs "【需要澄清】" or "【信息充分】")

When modifying agent behavior, edit the `system_message` in the corresponding agent file.

### Model Client Configuration

The system uses `OpenAIChatCompletionClient` from `autogen-ext[openai]`, which is **compatible with any OpenAI-format API**:
- Default: DeepSeek API (`https://api.deepseek.com/v1`)
- Also supports: OpenAI, Azure OpenAI, or any compatible service
- Configuration via `.env`: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `MODEL_NAME`

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
# For DeepSeek (default)
OPENAI_API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# For OpenAI
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# For other compatible services
OPENAI_API_BASE=https://your-service.com/v1
MODEL_NAME=your-model-name
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
