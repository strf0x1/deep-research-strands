"""Supervisor Agent using Strands Agents SDK."""

from typing import Dict, Any, List
import json
from rich.console import Console
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from src.utils.config import Config
from src.tools.planning_tool import PlanningTool
from src.tools.search_tool import SearchTool

# Initialize rich console
console = Console()

# Initialize tools
planning_tool_instance = PlanningTool()
search_tool_instance = SearchTool()

@tool
def planning_agent_tool(research_query: str) -> str:
    """
    Generates Exa-optimized subqueries for a research topic.
    Takes a research query and returns JSON with 3-5 subqueries optimized for neural search.
    """
    if Config.DEBUG:
        console.print(f"\n[bold yellow][DEBUG] planning_agent_tool called with:[/bold yellow] {research_query}")
    result = planning_tool_instance.execute(research_query)
    if Config.DEBUG:
        console.print(f"[dim][DEBUG] planning_agent_tool returning:[/dim] {result[:200]}...")
    return result

@tool
def web_search_retriever_tool(research_query: str, subqueries_json: Any) -> str:
    """
    Executes web searches using Exa API for provided subqueries and synthesizes findings.
    Returns organized research findings with sources.
    """
    if Config.DEBUG:
        console.print(f"\n[bold yellow][DEBUG] web_search_retriever_tool called[/bold yellow]")
        console.print(f"[dim]Query: {research_query}[/dim]")
    
    # Handle both string and dict/list inputs
    if isinstance(subqueries_json, (dict, list)):
        if Config.DEBUG:
            console.print(f"[dim][DEBUG] subqueries_json received as {type(subqueries_json).__name__}, converting to string[/dim]")
        subqueries_json = json.dumps(subqueries_json)
    else:
        if Config.DEBUG:
            console.print(f"[dim]Subqueries JSON: {str(subqueries_json)[:200]}...[/dim]")
        
    result = search_tool_instance.retrieve(research_query, subqueries_json)
    if Config.DEBUG:
        console.print(f"[dim][DEBUG] web_search_retriever_tool returning:[/dim] {result[:200]}...")
    return result

class SupervisorAgent:
    """
    Main supervisor agent that coordinates research workflow using Strands Agents.
    """

    def __init__(self):
        """Initialize Supervisor Agent."""
        self.system_prompt = """You are a deep research coordinator specializing in comprehensive, academic-quality research reports. Your goal is to produce thorough, well-structured, in-depth analysis.

You have access to the following tools:

1. planning_agent_tool - Breaks down research queries into 8-12 Exa-optimized subqueries
   - Input: research_query (string)
   - Returns: JSON with optimized subqueries covering multiple dimensions

2. web_search_retriever_tool - Searches the web using Exa and synthesizes findings
   - Input: research_query (string), subqueries_json (string)
   - Returns: Comprehensive organized findings with sources

Research Workflow:
1. Call planning_agent_tool with the user's research query to generate comprehensive subqueries
2. Call web_search_retriever_tool with the research query and subqueries to gather extensive information
3. Synthesize a COMPREHENSIVE research report (15-30 pages equivalent) with the following structure:

## Required Report Structure:

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

### Sources and Citations
   - Comprehensive list of all sources with URLs
   - Organized by category or theme

## Quality Guidelines:
- Be EXTREMELY thorough and detailed - aim for 5-10x more content than a typical report
- Use specific data, statistics, and concrete examples throughout
- Quote experts and authoritative sources
- Explain technical concepts clearly
- Make connections across different aspects of the topic
- Maintain academic rigor and objectivity
- Use clear section headers and subsections
- Provide context and background for all major points
- Include both breadth (covering many aspects) and depth (detailed analysis)

## CRITICAL: Inline Citations Format
- **ALWAYS include inline citations** immediately after claims, data, or quotes
- Use markdown link format: `[descriptive text](URL)` for all citations
- Place citations right where information is used, not just at the end
- Examples:
  * "The market is projected to reach $47 billion by 2030 [according to Grand View Research](https://www.example.com/report)"
  * "As noted by [Nick Bostrom's research on AI safety](https://example.com/paper), superintelligence poses..."
  * "Studies show a 44% growth rate [Statista Market Analysis](https://example.com/stats)"
- When citing statistics: include the source inline: "Growth rates of 44% [Source](URL)"
- When quoting experts: cite immediately: "According to [Expert Name](URL), '...'"
- Every factual claim, statistic, or data point MUST have an inline citation
- The final Sources section should be a comprehensive list, but inline citations are PRIMARY"""

        # Initialize Minimax Model (via OpenAI interface)
        self.model = OpenAIModel(
            client_args={
                "api_key": Config.OPENROUTER_API_KEY,
                "base_url": Config.OPENROUTER_BASE_URL,
            },
            model_id=Config.OPENROUTER_MODEL,
        )

        # Initialize Strands Agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=[planning_agent_tool, web_search_retriever_tool],
        )

    def research(self, query: str) -> str:
        """
        Conduct research on a given query.

        Args:
            query: Research question or topic

        Returns:
            Comprehensive research report
        """
        console.print(f"[bold cyan]Starting research on:[/bold cyan] {query}")
        
        try:
            # Run the agent
            response = self.agent(query)
            return str(response)
        except Exception as e:
            console.print(f"[bold red]Error during research execution:[/bold red] {e}")
            return f"An error occurred during research: {str(e)}"
