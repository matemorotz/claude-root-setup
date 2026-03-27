# Agent Coordination

**Source:** AGENT_COORDINATION_PATTERN.md
**Section:** I/O Style Coordination

---

# Agent Coordination Pattern: Parent-Verifies-Child

**Document Version:** 1.0.0
**Created:** 2025-12-16
**Purpose:** Document the I/O style agent coordination pattern used in fractal orchestration

---

## Core Pattern

### Parent-Verifies-Child Architecture

When an agent spawns a subagent, the **parent agent's hook** is responsible for verifying the subagent's response:

```
┌─────────────────────────────────────────────────────────┐
│                   PARENT AGENT                           │
│  (e.g., OpusPlanner, SonnetCoder)                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Determine task needs subagent                        │
│  2. Package context + task + expected outcome            │
│  3. Spawn subagent (background)                          │
│  4. Continue other work (non-blocking)                   │
│  5. **Parent's hook verifies response**                  │
│  6. Validate against expected outcome                    │
│  7. Accept, retry, or escalate                           │
│                                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
                   Spawn subagent
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  SUBAGENT (Background)                   │
│  (e.g., SonnetCoder, HaikuExecutor)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Receive: context + task + expected outcome           │
│  2. Execute task independently                           │
│  3. Return: result                                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
                   Return result
                          ↓
┌─────────────────────────────────────────────────────────┐
│              PARENT'S HOOK (Verification)                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Check: Does result match expected outcome?              │
│    ✅ YES → Accept result, continue                      │
│    ❌ NO  → Retry or escalate                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## I/O Style Coordination

### Input Structure (Parent → Subagent)

```python
subagent_input = {
    "context": {
        # Engineered context from fractal memory
        # Only what subagent needs (not full project context)
        "task_context": task_context,      # From Sonnet level
        "seed_rules": relevant_seed_rules,  # Filtered patterns
        "files": file_references            # Specific files only
    },

    "task": {
        # What to do
        "action": "Implement user authentication",
        "step_id": "2.1",
        "agent_type": "sonnet-coder"
    },

    "expected_outcome": {
        # Verification criteria
        "type": "code_implementation",
        "validation": {
            "files_created": ["app/auth.py"],
            "tests_passing": True,
            "no_security_issues": True
        },
        "success_criteria": "JWT authentication working with tests"
    }
}

# Spawn background agent
agent_id = Task(
    subagent_type="sonnet-coder",
    prompt=format_task_prompt(subagent_input),
    run_in_background=True
)
```

### Output Structure (Subagent → Parent)

```python
subagent_output = {
    "task_id": "2.1",
    "status": "success" | "error" | "partial",

    "result": {
        # What was accomplished
        "files_created": ["app/auth.py"],
        "files_modified": ["app/main.py"],
        "tests_added": ["tests/test_auth.py"]
    },

    "validation_results": {
        # Self-reported validation
        "tests_passing": True,
        "linting_passed": True,
        "security_check": "no_issues"
    },

    "metadata": {
        "execution_time": "45s",
        "agent_type": "sonnet-coder",
        "context_tokens_used": 12500
    }
}
```

### Verification (Parent's Hook)

```python
def verify_subagent_response(expected_outcome, subagent_output):
    """
    Parent agent's hook verifies subagent response

    This is NOT done by a separate system - the parent agent
    is responsible for validation.
    """

    # 1. Check status
    if subagent_output["status"] == "error":
        return handle_error(subagent_output)

    # 2. Validate against expected outcome
    validation = expected_outcome["validation"]
    result = subagent_output["result"]

    checks = {
        "files_created": all(
            f in result["files_created"]
            for f in validation["files_created"]
        ),
        "tests_passing": subagent_output["validation_results"]["tests_passing"],
        "security": subagent_output["validation_results"]["security_check"] == "no_issues"
    }

    # 3. Decide action
    if all(checks.values()):
        return {"action": "accept", "result": subagent_output}
    elif checks["files_created"] and not checks["tests_passing"]:
        return {"action": "retry", "reason": "tests_failing", "retry_with": "fix_tests"}
    else:
        return {"action": "escalate", "reason": "validation_failed", "checks": checks}
