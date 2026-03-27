# Phase 7: Archetype Generation

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 6
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 6: State Evolution Example`](@phase6_state_evolution.md)

**Next:** [`Phase 8: Code Generation`](@phase8_code_generation.md)

---

## Detailed Process

**Goal:** Save graph pattern for reuse

### Archetype Structure:

```json
{
  "archetype_name": "your_pattern_name",
  "description": "...",
  "complexity": "simple|medium|complex",
  "node_count": N,
  "subgraphs": ["list", "of", "subgraphs"],
  "state_schema": {...},
  "nodes": [...],
  "edges": [...],
  "conditional_edges": [...],
  "key_features": [...]
}
```

### Saved To:

`assets/archetypes/{archetype_name}.json`

### Future Use:

- Load archetype for similar projects
- Customize node details
- Reuse proven patterns

**Output:** Reusable archetype JSON + updated library

---

---

## Common Pitfalls

Phase 7 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 8:
- [ ] Phase 7 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 6: State Evolution Example`](@phase6_state_evolution.md)

**Next:** [`Phase 8: Code Generation`](@phase8_code_generation.md)


