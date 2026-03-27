# Fractal Memory Architecture

**Concept:** Memory distillation mirrors agent hierarchy
**Principle:** Each level holds progressively refined context, just like agents

---

## The Problem with Flat Memory

**Traditional Approach:**
```
Memory Store (Single Level)
├── All context dumped in one place
├── Agents read everything or nothing
└── No context optimization
```

**Issues:**
- Every agent loads full context (token waste)
- No hierarchical knowledge distillation
- Breaks fractal principle (context engineering lost)

---

## Fractal Memory Solution

**Mirror the agent hierarchy with memory layers:**

```
┌─────────────────────────────────────────────────────┐
│ USER LEVEL (Full Context)                          │
│ - Complete project knowledge                       │
│ - All files, all history, all patterns            │
│ - No token limits                                  │
└─────────────────────────────────────────────────────┘
                    ↓ Context Engineering
┌─────────────────────────────────────────────────────┐
│ OPUS LEVEL (Orchestration Memory)                  │
│ - Project-wide patterns and seed rules             │
│ - Architectural decisions and rationale            │
│ - Cross-cutting concerns                           │
│ - 10-50K tokens                                    │
└─────────────────────────────────────────────────────┘
                    ↓ Task-Oriented Distillation
┌─────────────────────────────────────────────────────┐
│ SONNET LEVEL (Execution Memory)                    │
│ - Task-specific patterns                           │
│ - Relevant files and functions                     │
│ - Current work context                             │
│ - 5-15K tokens                                     │
└─────────────────────────────────────────────────────┘
                    ↓ Minimal Context Extraction
┌─────────────────────────────────────────────────────┐
│ HAIKU LEVEL (Step Memory)                          │
│ - Single step essentials                           │
│ - Inline instructions only                         │
│ - Absolute minimum context                         │
│ - <2K tokens                                       │
└─────────────────────────────────────────────────────┘
```

---

## Layer 1: User Level (Infinite Context)

**What Lives Here:**
- Complete project files
- Full CLAUDE.md, state.md, todo.md
- All research documents
- Historical context
- External dependencies

**Storage:**
```
.claude/memory/user_level/
├── projects/
│   ├── peti/
│   │   ├── full_context.json
│   │   ├── files_snapshot.json
│   │   └── history.json
│   └── flow/
│       └── ...
├── research/
│   ├── patterns_discovered.json
│   └── best_practices.json
└── system/
    ├── all_files_index.json
    └── global_knowledge.json
```

**Who Reads This:**
- Only OpusPlanner when building initial context
- Never passed directly to execution agents

**Operations:**
- `store_project_context(project, full_context)` - Store everything
- `get_full_context(project)` - Retrieve for orchestration

---

## Layer 2: Opus Level (Orchestration Memory)

**What Lives Here:**
- **Seed rules** extracted from project
- **Architectural patterns** (auth strategy, DB design, API conventions)
- **Cross-cutting concerns** (error handling, logging, security)
- **Project conventions** (naming, structure, testing approach)

**Storage:**
```
.claude/memory/opus_level/
├── seed_rules/
│   ├── peti_seeds.json
│   └── flow_seeds.json
├── patterns/
│   ├── authentication_pattern.json
│   ├── api_design_pattern.json
│   └── error_handling_pattern.json
├── architecture/
│   ├── peti_architecture.json
│   └── decisions.json
└── conventions/
    ├── naming_conventions.json
    └── code_style.json
```

**Example Seed Rules (10-50K tokens):**
```json
{
  "project": "peti",
  "seed_rules": {
    "authentication": {
      "pattern": "JWT with bcrypt",
      "implementation": "app/auth.py handles all auth logic",
      "conventions": ["Use @require_auth decorator", "Tokens expire in 24h"],
      "examples": ["@/app/routes/user.py:12-45"]
    },
    "database": {
      "pattern": "SQLAlchemy ORM with Alembic migrations",
      "models_location": "app/models/",
      "conventions": ["Use declarative base", "Timestamps on all models"],
      "examples": ["@/app/models/user.py"]
    },
    "api_design": {
      "pattern": "RESTful with FastAPI",
      "conventions": ["Use Pydantic schemas", "HTTP codes strictly followed"],
      "error_format": {"error": "message", "code": "ERROR_CODE"}
    }
  },
  "architectural_decisions": [
    {
      "decision": "PDF processing via background tasks",
      "rationale": "Large files block requests",
      "implementation": "Celery + Redis"
    }
  ]
}
```

**Who Reads This:**
- OpusPlanner when generating execution plans
- SeedAnalyzer when extracting patterns
- Used to engineer context for Sonnet agents

