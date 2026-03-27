# Knowledge Hierarchy - Logical Element Breakdown

**Principle:** Every concept has 4 levels of detail
**Navigation:** Each level links up/down for easy access

---

## 4-Level Knowledge Pyramid (Context-Optimized)

```
┌─────────────────────────────────────┐
│  Level 1: WHAT (High-Level)         │  ← ~2K tokens (HaikuExecutor)
│  - Complete logical overview         │    Quick reference, minimal
│  - Why it exists, what problem       │
│  - Link to Level 2 for concepts     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Level 2: HOW (Concepts)            │  ← 5-15K tokens (SonnetCoder)
│  - Complete conceptual model         │    Task-focused, sufficient context
│  - How it works with diagrams       │
│  - Link to Level 1 for overview     │
│  - Link to Level 3 for code         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Level 3: DETAILS (Implementation)  │  ← 5-15K tokens (SonnetCoder)
│  - Complete implementation guide     │    Practical, code-heavy
│  - All code examples                │
│  - Link to Level 2 for concepts     │
│  - Link to Level 4 for API          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Level 4: REFERENCE (Complete API)  │  ← 10-50K tokens (OpusPlanner)
│  - Complete API documentation        │    Strategic reference
│  - All parameters, all methods      │
│  - Link to Level 3 for examples     │
└─────────────────────────────────────┘
```

**Context Engineering Principle:**
- Each file = complete logical unit (no need to read multiple files)
- Size matches agent context limits (not arbitrary minimization)
- Level 1 (HaikuExecutor): Quick refs, <2K tokens
- Level 2-3 (SonnetCoder): Full concepts/implementation, 5-15K tokens
- Level 4 (OpusPlanner): Strategic references, 10-50K tokens

---

## Example: Fractal Memory

### Level 1: WHAT (overview/MEMORY_SYSTEM.md)

```markdown
# Memory System - What Is It?

**Definition:** Hierarchical storage that mirrors agent complexity.

**Why:** Agents need different amounts of context:
- OpusPlanner: 10-50K tokens (full strategic view)
- SonnetCoder: 5-15K tokens (task-focused)
- HaikuExecutor: <2K tokens (minimal step context)

Fractal memory provides exactly the right amount to each agent.

**Learn more:** [How Memory Works](HOW_MEMORY_WORKS.md) (Level 2)
```

### Level 2: HOW (architecture/MEMORY_HIERARCHY.md)

```markdown
# Memory Hierarchy - How It Works

**Back to:** [What is Memory?](../overview/MEMORY_SYSTEM.md)

## 4 Storage Levels

1. **User Level** - Full context (unlimited)
2. **Opus Level** - Seed rules (10-50K tokens)
3. **Sonnet Level** - Task contexts (5-15K tokens)
4. **Haiku Level** - Step contexts (<2K tokens)

## Distillation Flow

User → Opus → Sonnet → Haiku
(Full) (Rules) (Tasks) (Steps)

Each level extracts only what the next needs.

**Details:** [Memory Implementation](../memory/IMPLEMENTATION.md) (Level 3)
**Reference:** [Memory API](../memory/API_REFERENCE.md) (Level 4)
```

### Level 3: DETAILS (memory/IMPLEMENTATION.md)

```markdown
# Memory Implementation - Details

**Back to:** [Memory Hierarchy](../architecture/MEMORY_HIERARCHY.md)

## File-Based Storage

```
.claude/memory/
├── user_level/projects/{project}.json
├── opus_level/seed_rules/{project}.json
├── sonnet_level/task_contexts/{task_id}.json
└── haiku_level/step_contexts/{step_id}.json
```

## Code Example

```python
from fractal_memory import FractalMemory

memory = FractalMemory()

# Store full context
memory.store_project("myproject", full_context)

# Distill to seed rules
seed_rules = memory.distill_to_opus("myproject")

# Engineer task context
task_context = memory.distill_to_sonnet("myproject", task)
```

**Complete API:** [API Reference](API_REFERENCE.md) (Level 4)
```

### Level 4: REFERENCE (memory/API_REFERENCE.md)

```markdown
# Memory API Reference - Complete

**Back to:** [Implementation Details](IMPLEMENTATION.md)

## FractalMemory Class

### Constructor

```python
FractalMemory(base_path: str = ".claude/memory")
```

**Parameters:**
- `base_path`: Root directory for memory storage (default: `.claude/memory`)

### Methods

#### store_project()

```python
def store_project(project: str, full_context: Dict) -> None
```

Stores complete project context at User level.

**Parameters:**
- `project` (str): Project name
- `full_context` (Dict): Complete project knowledge

**Returns:** None

**Example:**
```python
memory.store_project("api_server", {
    "files": [...],
    "patterns": {...}
})
```

... [complete API continues]
```

---

## Template Structure

### Every Topic Has 4 Files

Example: "Orchestrator Pattern"

1. `overview/ORCHESTRATOR_WHAT.md` (Level 1: WHAT)
   - 1 paragraph definition
   - Why it exists
   - → Link to Level 2

