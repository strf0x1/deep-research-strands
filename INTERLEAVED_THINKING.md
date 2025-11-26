# Interleaved Thinking in Strands Agents

This document explains the concept of **Interleaved Thinking** and how it is implemented within the `strands` library used in this project.

## Concept

Interleaved thinking is a mechanism that preserves the full chain of reasoning across multiple turns of an agentic workflow. Instead of summarizing or discarding intermediate steps, the supervisor agent maintains a complete history of:

1.  **Thinking**: The model's internal reasoning process.
2.  **Tool Use**: The specific requests made to external tools.
3.  **Tool Results**: The raw output returned by those tools.

This approach prevents "state drift" and results in more coherent, contextualized research reports because the model always has access to its previous logic and the exact data it retrieved.

## Implementation in Strands

In the `strands` library, this behavior is core to the event loop located in `.venv/lib/python3.12/site-packages/strands/event_loop/event_loop.py`.

### 1. Preserving Model Reasoning & Tool Requests

When the model generates a response (which includes its reasoning and any tool calls), the `_handle_model_execution` function immediately appends this full message to the agent's conversation history.

```python
# strands/event_loop/event_loop.py

# ... inside _handle_model_execution ...
# Add the response message to the conversation
agent.messages.append(message)
await agent.hooks.invoke_callbacks_async(MessageAddedEvent(agent=agent, message=message))
```

### 2. Preserving Tool Results

After tools are executed, their outputs are not just processed and discarded. In `_handle_tool_execution`, the results are packaged into a new `user` message with `toolResult` content blocks and appended to the history.

```python
# strands/event_loop/event_loop.py

# ... inside _handle_tool_execution ...
tool_result_message: Message = {
    "role": "user",
    "content": [{"toolResult": result} for result in tool_results],
}

agent.messages.append(tool_result_message)
await agent.hooks.invoke_callbacks_async(MessageAddedEvent(agent=agent, message=tool_result_message))
```

### 3. The Recursive Loop

The cycle continues via `recurse_event_loop`. Because `agent.messages` now contains the sequence `[User Input] -> [Model Reasoning + Tool Call] -> [Tool Result]`, the next inference step has perfect context of what it tried to do and what happened, allowing it to synthesize the information accurately or correct its course.

```python
# strands/event_loop/event_loop.py

events = recurse_event_loop(
    agent=agent, invocation_state=invocation_state, structured_output_context=structured_output_context
)
```

## How This Works in the Deep Research Agent

In this project, interleaved thinking creates a powerful multi-layered context pipeline that flows from research planning through to the final report.

### The Research Context Flow

When a research query is submitted, the supervisor agent's `agent.messages` builds up like this:

```
1. [User Message] Original research query
   ↓
2. [Assistant Message] Supervisor's thinking + planning_agent_tool call
   ↓
3. [User Message] Tool result: 8-12 optimized subqueries with metadata
   ↓
4. [Assistant Message] Supervisor's thinking + web_search_retriever_tool call
   ↓
5. [User Message] Tool result: Synthesized findings from 150-200+ search results
   ↓
6. [Assistant Message] Comprehensive research report (supervisor's synthesis)
```

### Why This Architecture is Powerful

**1. Evidence-Grounded Reasoning**
- The supervisor doesn't hallucinate or rely solely on training data
- It has access to actual URLs, titles, and excerpts from recent web searches
- Multiple independent sources per research angle validate findings
- Inline citations are backed by real results in the context

**2. Multi-Dimensional Coverage via Hierarchical Planning**
The context includes:
- **Planning Layer**: 8-12 subqueries covering core concepts, latest developments, historical context, technical implementations, expert opinions, academic research, market analysis, future implications, challenges, and comparisons
- **Search Layer**: 20 results per high-priority subquery, plus `find_similar()` expansion for discovery
- **Synthesis Layer**: Another LLM pass organizes findings by theme with connections across sources

Each layer builds on the previous one without losing information—it's structured, not flattened.

**3. No State Drift = Perfect Continuity**
Because the entire conversation history (reasoning + requests + results) stays in `agent.messages`:
- The supervisor remembers exactly which subqueries it decomposed the problem into
- It sees which results came from which searches
- It can reason about gaps or redundancies across sources
- It connects dots across different research angles without confusion

**4. Synthesis Without Information Loss**
The data pipeline is optimized for quality:
- **Planning Tool**: Takes raw query → generates subqueries with content type, time period, priority, domain filters
- **Search Tool**: Executes searches → discovers similar content → synthesizes into organized findings (up to 6000 tokens)
- **Supervisor**: Receives pre-organized, thematic findings (not raw results) → writes report

Each step filters and structures information hierarchically, making it more useful without inflating context unnecessarily.

### Context Window Efficiency

A typical research flow uses:
- Planning results: ~1-2 KB (structured subquery metadata)
- Search synthesis: ~4-6 KB (organized findings summary)
- **Total structured context: ~10-15 KB**

This is well within even smaller context windows. Minimax M2 has ~200K context, meaning this approach uses <1% of available space. The magic is that the data is organized hierarchically—each layer filters and prepares information for the next, preventing information bloat while maintaining full traceability.

### The Result

The supervisor writes reports that are:
- **Comprehensive**: Multi-angle coverage from the hierarchical planning
- **Recent**: Based on current web search results, not stale training data
- **Cited**: Every claim is backed by URLs in the context history
- **Coherent**: Interleaved thinking preserves reasoning throughout, preventing contradictions
- **Verifiable**: Developers can inspect `agent.messages` to see exactly what the supervisor saw and when it saw it
