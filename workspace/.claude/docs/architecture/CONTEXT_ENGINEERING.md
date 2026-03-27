# Context Engineering

**Source:** CONTEXT_ENGINEERING_DELEGATION.md
**Section:** Context Engineering Delegation

---

# Context Engineering Delegation Pattern

**Document Version:** 1.0.0
**Created:** 2025-12-16
**Purpose:** Prevent context accumulation in orchestrators by delegating context engineering

---

## Problem Statement

### Context Accumulation in Orchestrators

**Without Delegation:**

```
OpusPlanner's Context Window:
┌─────────────────────────────────────────────────────┐
│ Initial planning conversation       (5,000 tokens)  │
│ + Full project context (User level) (50,000 tokens) │
│ + Seed rules extraction            (25,000 tokens)  │
│ + Task context engineering #1       (8,000 tokens)  │
│ + Task context engineering #2       (8,000 tokens)  │
│ + Task context engineering #3       (8,000 tokens)  │
│ + Results from task 1               (5,000 tokens)  │
│ + Results from task 2               (5,000 tokens)  │
│ + Progress tracking                 (3,000 tokens)  │
│ + User communication                (2,000 tokens)  │
├─────────────────────────────────────────────────────┤
│ TOTAL: 119,000 tokens ❌ CONTEXT OVERFLOW            │
└─────────────────────────────────────────────────────┘
```

**Problem:** OpusPlanner accumulates everything and loses focus.

---

## Solution: Delegation Pattern

### OpusPlanner Role (Focused)

**Responsibilities:**
1. ✅ **Control** - Orchestrate workflow, spawn agents
2. ✅ **Architecture** - Make high-level decisions
3. ✅ **User Communication** - Report progress, ask questions
4. ❌ **NOT Context Engineering** - Delegate to specialist

**Context Window (Minimal):**
```
OpusPlanner's Context Window:
┌─────────────────────────────────────────────────────┐
│ Initial planning conversation       (5,000 tokens)  │
│ + High-level architecture plan     (10,000 tokens)  │
│ + Task dependencies graph           (2,000 tokens)  │
│ + Progress summary                  (1,000 tokens)  │
│ + User communication                (2,000 tokens)  │
├─────────────────────────────────────────────────────┤
│ TOTAL: 20,000 tokens ✅ FOCUSED                      │
└─────────────────────────────────────────────────────┘
```

### Context Engineering Agent (Specialized)

**New Agent:** `ContextEngineer`
**Purpose:** Handle all knowledge base filtering and context building

**Responsibilities:**
1. Load full project context (User level)
2. Extract seed rules (Opus level)
3. Engineer task contexts (Sonnet level)
4. Build step contexts (Haiku level)
5. Store in fractal memory
6. Report completion to OpusPlanner

**Context Window:**
```
ContextEngineer's Context Window:
┌─────────────────────────────────────────────────────┐
│ Full project context (User level)  (50,000 tokens)  │
│ + Distillation algorithms           (5,000 tokens)  │
│ + Current task specification        (2,000 tokens)  │
├─────────────────────────────────────────────────────┤
│ TOTAL: 57,000 tokens ✅ SPECIALIZED                  │
└─────────────────────────────────────────────────────┘
```

After completion, ContextEngineer **terminates** - context is freed.

---

## Workflow: OpusPlanner → ContextEngineer

### Phase 1: Initial Planning (OpusPlanner)

```
User Request
    ↓
OpusPlanner analyzes
    ↓
Creates high-level plan:
    - Architecture decisions
    - Task breakdown
    - Dependency graph
    - Success criteria
    ↓
Stores plan skeleton (minimal)
```

