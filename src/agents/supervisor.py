"""Supervisor Agent using Strands Agents SDK - Orchestrator for deep research."""

from rich.console import Console
from strands import Agent
from strands.models.openai import OpenAIModel
from src.utils.config import Config
from src.agents.planning_agent import planning_agent_tool
from src.agents.search_agent import web_search_retriever_tool

# Initialize rich console
console = Console()

class SupervisorAgent:
    """
    Main supervisor agent that coordinates research workflow using Strands Agents.
    """

    def __init__(self, report_structure: str = None):
        """Initialize Supervisor Agent."""
        
        default_structure = """## Required Report Structure:

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
   - Organized by category or theme"""

        structure_to_use = report_structure if report_structure else default_structure

        self.system_prompt = f"""You are a deep research orchestrator specializing in comprehensive, academic-quality research reports. Your goal is to produce thorough, well-structured, in-depth analysis by coordinating specialized agents.

You have access to specialized agents:

1. planning_agent_tool - A specialized planning agent that breaks down research queries into 8-12 Exa-optimized subqueries
2. web_search_retriever_tool - A specialized search agent that executes web searches and synthesizes findings

Research Workflow:
1. Use planning_agent_tool to decompose the user's research query into comprehensive subqueries
2. Use web_search_retriever_tool with the research query and subqueries to gather extensive information
3. Synthesize a COMPREHENSIVE research report (15-30 pages equivalent) with the following structure:

{structure_to_use}

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
