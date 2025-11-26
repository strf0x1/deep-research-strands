# Deep Research Agent (Strands Version)

This is a re-implementation of the M2 MinimaxDeep Research Agent found [here](https://github.com/dair-ai/m2-deep-research) using the AWS Strands Agents SDK. I just like working with this agent framework because the code is clean and it is easy to extend.

## Overview

This agent leverages Minimax M2 (via OpenRouter) and Exa API to conduct deep, comprehensive research on any given topic. It breaks down queries into sub-questions, searches the web, and synthesizes a detailed report.

## Features

- **Strands Agents SDK**: Uses the lightweight and flexible Strands framework for agent orchestration.
- **Minimax M2 via OpenRouter**: Powered by the Minimax M2 model accessed through OpenRouter for reasoning and planning.
- **Exa Neural Search**: Utilizes Exa for high-quality, semantic web search.
- **Comprehensive Reports**: Generates detailed, academic-quality research reports with inline citations.
- **Interleaved Thinking**: The agent can think step by step and explain its reasoning. See more [here](INTERLEAVED_THINKING.md).

## Setup

1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and add your API keys:
    - `OPENROUTER_API_KEY` - OpenRouter API key for accessing Minimax M2
    - `EXA_API_KEY` - Exa API key for neural web search

## Configuration

### Environment Variables

All configuration is done through environment variables in your `.env` file:

#### Required API Keys
- `OPENROUTER_API_KEY` - Your OpenRouter API key (for Minimax M2 access)
- `EXA_API_KEY` - Your Exa API key

#### Optional Settings
- `DEBUG` - Enable debug logging (`true` or `false`, default: `false`)
- `EXA_HIGH_PRIORITY_RESULTS` - Number of results for high-priority queries (default: `20`)
- `EXA_NORMAL_PRIORITY_RESULTS` - Number of results for normal-priority queries (default: `15`)
- `EXA_SIMILAR_RESULTS` - Number of similar content results per query (default: `5`)

**Example `.env` file:**
```bash
# API Keys (Required)
OPENROUTER_API_KEY=your_openrouter_key_here
EXA_API_KEY=your_exa_key_here

# Optional Configuration
DEBUG=false
EXA_HIGH_PRIORITY_RESULTS=20
EXA_NORMAL_PRIORITY_RESULTS=15
EXA_SIMILAR_RESULTS=5
```

## Usage

**Interactive Mode**:
```bash
uv run main.py
```

**Single Query**:
```bash
uv run main.py -q "Your research query here"
```

**Save to File**:
```bash
uv run main.py -q "Your research query here" --output report.md
```

**Custom Report Structure**:
You can define a custom structure for the report by creating a text file (e.g., `structure.txt`) and passing it with the `--structure` flag.
```bash
uv run main.py -q "Your research query here" --structure structure.txt
```
