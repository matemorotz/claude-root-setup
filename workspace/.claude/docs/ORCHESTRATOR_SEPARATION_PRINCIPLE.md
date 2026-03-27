# Orchestrator Separation Principle

**Core Principle:** High-level orchestrator stays lightweight, focused on control flow and verification. Detailed context lives in memory.

**Created:** 2025-12-16
**Status:** Foundational Architecture Pattern

---

## The Problem

**Traditional orchestration (WRONG):**
```
OpusPlanner Context Window:
├── Long-term goals (1K tokens)
├── Full project context (50K tokens)
├── Seed rules (25K tokens)
├── Plan details (10K tokens)
├── Task contexts for all tasks (30K tokens)
├── Execution results (15K tokens)
├── Problem-solving history (10K tokens)
└── TOTAL: 141K tokens ❌ OVERFLOW + LOSS OF FOCUS
```

OpusPlanner becomes:
- ❌ Overloaded with details
- ❌ Loses sight of long-term goals
- ❌ Context window filled with task minutiae
- ❌ Can't maintain strategic oversight

---

## The Solution: Separation of Concerns

### OpusPlanner (High-Level Orchestrator)
**Role:** Control, verification, problem-solving coordination
**Context Window:** 5-25K tokens (stays lightweight)

```
OpusPlanner Responsibilities:
┌─────────────────────────────────────────────┐
│ 1. CONTROL FLOW                             │
│    - Maintain long-term goals               │
│    - Track plan progress                    │
│    - Decide what happens next               │
│                                             │
│ 2. VERIFICATION                             │
│    - Verify subagent results                │
│    - Check against expected outcomes        │
│    - Validate plan phase completion         │
│                                             │
│ 3. PROBLEM-SOLVING COORDINATION             │
│    - Detect blockers                        │
│    - Spawn debugger agents                  │
│    - Re-plan when needed                    │
│                                             │
│ 4. USER COMMUNICATION                       │
│    - Report progress                        │
│    - Escalate decisions                     │
│    - Request clarifications                 │
└─────────────────────────────────────────────┘

OpusPlanner NEVER loads:
❌ Full project context
❌ Seed rules (reads from memory reference only)
❌ Task implementation details
❌ Step-by-step instructions
❌ File contents
```

### Memory System (Knowledge Repository)
**Role:** Store detailed context, plans, and execution state
**Storage:** File-based hierarchy (`.claude/memory/`)

```
Memory Hierarchy:
┌─────────────────────────────────────────────┐
│ user_level/                                 │
│   └── Full project context (unlimited)      │
│                                             │
│ opus_level/                                 │
│   └── Seed rules (10-50K tokens)            │
│                                             │
│ sonnet_level/                               │
│   └── Task contexts (5-15K tokens each)     │
│                                             │
│ haiku_level/                                │
│   └── Step contexts (<2K tokens each)       │
└─────────────────────────────────────────────┘

Execution agents READ from memory directly
OpusPlanner does NOT pass context
```

### Specialist Agents (Context Handlers)
**Role:** Load, process, and operate on detailed context
**Models:** Sonnet (tasks), Haiku (steps), specialized context engineers

```
Specialist Agent Workflow:
1. Spawned by OpusPlanner with task ID
2. Reads context from memory (agent_type → memory_level)
3. Executes task with full context
4. Stores result in memory
5. Returns lightweight summary to OpusPlanner
```

---

## Orchestration Workflow Pattern

### Verification → Execution → Verification Loop

