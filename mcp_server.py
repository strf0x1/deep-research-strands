"""MCP Server for Deep Research Agent - Exposes research capabilities via Model Context Protocol."""

import json
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Import existing components
from src.agents.supervisor import SupervisorAgent
from src.agents.planning_agent import planning_agent_tool
from src.agents.search_agent import web_search_retriever_tool
from src.tools.exa_tool import ExaTool
from src.tools.nci_scoring_tool import NCIScoringTool
from src.utils.config import Config

# Initialize MCP server
mcp = FastMCP(
    name="deep-research-agent",
    instructions="""Deep Research Agent provides comprehensive, academic-quality research capabilities using:
- Exa neural web search for high-quality source discovery
- Multi-agent orchestration for query decomposition and synthesis
- Optional NCI (Narrative Credibility Index) scoring for source credibility analysis

Use run_research for complete research reports, or use individual tools for custom workflows."""
)

# Initialize configuration and validate on startup
import sys

try:
    config = Config()
    config.validate()
except Exception as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    raise

# Initialize tools once for reuse
exa_tool = ExaTool()
nci_tool = NCIScoringTool() if Config.NCI_SCORING_ENABLED else None

# Default report structure (from supervisor.py lines 74-131)
DEFAULT_STRUCTURE = """## Required Report Structure:

### Executive Summary (3-5 paragraphs)
   - Overview of research scope
   - Key findings summary
   - Main conclusions and implications

### Introduction (2-3 paragraphs)
   - Context and background
   - Research objectives
   - Methodology overview

### Key Findings (Multiple detailed sections organized by theme)
   - Each major theme gets its own section with subsections
   - Include data, statistics, expert opinions
   - Cite sources inline with URLs
   - Provide examples and case studies

### Detailed Analysis (Deep dive into each area)
   - Technical details and mechanisms
   - Historical context and evolution
   - Current state of the art
   - Comparisons and contrasts
   - Strengths and limitations

### Industry/Application Analysis (if relevant)
   - Real-world applications
   - Market trends and adoption
   - Key players and institutions
   - Success stories and challenges

### Future Implications and Trends
   - Emerging developments
   - Predictions and projections
   - Challenges ahead
   - Opportunities and potential

### Critical Analysis
   - Debates and controversies
   - Limitations and challenges
   - Alternative perspectives
   - Unanswered questions

### Conclusion
   - Summary of main points
   - Broader implications
   - Recommendations (if applicable)

### Source Credibility Analysis (if NCI scoring enabled)
   - Overview of Narrative Credibility Index (NCI) methodology
   - Risk distribution summary of assessed sources
   - Table of flagged sources with scores and manipulation indicators
   - Interpretation and recommendations for source corroboration
   - Note about which sources were scored vs. unscored

### Sources and Citations
   - Comprehensive list of all sources with URLs
   - Organized by category or theme"""


# ============================================================================
# TIER 1: Core Research Tools
# ============================================================================

@mcp.tool()
def run_research(query: str, report_structure: Optional[str] = None) -> str:
    """
    Conduct comprehensive deep research on a query and generate a detailed academic-quality report.

    This is the main research tool that orchestrates the full research pipeline:
    1. Query decomposition into 8-12 subqueries
    2. Web search across multiple sources using Exa neural search
    3. Optional NCI credibility scoring on top sources
    4. Synthesis into a comprehensive 15-30 page equivalent report

    Args:
        query: Research question or topic to investigate
        report_structure: Optional custom report structure in markdown format.
                         If not provided, uses default comprehensive structure.

    Returns:
        Comprehensive research report in markdown format with inline citations

    Example:
        run_research("What are the latest developments in quantum computing?")
    """
    try:
        # Create supervisor with optional custom structure
        supervisor = SupervisorAgent(report_structure=report_structure)

        # Execute research
        report = supervisor.research(query)

        return report

    except Exception as e:
        raise ToolError(f"Research execution failed: {str(e)}")


