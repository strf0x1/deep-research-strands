"""Planning Agent - Specialized agent for query decomposition and subquery generation."""

import json
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from src.utils.config import Config
from rich.console import Console

console = Console()

# System prompt for the planning agent
PLANNING_SYSTEM_PROMPT = """Generate 8-12 comprehensive Exa-optimized subqueries for deep research on the topic.

For thorough coverage, create subqueries across multiple dimensions:
- Core concepts and definitions
- Latest developments and breakthroughs (recent news)
- Historical context and evolution
- Technical implementations and applications
- Expert opinions and analysis
- Academic research and papers
- Industry trends and market analysis
- Future implications and predictions
- Challenges and limitations
- Related technologies and comparisons

Consider the following when creating subqueries:
- Neural search formulation: Use natural language questions and descriptive phrases
- Domain filters: Suggest specific domains when relevant (e.g., arxiv.org for papers, news sites)
- Time periods: Specify time relevance (recent, past_week, past_month, past_year, any)
- Content types: Specify type when relevant (news, research paper, pdf, blog, etc.)
- Priority: Assign priority 1-5 (1=highest priority)

Each subquery should focus on a different aspect of the research topic to ensure comprehensive, multi-dimensional coverage.

Output valid JSON in this exact format:
{
  "subqueries": [
    {
      "query": "descriptive natural language query",
      "type": "auto|news|research paper|pdf|etc",
      "time_period": "recent|past_week|past_month|past_year|any",
      "include_domains": ["example.com"],
      "exclude_domains": ["example.org"],
      "priority": 1
    }
  ]
}

Notes:
- include_domains and exclude_domains are optional (can be null or omitted)
- type should be "auto" unless you have specific content type needs
- Ensure queries are diverse and cover different angles of the topic"""


def create_planning_agent() -> Agent:
    """
    Create and return a planning agent specialized in query decomposition.
    
    Returns:
        Agent: Configured planning agent
    """
    model = OpenAIModel(
        client_args={
            "api_key": Config.OPENROUTER_API_KEY,
            "base_url": Config.OPENROUTER_BASE_URL,
        },
        model_id=Config.OPENROUTER_MODEL,
    )
    
    agent = Agent(
        name="Planning Agent",
        model=model,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        callback_handler=None,  # Suppress intermediate output
    )
    
    return agent


# Create the planning agent instance that will be used as a tool
planning_agent = create_planning_agent()


@tool
def planning_agent_tool(research_query: str) -> str:
    """
    Generates Exa-optimized subqueries for a research topic.
    Takes a research query and returns JSON with 8-12 subqueries optimized for neural search.
    
    Args:
        research_query: The main research question or topic to decompose
        
    Returns:
        JSON string containing subqueries with optimization parameters
    """
    if Config.DEBUG:
        console.print(f"\n[bold yellow][DEBUG] Planning Agent called with:[/bold yellow] {research_query}")
    
    # Format the query for the planning agent
    prompt = f"Research topic: {research_query}\n\nGenerate Exa-optimized subqueries for comprehensive research on this topic."
    
    try:
        # Call the planning agent
        response = planning_agent(prompt)
        result_text = str(response)
        
        if Config.DEBUG:
            console.print(f"[dim][DEBUG] Planning Agent returning:[/dim] {result_text[:200]}...")
        
        # Parse and validate the JSON response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Validate it's proper JSON
        parsed = json.loads(result_text)
        
        # Return as a formatted JSON string
        return json.dumps({
            "status": "success",
            "subqueries": parsed.get("subqueries", []),
            "research_query": research_query,
        }, indent=2)
        
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error parsing planning agent response:[/bold red] {e}")
        return json.dumps({
            "status": "error",
            "error": f"JSON parsing error: {str(e)}",
            "subqueries": [],
        }, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error in planning agent:[/bold red] {e}")
        return json.dumps({
            "status": "error",
            "error": f"Planning error: {str(e)}",
            "subqueries": [],
        }, indent=2)