**OpusPlanner Output:**
```json
{
  "plan_id": "feature-001",
  "architecture": {
    "approach": "Add JWT authentication",
    "tech_stack": ["FastAPI", "bcrypt", "PyJWT"],
    "files_to_modify": ["app/auth.py", "app/main.py"]
  },
  "tasks": [
    {
      "task_id": "1.1",
      "description": "Create auth module",
      "dependencies": []
    },
    {
      "task_id": "1.2",
      "description": "Add JWT endpoints",
      "dependencies": ["1.1"]
    }
  ],
  "context_engineering_needed": true  // Flag: need ContextEngineer
}
```

### Phase 2: Delegate Context Engineering

```python
# OpusPlanner delegates context engineering
context_engineer_id = Task(
    subagent_type="context-engineer",
    prompt=f"""
    Engineer contexts for plan: {plan_id}

    Project: {project_name}
    Tasks: {tasks}

    Workflow:
    1. Load full project context from User level
    2. Extract seed rules → Opus level
    3. For each task: Engineer task context → Sonnet level
    4. Store all in fractal memory
    5. Report completion

    Expected: Contexts ready for {len(tasks)} tasks
    """,
    run_in_background=True,
    model="haiku"  # Fast, focused task
)

# OpusPlanner continues planning other aspects
# (Does NOT wait for context engineering)
```

**Key Point:** OpusPlanner does NOT load full project context. ContextEngineer handles it.

### Phase 3: ContextEngineer Execution

```python
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
# OpusPlanner verifies context engineering complete
result = TaskOutput(task_id=context_engineer_id, block=True)

if result.status == "success":
    # Contexts ready in fractal memory
    # OpusPlanner can now spawn execution agents

    for task in tasks:
        # Each execution agent reads engineered context
        # OpusPlanner does NOT need to pass it
        spawn_execution_agent(task)
```

---