@mcp.tool()
def plan_research_subqueries(research_query: str) -> str:
    """
    Decompose a research query into 8-12 Exa-optimized subqueries for comprehensive coverage.

    Uses the planning agent to break down complex research topics into focused subqueries
    that cover multiple dimensions: core concepts, latest developments, historical context,
    technical implementations, expert opinions, academic research, industry trends, future
    implications, challenges, and related comparisons.

    Each subquery includes optimization parameters like content type, time period, domain
    filters, and priority level for targeted search execution.

    Args:
        research_query: The main research question or topic to decompose

    Returns:
        JSON string containing subqueries with search optimization parameters.
        Format: {"status": "success", "subqueries": [...], "research_query": "..."}

    Example:
        plan_research_subqueries("artificial general intelligence safety")
    """
    try:
        result = planning_agent_tool(research_query)

        # Validate it's valid JSON
        parsed = json.loads(result)

        if parsed.get("status") == "error":
            raise ToolError(f"Planning agent error: {parsed.get('error', 'Unknown error')}")

        return result

    except json.JSONDecodeError as e:
        raise ToolError(f"Invalid JSON response from planning agent: {str(e)}")
    except Exception as e:
        raise ToolError(f"Query planning failed: {str(e)}")


@mcp.tool()
def execute_web_search(research_query: str, subqueries_json: str) -> str:
    """
    Execute web searches using Exa API for provided subqueries and synthesize findings.

    This tool:
    1. Executes Exa neural searches for each subquery
    2. Uses find_similar() on best results to discover related content
    3. Applies optional NCI scoring to top N sources per query
    4. Synthesizes findings into organized, comprehensive summary

    Results include source URLs, titles, highlights, NCI scores (if enabled),
    and thematic organization of key findings.

    Args:
        research_query: The original research question or topic
        subqueries_json: JSON string containing subqueries from plan_research_subqueries.
                        Format: {"subqueries": [{"query": "...", "type": "...", ...}]}

    Returns:
        Comprehensive synthesized findings organized by theme with source citations
        and optional NCI credibility analysis

    Example:
        subqueries = plan_research_subqueries("climate change")
        findings = execute_web_search("climate change", subqueries)
    """
    try:
        # Validate subqueries JSON
        try:
            parsed = json.loads(subqueries_json)
        except json.JSONDecodeError as e:
            raise ToolError(f"Invalid subqueries JSON: {str(e)}")

        # Extract subqueries list
        if isinstance(parsed, list):
            subqueries = parsed
        elif isinstance(parsed, dict):
            subqueries = parsed.get("subqueries", [])
        else:
            raise ToolError("Subqueries must be a JSON array or object with 'subqueries' key")

        if not subqueries:
            raise ToolError("No subqueries provided in JSON")

        # Execute search and synthesis
        result = web_search_retriever_tool(research_query, subqueries_json)

        if result.startswith("Error:"):
            raise ToolError(result)

        return result

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Web search execution failed: {str(e)}")


# ============================================================================
# TIER 2: Direct Search Tools
# ============================================================================

@mcp.tool()
def exa_neural_search(
    query: str,
    num_results: int = 10,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    content_type: str = "auto"
) -> str:
    """
    Execute direct neural search using Exa API for precise, targeted queries.

    Exa uses neural search to find high-quality, semantically relevant content.
    This tool provides direct access to Exa search without agent orchestration.

    Args:
        query: Natural language search query
        num_results: Number of results to return (default: 10)
        start_published_date: Filter results published after this date (ISO 8601 format)
        end_published_date: Filter results published before this date (ISO 8601 format)
        include_domains: List of domains to include (e.g., ["arxiv.org", "nature.com"])
        exclude_domains: List of domains to exclude
        content_type: Type of content to search for. Options: "auto", "news",
                     "research paper", "pdf", "blog" (default: "auto")

    Returns:
        JSON string with search results including titles, URLs, excerpts, highlights,
        published dates, and relevance scores

    Example:
        exa_neural_search("quantum entanglement experiments", num_results=5,
                         include_domains=["arxiv.org"], content_type="research paper")
    """
    try:
        # Execute search
        results = exa_tool.search(
            query=query,
            num_results=num_results,
            start_published_date=start_published_date,
            end_published_date=end_published_date,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            type=content_type,
        )

        # Check for errors
        if "error" in results:
            raise ToolError(f"Exa search failed: {results['error']}")

        # Format results
        formatted = exa_tool.format_results(results)

        return json.dumps({
            "query": query,
            "num_results": len(formatted),
            "results": formatted
        }, indent=2)

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Exa search execution failed: {str(e)}")


