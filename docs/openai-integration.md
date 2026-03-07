<!-- openai-integration.md — Guide for integrating Interceptr with OpenAI Agents SDK -->
# OpenAI Agents SDK Integration

## Overview
Interceptr sits between your agent and tool execution. Before a tool runs, your app sends tool metadata to `POST /api/v1/intercept/`. Interceptr returns `ALLOWED` or `BLOCKED`, and your code decides whether to execute.

## Compatibility note
Interceptr works with any agent framework that performs tool calls over HTTP or can invoke an HTTP check before local tool execution.

## Installation
Install OpenAI Agents SDK and ensure Interceptr is running:

```bash
pip install openai-agents
uvicorn main:app --reload --port 8000
```

## Example: wrapping a tool with Interceptr
```python
import os
import httpx
from agents import Agent, Tool, Runner

INTERCEPTR_URL = os.getenv("INTERCEPTR_URL", "http://localhost:8000")


class ToolCallBlockedError(Exception):
    def __init__(self, tool: str, reason: str):
        self.tool = tool
        self.reason = reason
        super().__init__(f"Tool '{tool}' blocked by Interceptr: {reason}")


def intercepted(tool_name: str, tool_fn):
    """Wraps a tool function with Interceptr security check."""

    def wrapper(**kwargs):
        response = httpx.post(
            f"{INTERCEPTR_URL}/api/v1/intercept/",
            json={"agent": "my-agent", "tool": tool_name, "arguments": kwargs},
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()

        if result["decision"] == "BLOCKED":
            reason = result.get("reason") or "blocked_by_policy"
            raise ToolCallBlockedError(tool_name, reason)

        return tool_fn(**kwargs)

    return wrapper


# Real tool implementations
def get_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id, "name": "Ada Lovelace", "status": "active"}


def delete_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id, "deleted": True}


# Wrapped with Interceptr
safe_get_customer = intercepted("get_customer", get_customer)
safe_delete_customer = intercepted("delete_customer", delete_customer)


tools = [
    Tool(
        name="get_customer",
        description="Get customer details by ID",
        function=safe_get_customer,
    ),
    Tool(
        name="delete_customer",
        description="Delete customer by ID",
        function=safe_delete_customer,
    ),
]

agent = Agent(
    name="CustomerAgent",
    instructions="Use tools to manage customer records.",
    tools=tools,
)


if __name__ == "__main__":
    # Replace with your model configured for the Agents SDK runtime.
    result = Runner.run_sync(agent, "Get customer cus_123")
    print(result)
```

### Sample `policy.yaml` for this example
```yaml
version: "1.0"
agent: "my-agent"
rules:
  allow:
    - get_customer
  deny:
    - delete_customer
default: "deny"
```

With this policy:
- `get_customer` is allowed.
- `delete_customer` is blocked with `reason: policy_violation`.

## Analyzing inputs before the agent
Use `POST /api/v1/analyze/` to screen user inputs for prompt injection before calling the agent:

```python
import httpx
from agents import Runner

INTERCEPTR_URL = "http://localhost:8000"


def analyze_user_input(user_input: str, agent_name: str = "my-agent") -> dict:
    response = httpx.post(
        f"{INTERCEPTR_URL}/api/v1/analyze/",
        json={"input": user_input, "agent": agent_name},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def safe_agent_run(agent, user_input: str):
    analysis = analyze_user_input(user_input)

    if analysis["recommendation"] == "block":
        raise ValueError(
            f"Prompt rejected by Interceptr (severity={analysis['severity']}, "
            f"patterns={analysis['patterns_matched']})"
        )

    # recommendation is allow or monitor
    return Runner.run_sync(agent, user_input)
```

This gives you two protection layers:
1. Input-level screening (`/api/v1/analyze/`) before agent execution.
2. Tool-level enforcement (`/api/v1/intercept/`) before each tool call.
