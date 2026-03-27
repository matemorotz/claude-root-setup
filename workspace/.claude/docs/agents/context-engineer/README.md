# Readme

**Source:** CONTEXT_ENGINEERING_DELEGATION.md
**Section:** ContextEngineer Agent

---

# ContextEngineer agent (separate context window)
class ContextEngineerAgent:
    def execute(self, plan_id, project_name, tasks):
        # 1. Load full context (User level)
        full_context = memory.user_level.get_project(project_name)

        # 2. Extract seed rules (Opus level)
        seed_rules = distill_user_to_opus(full_context)
        memory.opus_level.store_seed_rules(project_name, seed_rules)

        # 3. Engineer task contexts (Sonnet level)
        for task in tasks:
            task_context = distill_opus_to_sonnet(
                seed_rules,
                task,
                token_limit=10000
            )
            memory.sonnet_level.store_task_context(
                task["task_id"],
                task_context
            )

        # 4. Report completion
        return {
            "status": "success",
            "seed_rules_stored": True,
            "task_contexts_engineered": len(tasks),
            "ready_for_execution": True
        }

        # After return, ContextEngineer terminates
        # Context window freed (57,000 tokens released)
```

### Phase 4: OpusPlanner Verification

```python


---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: CONTEXT_ENGINEERING_DELEGATION.md](../CONTEXT_ENGINEERING_DELEGATION.md)
