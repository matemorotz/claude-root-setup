# Validation Patterns for LangGraph

Strategies for validating LLM outputs, state transitions, and graph correctness.

---

## Builder → Syntax Check → Reviewer → Output Pattern

The gold standard validation pattern used in production (CoreTeam, Fly Achensee).

### Pattern Overview

```
builder_node (LLM)
    ↓
syntax_check_node (Deterministic)
    ├─ [APPROVED] → reviewer_node (LLM)
    └─ [REJECTED] → builder_node (retry)
         ↓
reviewer_node (LLM)
    ├─ [APPROVED] → output_node (Extract)
    └─ [REJECTED] → builder_node (retry)
         ↓
output_node (Extract to parent state)
    ↓
END
```

### Implementation

**Subgraph State:**
```python
class ValidationNodeState(TypedDict):
    # Inherited from parent
    messages: Annotated[List[AnyMessage], add_messages]
    context: List[Any]
    plan: str

    # Local working state
    node_messages: List[AnyMessage]  # Isolated conversation
    wrong_syntax_counter: int  # Syntax error tracking
    failed_review_counter: int  # Review rejection tracking
```

**Builder Node:**
```python
async def _builder_node(self, state: ValidationNodeState) -> Dict[str, Any]:
    """Generate output using LLM"""
    context_window = [
        SystemMessage(content=self._builder_prompt),
        SystemMessage(content=now_message())
    ] + state['node_messages']

    response = await self._model.ainvoke(context_window)
    return {"node_messages": state['node_messages'] + [response]}
```

**Syntax Check Node:**
```python
APPROVED_TOKEN = "[APPROVED]"
REJECTED_TOKEN = "[REJECTED]"
MAX_SYNTAX_ERRORS = 3

def _syntax_check_node(self, state: ValidationNodeState) -> Dict[str, Any]:
    """Validate JSON structure with error recovery"""

    def handle_error(error_msg: str) -> Dict[str, Any]:
        if state["wrong_syntax_counter"] < MAX_SYNTAX_ERRORS:
            return {
                "node_messages": state['node_messages'] +
                    [AIMessage(content=f"{REJECTED_TOKEN} {error_msg}")],
                "wrong_syntax_counter": state["wrong_syntax_counter"] + 1
            }
        else:
            raise AgentException(f"Max syntax errors exceeded: {error_msg}")

    try:
        # Extract JSON (handle markdown wrapping)
        content = state['node_messages'][-1].content
        json_str = extract_json_from_response(content)

        # Parse JSON
        obj = json.loads(json_str)

        # Validate with Pydantic (if applicable)
        validated = ValidationModel(**obj)

        # Success
        return {
            "node_messages": state['node_messages'] +
                [AIMessage(content=APPROVED_TOKEN)]
        }

    except json.JSONDecodeError as e:
        return handle_error(f"Invalid JSON syntax: {str(e)}")
    except ValidationError as e:
        return handle_error(f"Schema validation failed: {str(e)}")
```

**Reviewer Node:**
```python
MAX_REVIEW_FAILURES = 2

async def _reviewer_node(self, state: ValidationNodeState) -> Dict[str, Any]:
    """LLM reviews for quality and logic"""

    # Build context with original output to review
    context_window = [
        SystemMessage(content=self._reviewer_prompt)
    ] + state['node_messages']

    response = await self._model.ainvoke(context_window)

    # Check if max reviews exceeded
    if REJECTED_TOKEN in response.content:
        if state["failed_review_counter"] >= MAX_REVIEW_FAILURES:
            # Accept despite rejection if too many retries
            response.content = f"{APPROVED_TOKEN} (Accepted after max retries)"

    return {
        "node_messages": state['node_messages'] + [response],
        "failed_review_counter": state.get("failed_review_counter", 0) +
            (1 if REJECTED_TOKEN in response.content else 0)
    }
```

**Output Node:**
```python
def _output_node(self, state: ValidationNodeState) -> Dict[str, Any]:
    """Extract validated output to parent state"""
    # Approved output is 3 messages back:
    # [-1] = reviewer approval
    # [-2] = syntax approval
    # [-3] = actual output
    approved_output = state['node_messages'][-3].content

    return {"plan": approved_output}
```