```python
class OpusPlannerAgent:
    def orchestrate(self, user_request):
        # 1. INITIAL PLANNING (lightweight)
        long_term_goal = self.define_goal(user_request)  # 500 tokens
        plan_phases = self.create_plan_phases(long_term_goal)  # 2K tokens

        # Store plan in memory (OpusPlanner does NOT keep it)
        memory.opus_level.store_plan(plan_id, plan_phases)

        # 2. DELEGATE CONTEXT ENGINEERING (spawn & forget)
        context_task = Task(
            subagent_type="context-engineer",
            prompt=f"Engineer contexts for plan: {plan_id}",
            run_in_background=True
        )

        # OpusPlanner continues (does NOT wait)

        # 3. EXECUTION LOOP (lightweight control)
        for phase in plan_phases:
            # VERIFICATION (check if ready)
            if not self.verify_phase_ready(phase):
                self.handle_blocker(phase)
                continue

            # EXECUTION (delegate to specialists)
            results = self.execute_phase_parallel(phase)

            # VERIFICATION (check results)
            verification = self.verify_results(results, phase.expected_outcomes)

            if verification.status == "failed":
                # PROBLEM-SOLVING (spawn debugger)
                self.spawn_debugger(phase, verification.issues)

                # VERIFICATION (check if fixed)
                retry_results = self.retry_phase(phase)
                verification = self.verify_results(retry_results, phase.expected_outcomes)

            if verification.status == "success":
                # Update progress (lightweight)
                self.mark_phase_complete(phase)
            else:
                # Escalate to user
                user_decision = self.escalate(phase, verification)
                self.apply_decision(user_decision)

        # 4. FINAL VERIFICATION
        return self.verify_long_term_goal_achieved(long_term_goal)

    def verify_phase_ready(self, phase):
        """Lightweight check - no context loading"""
        dependencies_met = all(
            memory.opus_level.is_phase_complete(dep)
            for dep in phase.dependencies
        )
        return dependencies_met

    def execute_phase_parallel(self, phase):
        """Spawn agents, get lightweight summaries back"""
        task_ids = []
        for task in phase.tasks:
            # Spawn agent (agent reads context from memory)
            task_id = Task(
                subagent_type=task.agent_type,
                prompt=f"Execute task {task.id} (context in memory)",
                run_in_background=True
            )
            task_ids.append(task_id)

        # Collect lightweight summaries (NOT full results)
        summaries = [
            TaskOutput(tid, block=True).get_summary()
            for tid in task_ids
        ]

        return summaries  # Lightweight: 100-500 tokens per task

    def verify_results(self, results, expected_outcomes):
        """Lightweight verification - just pass/fail + issues"""
        verification = {
            "status": "success",
            "issues": []
        }

        for result, expected in zip(results, expected_outcomes):
            if not self.matches_expectation(result.summary, expected):
                verification["status"] = "failed"
                verification["issues"].append({
                    "task_id": result.task_id,
                    "expected": expected,
                    "got": result.summary
                })

        return verification

    def spawn_debugger(self, phase, issues):
        """Problem-solving coordination"""
        Task(
            subagent_type="sonnet-debugger",
            prompt=f"Debug phase {phase.id}, issues: {issues}",
            run_in_background=True
        )
```

---

## What Lives Where

### OpusPlanner Context (5-25K tokens)
```json
{
  "long_term_goal": "Implement user authentication system",
  "current_phase": "phase_2",
  "plan_phases": [
    {
      "phase_id": "phase_1",
      "status": "complete",
      "tasks": ["1.1", "1.2", "1.3"]
    },
    {
      "phase_id": "phase_2",
      "status": "in_progress",
      "tasks": ["2.1", "2.2"]
    }
  ],
  "recent_verification": {
    "phase": "phase_1",
    "status": "success",
    "timestamp": "2025-12-16T19:30:00Z"
  },
  "active_problems": []
}
```

**Total:** ~3K tokens (lightweight control state)

### Memory System (Detailed Context)
```json
{
  "user_level/projects/auth_system.json": {
    "full_context": "50,000 tokens of complete project knowledge"
  },

  "opus_level/seed_rules/auth_system.json": {
    "seed_rules": "25,000 tokens of distilled patterns"
  },

  "opus_level/plans/auth_system_plan.json": {
    "phases": "10,000 tokens of detailed plan"
  },

  "sonnet_level/task_contexts/2.1.json": {
    "task_context": "8,000 tokens of engineered context for task 2.1"
  },

  "haiku_level/step_contexts/2.1.1.json": {
    "step_context": "1,500 tokens for atomic step"
  }
}
```

**Total:** 94,500 tokens stored in memory (NOT in OpusPlanner window)

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

## Verification Patterns

### Expected Outcome Verification
```python
# OpusPlanner defines expectations (lightweight)
expected_outcome = {
    "task_id": "2.1",
    "type": "code_implementation",
    "validation": {
        "files_created": ["app/auth.py"],
        "tests_passing": True,
        "imports_valid": True
    }
}

# Agent executes, returns summary
result_summary = {
    "task_id": "2.1",
    "files_created": ["app/auth.py"],
    "tests_passing": True,
    "imports_valid": True
}

# OpusPlanner verifies (lightweight comparison)
if matches(result_summary, expected_outcome):
    mark_complete()
else:
    spawn_debugger()
```