## Detailed Workflow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   USER REQUEST                            │
│  "Add user authentication with JWT"                       │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 1: OpusPlanner - Initial Planning                  │
├──────────────────────────────────────────────────────────┤
│ OpusPlanner analyzes request                             │
│ Creates architecture plan                                │
│ Breaks down into tasks                                   │
│ Creates dependency graph                                 │
│ Stores plan skeleton (minimal, ~10K tokens)              │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 2: OpusPlanner - Delegate Context Engineering      │
├──────────────────────────────────────────────────────────┤
│ OpusPlanner spawns ContextEngineer (background)          │
│ Passes: plan_id, project_name, tasks list               │
│ Does NOT load full project context                       │
│ Continues other planning work                            │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 3: ContextEngineer - Knowledge Processing          │
│ (Separate Context Window)                                │
├──────────────────────────────────────────────────────────┤
│ 1. Load full project context (User level)                │
│    → 50,000 tokens                                       │
│                                                           │
│ 2. Extract seed rules (Opus level)                       │
│    → Patterns, conventions, architecture                 │
│    → 25,000 tokens                                       │
│    → Store in fractal memory                             │
│                                                           │
│ 3. Engineer task contexts (Sonnet level)                 │
│    → For each task: filter relevant patterns             │
│    → 8,000 tokens per task                               │
│    → Store in fractal memory                             │
│                                                           │
│ 4. Report completion to OpusPlanner                      │
│                                                           │
│ 5. ContextEngineer terminates                            │
│    → 57,000 token context freed ✅                        │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 4: OpusPlanner - Verification                      │
├──────────────────────────────────────────────────────────┤
│ OpusPlanner receives completion notification             │
│ Verifies contexts stored in fractal memory               │
│ Ready to spawn execution agents                          │
│ OpusPlanner context: Still ~20K tokens ✅                 │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 5: OpusPlanner - Spawn Execution Agents            │
├──────────────────────────────────────────────────────────┤
│ For each task:                                           │
│   - Spawn SonnetCoder/HaikuExecutor                      │
│   - Agent reads engineered context from memory           │
│   - OpusPlanner does NOT pass context                    │
│   - OpusPlanner only passes task_id                      │
│                                                           │
│ Execution agents work independently                      │
│ OpusPlanner monitors progress (minimal context)          │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ PHASE 6: OpusPlanner - Result Verification               │
├──────────────────────────────────────────────────────────┤
│ Agents complete and report results                       │
│ OpusPlanner verifies against expected outcomes           │
│ Communicates success to user                             │
│ OpusPlanner context: ~20K tokens throughout ✅            │
└──────────────────────────────────────────────────────────┘
```

---

## Agent Specification: ContextEngineer

### Overview

**Agent Type:** `context-engineer`
**Model:** Haiku (fast, focused task)
**Purpose:** Specialized knowledge base processing and context engineering
**Lifecycle:** Spawn → Execute → Terminate (single-use)

### Inputs

```python
{
    "plan_id": "feature-001",
    "project_name": "api_server",
    "tasks": [
        {
            "task_id": "1.1",
            "description": "Create auth module",
            "agent_type": "sonnet-coder"
        },
        {
            "task_id": "1.2",
            "description": "Add JWT endpoints",
            "agent_type": "haiku-executor"
        }
    ],
    "options": {
        "include_step_contexts": False,  // Only if tasks have steps
        "seed_rule_max_tokens": 25000,
        "task_context_max_tokens": 10000
    }
}
```

### Workflow

```python
class ContextEngineerAgent:
    """
    Specialized agent for context engineering

    Responsibilities:
    1. Load full project context
    2. Extract seed rules
    3. Engineer task contexts
    4. Store in fractal memory
    5. Report completion
    """

    def execute(self, input_spec):
        # Step 1: Load full context
        full_context = self.load_project_context(
            input_spec["project_name"]
        )

        # Step 2: Extract seed rules
        seed_rules = self.extract_seed_rules(
            full_context,
            max_tokens=input_spec["options"]["seed_rule_max_tokens"]
        )

        # Store at Opus level
        memory.opus_level.store_seed_rules(
            input_spec["project_name"],
            seed_rules
        )

        # Step 3: Engineer task contexts
        task_contexts = []
        for task in input_spec["tasks"]:
            task_context = self.engineer_task_context(
                seed_rules,
                task,
                max_tokens=input_spec["options"]["task_context_max_tokens"]
            )

            # Store at Sonnet level
            memory.sonnet_level.store_task_context(
                task["task_id"],
                task_context
            )

            task_contexts.append({
                "task_id": task["task_id"],
                "context_size": len(json.dumps(task_context)) // 4,
                "stored": True
            })

        # Step 4: Report completion
        return {
            "status": "success",
            "plan_id": input_spec["plan_id"],
            "seed_rules": {
                "patterns_count": len(seed_rules.get("patterns", {})),
                "conventions_count": len(seed_rules.get("conventions", [])),
                "tokens": len(json.dumps(seed_rules)) // 4
            },
            "task_contexts": task_contexts,
            "ready_for_execution": True
        }

    def load_project_context(self, project_name):
        """Load full context from User level"""
        return memory.user_level.get_project(project_name)

    def extract_seed_rules(self, full_context, max_tokens):
        """Extract patterns and conventions"""
        from context_distiller import distill_user_to_opus
        return distill_user_to_opus(full_context)

    def engineer_task_context(self, seed_rules, task, max_tokens):
        """Engineer task-specific context"""
        from context_distiller import distill_opus_to_sonnet
        return distill_opus_to_sonnet(seed_rules, task, max_tokens)