**Graph Edges:**
```python
def _syntax_approved_edge(state: ValidationNodeState) -> str:
    """Route based on syntax check result"""
    return "reviewer" if APPROVED_TOKEN in state['node_messages'][-1].content else "builder"

def _review_approved_edge(state: ValidationNodeState) -> str:
    """Route based on reviewer result"""
    return "output" if APPROVED_TOKEN in state['node_messages'][-1].content else "builder"

# Build graph
workflow = StateGraph(ValidationNodeState)
workflow.add_node("builder", self._builder_node)
workflow.add_node("syntax_check", self._syntax_check_node)
workflow.add_node("reviewer", self._reviewer_node)
workflow.add_node("output", self._output_node)

workflow.add_edge(START, "builder")
workflow.add_edge("builder", "syntax_check")
workflow.add_conditional_edges("syntax_check", self._syntax_approved_edge)
workflow.add_conditional_edges("reviewer", self._review_approved_edge)
workflow.add_edge("output", END)
```

---

## JSON Extraction from Markdown

LLMs often wrap JSON in markdown code blocks. Extract gracefully:

```python
import re

def extract_json_from_response(content: str) -> str:
    """Extract JSON from markdown-wrapped or raw JSON responses"""

    # Try markdown code block (```json or ```)
    json_match = re.search(
        r'```(?:json)?\s*(\{.*?\})\s*```',
        content,
        re.DOTALL
    )
    if json_match:
        return json_match.group(1)

    # Try raw JSON object
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json_match.group(0)

    # Try JSON array
    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if json_match:
        return json_match.group(0)

    # Return as-is if no extraction succeeded
    return content
```

---

## Pydantic Validation Models

Use Pydantic for structured validation:

### Basic Model

```python
from pydantic import BaseModel, Field, validator
from typing import List, Literal

class PlanStep(BaseModel):
    """Single step in execution plan"""
    agent: str = Field(..., min_length=1, description="Agent name")
    task: str = Field(..., min_length=10, description="Task description")
    done: bool = Field(default=False, description="Completion status")

    @validator('agent')
    def validate_agent(cls, v, values, **kwargs):
        """Ensure agent exists in available agents"""
        available_agents = ['booking_agent', 'gmail_agent', 'calendar_agent']
        if v not in available_agents:
            raise ValueError(f"Unknown agent: {v}. Available: {available_agents}")
        return v

class PlanModel(BaseModel):
    """Complete execution plan"""
    steps: List[PlanStep] = Field(..., min_items=1, description="Plan steps")
    reasoning: str = Field(default="", description="Optional reasoning")

    class Config:
        extra = "forbid"  # Reject unknown fields
```

### Usage

```python
def validate_plan(json_str: str) -> PlanModel:
    """Parse and validate plan JSON"""
    try:
        obj = json.loads(json_str)
        return PlanModel(**obj)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")
```

---

## Retry Counter Patterns

### Simple Counter

```python
def node_with_retry(self, state: State) -> Dict[str, Any]:
    """Node with max retry limit"""
    MAX_RETRIES = 3

    try:
        result = perform_operation(state)
        return {"output": result}
    except Exception as e:
        if state.get("retry_count", 0) < MAX_RETRIES:
            return {
                "error_message": str(e),
                "retry_count": state.get("retry_count", 0) + 1
            }
        else:
            raise AgentException(f"Max retries exceeded: {e}")
```

### Separate Counters for Different Error Types

```python
class NodeState(TypedDict):
    node_messages: List[AnyMessage]
    syntax_errors: int  # JSON parse errors
    validation_errors: int  # Schema errors
    review_failures: int  # Quality rejections

def validation_node(self, state: NodeState) -> Dict[str, Any]:
    """Track different error types separately"""
    MAX_SYNTAX = 3
    MAX_VALIDATION = 2

    try:
        json_obj = json.loads(extract_json(content))
    except json.JSONDecodeError as e:
        if state.get("syntax_errors", 0) < MAX_SYNTAX:
            return {
                "node_messages": [...],
                "syntax_errors": state.get("syntax_errors", 0) + 1
            }
        raise AgentException("Too many syntax errors")

    try:
        validated = Model(**json_obj)
    except ValidationError as e:
        if state.get("validation_errors", 0) < MAX_VALIDATION:
            return {
                "node_messages": [...],
                "validation_errors": state.get("validation_errors", 0) + 1
            }
        raise AgentException("Too many validation errors")

    return {"node_messages": [...]}  # Success
```