### Progressive Verification
```python
# Phase-level verification
for phase in plan_phases:
    # Pre-phase verification
    if not dependencies_met(phase):
        handle_blocker()
        continue

    # Execute phase
    results = execute_phase(phase)

    # Post-phase verification
    if not phase_goals_met(results):
        problem_solve(phase, results)
        results = retry_phase(phase)

    # Final verification
    assert phase_goals_met(results)
    mark_phase_complete(phase)
```

---

## Problem-Solving Coordination

### Lightweight Problem Detection
```python
class OpusPlanner:
    def detect_problems(self, phase_results):
        """Lightweight problem detection from summaries"""
        problems = []

        for result in phase_results:
            if result.status == "failed":
                problems.append({
                    "type": "execution_failure",
                    "task_id": result.task_id,
                    "error": result.error_summary  # Lightweight
                })

            elif result.tests_passing == False:
                problems.append({
                    "type": "test_failure",
                    "task_id": result.task_id
                })

        return problems

    def coordinate_problem_solving(self, problems):
        """Spawn debuggers, don't solve yourself"""
        for problem in problems:
            Task(
                subagent_type="sonnet-debugger",
                prompt=f"Debug {problem.task_id}: {problem.type}",
                run_in_background=True
            )

        # OpusPlanner does NOT load code to debug
        # Debugger agents handle that
```

---

## Benefits of Separation

### Orchestrator Benefits
- ✅ **Focused:** Maintains long-term goals, not lost in details
- ✅ **Lightweight:** 5-25K tokens, never overflows
- ✅ **Strategic:** Can see forest, not just trees
- ✅ **Responsive:** Fast decision-making (no huge context)
- ✅ **Scalable:** Can orchestrate unlimited complexity

### Execution Benefits
- ✅ **Context-Rich:** Agents get full context they need
- ✅ **Specialized:** Each agent sees only relevant level
- ✅ **Parallel:** Multiple agents work simultaneously
- ✅ **Efficient:** No context duplication

### System Benefits
- ✅ **Inspectable:** All state visible in files
- ✅ **Debuggable:** Can trace through memory files
- ✅ **Recoverable:** Persistent state survives crashes
- ✅ **Auditable:** Complete execution history

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

## Correct Orchestration Pattern

```python
class OpusPlannerAgent:
    """
    High-level orchestrator - maintains goals, delegates work

    Context window stays 5-25K tokens:
    - Long-term goals (500 tokens)
    - Plan phase overview (2K tokens)
    - Current verification state (1K tokens)
    - Recent problem summaries (2K tokens)
    - User communication (1K tokens)

    NEVER loads:
    - Full project context
    - Seed rules (beyond references)
    - Task implementation details
    - File contents
    - Execution history (beyond recent summaries)
    """

    def execute(self, user_request):
        # 1. Define long-term goal (lightweight)
        goal = self.define_goal(user_request)  # 500 tokens

        # 2. Create high-level plan (phases only)
        phases = self.create_plan_phases(goal)  # 2K tokens

        # 3. Store detailed plan in memory (NOT in context)
        memory.opus_level.store_plan(self.plan_id, phases)

        # 4. Delegate context engineering (background)
        Task("context-engineer", f"Prepare {self.plan_id}", run_in_background=True)

        # 5. Execute phases (verification loop)
        for phase in phases:
            # Verification → Execution → Verification
            if self.verify_phase_ready(phase):
                results = self.execute_phase(phase)  # Spawns agents

                if self.verify_phase_complete(results, phase):
                    self.mark_phase_complete(phase)
                else:
                    self.coordinate_problem_solving(phase, results)

        # 6. Final verification
        return self.verify_goal_achieved(goal)
```

---

## Summary

**Orchestrator Separation Principle:**
- **Orchestrator:** Control flow, verification, problem-solving coordination (lightweight)
- **Memory:** Detailed context, plans, execution state (file-based)
- **Agents:** Execute with full context, return lightweight summaries

**Result:** Scalable orchestration that maintains strategic focus without context overflow.

---

**Status:** ✅ Foundational pattern for fractal orchestration system
**Related:** CONTEXT_ENGINEERING_DELEGATION.md, AGENT_COORDINATION_PATTERN.md
