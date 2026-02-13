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

## Using as an MCP Server

The Deep Research Agent can be run as an MCP (Model Context Protocol) server, allowing AI agents like Claude to access deep research capabilities through standardized tool calls.

### Starting the MCP Server

Run the MCP server in STDIO mode (default):
```bash
uv run mcp_server.py
```

The server exposes research tools and resources that can be used by any MCP-compatible client.

### Configuring Claude Desktop

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "deep-research-agent": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "cwd": "/path/to/deep-research-strands",
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_key_here",
        "EXA_API_KEY": "your_exa_key_here"
      }
    }
  }
}
```

**Note**: You can either:
1. Add API keys in the `env` section as shown above, OR
2. Use a `.env` file in the project directory (recommended)

A template configuration file is provided: `claude_desktop_config.example.json`

After restarting Claude Desktop, the research tools will be available for use.

### Available MCP Tools

#### Tier 1: Core Research Tools

**`run_research`** - Full research pipeline
- **Parameters**:
  - `query` (str): Research question or topic
  - `report_structure` (str, optional): Custom report structure in markdown
- **Returns**: Comprehensive markdown research report (15-30 pages equivalent)
- **Example**: `run_research("What are the latest developments in quantum computing?")`

**`plan_research_subqueries`** - Query decomposition
- **Parameters**: `research_query` (str)
- **Returns**: JSON with 8-12 Exa-optimized subqueries
- **Example**: `plan_research_subqueries("artificial general intelligence safety")`

**`execute_web_search`** - Search and synthesis
- **Parameters**:
  - `research_query` (str): Original research question
  - `subqueries_json` (str): JSON from `plan_research_subqueries`
- **Returns**: Synthesized findings with sources and optional NCI scores
- **Example**:
  ```python
  subqueries = plan_research_subqueries("climate change")
  findings = execute_web_search("climate change", subqueries)
  ```

#### Tier 2: Direct Search Tools

**`exa_neural_search`** - Direct Exa search
- **Parameters**:
  - `query` (str): Natural language search query
  - `num_results` (int, default=10): Number of results
  - `start_published_date` (str, optional): ISO format date filter
  - `end_published_date` (str, optional): ISO format date filter
  - `include_domains` (list[str], optional): Domain whitelist
  - `exclude_domains` (list[str], optional): Domain blacklist
  - `content_type` (str, default="auto"): Type filter (auto, news, research paper, pdf, blog)
- **Returns**: JSON with formatted search results
- **Example**:
  ```python
  exa_neural_search("quantum entanglement experiments",
                    num_results=5,
                    include_domains=["arxiv.org"],
                    content_type="research paper")
  ```

**`exa_find_similar`** - Find related content
- **Parameters**:
  - `url` (str): Source URL
  - `num_results` (int, default=5): Number of similar results
  - `exclude_source_domain` (bool, default=True): Exclude same domain
- **Returns**: JSON with similar content results
- **Example**: `exa_find_similar("https://arxiv.org/abs/2303.08774", num_results=10)`

#### Tier 3: NCI Scoring Tools (when enabled)

**`nci_score_source`** - Score single source
- **Parameters**:
  - `text` (str): Source content to analyze
  - `url` (str, optional): Source URL
  - `title` (str, optional): Source title
- **Returns**: JSON with NCI score (0-20), risk level, criteria breakdown
- **Note**: Only available when `NCI_SCORING_ENABLED=true`
- **Example**:
  ```python
  nci_score_source("Article text...",
                   url="https://example.com",
                   title="Article Title")
  ```

**`nci_batch_score`** - Score multiple sources
- **Parameters**: `sources` (str): JSON array of source objects with `text`, `url`, `title`
- **Returns**: JSON with array of scores and aggregate statistics
- **Note**: Only available when `NCI_SCORING_ENABLED=true`
- **Example**:
  ```python
  sources = json.dumps([
      {"text": "Article 1...", "url": "https://ex1.com", "title": "Title 1"},
      {"text": "Article 2...", "url": "https://ex2.com", "title": "Title 2"}
  ])
  nci_batch_score(sources)
  ```

### Available MCP Resources

**`template://default`** - Default comprehensive report structure
- Academic-quality structure for 15-30 page equivalent reports
- Includes executive summary, introduction, key findings, analysis, future trends, critical analysis, conclusion, and sources

**`template://custom`** - Custom report structure
- Loads `custom_structure.txt` if available
- Allows for project-specific report formatting

**`template://library`** - Library documentation structure
- Loads `library_readme_structure.txt` if available
- Optimized for generating library/tool documentation

