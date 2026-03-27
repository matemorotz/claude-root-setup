# Phase 6: State Evolution Example

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 5
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 5: LLM Call Planning`](@phase5_llm_prompts.md)

**Next:** [`Phase 7: Archetype Generation`](@phase7_archetypes.md)

---

## Detailed Process

**Goal:** Validate understanding through concrete example

### Process:

1. **Create simple scenario** relevant to graph purpose
2. **Trace execution** node by node
3. **Show state at each step** (what fields changed)
4. **Get your feedback** on flow correctness

### Example Format:

```
Scenario: "User requests: Book flight to Paris next week"

START
↓
init_state
  State: {messages: [HumanMessage("Book flight...")], context: [], plan: "", iteration_count: 0}
↓
plan_node
  State: {messages: [...], context: [], plan: '{"steps": [{"agent": "booking_agent", "task": "Search flights to Paris"}]}', iteration_count: 1}
↓
next_node
  State: {messages: [...route to booking_agent...], ...}
↓
booking_agent
  State: {messages: [...tool results...], ...}
↓
context_node
  State: {messages: [...], context: ["Flight options found"], ...}
↓
next_node (decides complete)
  State: {messages: [...route to END...], ...}
↓
END
```

**Your Feedback:**
- Does this flow make sense?
- Any corrections needed?
- Should we add validation or branching?

**Output:** Validated state evolution trace

---

---

## Common Pitfalls

Phase 6 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 7:
- [ ] Phase 6 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 5: LLM Call Planning`](@phase5_llm_prompts.md)

**Next:** [`Phase 7: Archetype Generation`](@phase7_archetypes.md)