@mcp.tool()
def exa_find_similar(
    url: str,
    num_results: int = 5,
    exclude_source_domain: bool = True
) -> str:
    """
    Find content similar to a given URL using Exa's neural similarity search.

    Uses neural embeddings to discover related content that shares semantic similarity
    with the source URL. Useful for finding related research, complementary sources,
    or alternative perspectives on the same topic.

    Args:
        url: Source URL to find similar content for
        num_results: Number of similar results to return (default: 5)
        exclude_source_domain: Exclude results from the same domain as source (default: True)

    Returns:
        JSON string with similar search results including titles, URLs, excerpts,
        highlights, and similarity scores

    Example:
        exa_find_similar("https://arxiv.org/abs/2303.08774", num_results=10)
    """
    try:
        # Execute similarity search
        results = exa_tool.find_similar(
            url=url,
            num_results=num_results,
            exclude_source_domain=exclude_source_domain,
        )

        # Check for errors
        if "error" in results:
            raise ToolError(f"Exa find_similar failed: {results['error']}")

        # Format results
        formatted = exa_tool.format_results(results)

        return json.dumps({
            "source_url": url,
            "num_results": len(formatted),
            "results": formatted
        }, indent=2)

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Exa find_similar execution failed: {str(e)}")


# ============================================================================
# TIER 3: NCI Scoring Tools (Conditional)
# ============================================================================

