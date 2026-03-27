# Phase 2: Nodes, Edges, and State Objects

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 1
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 1: Graph Complexity Analysis`](@phase1_complexity_analysis.md)

**Next:** [`Phase 3: I/O for Every Node`](@phase3_node_io.md)

---

## Detailed Process

**Goal:** Define graph structure at high level

### Node Types to Consider:

**LLM Nodes** (async with await)
- Generation (plans, analyses, summaries)
- Analysis (extraction, classification)
- Routing decisions (embedded JSON)

**Tool Nodes** (async, calls MCP/APIs)
- MCP tool calls
- API requests
- Database queries

**Validation Nodes** (synchronous)
- Syntax checking (JSON validation)
- Business logic validation
- Quality evaluation

**Routing Nodes** (synchronous or async)
- Conditional decision making
- Agent selection
- Path determination

**Output Nodes** (synchronous)
- State extraction
- Result formatting
- Parent state updates

### Flow Mapping:

I will help you map:
- **Initial flow:** START → init → processing → routing → END
- **Loops:** Validation retries, refinement cycles (with iteration limits)
- **Branches:** Conditional paths based on state

### State Schema Design:

We'll design TypedDict with:
- **Required fields:** Always present (e.g., `messages`, `context`)
- **Optional fields:** NotRequired for conditional data
- **Reducers:** Annotated types for lists (e.g., `add_messages`)
- **State isolation:** Parent vs subgraph state separation

**Output:** Node catalog + edge map + complete state schema structure

---

---

## Common Pitfalls

Phase 2 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 3:
- [ ] Phase 2 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 1: Graph Complexity Analysis`](@phase1_complexity_analysis.md)

**Next:** [`Phase 3: I/O for Every Node`](@phase3_node_io.md)