**`config://settings`** - Current configuration
- Returns JSON with current server configuration
- Shows API settings, search parameters, and NCI configuration
- API keys are masked for security

**`example://structures/list`** - List available templates
- Returns JSON array of all available structure templates
- Includes template names, filenames, descriptions, and URIs

**`example://structures/{filename}`** - Get example structure
- Load specific structure file by filename
- Supported: `custom_structure.txt`, `library_readme_structure.txt`

### Example MCP Workflows

#### Basic Research Query
```python
# Ask Claude with MCP server connected:
"Use the deep research agent to investigate the latest developments
in quantum computing and provide a comprehensive report"

# Claude will call: run_research("latest developments in quantum computing")
```

#### Custom Report Structure
```python
# First, load a custom template
template = read_resource("template://library")

# Then run research with custom structure
run_research("FastAPI best practices", report_structure=template)
```

#### Multi-Step Research
```python
# 1. Plan the research
subqueries = plan_research_subqueries("impact of AI on healthcare")

# 2. Execute searches
findings = execute_web_search("impact of AI on healthcare", subqueries)

# 3. Score credibility (if NCI enabled)
# Extract sources from findings and score them
scores = nci_batch_score(sources_json)

# 4. Synthesize final report using findings and scores
```

#### Targeted Academic Search
```python
# Search specific academic domains
results = exa_neural_search(
    "CRISPR gene editing ethical implications",
    num_results=20,
    include_domains=["arxiv.org", "nature.com", "science.org"],
    content_type="research paper",
    start_published_date="2024-01-01T00:00:00.000Z"
)

# Find related papers
similar = exa_find_similar(results[0]["url"], num_results=10)
```

### Environment Variables

The MCP server uses the same environment variables as the CLI tool:

**Required:**
- `OPENROUTER_API_KEY` - OpenRouter API key for Minimax M2
- `EXA_API_KEY` - Exa API key for neural search

**Optional:**
- `DEBUG` - Enable debug logging (default: false)
- `EXA_HIGH_PRIORITY_RESULTS` - Results for high-priority queries (default: 20)
- `EXA_NORMAL_PRIORITY_RESULTS` - Results for normal queries (default: 15)
- `EXA_SIMILAR_RESULTS` - Results for similarity search (default: 5)
- `NCI_SCORING_ENABLED` - Enable NCI credibility scoring (default: false)
- `NCI_SCORE_THRESHOLD` - Minimum score threshold (default: 6)
- `NCI_TOP_N_SOURCES` - Number of sources to score per query (default: 5)

### Troubleshooting

**Server won't start:**
- Check that all dependencies are installed: `uv sync`
- Verify API keys are set in `.env` file
- Check logs for configuration validation errors

**Tools not appearing in Claude:**
- Restart Claude Desktop after adding MCP server configuration
- Verify the `cwd` path in configuration is correct
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`

**Search returning no results:**
- Verify `EXA_API_KEY` is valid
- Check query formatting (use natural language)
- Try broader domain filters or remove date restrictions

**NCI tools not available:**
- Set `NCI_SCORING_ENABLED=true` in `.env`
- Restart the MCP server after changing configuration

### MCP Prompts (Skills)

The MCP server includes **4 built-in prompts** that appear as skills in Claude Desktop:

1. **explain_research_agent** - Complete guide to using the agent, NCI scoring, report format
2. **research_template_comparison** - Template for comparison-focused research (tools, frameworks)
3. **research_template_quickstart** - Template for quick-start guide format
4. **research_with_nci_focus** - Template for credibility-focused research (controversial topics)

**Usage in Claude Desktop:**
```
Use the explain_research_agent prompt
```

See `MCP_PROMPTS.md` for detailed information on each prompt.

### Documentation

For comprehensive usage guides:
- **Prompts/Skills**: `MCP_PROMPTS.md` - Built-in prompts and how to use them
- **Quick Setup**: `MCP_QUICKSTART.md` - Installation and configuration
- **Skill Guide**: `MCP_SKILL_GUIDE.md` - Detailed usage, report formatting, and use cases
- **Architecture**: `CLAUDE.md` - System design and code patterns

TODO
* silently fails and dumps final llm output error to doc. for example, last run failed on tool execution #2 web_search but no idea why
* use uv scripts to implement a more streamlined ai code editor doc generator
* bring rest of repo up to uv standards
* add ruff
* make this a cli tool, would be so nice to have in any term im in
* add cost counter?
* add an output token counter, so i know the estimated cost on the llm when doing a task