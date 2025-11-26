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
