# Fractal Principles - Recursive Context Architecture

**Purpose**: Core architectural principles for adaptive complexity management
**Last Updated**: 2025-12-16

---

## What Is a Fractal Architecture?

A **fractal** is a pattern that repeats at different scales. In our system, the SAME STRUCTURE exists at every level, just with progressively less detail.

### Visual Representation

```
User Level (Full Tree)
├─ Project A
│  ├─ Authentication
│  │  ├─ JWT implementation
│  │  ├─ Password hashing
│  │  └─ Token validation
│  ├─ Database
│  │  ├─ User model
│  │  ├─ Migrations
│  │  └─ Queries
│  └─ API
│     ├─ Routes
│     ├─ Schemas
│     └─ Validation

Opus Level (Seed Rules - Pruned Tree)
├─ Project A
│  ├─ Authentication: "JWT with bcrypt"
│  ├─ Database: "SQLAlchemy ORM"
│  └─ API: "FastAPI REST"

Sonnet Level (Task Context - Single Branch)
└─ Task: Add password reset
   └─ Authentication: "JWT with bcrypt"
      └─ Files: [app/auth.py, app/models/user.py]

Haiku Level (Step Context - Single Leaf)
└─ Step: Create email template
   └─ Location: app/templates/emails/reset_password.html
```

**Same structure, different granularity.**

---

## Core Fractal Principles

### 1. Self-Similarity

**Definition**: The same pattern repeats at different scales

**Example**:

```python
# ALL LEVELS use the same structure:
{
    "patterns": {...},
    "files": [...],
    "conventions": [...]
}

# But with different amounts of detail:

# User Level (unlimited)
{
    "patterns": {
        "authentication": {
            "full_implementation": "...",
            "all_files": [...],
            "all_functions": [...],
            "all_tests": [...]
        }
    }
}

# Opus Level (10-50K tokens)
{
    "patterns": {
        "authentication": {
            "pattern": "JWT with bcrypt",
            "files": ["app/auth.py"],
            "conventions": ["Use @require_auth"]
        }
    }
}

# Sonnet Level (5-15K tokens)
{
    "patterns": {
        "authentication": {
            "pattern": "JWT",
            "files": ["app/auth.py"]
        }
    }
}

# Haiku Level (<2K tokens)
{
    "action": "Validate JWT token",
    "location": "app/auth.py:42"
}
```

### 2. Recursive Distillation

**Definition**: Each level is created by distilling the level above

```
User → distill_user_to_opus() → Opus
Opus → distill_opus_to_sonnet() → Sonnet
Sonnet → distill_sonnet_to_haiku() → Haiku
```

**Process**:

1. **Start with full context** (User level)
2. **Extract patterns** (Opus level)
3. **Select relevant patterns** (Sonnet level)
4. **Extract minimum action** (Haiku level)

**Key**: Each distillation is INTELLIGENT, not just truncation.

### 3. Context Splitting

**Definition**: Split context by relevance, not arbitrarily

**Bad Approach** (Arbitrary Truncation):
```python
# ❌ Just cut at token limit
full_context = load_all()  # 50,000 tokens
truncated = full_context[:10000]  # First 10K only
```

**Good Approach** (Intelligent Splitting):
```python
# ✅ Extract only relevant patterns
full_context = load_all()  # 50,000 tokens
seed_rules = extract_patterns(full_context)  # 25,000 tokens
task_context = select_relevant(seed_rules, task)  # 8,000 tokens
```

**Result**: Each level has EXACTLY what it needs, nothing more.

### 4. Hierarchical Composition

**Definition**: Lower levels compose to form higher levels

```
Step 1.2.1 ]
Step 1.2.2 ] → Task 1.2
Step 1.2.3 ]

Task 1.1 ]
Task 1.2 ] → Section 1
Task 1.3 ]

Section 1 ]
Section 2 ] → Plan
Section 3 ]

Plan 1 ]
Plan 2 ] → Project
Plan 3 ]
```

**Composition Direction**:
- **Bottom-up**: Steps → Tasks → Sections → Plans → Project
- **Top-down**: Project → Plans → Sections → Tasks → Steps

**Both directions work because of fractal self-similarity.**

---

## Adaptive Complexity Management

### The Challenge

Different tasks need different amounts of context:

| Task | Context Needed |
|------|----------------|
| "Fix typo in README" | Minimal (file location) |
| "Add type hint to function" | Low (function signature) |
| "Implement password reset" | Medium (auth patterns, email, database) |
| "Build authentication system" | High (full project architecture) |

### The Solution: Fractal Scaling