2. `architecture/ORCHESTRATOR_HOW.md` (Level 2: HOW)
   - Core principles (3-5 concepts)
   - Conceptual flow diagram
   - ← Link to Level 1
   - → Link to Level 3

3. `implementation/ORCHESTRATOR_DETAILS.md` (Level 3: DETAILS)
   - Code examples
   - Configuration
   - Usage patterns
   - ← Link to Level 2
   - → Link to Level 4

4. `reference/ORCHESTRATOR_API.md` (Level 4: REFERENCE)
   - Complete function signatures
   - All parameters documented
   - All return values
   - ← Link to Level 3

---

## Navigation Pattern

### From User Perspective

**Scenario 1: Learning (High → Low)**
```
User reads: "What is Orchestrator?" (Level 1)
  → Wants details: Click "How it works" (Level 2)
  → Wants code: Click "Implementation" (Level 3)
  → Needs API: Click "Reference" (Level 4)
```

**Scenario 2: Looking Up API (Low → High)**
```
User needs: Parameter format (Level 4)
  → Needs context: Click "Implementation" (Level 3)
  → Needs concept: Click "How it works" (Level 2)
  → Needs overview: Click "What is it?" (Level 1)
```

**Scenario 3: Implementing (Medium → Low/High)**
```
Developer reads: "How it works" (Level 2)
  → Needs code: Click "Implementation" (Level 3)
  → Also checks: Click "What is it?" (Level 1) to verify understanding
```

---

## Cross-Reference Format

**In every file, add navigation block:**

```markdown
---

## Navigation

**Level:** [WHAT / HOW / DETAILS / REFERENCE]

**Up:** [Higher level overview](../category/HIGHER.md)
**Down:** [Lower level details](../category/LOWER.md)
**Related:** [Related concept](../other/RELATED.md)

---
```

**Example:**

```markdown
---

## Navigation

**Level:** HOW (Concepts)

**Up:** [What is Memory?](../overview/MEMORY_SYSTEM.md)
**Down:** [Memory Implementation](../implementation/MEMORY_DETAILS.md)
**Related:**
- [Context Engineering](CONTEXT_ENGINEERING.md)
- [Agent Hierarchy](AGENT_HIERARCHY.md)

---
```

---

## File Naming Convention

**Pattern:** `{LEVEL}_{TOPIC}_{DETAIL}.md`

**Levels:**
- `WHAT_` - Level 1 (overview)
- `HOW_` - Level 2 (concepts)
- `IMPL_` - Level 3 (implementation)
- `API_` - Level 4 (reference)

**Examples:**
- `WHAT_FRACTAL_MEMORY.md` - High-level overview
- `HOW_MEMORY_DISTILLATION.md` - Conceptual flow
- `IMPL_MEMORY_STORAGE.md` - File structure and code
- `API_FRACTAL_MEMORY.md` - Complete class reference

---

## Logical Element Breakdown Example

### Topic: "Task Hooks"

**Level 1 (WHAT):** `overview/WHAT_HOOKS.md`
```
Hooks are lifecycle scripts that run before/after tasks.
They prepare context (pre-task) and store results (post-task).

→ Learn more: HOW_HOOKS.md
```

**Level 2 (HOW):** `architecture/HOW_HOOKS.md`
```
Pre-task hook:
1. Load context from memory
2. Validate agent access
3. Initialize state marker

Post-task hook:
1. Store result in memory
2. Check dependencies
3. Trigger ready tasks

→ Details: IMPL_HOOKS.md
```

**Level 3 (DETAILS):** `implementation/IMPL_HOOKS.md`
```bash
# Pre-task.sh location
.claude/hooks/pre-task.sh

# Called by execution engine
pre-task.sh <agent_type> <task_id> <project>

# Reads from
.claude/memory/{level}/contexts/{id}.json

→ API: API_HOOKS.md
```

**Level 4 (API):** `reference/API_HOOKS.md`
```bash
pre-task.sh <agent_type> <task_id> <project>

Parameters:
  agent_type: opus-planner|sonnet-coder|...
  task_id: Task identifier (format: X.Y or X.Y.Z)
  project: Project name (no path traversal)

Exit codes:
  0: Success
  1: Validation failed
  2: Context not found

Environment:
  CLAUDE_ROOT: Root directory
  MEMORY_DIR: Memory storage location
```

---

## Benefits

**Easy Access:**
- New users → Start at Level 1 (WHAT)
- Implementers → Jump to Level 3 (DETAILS)
- API users → Go to Level 4 (REFERENCE)

**Bidirectional:**
- Can navigate up for context
- Can navigate down for details
- Never lost in documentation

**Scalable:**
- Add new levels if needed
- Split levels into sub-topics
- Maintain hierarchy

**Maintainable:**
- Small focused files
- Clear responsibilities
- Easy to update

---

## Summary

**Knowledge Hierarchy:**
1. WHAT (high-level overview)
2. HOW (key concepts)
3. DETAILS (implementation)
4. REFERENCE (complete API)

**Each level:**
- Links up (for context)
- Links down (for details)
- Links related (for cross-reference)

**Result:** Fractal knowledge graph - easy access to relevant data at every level
