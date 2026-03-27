# Phase 4: Conditional Edges Planning

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 3
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 3: I/O for Every Node`](@phase3_node_io.md)

**Next:** [`Phase 5: LLM Call Planning`](@phase5_llm_prompts.md)

---

## Detailed Process

**Goal:** Determine routing logic and ensure termination

### For Each Node:

**Decision:** Does it need direct edge or conditional edge?
- **Direct:** Always goes to same next node
- **Conditional:** Routes based on state analysis

### For Conditional Edges:

We'll define:
1. **Routing function signature**
2. **Conditions checked** (state fields, message content, counters)
3. **Possible destinations** (including END)
4. **Fallback logic** (what if conditions fail?)

### Termination Validation Pattern:

```python
def routing_function(state: AgentState) -> str:
    # TERMINATION CHECKS FIRST (CRITICAL!)
    if state.get("task_complete"):
        return END
    if state.get("iteration_count", 0) > 50:
        return END
    if state.get("error_count", 0) > 5:
        return END

    # Business logic routing
    if needs_validation(state):
        return "validation_node"

    return "next_node"
```

**Validation:** Every conditional path must have route to END

**Output:** Routing logic specification + termination validation ✓

---

---

## Common Pitfalls

Phase 4 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 5:
- [ ] Phase 4 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 3: I/O for Every Node`](@phase3_node_io.md)

**Next:** [`Phase 5: LLM Call Planning`](@phase5_llm_prompts.md)