```python
# Simple task - minimal seed rules
simple_task = "Fix typo in README"
seed_rules = {}  # No patterns needed
task_context = {
    "action": "Fix typo",
    "file": "README.md:42"
}  # ~100 tokens

# Medium task - relevant patterns
medium_task = "Add password reset endpoint"
seed_rules = {
    "authentication": "JWT with bcrypt"
}  # 5,000 tokens
task_context = {
    "action": "Add endpoint",
    "patterns": {"authentication": "..."},
    "files": ["app/auth.py"]
}  # 8,000 tokens

# Complex task - comprehensive patterns
complex_task = "Build authentication system"
seed_rules = {
    "authentication": {...},
    "database": {...},
    "api_design": {...}
}  # 25,000 tokens
task_context = {
    "action": "Build system",
    "patterns": {...},
    "files": [...],
    "conventions": [...]
}  # 15,000 tokens
```

**The fractal system automatically scales to task complexity.**

---

## Fractal Memory Layers

### Layer Characteristics

```
┌─────────────────────────────────────────────────┐
│ User Level - UNLIMITED                          │
│ Purpose: Store everything                       │
│ Used By: OpusPlanner (read only)                │
│ Storage: Full context, all files, all details   │
└─────────────────────────────────────────────────┘
                    ↓ distill
┌─────────────────────────────────────────────────┐
│ Opus Level - 10-50K tokens (FOUNDATION)         │
│ Purpose: Seed rules, patterns, architecture     │
│ Used By: OpusPlanner (read/write)               │
│ Storage: Patterns, conventions, decisions       │
└─────────────────────────────────────────────────┘
                    ↓ engineer
┌─────────────────────────────────────────────────┐
│ Sonnet Level - 5-15K tokens                     │
│ Purpose: Task-specific context                  │
│ Used By: SonnetCoder, SonnetDebugger, Tracker   │
│ Storage: Task context, results, progress        │
└─────────────────────────────────────────────────┘
                    ↓ extract
┌─────────────────────────────────────────────────┐
│ Haiku Level - <2K tokens                        │
│ Purpose: Minimal step context                   │
│ Used By: HaikuExecutor                          │
│ Storage: Step context, step results             │
└─────────────────────────────────────────────────┘
```

### Layer Interactions

**Write Path** (Top-down):
```
OpusPlanner → distill → Opus (seed rules)
OpusPlanner → engineer → Sonnet (task context)
SonnetCoder → extract → Haiku (step context)
```

**Read Path** (Bottom-up):
```
HaikuExecutor → read → Haiku (step context)
HaikuExecutor → store → Haiku (step result)

SonnetCoder → read → Sonnet (task context)
SonnetCoder → store → Sonnet (task result)

SonnetTracker → read → Sonnet (all task results)
SonnetTracker → synthesize → Sonnet (aggregated result)

OpusPlanner → read → Opus (seed rules)
OpusPlanner → read → Sonnet (progress)
```

---

## Distillation Functions

### User → Opus (Pattern Extraction)

**Purpose**: Extract seed rules from full project context

**Input**: Full context (unlimited tokens)
**Output**: Seed rules (10-50K tokens)

```python
from context_distiller import distill_user_to_opus

seed_rules = distill_user_to_opus(full_context)
```

**Process**:
1. Scan files for patterns (auth, database, API)
2. Extract conventions from CLAUDE.md
3. Extract architecture from project.md
4. Infer patterns from file structure

**Reduction**: ~50% (50K → 25K typical)

### Opus → Sonnet (Context Engineering)

**Purpose**: Build task-specific context from seed rules

**Input**: Seed rules (10-50K tokens) + Task description
**Output**: Task context (5-15K tokens)

```python
from context_distiller import distill_opus_to_sonnet

task_context = distill_opus_to_sonnet(seed_rules, task)
```

**Process**:
1. Match task keywords to patterns
2. Select relevant patterns only
3. Get files from matched patterns
4. Filter conventions by task type

**Reduction**: ~70% (25K → 8K typical)

### Sonnet → Haiku (Minimal Extraction)

**Purpose**: Extract minimum context for single step

**Input**: Task context (5-15K tokens) + Step description
**Output**: Step context (<2K tokens)

**Process**:
1. Extract step action and requirements
2. Add single most relevant file (if needed)
3. Add location hint for creation

**Reduction**: ~85% (8K → 1.5K typical)

---

## Benefits of Fractal Architecture

### 1. Token Efficiency

```
Without Fractal:
- Every agent gets full context: 50,000 tokens × 5 agents = 250,000 tokens

With Fractal:
- OpusPlanner: 25,000 tokens (seed rules)
- SonnetCoder: 8,000 tokens (task context)
- HaikuExecutor: 1,500 tokens (step context)
- SonnetDebugger: 8,000 tokens (task context)
- SonnetTracker: 8,000 tokens (results)
Total: 50,500 tokens (80% reduction)
```