```

### Outputs

```python
{
    "status": "success",
    "plan_id": "feature-001",
    "seed_rules": {
        "patterns_count": 5,
        "conventions_count": 12,
        "tokens": 25000
    },
    "task_contexts": [
        {
            "task_id": "1.1",
            "context_size": 8500,
            "stored": True
        },
        {
            "task_id": "1.2",
            "context_size": 7200,
            "stored": True
        }
    ],
    "ready_for_execution": True
}
```

### Expected Outcome

- Seed rules stored at Opus level
- Task contexts stored at Sonnet level
- All contexts ready in fractal memory
- Agent terminates (context freed)

---

## OpusPlanner Integration

### Updated OpusPlanner Workflow

```python
class OpusPlannerAgent:
    """
    OpusPlanner - Focused on control and communication

    Responsibilities:
    - Create high-level architecture plan
    - Delegate context engineering
    - Spawn execution agents
    - Verify results
    - Communicate with user
    """

    def execute(self, user_request):
        # Phase 1: Create high-level plan
        plan = self.create_plan(user_request)

        # Phase 2: Delegate context engineering
        context_ready = self.delegate_context_engineering(plan)

        # Phase 3: Spawn execution agents
        results = self.spawn_execution_agents(plan)

        # Phase 4: Verify and report
        return self.verify_and_report(results)

    def create_plan(self, user_request):
        """
        Create high-level architecture plan

        OpusPlanner does NOT load full context here.
        Only creates architecture and task breakdown.
        """
        return {
            "plan_id": generate_plan_id(),
            "architecture": self.design_architecture(user_request),
            "tasks": self.break_down_tasks(user_request),
            "dependencies": self.create_dependency_graph(),
            "success_criteria": self.define_success_criteria()
        }

    def delegate_context_engineering(self, plan):
        """
        Delegate to ContextEngineer

        OpusPlanner spawns specialist and waits for completion.
        Does NOT accumulate context in own window.
        """
        context_engineer_id = Task(
            subagent_type="context-engineer",
            prompt=format_context_engineering_task(plan),
            run_in_background=True,
            model="haiku"  # Fast specialist
        )

        # Wait for completion
        result = TaskOutput(task_id=context_engineer_id, block=True)

        # Verify contexts ready
        if result.status != "success":
            raise ContextEngineeringError("Failed to prepare contexts")

        return result

    def spawn_execution_agents(self, plan):
        """
        Spawn execution agents

        Agents read contexts from fractal memory.
        OpusPlanner does NOT pass context (keeps window small).
        """
        agent_ids = []

        for task in plan["tasks"]:
            # Spawn agent with minimal info
            agent_id = Task(
                subagent_type=task["agent_type"],
                prompt=f"""
                Execute task: {task["task_id"]}

                Context available in fractal memory.
                Load from Sonnet level: {task["task_id"]}
                """,
                run_in_background=True
            )
            agent_ids.append(agent_id)

        return self.collect_results(agent_ids)

    def verify_and_report(self, results):
        """
        Verify results and communicate with user

        OpusPlanner focuses on high-level verification.
        Detailed context not needed.
        """
        summary = {
            "tasks_completed": len([r for r in results if r.status == "success"]),
            "tasks_failed": len([r for r in results if r.status == "error"]),
            "overall_status": "success" if all(r.status == "success" for r in results) else "partial"
        }

        return summary
```

---

## Benefits of Delegation

### 1. Context Window Management

**Before (No Delegation):**
- OpusPlanner: 119,000 tokens ❌ Overflow
- Risk of losing important context
- Slow processing

**After (With Delegation):**
- OpusPlanner: 20,000 tokens ✅ Focused
- ContextEngineer: 57,000 tokens (then freed)
- Fast, focused processing

### 2. Separation of Concerns

- **OpusPlanner:** Control, architecture, communication
- **ContextEngineer:** Knowledge processing, pattern extraction
- **Execution Agents:** Task implementation

Each agent has clear, focused responsibility.

### 3. Scalability

Large projects don't overwhelm OpusPlanner:

| Project Size | OpusPlanner Context | ContextEngineer Context |
|--------------|--------------------|-----------------------|
| Small | 20K tokens | 30K tokens (freed) |
| Medium | 20K tokens | 57K tokens (freed) |
| Large | 20K tokens | 80K tokens (freed) |

**OpusPlanner stays constant** regardless of project size.

### 4. Parallel Context Engineering

Multiple projects:

```python
# Spawn context engineers in parallel
context_engineers = [
    Task(subagent_type="context-engineer", project="api_server", ...),
    Task(subagent_type="context-engineer", project="web_app", ...),
    Task(subagent_type="context-engineer", project="mobile_app", ...)
]

