# Anti Patterns

**Source:** ORCHESTRATOR_SEPARATION_PRINCIPLE.md
**Section:** Anti-Patterns to Avoid

---

## Anti-Patterns to Avoid

### ❌ Orchestrator Accumulation
```python
# BAD: Orchestrator accumulates context
class OpusPlanner:
    def __init__(self):
        self.full_context = load_everything()  # ❌
        self.all_results = []  # ❌ Grows unbounded
        self.execution_history = []  # ❌ Never cleared
```

### ❌ Inline Context Passing
```python
# BAD: Pass context directly to agents
spawn_agent(
    task="Implement auth",
    context={
        "full_files": [...],  # ❌ 30K tokens
        "seed_rules": {...},   # ❌ 25K tokens
        "history": [...]       # ❌ 10K tokens
    }
)
```

### ❌ Result Accumulation
```python
# BAD: Store all results in orchestrator
class OpusPlanner:
    def execute_phase(self, phase):
        results = []
        for task in phase.tasks:
            result = execute_task(task)
            results.append(result)  # ❌ Accumulates

        self.all_results.extend(results)  # ❌ Never freed
```

### ❌ Detail-Level Decisions
```python
# BAD: Orchestrator makes low-level decisions
class OpusPlanner:
    def execute(self):
        # ❌ Should NOT decide which function to call
        if needs_jwt_validation():
            write_function("validate_jwt")

        # ✅ Should delegate entire task
        Task("sonnet-coder", "Implement JWT auth")
```

---



---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: ORCHESTRATOR_SEPARATION_PRINCIPLE.md](../ORCHESTRATOR_SEPARATION_PRINCIPLE.md)