---

## Error Recovery Strategies

### Strategy 1: Graceful Degradation

```python
async def node_with_fallback(state: State) -> Dict[str, Any]:
    """Try primary path, fall back to secondary"""
    try:
        # Primary: Generate detailed plan
        result = await generate_detailed_plan(state)
        return {"plan": result}
    except Exception as e:
        logger.warning(f"Detailed plan failed: {e}, using simple fallback")
        # Fallback: Generate simple plan
        try:
            result = await generate_simple_plan(state)
            return {"plan": result, "fallback_used": True}
        except Exception as e2:
            logger.error(f"Both planning strategies failed: {e2}")
            return {
                "plan": "ERROR",
                "error_count": state.get("error_count", 0) + 1
            }
```

### Strategy 2: Partial Success

```python
async def batch_processing_node(state: State) -> Dict[str, Any]:
    """Process items, accept partial success"""
    items = state['items_to_process']
    results = []
    errors = []

    for item in items:
        try:
            result = await process_item(item)
            results.append(result)
        except Exception as e:
            errors.append({"item": item, "error": str(e)})
            logger.warning(f"Failed to process {item}: {e}")

    return {
        "processed_items": results,
        "failed_items": errors,
        "success_rate": len(results) / len(items)
    }
```

### Strategy 3: Circuit Breaker

```python
class CircuitBreaker:
    """Prevent cascade failures"""
    def __init__(self, max_failures: int = 5, timeout: int = 60):
        self.max_failures = max_failures
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures:
                self.state = "OPEN"
            raise

# Usage
circuit_breaker = CircuitBreaker(max_failures=5, timeout=60)

async def node_with_circuit_breaker(state: State) -> Dict[str, Any]:
    try:
        result = circuit_breaker.call(expensive_operation, state)
        return {"output": result}
    except Exception as e:
        return {"error": str(e), "circuit_open": True}
```

---

## State Transition Validation

### Check State Changes

```python
def validate_state_transition(
    old_state: Dict[str, Any],
    new_state: Dict[str, Any],
    node_name: str
) -> None:
    """Validate state changes are expected"""

    # Check only expected fields changed
    expected_changes = get_expected_changes(node_name)
    actual_changes = {
        k for k in new_state.keys()
        if new_state.get(k) != old_state.get(k)
    }

    unexpected = actual_changes - expected_changes
    if unexpected:
        logger.warning(f"{node_name} changed unexpected fields: {unexpected}")

    # Check required fields present
    required_fields = get_required_fields(node_name)
    missing = required_fields - new_state.keys()
    if missing:
        raise ValueError(f"{node_name} missing required fields: {missing}")
```

### Verify Reducers Work Correctly

```python
def test_message_reducer():
    """Test add_messages reducer"""
    from langgraph.graph.message import add_messages

    # Initial state
    state1 = [HumanMessage(content="Hello")]

    # Add new message
    update = [AIMessage(content="Hi")]
    result = add_messages(state1, update)

    assert len(result) == 2
    assert result[0].content == "Hello"
    assert result[1].content == "Hi"

def test_context_accumulation():
    """Test custom context reducer"""
    def accumulate_unique(existing: List, new: List) -> List:
        """Add only unique items"""
        result = existing.copy()
        for item in new:
            if item not in result:
                result.append(item)
        return result

    existing = ["fact1", "fact2"]
    new = ["fact2", "fact3"]  # fact2 is duplicate
    result = accumulate_unique(existing, new)

    assert result == ["fact1", "fact2", "fact3"]
```

---

## Graph Structure Validation

### Check Termination Paths