if Config.NCI_SCORING_ENABLED:

    @mcp.tool()
    def nci_score_source(text: str, url: str = "", title: str = "") -> str:
        """
        Analyze a single source for narrative manipulation using NCI (Narrative Credibility Index).

        The NCI scoring system evaluates text against 20 criteria to detect potential
        manipulation tactics including emotional manipulation, uniform messaging, logical
        fallacies, tribal division, false dilemmas, cherry-picked data, and other
        psychological techniques used in coordinated disinformation campaigns.

        Score interpretation:
        - LOW (0-5): Minimal manipulation indicators
        - MODERATE (6-10): Some concerning patterns
        - HIGH (11-15): Significant manipulation indicators
        - CRITICAL (16-20): Severe manipulation patterns

        Args:
            text: Source content to analyze (minimum 50 characters)
            url: Optional source URL for reference
            title: Optional source title for context

        Returns:
            JSON string with aggregate score (0-20), risk level, summary of manipulation
            tactics, and detailed breakdown of matched criteria with explanations

        Example:
            nci_score_source("Article text here...",
                           url="https://example.com/article",
                           title="Article Title")

        Note: Only available when NCI_SCORING_ENABLED=true in configuration
        """
        try:
            if not nci_tool:
                raise ToolError("NCI scoring is not enabled. Set NCI_SCORING_ENABLED=true")

            # Score the text
            score = nci_tool.score_text(text=text, url=url, title=title)

            # Check for error
            if "error" in score:
                raise ToolError(f"NCI scoring failed: {score['error']}")

            return json.dumps(score, indent=2)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"NCI scoring execution failed: {str(e)}")


    @mcp.tool()
    def nci_batch_score(sources: str) -> str:
        """
        Score multiple sources for narrative manipulation using NCI in batch.

        Efficiently analyzes multiple sources against the 20-criterion NCI framework.
        Useful for evaluating a collection of sources to identify potential manipulation
        patterns across multiple documents.

        Args:
            sources: JSON string with array of source objects. Each source must have:
                    - text: Source content (string, minimum 50 characters)
                    - url: Source URL (string, can be empty)
                    - title: Source title (string, can be empty)
                    Format: [{"text": "...", "url": "...", "title": "..."}, ...]

        Returns:
            JSON string with array of score results. Each result includes aggregate score,
            risk level, summary, and criteria breakdown. Also includes aggregate statistics.

        Example:
            sources = json.dumps([
                {"text": "Article 1 text...", "url": "https://ex1.com", "title": "Title 1"},
                {"text": "Article 2 text...", "url": "https://ex2.com", "title": "Title 2"}
            ])
            nci_batch_score(sources)

        Note: Only available when NCI_SCORING_ENABLED=true in configuration
        """
        try:
            if not nci_tool:
                raise ToolError("NCI scoring is not enabled. Set NCI_SCORING_ENABLED=true")

            # Parse sources JSON
            try:
                sources_list = json.loads(sources)
            except json.JSONDecodeError as e:
                raise ToolError(f"Invalid sources JSON: {str(e)}")

            if not isinstance(sources_list, list):
                raise ToolError("Sources must be a JSON array")

            # Validate each source has required fields
            for i, source in enumerate(sources_list):
                if not isinstance(source, dict):
                    raise ToolError(f"Source {i} must be an object")
                if "text" not in source:
                    raise ToolError(f"Source {i} missing required 'text' field")

            # Execute batch scoring
            scores = nci_tool.batch_score(sources_list)

            # Calculate summary statistics
            valid_scores = [s for s in scores if "error" not in s]
            avg_score = sum(s.get("aggregate_score", 0) for s in valid_scores) / len(valid_scores) if valid_scores else 0

            distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
            for score in valid_scores:
                risk = score.get("risk_level", "UNKNOWN")
                if risk in distribution:
                    distribution[risk] += 1

            return json.dumps({
                "total_sources": len(sources_list),
                "successfully_scored": len(valid_scores),
                "average_score": round(avg_score, 2),
                "risk_distribution": distribution,
                "scores": scores
            }, indent=2)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"NCI batch scoring failed: {str(e)}")


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("template://default")
def get_default_template() -> str:
    """
    Default comprehensive report structure for deep research reports.

    This structure produces academic-quality reports (15-30 page equivalent) with:
    - Executive summary and introduction
    - Detailed findings organized by theme
    - Deep analysis of technical details and context
    - Industry/application analysis
    - Future implications and trends
    - Critical analysis of debates and limitations
    - Conclusion with recommendations
    - Optional NCI source credibility analysis
    - Comprehensive sources and citations
    """
    return DEFAULT_STRUCTURE


@mcp.resource("config://settings")
def get_config_settings() -> str:
    """
    Current MCP server configuration and settings.

    Returns configuration including API endpoints, search parameters, NCI settings,
    and feature flags. API keys are masked for security.
    """
    config_data = {
        "openrouter": {
            "base_url": Config.OPENROUTER_BASE_URL,
            "model": Config.OPENROUTER_MODEL,
            "api_key_configured": bool(Config.OPENROUTER_API_KEY),
        },
        "exa": {
            "base_url": Config.EXA_BASE_URL,
            "api_key_configured": bool(Config.EXA_API_KEY),
            "high_priority_results": Config.EXA_HIGH_PRIORITY_RESULTS,
            "normal_priority_results": Config.EXA_NORMAL_PRIORITY_RESULTS,
            "similar_results": Config.EXA_SIMILAR_RESULTS,
        },
        "nci": {
            "scoring_enabled": Config.NCI_SCORING_ENABLED,
            "score_threshold": Config.NCI_SCORE_THRESHOLD,
            "top_n_sources": Config.NCI_TOP_N_SOURCES,
        },
        "debug": Config.DEBUG,
    }

    return json.dumps(config_data, indent=2)


