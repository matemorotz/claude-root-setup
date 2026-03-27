# Phase 2: Agent Coordination & Execution Engine

**Status:** Planning
**Previous:** Phase 1 Complete ✅ (Execution strategies, task patterns, dependency graphs, result synthesis)
**Goal:** Build coordination logic and execution engine for the Fractal Orchestration System

---

## Overview

Phase 2 transforms our orchestration system from **architectural design** to **working implementation**. We're building the coordination layer that enables agents to work together intelligently.

**What Phase 1 Gave Us:**
- ✅ Agent specifications (what each agent does)
- ✅ Execution strategies (how to organize work)
- ✅ Task patterns (proven workflows)
- ✅ Dependency graphs (parallel optimization)
- ✅ Result synthesis (output aggregation)

**What Phase 2 Adds:**
- 🔄 Task-level hooks (agent lifecycle coordination)
- 🔄 Memory coordination (inter-agent communication)
- 🔄 Execution engine (plan processing and orchestration)
- 🔄 Testing framework (validation and quality)

---

## Phase 2 Components

### 1. Task-Level Hooks (Medium Priority)

**Purpose:** Coordinate agent lifecycle and enable inter-agent communication

**Files to Create:**
- `/root/software/.claude/hooks/pre-task.sh`
- `/root/software/.claude/hooks/post-task.sh`

**Pre-Task Hook Responsibilities:**
```bash
#!/bin/bash
# Pre-task hook: Prepare agent for execution

TASK_ID="$1"
AGENT_TYPE="$2"
PLAN_FILE="$3"

# 1. Restore agent context from memory
if [ -f ".claude/memory/${AGENT_TYPE}_context.json" ]; then
  cat ".claude/memory/${AGENT_TYPE}_context.json"
fi

# 2. Load task-specific context from plan
# Extract engineered context for this specific task

# 3. Initialize agent state
mkdir -p ".claude/state/${AGENT_TYPE}"
echo "${TASK_ID}" > ".claude/state/${AGENT_TYPE}/current_task"

# 4. Notify dependencies (if any waiting)
# Check if other agents are blocked on this task starting
```

**Post-Task Hook Responsibilities:**
```bash
#!/bin/bash
# Post-task hook: Store results and notify dependencies

TASK_ID="$1"
AGENT_TYPE="$2"
RESULT="$3"
STATUS="$4"

# 1. Store results in memory
mkdir -p ".claude/memory/task_results"
echo "${RESULT}" > ".claude/memory/task_results/${TASK_ID}.json"

# 2. Update plan progress (via SonnetTracker)
# Mark task as completed in execution plan

# 3. Notify downstream agents
# Trigger dependent tasks if all prerequisites complete

# 4. Store agent learnings
# What patterns worked? What failed?
```

**Integration Points:**
- Called by execution engine before/after agent invocation
- Reads/writes to `.claude/memory/` directory
- Updates execution plan status
- Enables agent-to-agent coordination

---

### 2. Memory Coordination (High Priority)

**Purpose:** Enable agents to share context and coordinate work

**Architecture:**
```
.claude/memory/
├── agent_contexts/          # Per-agent persistent context
│   ├── opus-planner.json
│   ├── sonnet-coder.json
│   └── haiku-executor.json
├── task_results/            # Completed task outputs
│   ├── task_1.1.json
│   └── task_1.2.json
├── shared_state/            # Cross-agent shared data
│   ├── discovered_patterns.json
│   └── project_insights.json
└── coordination/            # Agent coordination metadata
    ├── waiting_agents.json  # Blocked on dependencies
    └── active_tasks.json    # Currently executing
```

**Memory Operations:**

**Write Context (OpusPlanner):**
```json
{
  "agent": "sonnet-coder",
  "task_id": "1.2",
  "engineered_context": {
    "project": "peti",
    "tech_stack": ["FastAPI", "SQLAlchemy"],
    "patterns": {"auth": "JWT with bcrypt"},
    "essential_files": [
      {"path": "app/auth.py", "sections": ["login", "verify_token"]},
      {"path": "app/models.py", "sections": ["User"]}
    ],
    "inline_context": "Add password reset endpoint following existing auth patterns"
  },
  "timestamp": "2025-12-16T20:00:00Z"
}
```

**Read Context (SonnetCoder):**
```python
# Agent reads its engineered context
with open(f".claude/memory/agent_contexts/{agent_type}.json") as f:
    context = json.load(f)

# Agent receives ONLY task-oriented context, not full project
# OpusPlanner already distilled it down
```

**Share Results (HaikuExecutor):**
```json
{
  "task_id": "1.1",
  "status": "completed",
  "output": "Created auth endpoint at app/routes/auth.py",
  "files_modified": ["app/routes/auth.py", "app/main.py"],
  "patterns_used": ["JWT authentication", "bcrypt password hashing"],
  "timestamp": "2025-12-16T20:05:00Z"
}
```