### 2. Faster Execution

Less context = faster processing:
- **HaikuExecutor**: <10s per step (minimal context)
- **SonnetCoder**: 10-30s per task (task context)
- **OpusPlanner**: 30-60s for planning (seed rules)

### 3. Better Focus

Each agent sees only what it needs:
- **HaikuExecutor**: Single step action (no distractions)
- **SonnetCoder**: Task patterns (no irrelevant code)
- **OpusPlanner**: Seed rules (no implementation details)

### 4. Scalability

System scales to project size:

| Project Size | Full Context | Seed Rules | Task Context | Step Context |
|--------------|--------------|------------|--------------|--------------|
| Small (5 files) | 10K tokens | 5K tokens | 2K tokens | 500 tokens |
| Medium (50 files) | 100K tokens | 50K tokens | 15K tokens | 2K tokens |
| Large (500 files) | 1M tokens | 50K tokens | 15K tokens | 2K tokens |

**Note**: Seed rules cap at ~50K, task context at ~15K, step context at ~2K
**Result**: Large projects are as efficient as small ones

---

## Recursive Patterns in Code

### Pattern 1: Memory Layer Structure

Every layer has the same interface:

```python
class MemoryLayer:
    def store(self, category: str, key: str, data: Dict) -> None
    def retrieve(self, category: str, key: str) -> Optional[Dict]
    def list_keys(self, category: str) -> List[str]
    def exists(self, category: str, key: str) -> bool
```

**Fractal**: Same interface, different storage locations

### Pattern 2: Context Structure

Every context has the same shape:

```python
{
    "id": "...",           # Unique identifier
    "content": {...},      # Actual content (varies by level)
    "metadata": {...},     # Metadata about content
    "timestamp": "..."     # When created
}
```

**Fractal**: Same structure, different content size

### Pattern 3: Distillation Process

Every distillation follows same steps:

```python
def distill(input_context, target_size):
    # 1. Identify relevant patterns
    patterns = identify_patterns(input_context)

    # 2. Select by relevance
    selected = select_relevant(patterns, target)

    # 3. Trim to size limit
    trimmed = trim_to_limit(selected, target_size)

    return trimmed
```

**Fractal**: Same process, different inputs/outputs

---

## Emergent Properties

### Property 1: Self-Healing

If a level is corrupted:
- Regenerate from level above
- User → Opus (extract seed rules again)
- Opus → Sonnet (engineer task context again)

### Property 2: Caching

Each level caches for efficiency:
- Seed rules change rarely → cache at Opus
- Task context per task → cache at Sonnet
- Step context per step → cache at Haiku

### Property 3: Parallel Distillation

Independent tasks can distill in parallel:
```python
# Parallel task context engineering
task_contexts = parallel_map(
    lambda task: distill_opus_to_sonnet(seed_rules, task),
    tasks
)
```

---

## Integration with Agents

Agents operate at specific levels:

```
OpusPlanner (Orchestration)
└─ Operates at: User + Opus + Sonnet
   ├─ Reads: User (full context)
   ├─ Writes: Opus (seed rules)
   └─ Writes: Sonnet (task contexts)

SonnetCoder (Execution)
└─ Operates at: Sonnet
   ├─ Reads: Sonnet (task context)
   └─ Writes: Sonnet (task results)

HaikuExecutor (Execution)
└─ Operates at: Haiku
   ├─ Reads: Haiku (step context)
   └─ Writes: Haiku (step results)

SonnetDebugger (Execution)
└─ Operates at: Sonnet + Opus
   ├─ Reads: Sonnet (task context)
   ├─ Reads: Opus (seed rules for patterns)
   └─ Writes: Opus (new seed rules if pattern found)

SonnetTracker (Execution)
└─ Operates at: Sonnet
   ├─ Reads: Sonnet (all task results)
   └─ Writes: Sonnet (synthesized results, progress)
```

**Fractal**: Each agent has a clear position in the hierarchy

---

## Best Practices

### DO:
- ✅ Use distillation functions for all context creation
- ✅ Maintain same structure at all levels
- ✅ Cache at appropriate levels
- ✅ Let system scale automatically
- ✅ Trust the fractal hierarchy

### DON'T:
- ❌ Pass full context to lower levels
- ❌ Skip distillation steps
- ❌ Arbitrarily truncate context
- ❌ Mix levels (e.g., Haiku reading Opus)
- ❌ Duplicate information across levels

---

**Status**: ✅ Foundational Architecture
**Applies To**: All context engineering, all agents
**Maintained By**: Fractal infrastructure code