@mcp.resource("template://{name}")
def get_custom_template(name: str) -> str:
    """
    Load custom report structure templates by name.

    Available templates:
    - custom: Custom report structure from custom_structure.txt
    - library: Library/documentation focused structure from library_readme_structure.txt

    Templates are markdown-formatted structures that guide the report generation process.
    """
    template_map = {
        "custom": Path("custom_structure.txt"),
        "library": Path("library_readme_structure.txt"),
    }

    if name not in template_map:
        raise ToolError(
            f"Template '{name}' not found. Available templates: {', '.join(template_map.keys())}"
        )

    template_path = template_map[name]

    if not template_path.exists():
        raise ToolError(f"Template file not found: {template_path}")

    return template_path.read_text()


@mcp.resource("example://structures/list")
def list_example_structures() -> str:
    """
    List all available example report structure templates.

    Returns JSON array of available template files with descriptions.
    """
    examples = []

    # Check for custom structure
    custom_path = Path("custom_structure.txt")
    if custom_path.exists():
        examples.append({
            "name": "custom",
            "filename": "custom_structure.txt",
            "description": "Custom report structure template",
            "uri": "template://custom"
        })

    # Check for library structure
    library_path = Path("library_readme_structure.txt")
    if library_path.exists():
        examples.append({
            "name": "library",
            "filename": "library_readme_structure.txt",
            "description": "Library/documentation focused structure",
            "uri": "template://library"
        })

    return json.dumps({
        "available_templates": len(examples),
        "templates": examples
    }, indent=2)


@mcp.resource("example://structures/{filename}")
def get_example_structure(filename: str) -> str:
    """
    Retrieve example report structure template by filename.

    Supported filenames:
    - custom_structure.txt
    - library_readme_structure.txt
    """
    allowed_files = ["custom_structure.txt", "library_readme_structure.txt"]

    if filename not in allowed_files:
        raise ToolError(
            f"File '{filename}' not allowed. Available files: {', '.join(allowed_files)}"
        )

    file_path = Path(filename)

    if not file_path.exists():
        raise ToolError(f"Example structure file not found: {filename}")

    return file_path.read_text()


# ============================================================================
# MCP Prompts (Show up as skills in Claude Desktop)
# ============================================================================