**Integration with Existing Memory System:**
- Use `/root/software/memory_system/` MCP server for persistence
- Store coordination metadata in local `.claude/memory/`
- OpusPlanner decides what context to share (fractal principle)

---

### 3. Execution Engine (High Priority)

**Purpose:** Process execution plans and orchestrate agent coordination

**File:** `/root/software/.claude/scripts/execute-plan.py`

**Core Responsibilities:**

**a) Plan Loading:**
```python
def load_execution_plan(plan_path: Path) -> Dict:
    """Load and validate execution plan against schema"""
    with open(plan_path) as f:
        plan = json.load(f)

    # Validate against execution-plan.schema.json
    validate_plan(plan)

    return plan
```

**b) Dependency Resolution:**
```python
def resolve_dependencies(plan: Dict) -> List[List[str]]:
    """Convert dependency graph to execution batches

    Returns:
        List of step batches that can run in parallel
        Each batch contains step IDs with no interdependencies
    """
    dependencies = plan.get("dependencies", {})

    # Topological sort to determine execution order
    # Group steps that can run in parallel

    return execution_batches
```

**c) Agent Invocation:**
```python
async def execute_step(step: Dict, agent_context: Dict):
    """Execute a single step with appropriate agent

    1. Run pre-task hook
    2. Invoke agent via Task tool
    3. Wait for completion
    4. Run post-task hook
    5. Store results
    """
    agent_type = step["agent_type"]

    # Pre-task hook
    subprocess.run([".claude/hooks/pre-task.sh",
                   step["step_id"], agent_type, plan_path])

    # Invoke agent (via Claude Code Task tool)
    result = await invoke_agent(agent_type, step, agent_context)

    # Post-task hook
    subprocess.run([".claude/hooks/post-task.sh",
                   step["step_id"], agent_type,
                   json.dumps(result), result["status"]])

    return result
```

**d) Parallel Execution:**
```python
async def execute_batch_parallel(batch: List[str], plan: Dict):
    """Execute multiple steps in parallel"""
    tasks = []

    for step_id in batch:
        step = get_step(plan, step_id)
        task = asyncio.create_task(execute_step(step, context))
        tasks.append(task)

    # Wait for all parallel tasks
    results = await asyncio.gather(*tasks)

    return results
```

**e) Strategy Selection:**
```python
def select_execution_strategy(plan: Dict) -> str:
    """Determine optimal execution strategy

    Strategies from Phase 1:
    - parallel: All independent tasks simultaneously
    - sequential: Strict ordered execution
    - adaptive: Dynamic based on progress
    - balanced: Mix of parallel and sequential (default)
    """
    # Check plan metadata for strategy hint
    strategy = plan.get("execution_strategy", "balanced")

    # Analyze dependency graph
    if has_no_dependencies(plan):
        return "parallel"
    elif has_strict_ordering(plan):
        return "sequential"

    return strategy
```

**f) Progress Tracking:**
```python
def update_plan_progress(plan_path: Path, step_id: str, status: str):
    """Update execution plan with step progress"""
    plan = load_plan(plan_path)

    # Find step and update status
    update_step_status(plan, step_id, status)

    # Save updated plan
    save_plan(plan_path, plan)

    # Trigger SonnetTracker for progress report
```

**Main Execution Loop:**
```python
async def execute_plan(plan_path: Path):
    """Main execution engine"""
    plan = load_execution_plan(plan_path)
    strategy = select_execution_strategy(plan)

    if strategy == "parallel":
        # Execute all steps in parallel
        await execute_all_parallel(plan)

    elif strategy == "sequential":
        # Execute steps in order
        for step in get_all_steps(plan):
            await execute_step(step, context)

    elif strategy == "balanced":
        # Execute in batches (default)
        batches = resolve_dependencies(plan)
        for batch in batches:
            await execute_batch_parallel(batch, plan)

    elif strategy == "adaptive":
        # Dynamic execution with progress monitoring
        await execute_adaptive(plan)
```

---

### 4. Testing Framework (Medium Priority)

**Purpose:** Validate orchestration system works end-to-end

**Test Scenarios:**

**a) Simple Sequential Task:**
```yaml
test: "Simple three-step sequential"
plan:
  - step_1: "Create file" (haiku-executor)
  - step_2: "Modify file" (haiku-executor) [depends on step_1]
  - step_3: "Verify file" (sonnet-tracker) [depends on step_2]
validation:
  - All steps complete in order
  - File exists and contains expected content
  - No parallel execution
```

