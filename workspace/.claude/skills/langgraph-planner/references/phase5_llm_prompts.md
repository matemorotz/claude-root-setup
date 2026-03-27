# Phase 5: LLM Call Planning

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 4
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 4: Conditional Edges Planning`](@phase4_conditional_edges.md)

**Next:** [`Phase 6: State Evolution Example`](@phase6_state_evolution.md)

---

## Detailed Process

**Goal:** Design every LLM prompt in execution order

### For Each LLM Node:

**System Prompt Design:**
- Role definition
- Constraints
- Output format (JSON structure)
- Examples (input/output pairs)

**User Prompt Template:**
- How to inject state fields
- Message history handling
- Context window management

**Output Format:**
- JSON structure (strict schema)
- Markdown (structured text)
- Plain text

**Model Selection:**
- Fast model (gpt-4o-mini): Routing, validation, extraction
- Balanced model (gpt-4o): Most tasks
- Powerful model (gpt-4o): Complex reasoning

**Temperature:**
- 0.0: Deterministic (validation, routing)
- 0.3: Balanced (most generation)
- 0.7: Creative (brainstorming)

### Prompt Externalization:

Create `.prompt` files with `$placeholder` syntax:

```
File: builder.prompt

You are an expert $role_name for $workflow workflow.

Output Format (STRICT JSON):
{
  "field": "value"
}

Available Resources: $available_resources
Keywords: $user_key_word, $cancel_key_word, $terminate_key_word
```

### Validation Prompts:

Design approval/rejection tokens:
- `[APPROVED]` for valid outputs
- `[REJECTED] Reason: ...` for invalid outputs

**Output:** Complete prompt library for all LLM nodes

---

---

## Common Pitfalls

Phase 5 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 6:
- [ ] Phase 5 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 4: Conditional Edges Planning`](@phase4_conditional_edges.md)

**Next:** [`Phase 6: State Evolution Example`](@phase6_state_evolution.md)