```python
def validate_termination(graph: StateGraph) -> List[str]:
    """Verify all paths lead to END"""
    issues = []

    # Get all nodes
    nodes = graph.nodes

    # Check each conditional edge
    for node_name, edge_config in graph.edges.items():
        if edge_config['type'] == 'conditional':
            destinations = edge_config['destinations']

            # Must have END in destinations or route to node that reaches END
            if 'END' not in destinations:
                # Check if all destinations eventually reach END
                for dest in destinations:
                    if not can_reach_end(graph, dest):
                        issues.append(
                            f"Node '{node_name}' conditional edge to '{dest}' "
                            f"has no path to END"
                        )

    return issues

def can_reach_end(graph: StateGraph, start_node: str, visited=None) -> bool:
    """Check if node can reach END"""
    if visited is None:
        visited = set()

    if start_node == 'END':
        return True

    if start_node in visited:
        return False  # Cycle detected

    visited.add(start_node)

    # Check outgoing edges
    edge_config = graph.edges.get(start_node)
    if not edge_config:
        return False

    if edge_config['type'] == 'direct':
        return can_reach_end(graph, edge_config['target'], visited)
    elif edge_config['type'] == 'conditional':
        # At least one destination must reach END
        return any(
            can_reach_end(graph, dest, visited.copy())
            for dest in edge_config['destinations']
        )

    return False
```

### Check for Infinite Loops

```python
def check_for_infinite_loops(graph: StateGraph) -> List[str]:
    """Detect potential infinite loops"""
    issues = []

    # Find cycles
    cycles = find_cycles(graph)

    for cycle in cycles:
        # Check if cycle has termination condition
        has_termination = False

        for node in cycle:
            # Check if node updates iteration counter
            if updates_iteration_counter(node):
                has_termination = True
                break

            # Check if conditional edge in cycle routes to END
            if has_end_route(graph, node):
                has_termination = True
                break

        if not has_termination:
            issues.append(
                f"Potential infinite loop detected: {' -> '.join(cycle)}"
            )

    return issues
```

---

## Testing Patterns

### Unit Test Individual Nodes

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_builder_node():
    """Test builder node in isolation"""
    # Mock dependencies
    mock_model = AsyncMock()
    mock_model.ainvoke.return_value = AIMessage(
        content='{"steps": [{"agent": "test", "task": "test task", "done": false}]}'
    )

    # Create node instance
    node = PlanNode(model=mock_model)

    # Test input state
    input_state = {
        "node_messages": [HumanMessage(content="Test request")]
    }

    # Call node
    output = await node._builder_node(input_state)

    # Verify output
    assert "node_messages" in output
    assert len(output["node_messages"]) == 2  # Input + response
    assert "steps" in output["node_messages"][-1].content
```

### Integration Test Full Subgraph

```python
@pytest.mark.asyncio
async def test_plan_subgraph_valid_input():
    """Test complete plan subgraph with valid input"""
    plan_node = PlanNode(model=real_model)
    graph = plan_node.build_graph()

    input_state = {
        "messages": [HumanMessage(content="Book a flight")],
        "context": [],
        "plan": "",
        "node_messages": [],
        "wrong_syntax_counter": 0,
        "failed_review_counter": 0
    }

    result = await graph.ainvoke(input_state)

    # Verify plan was generated
    assert result["plan"] != ""

    # Verify valid JSON
    plan_obj = json.loads(result["plan"])
    assert "steps" in plan_obj
    assert len(plan_obj["steps"]) > 0
```

### Test Error Recovery

```python
@pytest.mark.asyncio
async def test_syntax_error_recovery():
    """Test recovery from JSON syntax errors"""
    # Mock model that returns invalid JSON first, then valid
    call_count = 0

    async def mock_ainvoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return AIMessage(content="Invalid JSON: {bad syntax")
        else:
            return AIMessage(content='{"steps": []}')

    mock_model = AsyncMock()
    mock_model.ainvoke = mock_ainvoke

    plan_node = PlanNode(model=mock_model)
    graph = plan_node.build_graph()

    result = await graph.ainvoke(input_state)

    # Should have retried and succeeded
    assert result["plan"] != ""
    assert call_count == 2  # Builder called twice
```

---

## Summary

**Key Validation Patterns:**
1. ✓ Builder → Syntax Check → Reviewer → Output (gold standard)
2. ✓ JSON extraction from markdown wrappers
3. ✓ Pydantic models for schema validation
4. ✓ Retry counters with max limits
5. ✓ Graceful degradation and fallbacks
6. ✓ State transition verification
7. ✓ Graph structure validation (termination, loops)
8. ✓ Comprehensive testing (unit, integration, error recovery)

Use these patterns to build robust, error-tolerant LangGraph implementations.