**b) Parallel Execution:**
```yaml
test: "Parallel independent tasks"
plan:
  - step_1a: "Create fileA" (haiku-executor)
  - step_1b: "Create fileB" (haiku-executor)
  - step_1c: "Create fileC" (haiku-executor)
  - step_2: "Combine files" (sonnet-coder) [depends on all step_1*]
validation:
  - Steps 1a, 1b, 1c execute simultaneously
  - Step 2 waits for all to complete
  - Total time < sequential execution
```

**c) Error Handling:**
```yaml
test: "Error escalation to debugger"
plan:
  - step_1: "Task that will fail" (haiku-executor)
  - step_2: "Fix the error" (sonnet-debugger) [triggered by step_1 failure]
validation:
  - Haiku fails with error
  - SonnetDebugger automatically invoked
  - Solution provided and implemented
```

**d) Context Engineering:**
```yaml
test: "Fractal context distillation"
plan:
  - step_1: OpusPlanner analyzes 50K token project
  - step_2: SonnetCoder receives 10K engineered context
  - step_3: HaikuExecutor receives <2K minimal context
validation:
  - OpusPlanner holds full context
  - Each agent receives only task-relevant info
  - Token counts within limits
  - Work completes successfully
```

---

## Implementation Order

### Week 1: Foundation
1. **Day 1-2:** Memory coordination structure
   - Create `.claude/memory/` directories
   - Implement basic read/write operations
   - Test agent context storage/retrieval

2. **Day 3-4:** Task-level hooks
   - Implement pre-task.sh
   - Implement post-task.sh
   - Test hook triggers manually

3. **Day 5:** Integration testing
   - Test hooks + memory together
   - Verify agent lifecycle works

### Week 2: Execution Engine
1. **Day 1-2:** Plan loading and validation
   - Load plans from JSON
   - Validate against schema
   - Parse dependencies

2. **Day 3-4:** Execution logic
   - Implement sequential execution
   - Implement parallel execution
   - Strategy selection

3. **Day 5:** Agent invocation
   - Integrate with Task tool
   - Test end-to-end execution

### Week 3: Testing & Refinement
1. **Day 1-2:** Test scenarios
   - Simple sequential
   - Parallel execution
   - Error handling

2. **Day 3-4:** Performance optimization
   - Token usage monitoring
   - Execution time tracking
   - Memory efficiency

3. **Day 5:** Documentation
   - Update ORCHESTRATION_STRATEGIES.md
   - Create EXECUTION_ENGINE.md
   - Update README.md

---

## Success Criteria

### Memory Coordination ✅
- [ ] Agents can write context to memory
- [ ] Agents can read engineered context
- [ ] Task results stored and retrievable
- [ ] Shared state accessible across agents

### Task Hooks ✅
- [ ] Pre-task hook runs before agent execution
- [ ] Post-task hook runs after completion
- [ ] Hooks can access plan and context
- [ ] Hooks update coordination metadata

### Execution Engine ✅
- [ ] Can load and validate execution plans
- [ ] Resolves dependencies correctly
- [ ] Executes parallel tasks simultaneously
- [ ] Executes sequential tasks in order
- [ ] Handles errors and escalates to debugger
- [ ] Tracks progress and updates plan

### End-to-End Testing ✅
- [ ] Simple sequential task completes
- [ ] Parallel tasks run simultaneously
- [ ] Error handling triggers debugger
- [ ] Context engineering works (token limits respected)
- [ ] Result synthesis aggregates outputs

---

## Questions to Resolve

1. **Memory System Integration:**
   - Use existing `/root/software/memory_system/` MCP server?
   - Or lightweight local `.claude/memory/` only?
   - Decision: Start local, integrate MCP later

2. **Agent Invocation:**
   - Direct subprocess calls?
   - Claude Code Task tool API?
   - Decision: Use Task tool for consistency

3. **Execution Mode:**
   - Synchronous (wait for each step)?
   - Asynchronous (parallel processing)?
   - Decision: Async with asyncio for parallel support

4. **Error Recovery:**
   - Automatic retry logic?
   - Manual intervention required?
   - Decision: SonnetDebugger analyzes, user approves fix

---

## Next Steps

**Immediate:**
1. Create `.claude/memory/` directory structure
2. Implement basic memory read/write functions
3. Draft pre-task.sh and post-task.sh hooks

**This Session:**
- Review and approve Phase 2 plan
- Start with highest priority: Memory coordination OR execution engine
- Create first test scenario

**Next Session:**
- Complete chosen component
- Move to next priority component
- Begin integration testing

---

**Status:** Planning complete, awaiting approval to begin implementation
**Estimated Effort:** 3 weeks for full Phase 2 (can be done incrementally)
**Dependencies:** Phase 1 complete ✅