```

---

## Agent Hierarchy and Verification

### OpusPlanner → SonnetCoder

**Scenario:** OpusPlanner orchestrates implementation

```python
# OpusPlanner spawns SonnetCoder for task implementation
agent_id = Task(
    subagent_type="sonnet-coder",
    prompt=f"""
    Implement authentication feature.

    Context: {task_context}
    Expected: JWT auth with tests passing
    Files: Create app/auth.py, tests/test_auth.py
    """,
    run_in_background=True
)

# OpusPlanner's hook verifies when SonnetCoder completes
result = TaskOutput(task_id=agent_id, block=True)

# Verification by OpusPlanner
if result.status == "success":
    # Check: Are required files present?
    # Check: Do tests pass?
    # Check: Matches expected outcome?
    if verify_implementation(result, expected_outcome):
        proceed_to_next_task()
    else:
        retry_with_clarification()
```

**Key Point:** OpusPlanner (parent) verifies SonnetCoder (child) work, not a separate verification agent.

### SonnetCoder → HaikuExecutor

**Scenario:** SonnetCoder breaks down task into steps

```python
# SonnetCoder spawns multiple HaikuExecutors for parallel steps
steps = [
    {"id": "2.1.1", "action": "Create auth.py skeleton"},
    {"id": "2.1.2", "action": "Add JWT token generation"},
    {"id": "2.1.3", "action": "Add password hashing"}
]

agent_ids = []
for step in steps:
    agent_id = Task(
        subagent_type="haiku-executor",
        prompt=f"""
        Execute step: {step['action']}
        Context: {minimal_step_context}
        Expected: Code snippet added to auth.py
        """,
        run_in_background=True
    )
    agent_ids.append(agent_id)

# SonnetCoder's hook verifies each HaikuExecutor
for agent_id in agent_ids:
    result = TaskOutput(task_id=agent_id, block=True)

    # Verification by SonnetCoder (parent)
    if not verify_step_output(result):
        # SonnetCoder decides: retry or fix manually
        handle_step_failure(result)
```

**Key Point:** SonnetCoder (parent) verifies HaikuExecutor (child) steps.

### OpusPlanner → SonnetDebugger

**Scenario:** Error escalation for debugging

```python
# SonnetCoder task failed, OpusPlanner escalates to debugger
agent_id = Task(
    subagent_type="sonnet-debugger",
    prompt=f"""
    Debug failed task: {failed_task_id}

    Error: {error_details}
    Context: {task_context + seed_rules}
    Expected: Root cause analysis + fix
    """,
    run_in_background=True
)

# OpusPlanner's hook verifies debugger solution
result = TaskOutput(task_id=agent_id, block=True)

# Verification by OpusPlanner
if result.status == "success":
    # Check: Is root cause identified?
    # Check: Is fix valid?
    # Check: Should this become a seed rule?
    if result.suggests_seed_rule:
        update_opus_level_seed_rules(result.seed_rule)

    # Re-attempt original task with fix
    retry_with_fix(failed_task_id, result.fix)
```

**Key Point:** OpusPlanner (parent) verifies SonnetDebugger (child) solution and decides whether to promote to seed rule.

---

## Context Passing Rules

### What Parent Passes to Subagent

1. **Engineered Context** (from fractal memory)
   - Parent reads from appropriate memory level
   - Distills to subagent's level
   - Passes only what's needed

2. **Task Specification**
   - Clear action description
   - Step ID for tracking
   - Agent type recommendation

3. **Expected Outcome**
   - Success criteria
   - Validation checklist
   - Deliverables list

### What Parent Does NOT Pass

❌ **Full project context** (too large, unnecessary)
❌ **Parent's internal state** (not relevant to subagent)
❌ **Other subagent results** (unless explicitly needed for this task)
❌ **User preferences** (unless task-specific)

### Example: OpusPlanner → SonnetCoder

```python
# OpusPlanner has full context (User level)
full_context = memory.user_level.get_project("api_server")  # 50,000 tokens

