# Phase 8: Code Generation

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase 7
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

## Navigation

**Previous:** [`Phase 7: Archetype Generation`](@phase7_archetypes.md)

**Next:** [`Phase 9: Final Structure Check & Logic Control`](@phase9_structure_check.md)

---

## Detailed Process

**Goal:** Generate well-structured, human-readable production code

### File Structure Generated:

```
src/agents/{graph_name}_graph/
├── common.py              # State schemas (TypedDict)
├── {graph_name}_agent.py  # Main graph class
├── init_node.py           # Initialization node
├── {node_name}_node.py    # Each major node/subgraph
├── routing.py             # Routing functions
├── prompts/
│   ├── builder.prompt     # External prompt files
│   ├── reviewer.prompt
│   └── router.prompt
└── validation.py          # Pydantic models (if used)
```

### Code Quality:

- ✓ Type hints throughout
- ✓ Docstrings for all functions
- ✓ Clear TODOs for customization points
- ✓ Error handling with try/except
- ✓ Async/await where appropriate
- ✓ Production patterns from real implementations

### What You Customize:

- Fill in system prompts in `.prompt` files
- Implement business logic in nodes (marked with TODO)
- Add Pydantic models for validation
- Configure model selection and temperature

### Validation Scripts Generated:

```bash
# Run before deployment
python scripts/validate_state.py plan.json      # Check TypedDict structure
python scripts/validate_termination.py plan.json # Verify END paths
python scripts/check_loops.py plan.json         # Detect infinite loops
python scripts/validate_json.py plan.json       # Enforce JSON I/O
```

**Output:** Complete, production-ready codebase

---

---

## Common Pitfalls

Phase 8 common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase 9:
- [ ] Phase 8 deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

## Navigation

**Previous:** [`Phase 7: Archetype Generation`](@phase7_archetypes.md)

**Next:** [`Phase 9: Final Structure Check & Logic Control`](@phase9_structure_check.md)