**Operations:**
- `extract_seed_rules(full_context) -> seed_rules` - Distill from user level
- `get_project_seeds(project) -> seed_rules` - Retrieve for planning
- `update_seed_rules(project, new_patterns)` - Evolve as project grows

---

## Layer 3: Sonnet Level (Execution Memory)

**What Lives Here:**
- **Task-specific context** (only relevant to current work)
- **Relevant patterns** (subset of seed rules)
- **Working memory** (files being modified)
- **Recent changes** (last few commits)

**Storage:**
```
.claude/memory/sonnet_level/
├── task_contexts/
│   ├── task_1.1_context.json
│   ├── task_1.2_context.json
│   └── task_2.1_context.json
├── working_memory/
│   ├── sonnet_coder_current.json
│   └── sonnet_debugger_current.json
└── results/
    ├── task_1.1_result.json
    └── task_1.2_result.json
```

**Example Task Context (5-15K tokens):**
```json
{
  "task_id": "1.2",
  "agent": "sonnet-coder",
  "action": "Add password reset endpoint",
  "engineered_context": {
    "relevant_seeds": {
      "authentication": {
        "pattern": "JWT with bcrypt",
        "key_files": ["app/auth.py", "app/models/user.py"],
        "conventions": ["Use @require_auth decorator"]
      }
    },
    "files_to_read": [
      {
        "path": "app/auth.py",
        "sections": ["login", "verify_token"],
        "reason": "Follow existing auth patterns"
      },
      {
        "path": "app/routes/auth.py",
        "sections": ["route structure"],
        "reason": "Add new route here"
      }
    ],
    "inline_instructions": "Add POST /auth/reset-password endpoint. Send reset email with token. Follow existing auth patterns in app/auth.py.",
    "validation": ["Endpoint accepts email", "Token generated and stored", "Email sent"]
  },
  "dependencies": ["task_1.1"],
  "expected_output": "Password reset endpoint functional"
}
```

**Who Reads This:**
- SonnetCoder when executing tasks
- SonnetDebugger when fixing errors
- Built by OpusPlanner via context engineering

**Operations:**
- `engineer_task_context(seed_rules, task) -> task_context` - Distill from Opus level
- `get_task_context(task_id) -> context` - Retrieve for execution
- `store_task_result(task_id, result)` - Save for synthesis

---

## Layer 4: Haiku Level (Step Memory)

**What Lives Here:**
- **Absolute minimum** for single step
- **Inline instructions** (few sentences)
- **File references** (paths only, not content)
- **Validation criteria** (what to check)

**Storage:**
```
.claude/memory/haiku_level/
├── step_contexts/
│   ├── step_1.1.json
│   └── step_1.2.json
└── step_results/
    ├── step_1.1_result.json
    └── step_1.2_result.json
```

**Example Step Context (<2K tokens):**
```json
{
  "step_id": "1.1",
  "agent": "haiku-executor",
  "action": "Create password reset email template",
  "minimal_context": {
    "task": "Create HTML email template for password reset",
    "location": "app/templates/emails/reset_password.html",
    "requirements": [
      "Include reset token link",
      "Match existing email style",
      "Add expiration notice (24h)"
    ],
    "reference_file": "app/templates/emails/welcome.html",
    "validation": ["File created", "Contains token placeholder", "Valid HTML"]
  }
}
```

**Who Reads This:**
- HaikuExecutor only
- Built by OpusPlanner or SonnetCoder (step decomposition)

**Operations:**
- `extract_step_context(task_context, step) -> step_context` - Distill from Sonnet level
- `get_step_context(step_id) -> context` - Retrieve for execution
- `store_step_result(step_id, result)` - Save for tracking

---

## Context Distillation Flow

**Step-by-Step Process:**

### 1. User Provides Task
```
User: "Add password reset functionality to the API"
```

### 2. OpusPlanner Reads User Level
```python
# Load FULL context (no limits)
full_context = memory.get_full_context("peti")
# Contains: All files, history, patterns, dependencies
```

### 3. OpusPlanner Extracts Opus Level
```python
# Distill to seed rules and patterns
seed_rules = memory.extract_seed_rules(full_context)
# Result: 10-50K tokens of essential patterns
```

### 4. OpusPlanner Engineers Sonnet Context
```python
# Create task-oriented context for SonnetCoder
task_context = engineer_context(
    seed_rules=seed_rules,
    task="Add password reset endpoint",
    relevant_patterns=["authentication", "email", "api_design"],
    relevant_files=["app/auth.py", "app/routes/auth.py"],
    token_limit=10000  # 5-15K for Sonnet
)
# Result: Only auth patterns + relevant files
```