# OpusPlanner engineers task context (Sonnet level)
task_context = memory.distill_to_sonnet("api_server", task, distill_opus_to_sonnet)  # 8,000 tokens

# OpusPlanner passes ONLY task context to SonnetCoder
subagent_input = {
    "context": task_context,  # 8,000 tokens (not 50,000)
    "task": {...},
    "expected_outcome": {...}
}
```

**Benefit:** SonnetCoder operates efficiently without irrelevant context.

---

## Verification Strategies

### Accept Strategy

```python
def accept_result(subagent_output):
    """
    Result meets expected outcome, accept and continue.
    """
    # Store result in fractal memory
    memory.store_result(subagent_output)

    # Update progress
    update_progress(task_id, "completed")

    # Trigger dependent tasks
    trigger_dependencies(task_id)

    return "accepted"
```

### Retry Strategy

```python
def retry_with_clarification(subagent_output, reason):
    """
    Result partial or unclear, retry with more context.
    """
    # Analyze what went wrong
    failure_analysis = analyze_failure(subagent_output, reason)

    # Add clarifying context
    enhanced_context = {
        **original_context,
        "previous_attempt": subagent_output,
        "clarification": failure_analysis.clarification,
        "examples": failure_analysis.examples
    }

    # Retry with enhanced context
    retry_count = get_retry_count(task_id)
    if retry_count < MAX_RETRIES:
        spawn_subagent_with_context(enhanced_context)
    else:
        escalate_to_parent()
```

### Escalate Strategy

```python
def escalate_to_debugger(subagent_output):
    """
    Result failed validation, escalate to debugger.
    """
    # Package failure for debugging
    debug_input = {
        "failed_task": task_id,
        "subagent_output": subagent_output,
        "expected_outcome": expected_outcome,
        "context": task_context,
        "seed_rules": seed_rules  # For pattern matching
    }

    # Spawn debugger
    debugger_id = Task(
        subagent_type="sonnet-debugger",
        prompt=format_debug_prompt(debug_input),
        run_in_background=True
    )

    # Parent waits for debugger solution
    debug_result = TaskOutput(task_id=debugger_id, block=True)

    # Apply fix and retry original task
    if debug_result.status == "success":
        retry_with_fix(task_id, debug_result.fix)
```

---

## Hook Integration

### Pre-Task Hook (Subagent Spawning)

```bash
# pre-task.sh prepares subagent environment
AGENT_TYPE="$1"  # e.g., "sonnet-coder"
TASK_ID="$2"     # e.g., "2.1"

# Load context appropriate for this agent type
case "$AGENT_TYPE" in
    "sonnet-coder")
        # Load task context (engineered by parent)
        CONTEXT_FILE="$MEMORY_DIR/sonnet_level/task_contexts/${TASK_ID}.json"
        ;;
    "haiku-executor")
        # Load step context (engineered by parent)
        CONTEXT_FILE="$MEMORY_DIR/haiku_level/step_contexts/${TASK_ID}.json"
        ;;
esac

# Parent has already prepared this context
if [ -f "$CONTEXT_FILE" ]; then
    echo "✅ Loaded context prepared by parent agent"
fi
```

### Post-Task Hook (Parent Verification)

```bash
# post-task.sh stores result for parent verification
AGENT_TYPE="$1"
TASK_ID="$2"
STATUS="$3"
RESULT_FILE="$4"

