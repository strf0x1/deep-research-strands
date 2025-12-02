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

#### NCI (Narrative Credibility Index) Scoring
The agent includes optional NCI scoring to detect potential narrative manipulation and psyop campaigns in search results:
- `NCI_SCORING_ENABLED` - Enable NCI scoring analysis (`true` or `false`, default: `false`)
- `NCI_SCORE_THRESHOLD` - Minimum credibility score to accept sources (0-20, default: `6`)
- `NCI_TOP_N_SOURCES` - Number of top search results to analyze with NCI scoring (default: `5`)

**About NCI Scoring**: The Narrative Credibility Index is a 20-criterion framework for detecting manipulation tactics in text. It analyzes sources for indicators such as emotional manipulation, uniform messaging, logical fallacies, tribal division, and other psychological techniques commonly used in coordinated disinformation campaigns. Each analyzed source receives an aggregate score (0-20) and a risk level (LOW, MODERATE, HIGH, CRITICAL) to help identify potentially unreliable or manipulative content.

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

# NCI (Narrative Credibility Index) Scoring - Optional
# Enable NCI scoring to detect potential manipulation in sources
NCI_SCORING_ENABLED=false
NCI_SCORE_THRESHOLD=6
NCI_TOP_N_SOURCES=5
```

## Example Usage

**Interactive Mode**:
```bash
uv run main.py
```

**Single Query**:
```bash
uv run main.py -q "Your research query here"
```

**Load Query from File**:
```bash
uv run main.py -f prompt.txt
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

**Multi-Line Prompt File Input**
If you have a large, specific prompt, you can use a file:
```bash
uv run main.py -f complex_requirements.txt
```

**Generate LLM-friendly Library Docs for Your Code Editor**
You can use deep research strands to comb the latest docs for a library or language for your ai code editor:
```bash
uv run main.py -f practical_code_editor_prompt.txt --structure library_readme_structure.txt -o uv_practical.md
```

TODO
* silently fails and dumps final llm output error to doc. for example, last run failed on tool execution #2 web_search but no idea why
* use uv scripts to implement a more streamlined ai code editor doc generator
* bring rest of repo up to uv standards 
* add ruff
* make this a cli tool, would be so nice to have in any term im in
* add an MCP server for integration into the exp-001 mcp repo
* add cost counter?
* add an output token counter, so i know the estimated cost on the llm when doing a task