@mcp.prompt()
def explain_research_agent() -> str:
    """
    Explains how to use the Deep Research Agent MCP, including report format, NCI scoring, and best practices.

    Use this prompt to learn about:
    - What reports include and their format
    - How NCI credibility scoring works
    - Available tools and when to use them
    - Example queries and use cases
    """
    return """# Deep Research Agent - Usage Guide

## What This Agent Does

I'm connected to a Deep Research Agent that can conduct comprehensive, academic-quality research on any topic. Here's what you need to know:

### Report Output Format

When you ask me to research something, I'll generate a **15-30 page equivalent markdown report** that includes:

**Structure:**
- **Executive Summary**: 3-5 paragraph overview of findings
- **Introduction**: Context, objectives, methodology
- **Key Findings**: Multiple detailed sections organized by theme
- **Detailed Analysis**: Deep technical dive into each area
- **Industry/Application Analysis**: Real-world usage, market trends, key players
- **Future Implications**: Emerging developments, predictions, opportunities
- **Critical Analysis**: Debates, limitations, alternative perspectives
- **Conclusion**: Summary, implications, recommendations
- **Sources**: Comprehensive list with URLs

**Citation Style:**
- All reports use **inline markdown citations**: `[Source Name](URL)`
- Citations appear immediately where claims are made
- Example: "The market grew 44% [according to Statista](https://example.com)"
- Typical reports have **50-100+ citations** from **30-60 unique sources**

**Quality Characteristics:**
- 5,000-15,000 words typical
- Academic-level depth with clear explanations
- Data-driven with statistics and examples
- Multiple expert perspectives
- Hierarchical structure with clear headers

### NCI Credibility Scoring (Optional)

When `NCI_SCORING_ENABLED=true`, the agent analyzes sources for manipulation:

**What NCI Scores Mean:**
- **Score Range**: 0-20 (higher = more manipulation indicators)
- **LOW (0-5)**: Minimal manipulation indicators, generally trustworthy
- **MODERATE (6-10)**: Some concerning patterns, verify with other sources
- **HIGH (11-15)**: Significant manipulation indicators, cross-check carefully
- **CRITICAL (16-20)**: Severe manipulation patterns, use with extreme caution

**What NCI Detects:**
- Emotional manipulation tactics
- Uniform messaging patterns (coordination indicators)
- Logical fallacies and reasoning errors
- Tribal division language
- False dilemmas and oversimplification
- Cherry-picked data
- Authority misuse
- Time pressure tactics
- Social proof manipulation
- And 11 more criteria...

**When Reports Include NCI:**
- Top 5 sources per subquery are scored
- Summary appears in "Source Credibility Analysis" section
- Flagged sources listed with scores and indicators
- Recommendations for cross-verification provided

### Available Tools

**For Complete Research:**
- Just ask naturally: "Research [topic]"
- I'll automatically use `run_research` tool
- You'll get a full comprehensive report

**For Custom Structures:**
- "Research [topic] using this structure: [your format]"
- Or: "Load template://library and research [topic]"

**For Targeted Search:**
- "Search arxiv.org for papers on [topic]"
- I'll use `exa_neural_search` with domain filters

**For Source Analysis:**
- "Analyze this article for credibility: [text/url]"
- I'll use `nci_score_source` (if enabled)

### Example Use Cases

**Technology Evaluation:**
"Research Rust web frameworks for production use. Include maturity, community support, performance, and limitations."

**Market Analysis:**
"Analyze the AI agent framework market in 2025. Focus on key players, differentiation, and trends."

**Academic Review:**
"Comprehensive review of transformer improvements since 2023. Include arxiv.org papers and key researchers."

**Technical Deep Dive:**
"How does Retrieval-Augmented Generation work? Include architecture, implementations, and trade-offs."

**Trend Forecasting:**
"What are emerging trends in edge computing for 2025-2026? Focus on adoption drivers and barriers."

### Best Practices

✅ **Do:**
- Be specific in your queries
- Request custom structures if you need specific formats
- Mention domain filters for academic/specialized research
- Ask for NCI analysis on controversial topics
- Specify time periods when relevant ("recent", "2024-2025")

❌ **Avoid:**
- Overly broad queries without focus
- Asking for opinions without evidence
- Expecting instant results (takes 2-5 minutes)

### Report Uses

These reports are great for:
- Technical decision documents
- Market research presentations
- Academic literature reviews
- Blog post research
- Competitive analysis
- Strategic planning documents
- Educational materials
- Policy/regulatory briefings

---

**Ready to start?** Just ask me to research any topic and I'll automatically use the appropriate tools to generate a comprehensive report with inline citations!"""


@mcp.prompt()
def research_template_comparison() -> str:
    """
    Get a prompt for researching tools/frameworks with a comparison matrix format.

    Perfect for: technology evaluation, framework selection, tool comparison.
    """
    return """I need to research {TOPIC} with a comparison-focused structure.

Please use this custom report structure:

# {TOPIC} - Comparison Analysis

## Executive Summary
Brief overview of the landscape

## Comparison Matrix
| Tool/Framework | Primary Use Case | Maturity Level | Community Size | Key Strengths | Notable Limitations | Best For |
|---|---|---|---|---|---|---|

## Detailed Profiles
### [Tool/Framework Name]
- **Overview**: Brief description
- **Current Status & Adoption**: Market position, user base
- **Technical Architecture**: Key design decisions
- **Strengths**: What it excels at
- **Limitations**: Known weaknesses
- **Best Use Cases**: When to choose this
- **Notable Users**: Companies/projects using it

## Selection Criteria Guide
### When to Choose [Option A]
### When to Choose [Option B]
### When to Choose [Option C]

## Ecosystem & Community
- Community activity and support
- Documentation quality
- Plugin/extension ecosystems
- Corporate backing

## Performance & Benchmarks
- Key performance metrics
- Benchmark comparisons
- Scalability considerations

## Migration & Integration
- Ease of adoption
- Migration paths from alternatives
- Integration with common stacks

## Key Insights & Recommendations
What's gaining traction and why

## Sources

---
Replace {TOPIC} with your specific research topic."""