### 5. SonnetCoder Executes with Sonnet Context
```python
# Reads engineered context (NOT full project)
context = memory.get_task_context("task_1.2")
# Contains: Auth patterns, 2 relevant files, inline instructions
# Total: ~8K tokens

# If complex, breaks into steps for Haiku
steps = decompose_into_steps(context)
```

### 6. SonnetCoder Creates Haiku Context (if needed)
```python
# Distill even further for HaikuExecutor
step_context = extract_step_context(
    task_context=context,
    step="Create email template",
    token_limit=2000  # <2K for Haiku
)
# Result: Just template location + requirements
```

### 7. HaikuExecutor Executes with Minimal Context
```python
# Reads minimal context
context = memory.get_step_context("step_1.1")
# Contains: File path, 3 requirements, 1 reference file
# Total: ~500 tokens

# Executes quickly with minimal context
```

---

## Memory Operations by Agent

### OpusPlanner
```python
# READ: Full context
full = memory.user_level.get_full_context(project)

# WRITE: Seed rules (distilled)
seeds = extract_seeds(full)
memory.opus_level.store_seed_rules(project, seeds)

# WRITE: Engineered contexts for tasks
for task in tasks:
    task_context = engineer_context(seeds, task)
    memory.sonnet_level.store_task_context(task.id, task_context)
```

### SonnetCoder
```python
# READ: Task context (engineered by Opus)
context = memory.sonnet_level.get_task_context(task_id)

# WRITE: Task result
result = execute_task(context)
memory.sonnet_level.store_task_result(task_id, result)

# WRITE: Step contexts (if decomposed)
if complex:
    for step in steps:
        step_context = extract_step_context(context, step)
        memory.haiku_level.store_step_context(step.id, step_context)
```

### HaikuExecutor
```python
# READ: Step context (minimal)
context = memory.haiku_level.get_step_context(step_id)

# WRITE: Step result
result = execute_step(context)
memory.haiku_level.store_step_result(step_id, result)
```

### SonnetTracker
```python
# READ: All results across levels
results = {
    "tasks": memory.sonnet_level.get_all_results(),
    "steps": memory.haiku_level.get_all_results()
}

# SYNTHESIZE: Aggregate and report
synthesis = synthesize_results(results)
memory.opus_level.store_synthesis(synthesis)
```

---

## Implementation Plan

### Step 1: Memory Layer Structure
```bash
mkdir -p .claude/memory/user_level/{projects,research,system}
mkdir -p .claude/memory/opus_level/{seed_rules,patterns,architecture,conventions}
mkdir -p .claude/memory/sonnet_level/{task_contexts,working_memory,results}
mkdir -p .claude/memory/haiku_level/{step_contexts,step_results}
```

### Step 2: Memory Manager Class
```python
# File: .claude/scripts/fractal_memory.py

class FractalMemory:
    def __init__(self, base_path=".claude/memory"):
        self.user_level = UserLevelMemory(f"{base_path}/user_level")
        self.opus_level = OpusLevelMemory(f"{base_path}/opus_level")
        self.sonnet_level = SonnetLevelMemory(f"{base_path}/sonnet_level")
        self.haiku_level = HaikuLevelMemory(f"{base_path}/haiku_level")

    def distill_context(self, from_level, to_level, filter_criteria):
        """Distill context from higher to lower level"""
        pass
```

### Step 3: Context Engineering Functions
```python
def engineer_context(
    full_context: Dict,
    target_level: str,  # "opus" | "sonnet" | "haiku"
    task: Dict,
    token_limit: int
) -> Dict:
    """
    Engineer context for specific level

    OpusPlanner uses this to create Sonnet contexts
    SonnetCoder uses this to create Haiku contexts
    """
    if target_level == "opus":
        return extract_seed_rules(full_context, token_limit)

    elif target_level == "sonnet":
        return extract_task_context(full_context, task, token_limit)

    elif target_level == "haiku":
        return extract_step_context(full_context, task, token_limit)
```

---

## Benefits of Fractal Memory

✅ **Token Efficiency**
- Each agent gets exactly what it needs
- No wasted context
- Faster execution

✅ **Consistent with Agent Architecture**
- Memory mirrors agent hierarchy
- Same fractal principle throughout
- Easier to understand

✅ **Scalable**
- Add projects without bloating lower levels
- Context grows at top, stays minimal at bottom
- Indefinite project growth

✅ **Maintainable**
- Clear separation of concerns
- Each level has defined purpose
- Easy to debug context issues

---

## Next: Implementation

Ready to implement step by step:
1. Create memory layer directories
2. Build FractalMemory class
3. Implement distillation functions
4. Integrate with agents
5. Test context engineering

Shall we start?
