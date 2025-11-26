"""Search Agent - Specialized agent for web search execution and synthesis."""

import json
from typing import Dict, Any, List
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from src.utils.config import Config
from src.tools.exa_tool import ExaTool
from src.tools.nci_scoring_tool import NCIScoringTool
from rich.console import Console

console = Console()

# System prompt for the search agent
SEARCH_SYSTEM_PROMPT = """You are a web search retrieval specialist and research synthesis expert.

Your job is to:
1. Execute Exa searches for each provided subquery
2. Use find_similar() on the best results to discover related content
3. Organize findings by relevance and topic
4. Extract key insights from the search results
5. Synthesize comprehensive findings that address the research query

Return structured results with:
- URLs and titles of sources
- Summaries of key findings organized by theme
- Relevant quotes and highlights with context
- How each source contributes to answering the research query
- Connections and patterns across different sources
- Notable experts, institutions, or authoritative voices
- Data, statistics, or concrete examples when available

Be comprehensive but focused. Prioritize high-quality, authoritative sources.
Organize your response in a clear, structured format that can be used for comprehensive research report generation."""


def create_search_agent() -> Agent:
    """
    Create and return a search agent specialized in web search and synthesis.
    
    Returns:
        Agent: Configured search agent
    """
    model = OpenAIModel(
        client_args={
            "api_key": Config.OPENROUTER_API_KEY,
            "base_url": Config.OPENROUTER_BASE_URL,
        },
        model_id=Config.OPENROUTER_MODEL,
    )
    
    agent = Agent(
        name="Search Agent",
        model=model,
        system_prompt=SEARCH_SYSTEM_PROMPT,
        callback_handler=None,  # Suppress intermediate output
    )
    
    return agent


# Create the search agent instance
search_agent = create_search_agent()


def execute_searches(subqueries: List[Dict[str, Any]], exa: ExaTool) -> List[Dict[str, Any]]:
    """
    Execute Exa searches for all subqueries.
    
    Args:
        subqueries: List of subquery dictionaries from planning agent
        exa: ExaTool instance for search execution
        
    Returns:
        List of search results for each subquery
    """
    all_results = []
    nci_scorer = None
    if Config.NCI_SCORING_ENABLED:
        nci_scorer = NCIScoringTool()
    
    for subquery in subqueries:
        if isinstance(subquery, str):
            query_text = subquery
            content_type = "auto"
            time_period = "any"
            include_domains = None
            exclude_domains = None
            priority = 3
        else:
            query_text = subquery.get("query", "")
            content_type = subquery.get("type", "auto")
            time_period = subquery.get("time_period", "any")
            include_domains = subquery.get("include_domains")
            exclude_domains = subquery.get("exclude_domains")
            priority = subquery.get("priority", 3)
        
        # Map time period to date filters (approximate)
        start_date = None
        if time_period == "recent" or time_period == "past_week":
            start_date = "2025-11-17T00:00:00.000Z"  # Approximate for recent
        elif time_period == "past_month":
            start_date = "2025-10-24T00:00:00.000Z"
        elif time_period == "past_year":
            start_date = "2024-11-24T00:00:00.000Z"
        
        # Execute search with more results for deeper research
        num_results = (
            Config.EXA_HIGH_PRIORITY_RESULTS if priority <= 2 
            else Config.EXA_NORMAL_PRIORITY_RESULTS
        )
        search_results = exa.search(
            query=query_text,
            num_results=num_results,
            start_published_date=start_date,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            type=content_type,
        )
        
        # Format results
        formatted_results = exa.format_results(search_results)
        
        # Score top N sources if NCI scoring is enabled
        nci_scores = []
        if nci_scorer and formatted_results:
            sources_to_score = formatted_results[:Config.NCI_TOP_N_SOURCES]
            for source in sources_to_score:
                score = nci_scorer.score_text(
                    text=source.get("text", "") or source.get("summary", ""),
                    url=source.get("url", ""),
                    title=source.get("title", ""),
                )
                nci_scores.append(score)
        
        # Find similar content for high-priority queries
        similar_results = []
        if formatted_results and priority <= 3:
            top_url = formatted_results[0].get("url")
            if top_url:
                similar_response = exa.find_similar(
                    url=top_url,
                    num_results=Config.EXA_SIMILAR_RESULTS,
                )
                similar_results = exa.format_results(similar_response)
        
        all_results.append({
            "subquery": query_text,
            "priority": priority,
            "results": formatted_results,
            "similar_results": similar_results,
            "nci_scores": nci_scores,
        })
    
    return all_results