@mcp.prompt()
def research_template_quickstart() -> str:
    """
    Get a prompt for creating quick reference / getting started guides.

    Perfect for: learning new tools, quick reference docs, onboarding materials.
    """
    return """I need to research {TOPIC} to create a practical quick-start guide.

Please use this custom report structure:

# {TOPIC} - Quick Start Guide

## TL;DR
One paragraph: What is it, why use it, top recommendation

## What Problem Does It Solve?
The core value proposition

## Quick Start (5 Minutes)
Minimal steps to get running:
1. Install/Setup
2. Basic example
3. First success

## Core Concepts
Essential concepts to understand (3-5 key ideas)

## Common Use Cases
### Use Case 1: [Scenario]
- When to use
- Example code/approach
- Expected outcome

### Use Case 2: [Scenario]
### Use Case 3: [Scenario]

## Best Practices
- Do's and Don'ts
- Common pitfalls to avoid
- Performance tips

## Architecture & How It Works
Technical overview for understanding

## Comparison with Alternatives
| Feature | {TOPIC} | Alternative A | Alternative B |
|---|---|---|---|

## Advanced Features
- Power user features
- Advanced configurations
- Optimization techniques

## Troubleshooting
Common issues and solutions

## Resources
- Official docs
- Tutorials
- Community links

## Sources

---
Replace {TOPIC} with your specific research topic."""


@mcp.prompt()
def research_with_nci_focus() -> str:
    """
    Get a prompt for research with strong emphasis on source credibility analysis.

    Perfect for: controversial topics, political research, health claims, financial analysis.
    Requires: NCI_SCORING_ENABLED=true
    """
    return """I need to research {TOPIC} with strong emphasis on source credibility.

**Important**: This requires NCI scoring to be enabled (NCI_SCORING_ENABLED=true).

Please conduct comprehensive research and:

1. **Focus on Authoritative Sources**
   - Academic institutions (.edu domains)
   - Peer-reviewed journals
   - Government/regulatory bodies (.gov)
   - Established research organizations
   - Subject matter experts with credentials

2. **Apply NCI Credibility Analysis**
   - Score all major sources
   - Flag any sources with MODERATE risk or higher
   - Provide detailed analysis of manipulation indicators
   - Note any coordination patterns across sources

3. **Cross-Verification Emphasis**
   - Verify key claims across multiple independent sources
   - Note where sources agree/disagree
   - Identify potential bias or conflicts of interest
   - Highlight well-supported vs. disputed claims

4. **Report Structure**
   Include standard sections plus:
   - **Credibility Assessment**: Detailed NCI analysis upfront
   - **Source Quality Tiers**: Group sources by reliability
   - **Disputed Claims**: What's controversial and why
   - **Confidence Levels**: High/Medium/Low for key findings

5. **Red Flags to Watch For**
   - Emotional manipulation
   - Cherry-picked data
   - False dilemmas
   - Tribal division language
   - Coordinated messaging patterns

---
Replace {TOPIC} with your research topic. Best for health, political, financial, or controversial subjects where source credibility is critical."""


# ============================================================================
# Server Entry Point
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    # Run the MCP server (default: STDIO transport)
    mcp.run()


if __name__ == "__main__":
    main()
