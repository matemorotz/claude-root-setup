# LangGraph Knowledge Base

**Compiled:** 2026-01-12
**Sources:** CoreTeam production codebase, LangGraph dev agents analysis, 2026 best practices
**Version:** 1.0

---

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [State Management](#state-management)
3. [Node Building Patterns](#node-building-patterns)
4. [Edge Configuration](#edge-configuration)
5. [Subgraph Architecture](#subgraph-architecture)
6. [Termination Patterns](#termination-patterns)
7. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
8. [Production Patterns](#production-patterns)
9. [Testing Strategies](#testing-strategies)
10. [Performance Optimization](#performance-optimization)

---

## Core Concepts

### What is LangGraph?

LangGraph is a framework for building stateful, multi-agent AI systems using graph-based workflows. It provides:
- **Nodes**: Functions that do computation
- **Edges**: Control flow between nodes
- **State**: Shared memory across the graph
- **Checkpointing**: Persistent state management

### Key Components

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# 1. Define State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]
    iteration_count: int

# 2. Create Graph
graph = StateGraph(AgentState)

# 3. Add Nodes
graph.add_node("node1", node1_function)
graph.add_node("node2", node2_function)

# 4. Add Edges
graph.add_edge(START, "node1")
graph.add_conditional_edges("node1", routing_function)
graph.add_edge("node2", END)

# 5. Compile
app = graph.compile(checkpointer=checkpointer)
```

---

## State Management

### Best Practices

#### 1. Keep State Small, Typed, and Validated

```python
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

# ✅ GOOD: Minimal, well-typed state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # With reducer
    context: list[str]                                    # Simple list
    plan: str                                              # Simple string
    iteration_count: int                                   # Safety counter

# ❌ BAD: Overly complex state
class BadState(TypedDict):
    messages: list  # No type hints
    context: dict   # Too vague
    arbitrary_data: Any  # Unclear purpose
    user_profile: dict   # Should be separate
```

#### 2. Use Reducers for List/Message State

```python
from langgraph.graph.message import add_messages

# Reducer automatically handles message accumulation
class State(TypedDict):
    # This will append new messages instead of replacing
    messages: Annotated[list[BaseMessage], add_messages]

# Custom reducer for context accumulation
def add_context(existing: list[str], new: list[str]) -> list[str]:
    """Append new context items, avoiding duplicates."""
    return existing + [item for item in new if item not in existing]

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: Annotated[list[str], add_context]  # Custom reducer
```

#### 3. State Isolation (Subgraphs)

**Critical Pattern:** Parent graphs handle routing, subgraphs handle internal logic.

```python
# ❌ WRONG: Sharing state between parent and subgraph
class SharedState(TypedDict):
    messages: list
    context: list  # Both parent and subgraph modify
    plan: str      # Both parent and subgraph modify

# ✅ CORRECT: Hierarchical isolation
class ParentState(TypedDict):
    """Parent state - routing only"""
    messages: Annotated[list[BaseMessage], add_messages]
    # No context, plan - those stay in subgraph

class SubgraphState(TypedDict):
    """Subgraph state - internal logic"""
    messages: Annotated[list[BaseMessage], add_messages]
    context: list  # Private to subgraph
    plan: str      # Private to subgraph
    iteration_count: int  # Private to subgraph
```

#### 4. Message-Based Routing

```python
import json
from langchain_core.messages import AIMessage

# Encode routing info in message content
def encode_next(agent: str, message: str, name: str) -> AIMessage:
    """Encode next agent and message in JSON format."""
    next_obj = {
        "next": {
            "agent": agent,
            "message": message
        }
    }
    return AIMessage(content=json.dumps(next_obj), name=name)

# Decode for routing
def decode_next(message: AIMessage) -> tuple[str, str]:
    """Extract next agent and message from AIMessage."""
    if not message.content or message.content.strip() == "":
        return "[TERMINATE]", "Empty response"

    try:
        next_obj = json.loads(message.content)["next"]
        return next_obj["agent"], next_obj["message"]
    except (json.JSONDecodeError, KeyError) as e:
        return "[TERMINATE]", f"Error parsing routing: {e}"
```

### State Validation

```python
def validate_state_update(state: AgentState, update: dict) -> dict:
    """Validate state updates before applying."""
    # Check required fields
    if "messages" in update and not isinstance(update["messages"], list):
        raise ValueError("messages must be a list")

    # Sanitize PII from context
    if "context" in update:
        update["context"] = [sanitize_pii(item) for item in update["context"]]

    return update
```

---

## Node Building Patterns

### Basic Node Structure

```python
from typing import Dict, Any
from langchain_core.messages import AIMessage

async def node_function(state: AgentState) -> Dict[str, Any]:
    """
    Node function: receives state, returns partial state update.

    Best practices:
    - Treat as pure function (no side effects)
    - Return partial state (only changed fields)
    - Use async for LLM calls
    - Validate inputs/outputs
    """
    # 1. Extract needed state
    messages = state["messages"]
    context = state.get("context", [])

    # 2. Perform computation (e.g., LLM call)
    response = await llm.ainvoke(messages)

    # 3. Update context
    new_context = context + [extract_info(response)]

    # 4. Return partial state update
    return {
        "messages": [response],  # Reducer will append
        "context": new_context,
        "iteration_count": state.get("iteration_count", 0) + 1
    }
```

### Node Types

#### 1. LLM Nodes

```python
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

async def llm_node(
    state: AgentState,
    model: BaseChatModel,
    system_prompt: str
) -> Dict[str, Any]:
    """Node that calls an LLM."""
    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]

    response = await model.ainvoke(messages)

    return {"messages": [response]}
```

#### 2. Tool Nodes

```python
from langchain_core.tools import BaseTool

async def tool_node(
    state: AgentState,
    tools: list[BaseTool]
) -> Dict[str, Any]:
    """Node that executes tools based on LLM calls."""
    last_message = state["messages"][-1]

    # Check if LLM called tools
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}  # No tools to execute

    # Execute tools
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool = next(t for t in tools if t.name == tool_call["name"])
        result = await tool.ainvoke(tool_call["args"])
        tool_messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    return {"messages": tool_messages}
```

#### 3. Validation Nodes

```python
def validation_node(state: AgentState) -> Dict[str, Any]:
    """Node that validates state and updates flags."""
    plan = state.get("plan", "")
    context = state.get("context", [])

    # Check completion criteria
    plan_complete = all([
        "task completed" in plan.lower(),
        len(context) > 0,
        state.get("iteration_count", 0) < 50
    ])

    return {
        "plan_complete": plan_complete,
        "waiting_for_user": "need more information" in plan.lower()
    }
```

#### 4. Router Nodes

```python
def router_node(state: AgentState) -> Dict[str, Any]:
    """Node that determines next agent based on state."""
    last_message = state["messages"][-1]

    # Analyze message to determine routing
    if "booking" in last_message.content.lower():
        next_agent = "booking_agent"
    elif "email" in last_message.content.lower():
        next_agent = "email_agent"
    else:
        next_agent = "governor_agent"

    return encode_next(next_agent, last_message.content, "router")
```

### Node Best Practices

1. **Validate Inputs/Outputs**
```python
def node_with_validation(state: AgentState) -> Dict[str, Any]:
    # Validate inputs
    assert state.get("messages"), "messages required"
    assert isinstance(state["messages"], list), "messages must be list"

    # Process
    result = process(state)

    # Validate outputs
    assert "messages" in result, "must return messages"
    return result
```

2. **Handle Errors Gracefully**
```python
async def safe_node(state: AgentState) -> Dict[str, Any]:
    try:
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        error_msg = AIMessage(content=f"Error: {str(e)}", name="error_handler")
        return {"messages": [error_msg], "error_count": state.get("error_count", 0) + 1}
```

3. **Context Window Management**
```python
def trim_context_node(state: AgentState) -> Dict[str, Any]:
    """Trim message history to prevent context overflow."""
    messages = state["messages"]

    # Keep first (system) and last N messages
    if len(messages) > 50:
        trimmed = [messages[0]] + messages[-49:]  # System + last 49
        return {"messages": trimmed}

    return {}  # No change
```

---

## Edge Configuration

### Edge Types

#### 1. Simple (Direct) Edges

```python
# Direct connection: node1 always goes to node2
graph.add_edge("node1", "node2")
graph.add_edge("node2", END)
```

**When to use:** Linear workflows where the next step is always the same.

#### 2. Conditional Edges

```python
def routing_function(state: AgentState) -> str:
    """
    Conditional routing based on state.

    Returns: Name of next node to execute.
    """
    if state.get("plan_complete"):
        return END
    elif state.get("waiting_for_user"):
        return "user_input_node"
    else:
        return "planning_node"

# Add conditional edge
graph.add_conditional_edges(
    "validation_node",  # Source node
    routing_function    # Returns next node name
)
```

**When to use:** Decision points where the next step depends on state.

#### 3. Conditional Edge with Mapping

```python
def routing_function(state: AgentState) -> str:
    """Return key from path_map."""
    if "booking" in state["messages"][-1].content:
        return "booking"
    elif "email" in state["messages"][-1].content:
        return "email"
    else:
        return "default"

# Map routing keys to node names
graph.add_conditional_edges(
    "router",
    routing_function,
    {
        "booking": "booking_agent",
        "email": "email_agent",
        "default": "governor_agent"
    }
)
```

**When to use:** Multiple routing options with clear categories.

### Routing Best Practices

#### 1. Keep Routing Functions Simple

```python
# ✅ GOOD: Simple, clear logic
def route(state: AgentState) -> str:
    if state.get("complete"):
        return END
    return "next_node"

# ❌ BAD: Complex logic in routing
def bad_route(state: AgentState) -> str:
    # Don't do heavy computation here
    analysis = complex_analysis(state)
    result = database_query(analysis)
    return "node" if result else END
```

#### 2. Validate Routing Returns

```python
def safe_routing(state: AgentState, valid_nodes: list[str]) -> str:
    """Routing with validation."""
    next_node = determine_next(state)

    # Validate
    if next_node not in valid_nodes and next_node != END:
        print(f"Warning: Invalid route '{next_node}', defaulting to governor")
        return "governor_agent"

    return next_node
```

#### 3. Handle Edge Cases

```python
def robust_routing(state: AgentState) -> str:
    """Routing with error handling."""
    try:
        last_message = state["messages"][-1]
        next_agent, _ = decode_next(last_message)
        return next_agent
    except (IndexError, KeyError, json.JSONDecodeError):
        return "governor_agent"  # Safe default
```

---

## Subgraph Architecture

### When to Use Subgraphs

Use subgraphs when:
1. **Complex multi-step workflows** need isolation
2. **Internal state** shouldn't pollute parent graph
3. **Reusable components** across different graphs
4. **Validation loops** or **retry logic** needed

### Subgraph Pattern

```python
# Subgraph State (isolated)
class SubgraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    internal_context: list[str]  # Private
    retry_count: int              # Private

# Build subgraph
subgraph = StateGraph(SubgraphState)
subgraph.add_node("step1", step1_function)
subgraph.add_node("step2", step2_function)
subgraph.add_node("validate", validate_function)
subgraph.add_edge(START, "step1")
subgraph.add_edge("step1", "step2")
subgraph.add_conditional_edges("step2", lambda s: "validate" if s["retry_count"] < 3 else END)
subgraph.add_conditional_edges("validate", lambda s: "step1" if not s.get("valid") else END)

# Compile subgraph
compiled_subgraph = subgraph.compile(name="my_subgraph")

# Use in parent graph
parent_graph = StateGraph(ParentState)
parent_graph.add_node("subgraph_node", compiled_subgraph)
```

### Governor-Agent Pattern (Production)

```python
"""
3-Layer Architecture:
Team Graph → Governor Subgraph → Specialist Agents
"""

# Layer 1: Team Graph (Routing)
class TeamState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def create_team(governor: CompiledStateGraph, specialists: list) -> CompiledStateGraph:
    graph = StateGraph(TeamState)

    # Add nodes
    graph.add_node("governor", governor)
    for specialist in specialists:
        graph.add_node(specialist.name, specialist.agent)

    # Routing
    graph.add_edge(START, "governor")
    graph.add_conditional_edges("governor", route_to_specialist)
    for specialist in specialists:
        graph.add_conditional_edges(specialist.name, route_to_specialist)

    return graph.compile(checkpointer=checkpointer)

# Layer 2: Governor Subgraph (Orchestration)
class GovernorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]      # Private
    plan: str               # Private
    iteration_count: int    # Private

def create_governor() -> CompiledStateGraph:
    graph = StateGraph(GovernorState)
    graph.add_node("update_context", update_context_node)
    graph.add_node("update_plan", update_plan_node)
    graph.add_node("route", route_node)

    graph.add_edge(START, "update_context")
    graph.add_edge("update_context", "update_plan")
    graph.add_edge("update_plan", "route")
    graph.add_edge("route", END)

    return graph.compile(name="governor")

# Layer 3: Specialist Agents
class SpecialistAgent:
    def __init__(self, name: str, tools: list[BaseTool]):
        self.name = name
        self.agent = create_react_agent(model, tools)
```

### Subgraph Communication

```python
# Parent → Subgraph: Messages only
def parent_node(state: ParentState) -> Dict[str, Any]:
    """Parent passes messages to subgraph."""
    return {
        "messages": [HumanMessage(content="task description")]
    }

# Subgraph → Parent: Results in messages
def subgraph_output_node(state: SubgraphState) -> Dict[str, Any]:
    """Subgraph returns results via messages."""
    result = compute_result(state["internal_context"])
    return {
        "messages": [AIMessage(content=json.dumps(result), name="subgraph")]
    }
```

---

## Termination Patterns

### Critical: Always Implement Termination

**Problem:** Graphs without proper termination hit recursion limits.

```python
# ❌ WRONG: No termination condition
def route_without_end(state: AgentState) -> str:
    if state.get("has_work"):
        return "work_node"
    return "work_node"  # Always loops!

# ✅ CORRECT: Explicit termination
def route_with_end(state: AgentState) -> str:
    if state.get("plan_complete"):
        return END
    if state.get("iteration_count", 0) > 50:
        return END  # Safety limit
    if state.get("has_work"):
        return "work_node"
    return END  # Default to end
```

### Multi-Layer Termination

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    plan_complete: bool           # Explicit completion flag
    waiting_for_user: bool        # User input needed
    iteration_count: int          # Safety counter
    error_count: int              # Error threshold

def termination_check(state: AgentState) -> str:
    """Multi-condition termination logic."""
    # 1. Explicit completion
    if state.get("plan_complete", False):
        return END

    # 2. Waiting for user
    if state.get("waiting_for_user", False):
        return END

    # 3. Safety limits
    if state.get("iteration_count", 0) > 50:
        return END

    if state.get("error_count", 0) > 5:
        return END

    # 4. Continue workflow
    return "next_node"
```

### Recursion Limit Configuration

```python
from langgraph.checkpoint.memory import InMemorySaver

# Compile with checkpointer
app = graph.compile(checkpointer=InMemorySaver())

# Configure recursion limit
config = {
    "recursion_limit": 50,  # Default: 25
    "configurable": {
        "thread_id": "conversation-1"
    }
}

# Invoke with config
result = await app.ainvoke(initial_state, config=config)
```

### Handling Recursion Errors

```python
from langgraph.errors import GraphRecursionError

try:
    result = await app.ainvoke(state, config=config)
except GraphRecursionError as e:
    # Log details
    print(f"Recursion limit reached: {e}")
    print(f"Last state: {state}")

    # Attempt recovery
    state["plan_complete"] = True
    result = await app.ainvoke(state, config={**config, "recursion_limit": 10})
```

---

## Common Pitfalls & Solutions

### 1. Missing Termination Logic (Causes 45% of failures)

**Problem:**
```python
# Infinite loop
def route(state):
    return "planning_node"  # Always loops back!

graph.add_conditional_edges("planning_node", route)
```

**Solution:**
```python
def route(state):
    if state.get("plan_complete"):
        return END
    if state.get("iteration_count", 0) > 50:
        return END
    return "planning_node"
```

### 2. Missing JSON Error Handling (Causes 10% of failures)

**Problem:**
```python
def decode(message):
    return json.loads(message.content)["next"]  # Fails on empty/invalid
```

**Solution:**
```python
def decode(message):
    if not message.content:
        return "[TERMINATE]", "Empty response"

    try:
        return json.loads(message.content)["next"]
    except (json.JSONDecodeError, KeyError) as e:
        return "[TERMINATE]", f"Error: {e}"
```

### 3. State Pollution Across Subgraphs

**Problem:**
```python
# Shared state causes conflicts
class SharedState(TypedDict):
    messages: list
    context: list  # Both parent and subgraph modify
```

**Solution:**
```python
# Isolated state
class ParentState(TypedDict):
    messages: Annotated[list, add_messages]

class SubgraphState(TypedDict):
    messages: Annotated[list, add_messages]
    context: list  # Private to subgraph
```

### 4. Synchronous LLM Calls in Async Graphs

**Problem:**
```python
def node(state):
    response = model.invoke(messages)  # Blocking!
    return {"messages": [response]}
```

**Solution:**
```python
async def node(state):
    response = await model.ainvoke(messages)  # Non-blocking
    return {"messages": [response]}
```

### 5. Overly Complex Routing

**Problem:**
```python
def complex_route(state):
    # Heavy computation in routing
    analysis = analyze_full_context(state)
    db_result = query_database(analysis)
    return "node" if db_result else END
```

**Solution:**
```python
# Move computation to node
def simple_route(state):
    if state.get("routing_decision"):
        return state["routing_decision"]
    return END

def decision_node(state):
    # Heavy computation here
    decision = analyze_and_decide(state)
    return {"routing_decision": decision}
```

---

## Production Patterns

### 1. Checkpointing for Persistence

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Production: Postgres checkpointer
connection_string = "postgresql://user:pass@host:5432/db"
checkpointer = PostgresSaver.from_conn_string(connection_string)

app = graph.compile(checkpointer=checkpointer)

# Use thread_id for conversation persistence
config = {
    "configurable": {
        "thread_id": f"user-{user_id}-conversation"
    }
}

result = await app.ainvoke(state, config=config)
```

### 2. Observability with LangSmith

```python
import os

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"

# Runs will automatically be traced
result = await app.ainvoke(state, config=config)
```

### 3. Error Recovery

```python
def error_recovery_wrapper(node_func):
    """Wrapper for node error recovery."""
    async def wrapper(state: AgentState) -> Dict[str, Any]:
        try:
            return await node_func(state)
        except Exception as e:
            # Log error
            print(f"Error in {node_func.__name__}: {e}")

            # Return safe state update
            return {
                "messages": [AIMessage(content=f"Error: {e}", name="error_handler")],
                "error_count": state.get("error_count", 0) + 1
            }
    return wrapper

# Wrap nodes
graph.add_node("risky_node", error_recovery_wrapper(risky_node_function))
```

### 4. Token Accounting

```python
from langchain.callbacks import get_openai_callback

async def node_with_tracking(state: AgentState) -> Dict[str, Any]:
    """Node with token usage tracking."""
    with get_openai_callback() as cb:
        response = await model.ainvoke(state["messages"])

        # Log token usage
        print(f"Tokens: {cb.total_tokens}, Cost: ${cb.total_cost}")

    return {
        "messages": [response],
        "total_tokens": state.get("total_tokens", 0) + cb.total_tokens
    }
```

### 5. Graceful Degradation

```python
async def llm_node_with_fallback(state: AgentState) -> Dict[str, Any]:
    """LLM node with model fallback."""
    models = [primary_model, secondary_model, tertiary_model]

    for model in models:
        try:
            response = await model.ainvoke(state["messages"])
            return {"messages": [response]}
        except Exception as e:
            print(f"Model {model.model_name} failed: {e}")
            continue

    # All models failed
    return {
        "messages": [AIMessage(content="Error: All models failed", name="error")],
        "error_count": state.get("error_count", 0) + 1
    }
```

---

## Testing Strategies

### 1. Mock MCP Pattern

```python
# Create skeleton-based mocks
import test.mcp_skeletons.gmail_skeleton as gmail_skeleton

def mock_fetch_emails(user_id: str, limit: int):
    """Return Python objects, not JSON strings."""
    return [
        {
            "id": "email-1",
            "from": "user@example.com",
            "subject": "Test",
            "body": "Test email"
        }
    ]

# Register mocks
gmail_tools = gmail_skeleton.get_tools(
    fetch_mail_threads_implementation=mock_fetch_emails
)
```

### 2. Time Mocking

```python
from freezegun import freeze_time

@freeze_time("2025-06-10 10:17:32")
def test_booking_flow():
    """Test with frozen time for deterministic results."""
    now = "2025-06-10 10:17:32"

    # Email date < now, booking date > now
    state = {
        "messages": [HumanMessage(content="Check emails")]
    }

    result = app.invoke(state)
    assert result["success"]
```

### 3. Dataset Testing

```python
# Create test datasets
def create_dataset(scenario: str) -> dict:
    """Create test dataset for specific scenario."""
    return {
        "name": scenario,
        "initial_prompt": "...",
        "mock_tools": {...},
        "expected_outcome": "..."
    }

datasets = [
    create_dataset("simple_booking"),
    create_dataset("cancellation"),
    create_dataset("rescheduling")
]

# Run all datasets
for dataset in datasets:
    result = test_with_dataset(dataset)
    assert result["success"], f"Failed: {dataset['name']}"
```

---

## Performance Optimization

### 1. Context Window Management

```python
def prune_messages(messages: list, max_length: int = 50) -> list:
    """Keep system message + recent messages."""
    if len(messages) <= max_length:
        return messages

    # Keep system message + last N messages
    system_msg = [m for m in messages if isinstance(m, SystemMessage)]
    recent = messages[-(max_length - len(system_msg)):]

    return system_msg + recent
```

### 2. Parallel Tool Execution

```python
import asyncio

async def parallel_tool_node(state: AgentState, tools: list[BaseTool]):
    """Execute multiple tools in parallel."""
    tool_calls = state["messages"][-1].tool_calls

    # Execute all tools concurrently
    results = await asyncio.gather(*[
        tool.ainvoke(call["args"])
        for call in tool_calls
        for tool in tools if tool.name == call["name"]
    ])

    return {"messages": [ToolMessage(content=r) for r in results]}
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(input_data: str) -> str:
    """Cache expensive computations."""
    return compute_result(input_data)

def node_with_cache(state: AgentState) -> Dict[str, Any]:
    """Node that uses caching."""
    input_data = state["messages"][-1].content
    result = expensive_computation(input_data)
    return {"messages": [AIMessage(content=result)]}
```

### 4. Model Selection

```python
# Use faster models for simple tasks
def create_agent_with_model_tiers(tools: list[BaseTool]):
    """Different models for different complexity."""

    # Fast model for simple routing
    router_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Powerful model for complex reasoning
    planning_model = ChatOpenAI(model="gpt-4o", temperature=0)

    return {
        "router": router_model,
        "planner": planning_model
    }
```

---

## Real-World Example: CoreTeam Architecture

### Complete Implementation

```python
"""
Production LangGraph multi-agent system.
Source: /root/software/CoreTeam/TheCoreTeam/
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

# ===== LAYER 1: Team State (Routing) =====
class CoreTeamState(TypedDict):
    """Parent state - routing only."""
    messages: Annotated[list[AnyMessage], add_messages]

# ===== LAYER 2: Governor State (Orchestration) =====
class GovernorState(TypedDict):
    """Governor subgraph state - internal logic."""
    messages: Annotated[list[AnyMessage], add_messages]
    context: list[str]          # Accumulated facts
    plan: str                   # Current plan
    last_context_message: int   # Tracking
    iteration_count: int        # Safety

# ===== LAYER 3: Specialist Agents =====
class BookingAgent:
    """Specialist for flight bookings."""
    def __init__(self, model, tools):
        self.name = "booking_agent"
        self.agent = create_react_agent(model, tools)

# ===== Governor Subgraph =====
def create_governor_subgraph(models: dict) -> CompiledStateGraph:
    """Governor orchestrates workflow."""
    graph = StateGraph(GovernorState)

    # Nodes
    graph.add_node("init", init_state_node)
    graph.add_node("update_context", update_context_node)
    graph.add_node("update_plan", update_plan_node)
    graph.add_node("route", route_node)

    # Flow
    graph.add_edge(START, "init")
    graph.add_edge("init", "update_plan")
    graph.add_edge("update_plan", "route")
    graph.add_conditional_edges("route", decide_context_or_end)
    graph.add_edge("update_context", END)

    return graph.compile(name="governor", checkpointer=True)

# ===== Team Graph =====
def create_team(
    governor: CompiledStateGraph,
    specialists: list[BaseCoreTeamAgent],
    checkpointer
) -> CompiledStateGraph:
    """Top-level team graph."""

    all_agents = ["governor"] + [s.name for s in specialists]

    def route_to_next(state: CoreTeamState) -> str:
        """Route based on last message."""
        try:
            next_agent, _ = decode_next_from_state(state)
        except (json.JSONDecodeError, KeyError):
            return "governor"  # Safe default

        if next_agent == "[TERMINATE]":
            return END

        return next_agent

    # Build graph
    graph = StateGraph(CoreTeamState)
    graph.add_node("governor", governor)
    for specialist in specialists:
        graph.add_node(specialist.name, specialist.agent)

    # Routing
    graph.add_edge(START, "governor")
    graph.add_conditional_edges("governor", route_to_next)
    for specialist in specialists:
        graph.add_conditional_edges(specialist.name, route_to_next)

    return graph.compile(checkpointer=checkpointer)

# ===== Usage =====
async def main():
    """Run the team."""
    # Create components
    governor = create_governor_subgraph(models)
    booking_agent = BookingAgent(models["fast"], booking_tools)

    # Create team
    team = create_team(
        governor=governor,
        specialists=[booking_agent],
        checkpointer=PostgresSaver.from_conn_string(db_url)
    )

    # Run
    result = await team.ainvoke(
        {"messages": [HumanMessage(content="Book a flight")]},
        config={"recursion_limit": 50, "thread_id": "user-123"}
    )

    print(result["messages"][-1].content)
```

---

## Sources

This knowledge base was compiled from:

### Codebase Sources
- `/root/software/CoreTeam/TheCoreTeam/` - Production multi-agent system
- `/root/software/langgraph_dev_agents/` - LangGraph code analysis agents
- `/root/software/CoreTeam/COMPREHENSIVE_TEST_ANALYSIS.md` - 22-dataset test analysis

### External Sources (2026)
- [LangGraph Best Practices](https://www.swarnendu.de/blog/langgraph-best-practices/)
- [Graph API Overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Advanced LangGraph: Conditional Edges](https://dev.to/jamesli/advanced-langgraph-implementing-conditional-edges-and-tool-calling-agents-3pdn)
- [LangGraph Multi-Agent Orchestration](https://latenode.com/blog/ai-frameworks-technical-infrastructure/langgraph-multi-agent-orchestration/langgraph-multi-agent-orchestration-complete-framework-guide-architecture-analysis-2025)
- [How to Create and Control Loops](https://langchain-ai.github.io/langgraphjs/how-tos/recursion-limit/)
- [Recursion Limit Documentation](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT)

---

**Last Updated:** 2026-01-12
**Version:** 1.0
**Maintainer:** Claude Code