# Each handles knowledge processing independently
# OpusPlanner coordinates without accumulating context
```

### 5. Efficiency

- **ContextEngineer uses Haiku** (fast, cheap)
- **OpusPlanner uses Opus** (only for high-level decisions)
- **Execution agents use appropriate models**

Cost optimization: expensive models only where needed.

---

## Plugin Architecture

### Plugin Specification

**Location:** `.claude/plugins/context-engineering/`

```
context-engineering/
├── plugin.json                    # Plugin metadata
├── agents/
│   └── context-engineer.md        # Agent specification
├── workflows/
│   ├── extract-seed-rules.md      # Seed rule extraction workflow
│   ├── engineer-task-context.md   # Task context engineering workflow
│   └── build-step-context.md      # Step context building workflow
└── README.md                      # Plugin documentation
```

### plugin.json

```json
{
  "name": "context-engineering",
  "version": "1.0.0",
  "description": "Specialized context engineering and knowledge base processing",
  "agents": [
    {
      "type": "context-engineer",
      "model": "haiku",
      "purpose": "Process knowledge base and engineer contexts",
      "workflows": [
        "extract-seed-rules",
        "engineer-task-context",
        "build-step-context"
      ]
    }
  ],
  "dependencies": {
    "fractal-memory": ">=1.0.0",
    "context-distiller": ">=1.0.0"
  }
}
```

### Agent File: context-engineer.md

```markdown
# Context Engineer Agent

**Type:** context-engineer
**Model:** Haiku (fast specialist)
**Purpose:** Process knowledge base and engineer contexts for execution agents

## Responsibilities

1. **Load Full Context**: Read complete project from User level
2. **Extract Seed Rules**: Identify patterns, conventions, architecture
3. **Engineer Task Contexts**: Build task-specific contexts from seed rules
4. **Build Step Contexts**: Create minimal contexts for atomic steps
5. **Store in Memory**: Save at appropriate fractal levels
6. **Report Completion**: Notify orchestrator when ready

## Workflow

### Input
- plan_id: Execution plan identifier
- project_name: Project to process
- tasks: List of tasks requiring contexts
- options: Configuration (token limits, etc.)

### Output
- seed_rules: Patterns and conventions stored
- task_contexts: Engineered contexts for each task
- ready_for_execution: Boolean flag

### Process
1. Load full project context (User level)
2. Run distill_user_to_opus() → seed rules
3. For each task: Run distill_opus_to_sonnet() → task context
4. Store all in fractal memory
5. Terminate (free context window)

## Integration

### Called By
- OpusPlanner (during planning phase)

### Calls
- fractal_memory (read/write)
- context_distiller (distillation functions)

### Storage
- Opus level: seed rules
- Sonnet level: task contexts
- Haiku level: step contexts (if requested)
```

---

## Implementation Checklist

### Phase 1: Create ContextEngineer Agent
- [ ] Create `.claude/plugins/context-engineering/` directory
- [ ] Write `plugin.json` specification
- [ ] Write `agents/context-engineer.md` agent specification
- [ ] Document workflows in `workflows/` directory

### Phase 2: Update OpusPlanner
- [ ] Remove full context loading from OpusPlanner
- [ ] Add context engineering delegation logic
- [ ] Update to spawn ContextEngineer
- [ ] Verify minimal context window maintained

### Phase 3: Update Execution Engine
- [ ] Support `context-engineer` agent type
- [ ] Handle context engineering phase in execution
- [ ] Verify contexts loaded from fractal memory
- [ ] Test with sample plans

### Phase 4: Testing
- [ ] Test with small project (5 files)
- [ ] Test with medium project (50 files)
- [ ] Test with large project (500 files)
- [ ] Verify OpusPlanner context stays <25K tokens
- [ ] Verify ContextEngineer terminates correctly

### Phase 5: Documentation
- [ ] Update fractal README with delegation pattern
- [ ] Update OpusPlanner documentation
- [ ] Create workflow diagrams
- [ ] Document plugin usage

---

## Example: Complete Flow

### Scenario: Add Authentication Feature

**User Request:**
```
"Add user authentication with JWT to the API server"
```

**Step 1: OpusPlanner Planning**
```python
# OpusPlanner creates high-level plan
plan = {
    "plan_id": "auth-feature-001",
    "architecture": {
        "approach": "JWT with bcrypt",
        "files": ["app/auth.py", "app/models/user.py", "tests/test_auth.py"]
    },
    "tasks": [
        {"task_id": "1.1", "description": "Create auth module"},
        {"task_id": "1.2", "description": "Add User model"},
        {"task_id": "1.3", "description": "Add JWT endpoints"}
    ],
    "dependencies": {
        "1.1": [],
        "1.2": [],
        "1.3": ["1.1", "1.2"]
    }
}

