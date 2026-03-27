# Agent Architecture Patterns

## Overview
Multi-agent system built on LangGraph with governor-specialist pattern for autonomous task execution.

## Core Architecture

### Governor-Specialist Pattern
- **Governor Agent**: Central orchestrator that routes tasks to appropriate specialists
- **Specialist Agents**: Domain-specific agents (email, booking, calendar, etc.)
- **State Management**: LangGraph native persistent state across agent interactions
- **Context Flow**: Chain of thought pattern (update_context → update_plan → execute_plan)

## Agent Types

### Governor Agent
**Location**: `/root/CoreTeam/dev/main.py`
**Responsibilities**:
- Analyze incoming requests
- Route to appropriate specialist agent
- Aggregate results from multiple agents
- Handle multi-step workflows

**Key Components**:
```python
- Request classification
- Agent selection logic
- State coordination
- Response synthesis
```

### Specialist Agents
**Pattern**: Domain-focused, single-responsibility agents

**Current Specialists**:
- Email Agent: Email operations
- Booking Agent: Reservation management
- Calendar Agent: Schedule operations

**Agent Structure**:
```python
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    context: str
    plan: str
    # Domain-specific fields

def update_context(state: AgentState) -> AgentState:
    """Analyze situation, gather information"""
    pass

def update_plan(state: AgentState) -> AgentState:
    """Create execution plan based on context"""
    pass

def execute_plan(state: AgentState) -> AgentState:
    """Execute planned actions"""
    pass
```

## State Management

### LangGraph State Schema
```python
from typing import TypedDict, Annotated
import operator

class MultiAgentState(TypedDict):
    # Conversation
    messages: Annotated[list, operator.add]

    # Planning
    context: str
    plan: str

    # Routing
    current_agent: str
    next_agent: str

    # Results
    results: dict
    status: str
```

### State Persistence
- State persists across agent transitions
- Checkpoint mechanism for failure recovery
- State can be serialized for storage

## Workflow Patterns

### Single Agent Workflow
```
User Request
    ↓
Governor (classify)
    ↓
Specialist Agent
    ↓
    update_context → update_plan → execute_plan
    ↓
Response to User
```

### Multi-Agent Workflow
```
User Request
    ↓
Governor (classify as multi-step)
    ↓
Agent 1 (calendar check)
    ↓
Governor (aggregate result, route next)
    ↓
Agent 2 (booking create)
    ↓
Governor (synthesize response)
    ↓
Response to User
```

### Error Handling Workflow
```
Agent Execution
    ↓
Error Detected
    ↓
Governor (analyze error)
    ↓
Retry with Modified Plan
    OR
Alternative Agent
    OR
Escalate to User
```

## Agent Communication

### Inter-Agent Messages
```python
{
    "from_agent": "calendar_agent",
    "to_agent": "booking_agent",
    "type": "info",
    "content": {
        "available_slots": ["2025-10-31 14:00", "2025-10-31 15:00"]
    }
}
```

### State Handoff
```python
# Agent 1 completes
state["results"]["calendar_check"] = {
    "status": "success",
    "data": available_slots
}
state["next_agent"] = "booking_agent"

# Governor routes to Agent 2
# Agent 2 receives full state with Agent 1 results
```

## Technology Integration

### LangGraph Integration
- `StateGraph` for agent workflow definition
- `CompiledGraph` for execution
- Subgraphs for complex specialist agents
- Conditional edges for dynamic routing

### Azure OpenAI Integration
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name="gpt-4",
    api_version="2024-02-01"
)
```

### Memory System Integration
- Agents query memory via MCP endpoints
- Context retrieved from long-term memory
- Decisions stored for timeline tracking

## Best Practices

### Agent Design
✓ Single responsibility per specialist agent
✓ Clear state schema definition
✓ Comprehensive error handling
✓ Logging for debugging
✓ Type hints throughout

### State Management
✓ Minimal state required for operation
✓ Clear state transitions
✓ Immutable message history
✓ Checkpointing for recovery

### Performance
✓ Parallel agent execution when possible
✓ Caching for repeated queries
✓ Lazy loading of resources
✓ Timeout handling

## Common Patterns

### Routing Pattern
```python
def route_to_agent(state: MultiAgentState) -> str:
    """Determine next agent based on state"""
    request_type = classify_request(state["messages"][-1])

    if "calendar" in request_type:
        return "calendar_agent"
    elif "booking" in request_type:
        return "booking_agent"
    elif "email" in request_type:
        return "email_agent"
    else:
        return "general_agent"
```

### Aggregation Pattern
```python
def aggregate_results(state: MultiAgentState) -> dict:
    """Combine results from multiple agents"""
    combined = {
        "status": "success",
        "data": {}
    }

    for agent_name, result in state["results"].items():
        combined["data"][agent_name] = result

    return combined
```

### Fallback Pattern
```python
def execute_with_fallback(state: MultiAgentState) -> MultiAgentState:
    """Try primary agent, fallback to alternative"""
    try:
        result = primary_agent(state)
        return result
    except Exception as e:
        logger.warning(f"Primary failed: {e}, trying fallback")
        return fallback_agent(state)
```

## Testing Agents

### Unit Testing
```python
def test_agent_context_update():
    """Test agent updates context correctly"""
    state = {"messages": [{"role": "user", "content": "Book a room"}]}
    result = update_context(state)
    assert "context" in result
    assert "booking" in result["context"].lower()
```

### Integration Testing
```python
def test_governor_to_specialist():
    """Test governor routes to correct specialist"""
    workflow = create_multi_agent_system()
    result = workflow.invoke({
        "messages": [{"role": "user", "content": "Check my calendar"}]
    })
    assert result["current_agent"] == "calendar_agent"
```

## References

See also:
- `/root/CoreTeam/dev/main.py` - Governor implementation
- `/root/CoreTeam/dev/main_alt.py` - Alternative entry point
- `docs/agents/deployment.md` - Deployment procedures
- LangGraph docs: https://langchain-ai.github.io/langgraph/