# Store result at appropriate level
case "$AGENT_TYPE" in
    "sonnet-coder")
        # Store at Sonnet level for OpusPlanner to verify
        cp "$RESULT_FILE" "$MEMORY_DIR/sonnet_level/results/${TASK_ID}.json"
        ;;
    "haiku-executor")
        # Store at Haiku level for SonnetCoder to verify
        cp "$RESULT_FILE" "$MEMORY_DIR/haiku_level/step_results/${TASK_ID}.json"
        ;;
esac

# Parent agent's TaskOutput call will read from here
echo "✅ Result stored for parent verification"
```

### Parent Retrieves and Verifies

```python
# In parent agent (e.g., OpusPlanner)
def verify_subagent_completion(agent_id, expected_outcome):
    # Get result from TaskOutput
    result = TaskOutput(task_id=agent_id, block=True)

    # Result is in fractal memory (stored by post-task hook)
    task_result = memory.sonnet_level.get_result(result.task_id)

    # Parent's hook: Verify
    verification = verify_against_expected_outcome(
        task_result,
        expected_outcome
    )

    if verification.passed:
        return accept_result(task_result)
    elif verification.retryable:
        return retry_with_clarification(task_result, verification.reason)
    else:
        return escalate_to_debugger(task_result)
```

---

## Benefits of This Pattern

### 1. Clear Responsibility

- **Parent:** Plans, verifies, decides
- **Subagent:** Executes, reports
- **No ambiguity** about who validates what

### 2. Fractal Context Efficiency

- Parent engineers context for subagent
- Subagent receives minimal necessary context
- Token optimization (82-97% reduction)

### 3. Autonomous Operation

- Subagents run in background (non-blocking)
- Parent continues other work
- Parallel execution enabled

### 4. Error Handling

- Parent decides retry vs escalate
- Context preserved for debugging
- Seed rule learning from failures

### 5. Scalability

- Pattern works at any level (Opus→Sonnet, Sonnet→Haiku)
- Recursive structure (subagent can spawn sub-subagent)
- Maintains hierarchy

---

## Anti-Patterns (Avoid)

### ❌ Subagent Self-Verification

```python
# WRONG: Subagent declares own success without parent verification
def subagent_execute():
    result = implement_feature()

    # BAD: Subagent validates itself
    if self.validate(result):
        return {"status": "success", "result": result}
```

**Problem:** No independent verification, subagent may misjudge quality.

**Correct:** Subagent reports result, parent verifies.

### ❌ Central Verification Agent

```python
# WRONG: Separate "verifier" agent checks all work
def execute_plan():
    result = Task(subagent_type="sonnet-coder", ...)

    # BAD: Spawn separate verifier
    verification = Task(subagent_type="verifier", result=result, ...)
```

**Problem:** Parent loses control, extra agent overhead, unclear responsibility.

**Correct:** Parent agent verifies its own subagent's work.

### ❌ Passing Full Context

```python
# WRONG: Pass entire project context to subagent
subagent_input = {
    "context": full_project_context,  # 50,000 tokens
    "task": task
}
```

**Problem:** Wastes tokens, slows execution, irrelevant information.

**Correct:** Parent engineers minimal context for subagent.

### ❌ Fire-and-Forget

```python
# WRONG: Spawn subagent and never check result
agent_id = Task(subagent_type="haiku-executor", ..., run_in_background=True)
# No TaskOutput call, no verification
proceed_to_next_task()
```

**Problem:** No validation, errors undetected, broken workflow.

**Correct:** Parent always retrieves and verifies subagent result.

---

## Implementation Checklist

### Parent Agent Responsibilities

- [ ] Engineer appropriate context for subagent (use fractal memory)
- [ ] Define clear expected outcome with validation criteria
- [ ] Spawn subagent with Task tool (run_in_background=True)
- [ ] Retrieve result with TaskOutput (block=True when needed)
- [ ] Verify result against expected outcome
- [ ] Decide: accept, retry, or escalate
- [ ] Update fractal memory with verified result
- [ ] Trigger dependent tasks if verification passed

### Subagent Responsibilities

- [ ] Receive context + task + expected outcome
- [ ] Execute task independently
- [ ] Self-validate (basic checks only)
- [ ] Report result with metadata
- [ ] Do NOT assume success - parent decides

### Hook System Responsibilities

- [ ] Pre-task: Load context prepared by parent
- [ ] Post-task: Store result for parent retrieval
- [ ] Do NOT perform verification (that's parent's job)
- [ ] Enable parent to read result from fractal memory

---

## Example: Complete Flow

### Scenario: Add User Authentication

**OpusPlanner (Parent)**

```python
# 1. OpusPlanner plans task
task = {
    "task_id": "2.1",
    "action": "Implement JWT authentication",
    "agent_type": "sonnet-coder"
}

