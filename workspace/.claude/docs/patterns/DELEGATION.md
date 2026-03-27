# Delegation

**Source:** ORCHESTRATOR_SEPARATION_PRINCIPLE.md
**Section:** Orchestrator Never Loads Details

---

## Key Principles

### 1. Orchestrator Never Loads Details
```python
# ❌ WRONG - Orchestrator loads everything
class OpusPlanner:
    def execute(self):
        full_context = load_full_context()  # 50K tokens
        seed_rules = extract_seed_rules(full_context)  # +25K
        task_contexts = engineer_all_tasks(seed_rules)  # +40K
        # Now at 115K tokens before even starting!

# ✅ CORRECT - Orchestrator delegates
class OpusPlanner:
    def execute(self):
        plan_id = create_high_level_plan()  # 2K tokens
        Task("context-engineer", f"Prepare {plan_id}")  # Delegate
        # OpusPlanner stays at 2K tokens
```

### 2. Memory References, Not Content
```python
# ❌ WRONG - Pass full context
spawn_agent(task="Write auth.py", context=full_50K_context)

# ✅ CORRECT - Pass memory reference
spawn_agent(task="Write auth.py", context_ref="sonnet_level/task_contexts/2.1")
# Agent reads from memory itself
```

### 3. Lightweight Summaries Up, Full Results to Memory
```python
# Agent execution
result = execute_task(task_id)

# Store full result in memory
memory.sonnet_level.store_result(task_id, result)  # 5K tokens

# Return lightweight summary to orchestrator
return {
    "task_id": task_id,
    "status": "success",
    "summary": "Created auth.py with JWT support"  # 50 tokens
}
```

### 4. Plans Live in Memory
```python
# OpusPlanner creates plan
plan = create_detailed_plan(user_request)

# Store in memory (NOT in context window)
memory.opus_level.store_plan(plan_id, plan)

# OpusPlanner keeps only reference
self.current_plan_id = plan_id  # 10 tokens
self.current_phase = "phase_2"  # 10 tokens

# Execution agents read plan from memory
```

---



---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: ORCHESTRATOR_SEPARATION_PRINCIPLE.md](../ORCHESTRATOR_SEPARATION_PRINCIPLE.md)