# OpusPlanner context: ~15K tokens (architecture + plan)
```

**Step 2: OpusPlanner Delegates**
```python
# Spawn ContextEngineer
context_engineer_id = Task(
    subagent_type="context-engineer",
    prompt=f"""
    Prepare contexts for plan: auth-feature-001
    Project: api_server
    Tasks: {json.dumps(plan["tasks"])}
    """,
    run_in_background=True,
    model="haiku"
)

# OpusPlanner context: Still ~15K tokens ✅
```

**Step 3: ContextEngineer Execution**
```python
# ContextEngineer (separate context window)
# Loads: Full api_server context (50,000 tokens)

# Extracts seed rules:
seed_rules = {
    "patterns": {
        "authentication": "JWT with bcrypt",
        "api_design": "FastAPI + Pydantic",
        "database": "SQLAlchemy ORM"
    },
    "conventions": [
        "Use @require_auth decorator",
        "Password min length: 8 chars",
        "JWT expiry: 1 hour"
    ]
}
# Stored at Opus level (25,000 tokens)

# Engineers task contexts:
task_1_1_context = {
    "relevant_patterns": ["authentication"],
    "files_to_read": ["app/auth.py"],
    "conventions": ["Use @require_auth decorator"]
}
# Stored at Sonnet level (8,000 tokens)

# ... (engineers contexts for 1.2, 1.3)

# Reports completion and terminates
# ContextEngineer context: FREED (57,000 tokens released)
```

**Step 4: OpusPlanner Spawns Execution**
```python
# OpusPlanner spawns execution agents
for task in plan["tasks"]:
    agent_id = Task(
        subagent_type="sonnet-coder",
        prompt=f"""
        Execute task: {task["task_id"]}
        Context in fractal memory (Sonnet level)
        """,
        run_in_background=True
    )

# OpusPlanner context: Still ~15K tokens ✅
# Agents read contexts from fractal memory
```

**Result:**
- OpusPlanner: 15K tokens (focused on control)
- ContextEngineer: Terminated (57K freed)
- Execution agents: 8K tokens each (from memory)

**Total efficiency:** Massive context savings, clear separation of concerns.

---

## Summary

**Pattern:** Delegation to Specialist Agent

- **OpusPlanner:** Control, architecture, user communication (20K tokens)
- **ContextEngineer:** Knowledge processing, pattern extraction (57K tokens, then freed)
- **Execution Agents:** Task implementation (8K tokens from memory)

**Benefits:**
1. ✅ Prevents context accumulation in orchestrator
2. ✅ Clear separation of concerns
3. ✅ Scales to large projects
4. ✅ Parallel context engineering possible
5. ✅ Cost optimization (right model for each job)

**Implementation:** Plugin architecture with specialized agent

---

**Document Status:** Delegation pattern documented, ready for implementation
**Last Updated:** 2025-12-16


---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: CONTEXT_ENGINEERING_DELEGATION.md](../CONTEXT_ENGINEERING_DELEGATION.md)