# 2. Engineer task context (Opus → Sonnet distillation)
task_context = memory.distill_to_sonnet("api_server", task, distill_opus_to_sonnet)
# Result: 8,000 tokens (from 50,000 full context)

# 3. Store task context for subagent
memory.sonnet_level.store_task_context("2.1", task_context)

# 4. Define expected outcome
expected_outcome = {
    "files_created": ["app/auth.py", "tests/test_auth.py"],
    "tests_passing": True,
    "jwt_working": True
}

# 5. Spawn SonnetCoder (subagent)
agent_id = Task(
    subagent_type="sonnet-coder",
    prompt=f"""
    Implement JWT authentication for API server.

    Task Context: Available in fractal memory (2.1)
    Expected: Create auth.py with JWT, tests passing
    """,
    run_in_background=True
)

# 6. OpusPlanner continues other work (non-blocking)
plan_next_tasks()

# 7. When ready, retrieve and verify
result = TaskOutput(task_id=agent_id, block=True)

# 8. OpusPlanner's verification hook
if result.status == "success":
    task_result = memory.sonnet_level.get_result("2.1")

    # Verify against expected outcome
    if verify_implementation(task_result, expected_outcome):
        print("✅ Authentication implementation verified")
        trigger_dependent_tasks("2.1")
    else:
        print("⚠️ Verification failed, retrying with clarification")
        retry_with_enhanced_context("2.1", task_result)
```

**SonnetCoder (Subagent)**

```python
# 1. Pre-task hook loads task context
# (Automatically done by hook system)

# 2. SonnetCoder reads task context from fractal memory
task_context = memory.sonnet_level.get_task_context("2.1")
# Receives: 8,000 tokens (engineered by OpusPlanner)

# 3. Execute implementation
result = {
    "files_created": ["app/auth.py", "tests/test_auth.py"],
    "implementation": "...",
    "tests_passing": True
}

# 4. Store result
memory.sonnet_level.store_result("2.1", result)

# 5. Report to parent
return {
    "task_id": "2.1",
    "status": "success",
    "result": result
}

# 6. Post-task hook stores result for parent
# (Automatically done by hook system)
```

**Result:** OpusPlanner (parent) verified SonnetCoder (subagent) work and accepted it.

---

## Summary

**Key Principle:** Parent-Verifies-Child

- Parent agent spawns subagent with context + task + expected outcome
- Subagent executes independently and reports result
- Parent's hook verifies result against expected outcome
- Parent decides: accept, retry, or escalate

**Benefits:**
- Clear responsibility (parent owns verification)
- Efficient context (fractal distillation)
- Autonomous execution (background agents)
- Error handling (retry/escalate strategies)
- Scalable (works at any hierarchy level)

**Integration:**
- Hooks prepare context (pre-task) and store results (post-task)
- Fractal memory enables efficient context passing
- TaskOutput enables parent to retrieve and verify
- Pattern works recursively (Opus→Sonnet→Haiku)

---

**Document Status:** Core coordination pattern documented
**Last Updated:** 2025-12-16


---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: AGENT_COORDINATION_PATTERN.md](../AGENT_COORDINATION_PATTERN.md)
