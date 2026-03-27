# Phase 11: Mock Testing

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 10
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 10: Safety Analysis`](@phase10_safety_analysis.md)

**Next:** (Final phase - proceed to implementation)

---

## Detailed Process

**Goal:** Test graph logic before production deployment

### Why Mock Testing:

**Benefits:**
- ✅ Fast feedback loop (no API calls)
- ✅ Deterministic (same inputs → same outputs)
- ✅ Safe experimentation (no costs or rate limits)
- ✅ Test edge cases (hard to reproduce with real APIs)
- ✅ Catch logic errors before production

**When to Use Mocks:**
- During development (iterate quickly)
- For CI/CD pipelines (reproducible tests)
- When testing error paths (simulate failures)
- For performance testing (isolate graph logic)

**When to Use Real APIs:**
- Integration testing (verify real connections work)
- Production validation (smoke tests)
- When mock complexity exceeds real implementation

### What Gets Generated:

**1. Test Suite Template** (`test_mock.py`)
- Success path test (START → END)
- Validation retry test (error recovery)
- Safety limit test (max iterations)
- Error handling test (LLM failures)
- Edge case tests (empty input, large conversations)
- Integration tests (realistic scenarios)

**2. Mock Fixtures** (`mock_fixtures.json`)
- Test scenarios with expected outcomes
- Mock LLM responses (success and failure cases)
- Mock API responses (for external calls)

**3. Mock States** (`mock_states.json`)
- Fresh start scenario
- Mid-execution scenario
- Near completion scenario

**4. Mock LLM Responses** (`mock_llm_responses.json`)
- Per-node mock responses
- Valid and invalid JSON examples
- Error cases for testing validation

### Testing Philosophy:

**Start Simple:**
```python
# Test 1: Does the graph run at all?
def test_graph_runs():
    result = await graph.invoke(simple_input)
    assert result is not None

# Test 2: Does it reach END?
def test_graph_completes():
    result = await graph.invoke(simple_input)
    assert "END" in str(result) or result.get("task_complete")

# Test 3: Does it produce expected output?
def test_graph_output():
    result = await graph.invoke(simple_input)
    assert result.get("expected_field") == expected_value
```

**Then Add Complexity:**
- Edge cases (empty, malformed, unexpected input)
- Failure scenarios (API errors, timeouts)
- Performance tests (response time limits)
- Integration tests (realistic workflows)

### Running Mock Test Generator:

```bash
python scripts/create_mock_tests.py plan.json
```

**Output:**
- `tests_{graph_name}/` directory created
- `test_{graph_name}_mock.py` - Test suite template
- `mock_states.json` - State scenarios
- `mock_llm_responses.json` - LLM mocks
- `test_fixtures.json` - Test data

### Running Tests:

```bash
cd tests_{graph_name}/
pytest test_{graph_name}_mock.py -v
```

---

## Commenting Standards for Maintainability

### Why Document Solution Choices:

**Future You Will Thank Past You:**
- "Why did I choose X over Y?" - Documented decision rationale
- "What problem does this solve?" - Clear purpose statements
- "When should this be refactored?" - Complexity warnings

### Comment Types to Use:

**1. Decision Rationale Comments**
```python
# Why this solution: Subgraph isolation prevents state pollution bugs
# Alternative considered: Single graph with careful state management
# Trade-off: Added complexity for better safety
class PlanNode:
    ...
```

**2. Complexity Justification**
```python
# Complexity justified: Long-running sessions need message pruning
# Simple solution failed: Unbounded message list causes context overflow
# This approach: Keep last 11 messages (system + 10 turns)
def prune_messages(messages: List) -> List:
    ...
```

**3. Future Expansion Markers**
```python
# MODULAR EXPANSION: To add new specialist agent:
# 1. Add agent to children dict
# 2. Add routing case in route_next()
# 3. No other changes needed (design is extensible)
workflow.add_conditional_edges(...)
```

**4. Known Limitations**
```python
# LIMITATION: Max 3 retries for validation
# Why: Prevents infinite retry loops
# Future: Could make configurable via state or config
if retry_count < MAX_RETRIES:
    ...
```

**5. Performance Optimizations**
```python
# OPTIMIZATION: Cache KB metadata (saves ~500 tokens/turn)
# Why: KB overview rarely changes, fetch once per session
# Simple alternative: Fetch every turn (slower but simpler)
if 'kb_metadata' not in state:
    state['kb_metadata'] = await fetch_kb_overview()
```

### Comment Template:

```python
"""
Node: {node_name}
Purpose: {what it does}
Inputs: {state fields read}
Outputs: {state fields updated}
Why this approach: {decision rationale}
Alternatives considered: {what else was tried}
"""
async def node_function(state):
    # Implementation logic
    ...
```

### When NOT to Comment:

**Skip Comments When:**
- Code is self-explanatory (well-named variables/functions)
- Logic is standard pattern (everyone knows it)
- Change is trivial (obvious one-liners)

**Example - No Comment Needed:**
```python
# ❌ Increment counter by 1
iteration_count += 1

# ✅ Just write it
iteration_count += 1
```

**Example - Comment Needed:**
```python
# ✅ Explain non-obvious choice
# Why 11 messages: System prompt + 10 conversation turns
# Research showed 10 turns provide enough context without overflow
return [messages[0]] + messages[-10:]
```

---

## Modular Expansion Planning

### Design for Future Growth:

**When Planning Today, Consider Tomorrow:**

**1. Extensibility Points:**
```python
# EXTENSION POINT: Add new agents here
children = {
    "booking_agent": BookingAgent(...),
    "gmail_agent": GmailAgent(...),
    # Future: calendar_agent, slack_agent, etc.
}
```

**2. Configuration Over Hard-coding:**
```python
# FUTURE: Move to config file for easy customization
MAX_RETRIES = 3
MAX_ITERATIONS = 50
WINDOW_SIZE = 11
```

**3. Plugin Architecture:**
```python
# MODULAR: Subgraphs are independently testable
# Can swap implementations without changing parent graph
workflow.add_node("plan_node", plan_node_implementation)
# Future: workflow.add_node("plan_node", alternative_planner)
```

**4. Versioning Strategy:**
```python
# VERSION: v1.0 - Initial implementation
# COMPATIBILITY: State schema changes require version bump
# MIGRATION: Document breaking changes in CHANGELOG.md
class GraphStateV1(TypedDict):
    ...
```

### Leave Breadcrumbs:

**For Future Optimizations:**
```python
# TODO: Optimize for long-running sessions
# Current: Simple iteration counter
# Future: Add caching, checkpointing, resume capability
```

**For Known Debt:**
```python
# TECH DEBT: Validation logic duplicated across nodes
# Simple now: ~10 lines each
# Refactor when: 3+ nodes need same validation (DRY principle)
```

**For Scalability:**
```python
# SCALE: Current design handles ~100 items/batch
# Bottleneck: Sequential processing
# Future: Add parallel processing when load increases
```

---

---

## Common Pitfalls

Phase 11 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase implementation:
- [ ] Phase 11 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 10: Safety Analysis`](@phase10_safety_analysis.md)

**Next:** (Final phase - proceed to implementation)