def format_search_context(search_results: List[Dict[str, Any]]) -> str:
    """
    Format search results into context for the search agent.
    
    Args:
        search_results: Results from Exa searches
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for result_set in search_results:
        subquery = result_set.get("subquery", "")
        results = result_set.get("results", [])
        nci_scores = result_set.get("nci_scores", [])
        
        context_parts.append(f"\n## Subquery: {subquery}")
        
        # Create mapping of URLs to NCI scores
        nci_by_url = {}
        for score in nci_scores:
            if score.get("url"):
                nci_by_url[score["url"]] = score
        
        for i, result in enumerate(results[:10], 1):  # Top 10 per subquery
            title = result.get("title", "No title")
            url = result.get("url", "")
            highlights = result.get("highlights", [])
            text_excerpt = result.get("text", "")[:1000]  # 1000 chars for context
            
            context_parts.append(f"\n### Result {i}: {title}")
            context_parts.append(f"URL: {url}")
            
            # Include NCI score if available
            if url in nci_by_url:
                nci_data = nci_by_url[url]
                if "error" not in nci_data:
                    agg_score = nci_data.get("aggregate_score", 0)
                    risk_level = nci_data.get("risk_level", "UNKNOWN")
                    context_parts.append(f"NCI Score: {agg_score}/20 ({risk_level})")
            
            if highlights:
                context_parts.append(f"Highlights: {', '.join(highlights[:5])}")
            if text_excerpt:
                context_parts.append(f"Excerpt: {text_excerpt}...")
    
    return "\n".join(context_parts)


@tool
def web_search_retriever_tool(research_query: str, subqueries_json: Any) -> str:
    """
    Executes web searches using Exa API for provided subqueries and synthesizes findings.
    Returns organized research findings with sources.
    
    Args:
        research_query: The original research question or topic
        subqueries_json: JSON string or dict/list containing subqueries from planning agent
        
    Returns:
        Comprehensive synthesized findings as a string
    """
    if Config.DEBUG:
        console.print(f"\n[bold yellow][DEBUG] Search Agent called[/bold yellow]")
        console.print(f"[dim]Query: {research_query}[/dim]")
    
    try:
        # Handle both string and dict/list inputs
        if isinstance(subqueries_json, (dict, list)):
            if Config.DEBUG:
                console.print(f"[dim][DEBUG] subqueries_json received as {type(subqueries_json).__name__}, converting to string[/dim]")
            subqueries_data = subqueries_json
        else:
            if Config.DEBUG:
                console.print(f"[dim]Subqueries JSON: {str(subqueries_json)[:200]}...[/dim]")
            subqueries_data = json.loads(subqueries_json)
        
        # Extract subqueries list
        if isinstance(subqueries_data, list):
            subqueries = subqueries_data
        else:
            subqueries = subqueries_data.get("subqueries", [])
        
        if not subqueries:
            return "Error: No subqueries provided"
        
        # Initialize Exa tool
        exa = ExaTool()
        
        # Execute searches
        search_results = execute_searches(subqueries, exa)
        
        # Format context for the agent
        context = format_search_context(search_results)
        
        # Build NCI context if enabled
        nci_context = ""
        if Config.NCI_SCORING_ENABLED:
            nci_display = _compile_nci_report(search_results)
            if nci_display:
                nci_context = f"\n\n## Source Credibility Analysis (NCI Scores)\n{nci_display}"
        
        # Create synthesis prompt
        synthesis_prompt = f"""Research Query: {research_query}

Search Results:
{context}{nci_context}

Organize these findings into a comprehensive, detailed summary. Include:
1. Key findings organized by topic/theme with extensive details
2. Important sources with URLs and brief descriptions
3. Relevant quotes and highlights with context
4. How the sources address the research query
5. Connections and patterns across different sources
6. Notable experts, institutions, or authoritative voices
7. Data, statistics, or concrete examples when available

Be thorough and detailed - this will feed into a comprehensive research report."""
        
        # Call the search agent to synthesize
        response = search_agent(synthesis_prompt)
        result_text = str(response)
        
        # Score the synthesis if NCI is enabled
        synthesis_metadata = ""
        if Config.NCI_SCORING_ENABLED:
            nci_scorer = NCIScoringTool()
            synthesis_score = nci_scorer.score_synthesis(result_text)
            synthesis_metadata = f"\n\n[NCI Synthesis Analysis: {synthesis_score.get('aggregate_score', 0)}/20 - {synthesis_score.get('risk_level', 'UNKNOWN')}]"
        
        if Config.DEBUG:
            console.print(f"[dim][DEBUG] Search Agent returning:[/dim] {result_text[:200]}...")
        
        return result_text + synthesis_metadata
        
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing subqueries: {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        return error_msg
    except Exception as e:
        error_msg = f"Error in retrieval: {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        return error_msg


def _compile_nci_report(search_results: List[Dict[str, Any]]) -> str:
    """
    Compile NCI scores into a readable report format.
    
    Args:
        search_results: Search results with NCI scores
        
    Returns:
        Formatted NCI report string
    """
    all_scores = []
    for result_set in search_results:
        nci_scores = result_set.get("nci_scores", [])
        all_scores.extend(nci_scores)
    
    if not all_scores:
        return ""
    
    # Filter out errors and sort by score
    valid_scores = [s for s in all_scores if "error" not in s]
    if not valid_scores:
        return ""
    
    valid_scores.sort(key=lambda x: x.get("aggregate_score", 0), reverse=True)
    
    # Build report
    report_lines = []
    report_lines.append(f"Total sources scored: {len(valid_scores)}")
    
    # Distribution
    distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
    for score in valid_scores:
        risk = score.get("risk_level", "UNKNOWN")
        if risk in distribution:
            distribution[risk] += 1
    
    report_lines.append(f"Risk distribution - LOW: {distribution['LOW']}, MODERATE: {distribution['MODERATE']}, HIGH: {distribution['HIGH']}, CRITICAL: {distribution['CRITICAL']}")
    
    # Flagged sources (score >= threshold)
    flagged = [s for s in valid_scores if s.get("aggregate_score", 0) >= Config.NCI_SCORE_THRESHOLD]
    if flagged:
        report_lines.append("\nFlagged sources (potential manipulation indicators):")
        for i, source in enumerate(flagged[:10], 1):  # Top 10 flagged
            score = source.get("aggregate_score", 0)
            risk = source.get("risk_level", "UNKNOWN")
            title = source.get("title", "Unknown")[:60]
            summary = source.get("summary", "")
            report_lines.append(f"  {i}. [{score}/20 - {risk}] {title}")
    
    return "\n".join(report_lines)

