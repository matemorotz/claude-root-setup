# Context Engineering - Practical Guide

**Purpose**: How to use fractal infrastructure for smart context splitting
**Last Updated**: 2025-12-16

---

## What Is Context Engineering?

**Context Engineering** is the practice of building MINIMAL, ESSENTIAL context for each agent by intelligently selecting only what's needed from the full project context.

###Not Context Engineering

```python
# ❌ Truncation (bad)
context = full_project_context[:10000]  # Just cut off

# ❌ Everything (bad)
context = full_project_context  # Give everything
```

### Context Engineering

```python
# ✅ Intelligent extraction (good)
patterns = extract_patterns(full_context)
relevant = select_relevant(patterns, task)
context = build_minimal(relevant)  # Only what's needed
```

**Key Difference**: Engineering extracts MEANING, truncation cuts TOKENS.

---

## The Engineering Process

### Step 1: Full Context Collection (User Level)

**Goal**: Gather ALL project information

```python
full_context = {
    "project": "peti",
    "files": [
        {"path": "app/auth.py", "content": "..."},
        {"path": "app/models/user.py", "content": "..."},
        # ... all files
    ],
    "claude_md": read_file("CLAUDE.md"),
    "project_md": read_file("project.md"),
    "file_structure": list_all_files(),
    "tech_stack": ["Python", "FastAPI", "SQLAlchemy"]
}
```

**Size**: Unlimited (typically 50-100K tokens for medium project)

### Step 2: Pattern Extraction (Opus Level)

**Goal**: Extract seed rules - patterns, conventions, architecture

```python
from context_distiller import SeedRuleExtractor

extractor = SeedRuleExtractor()
seed_rules = extractor.extract(full_context)
```

**What Gets Extracted**:

1. **Authentication Pattern** (from code analysis):
   ```python
   {
       "authentication": {
           "pattern": "JWT",  # Detected from "import jwt"
           "files": ["app/auth.py"],
           "conventions": [
               "Use @require_auth decorator",  # Detected from decorator usage
               "bcrypt for password hashing"   # Detected from "import bcrypt"
           ]
       }
   }
   ```

2. **Database Pattern** (from model files):
   ```python
   {
       "database": {
           "pattern": "SQLAlchemy ORM",  # Detected from "from sqlalchemy import"
           "files": ["app/models/"],
           "conventions": [
               "Base class for models",      # Detected from class inheritance
               "Alembic for migrations"      # Detected from alembic directory
           ]
       }
   }
   ```

3. **API Pattern** (from routes):
   ```python
   {
       "api_design": {
           "pattern": "FastAPI REST",  # Detected from "@router.post"
           "files": ["app/routes/"],
           "conventions": [
               "RESTful endpoints",           # Detected from route structure
               "Pydantic for validation"     # Detected from BaseModel usage
           ]
       }
   }
   ```

4. **Conventions** (from CLAUDE.md):
   ```python
   {
       "coding_style": [
           "Use type hints in Python",
           "Follow PEP 8 style guide"
       ],
       "testing": [
           "Write tests before implementation",
           "Use pytest framework"
       ]
   }
   ```

**Size**: 10-50K tokens (50% reduction typical)

### Step 3: Task Context Engineering (Sonnet Level)

**Goal**: Build task-specific context from seed rules

**Input**:
```python
task = {
    "task_id": "1.2",
    "action": "Add password reset endpoint",
    "description": "Add POST /auth/reset-password endpoint. Send reset email with token."
}
```

**Process**:
```python
from context_distiller import TaskContextEngineer

engineer = TaskContextEngineer()
task_context = engineer.engineer(seed_rules, task)
```

**Algorithm**:

1. **Match Keywords**: "password reset" + "auth" → authentication pattern
2. **Select Patterns**: Extract ONLY authentication pattern (ignore database, API)
3. **Select Files**: Get files from matched patterns
4. **Filter Conventions**: Only auth-related conventions

**Output**:
```python
{
    "task_id": "1.2",
    "action": "Add password reset endpoint",
    "relevant_seeds": {
        "authentication": {  # ONLY this pattern
            "pattern": "JWT with bcrypt",
            "conventions": ["Use @require_auth", "Hash passwords"]
        }
    },
    "files_to_read": [
        {"path": "app/auth.py", "reason": "Auth pattern"},
        {"path": "app/models/user.py", "reason": "Auth pattern"}
    ],
    "conventions": [
        "Use @require_auth decorator",
        "Hash passwords with bcrypt"
    ],
    "inline_context": "Add POST /auth/reset-password endpoint. Send reset email.",
    "validation": ["Endpoint accepts email", "Token generated", "Email sent"]
}
```

**Size**: 5-15K tokens (82% reduction from full context)

### Step 4: Step Context Extraction (Haiku Level)

**Goal**: Extract MINIMAL context for single step

**Input**:
```python
step = {
    "step_id": "1.2.1",
    "action": "Create password reset email template",
    "description": "Create HTML email template for password reset",
    "requirements": [
        "Include reset token link",
        "Match existing email style",
        "Add expiration notice (24h)"
    ],
    "location": "app/templates/emails/reset_password.html",
    "validation": ["File created", "Contains token placeholder", "Valid HTML"]
}
```

**Process**:
```python
from context_distiller import StepContextExtractor

extractor = StepContextExtractor()
step_context = extractor.extract(task_context, step)
```

**Algorithm**:

1. **Extract Action**: What to do
2. **Extract Requirements**: Minimal list
3. **Add Location**: Where to create
4. **Add Validation**: How to verify

**Output**:
```python
{
    "step_id": "1.2.1",
    "action": "Create password reset email template",
    "task": "Create HTML email template for password reset",
    "requirements": [
        "Include reset token link",
        "Match existing email style",
        "Add expiration notice (24h)"
    ],
    "validation": ["File created", "Contains token placeholder", "Valid HTML"],
    "location": "app/templates/emails/reset_password.html",
    "reference_file": "app/auth.py"  # Single most relevant file
}
```

**Size**: <2K tokens (97% reduction from full context)

---

## Engineering Strategies

### Strategy 1: Keyword Matching

**Use For**: Pattern selection

```python
def select_relevant_patterns(patterns, task_text):
    task_lower = task_text.lower()
    relevant = {}

    for pattern_name, pattern_data in patterns.items():
        # Match keywords
        if any(keyword in task_lower for keyword in pattern_name.lower().split("_")):
            relevant[pattern_name] = pattern_data

    return relevant
```

**Example**:
- Task: "Add password reset" → matches "authentication" (contains "password")
- Task: "Create user model" → matches "database" (contains "model")
- Task: "Add API endpoint" → matches "api_design" (contains "endpoint")

### Strategy 2: File Relevance

**Use For**: Selecting files to read

```python
def select_relevant_files(patterns, task_text):
    files = []

    for pattern_name, pattern_data in patterns.items():
        if is_relevant(pattern_name, task_text):
            for file_path in pattern_data["files"]:
                files.append({
                    "path": file_path,
                    "reason": f"Related to {pattern_name}",
                    "load_full": False  # Load specific sections only
                })

    return files
```

**Example**:
- Task: "Add auth" → files: ["app/auth.py", "app/models/user.py"]
- Task: "Add database" → files: ["app/database.py", "app/models/"]
- Task: "Add API route" → files: ["app/routes/"]

### Strategy 3: Convention Filtering

**Use For**: Selecting relevant conventions

```python
def select_relevant_conventions(conventions, task_text):
    relevant = []
    task_lower = task_text.lower()

    for category, items in conventions.items():
        # Check if category is relevant to task
        if any(keyword in task_lower for keyword in category.lower().split("_")):
            relevant.extend(items)

    return relevant
```

**Example**:
- Task: "Add API" → conventions: API design conventions only
- Task: "Write tests" → conventions: Testing conventions only
- Task: "Add code" → conventions: Coding style conventions

### Strategy 4: Token Limit Enforcement

**Use For**: Ensuring context fits model limits

```python
def trim_to_limit(context, token_limit):
    # Priority order:
    # 1. task_id, action (ALWAYS keep)
    # 2. inline_context (ALWAYS keep)
    # 3. files_to_read (reduce count)
    # 4. relevant_seeds (reduce detail)
    # 5. conventions (reduce count)

    trimmed = {
        "task_id": context["task_id"],
        "action": context["action"],
        "inline_context": context["inline_context"]
    }

    current_tokens = estimate_tokens(trimmed)

    # Add files (limit to top 3)
    if current_tokens < token_limit and "files_to_read" in context:
        trimmed["files_to_read"] = context["files_to_read"][:3]
        current_tokens = estimate_tokens(trimmed)

    # Add patterns (simplified)
    if current_tokens < token_limit and "relevant_seeds" in context:
        simplified = {
            name: {"pattern": data["pattern"]}
            for name, data in context["relevant_seeds"].items()
        }
        trimmed["relevant_seeds"] = simplified
        current_tokens = estimate_tokens(trimmed)

    # Add conventions (limit to top 5)
    if current_tokens < token_limit and "conventions" in context:
        trimmed["conventions"] = context["conventions"][:5]

    return trimmed
```

---

## Practical Examples

### Example 1: Simple Task

**Task**: "Add type hint to calculate_total function"

**Full Context**: 50,000 tokens
**Engineered Context**:
```python
{
    "task_id": "t1",
    "action": "Add type hints",
    "files_to_read": [
        {"path": "utils.py", "sections": ["calculate_total"]}
    ],
    "conventions": ["Use type hints in Python"],
    "inline_context": "Add type hints: parameters and return value"
}
```
**Size**: ~500 tokens (99% reduction!)

**Why So Small**: Task is simple, needs minimal context

### Example 2: Medium Task

**Task**: "Add pagination to /users endpoint"

**Full Context**: 50,000 tokens
**Engineered Context**:
```python
{
    "task_id": "t2",
    "action": "Add pagination to /users endpoint",
    "relevant_seeds": {
        "api_design": {
            "pattern": "FastAPI REST",
            "conventions": ["Use Pydantic schemas", "Return JSON"]
        },
        "database": {
            "pattern": "SQLAlchemy ORM",
            "conventions": ["Use session management"]
        }
    },
    "files_to_read": [
        {"path": "app/routes/users.py", "reason": "Endpoint definition"},
        {"path": "app/models/user.py", "reason": "User model"}
    ],
    "conventions": [
        "RESTful endpoints",
        "Use query parameters for pagination",
        "Return total count in response"
    ],
    "inline_context": "Add page and page_size query parameters. Default page_size: 20, max: 100."
}
```
**Size**: ~8,000 tokens (84% reduction)

**Why Medium**: Needs API + database patterns

### Example 3: Complex Task

**Task**: "Build complete authentication system with JWT, email verification, and password reset"

**Full Context**: 50,000 tokens
**Engineered Context**:
```python
{
    "task_id": "t3",
    "action": "Build authentication system",
    "relevant_seeds": {
        "authentication": {
            "pattern": "JWT with bcrypt",
            "conventions": [...]  # All auth conventions
        },
        "database": {
            "pattern": "SQLAlchemy ORM",
            "conventions": [...]  # User model conventions
        },
        "api_design": {
            "pattern": "FastAPI REST",
            "conventions": [...]  # API conventions
        },
        "email": {
            "pattern": "SMTP with templates",
            "conventions": [...]  # Email conventions
        }
    },
    "files_to_read": [
        {"path": "app/auth.py"},
        {"path": "app/models/user.py"},
        {"path": "app/routes/auth.py"},
        {"path": "app/email.py"}
    ],
    "conventions": [...]  # Many conventions
}
```
**Size**: ~25,000 tokens (50% reduction)

**Why Large**: Comprehensive task needs many patterns

---

## Validation & Quality

### Context Quality Metrics

```python
def validate_context_quality(context):
    checks = []

    # 1. Has required fields
    checks.append("task_id" in context)
    checks.append("action" in context)

    # 2. Within token limits
    tokens = estimate_tokens(context)
    checks.append(tokens < TARGET_LIMIT)

    # 3. Has relevant patterns
    checks.append(len(context.get("relevant_seeds", {})) > 0)

    # 4. Has file references
    checks.append(len(context.get("files_to_read", [])) > 0)

    return all(checks)
```

### Pattern Coverage

```python
def check_pattern_coverage(task, context):
    # Ensure all task keywords have matching patterns
    task_keywords = extract_keywords(task["action"])
    pattern_keywords = context["relevant_seeds"].keys()

    coverage = len(set(task_keywords) & set(pattern_keywords))
    total = len(task_keywords)

    return coverage / total  # Should be > 0.7
```

---

## Best Practices

### DO:
- ✅ Extract patterns, not raw code
- ✅ Match by keywords and semantics
- ✅ Prioritize essential information
- ✅ Trim by importance, not arbitrarily
- ✅ Validate output quality
- ✅ Test with real scenarios

### DON'T:
- ❌ Just truncate at token limit
- ❌ Include unrelated patterns
- ❌ Duplicate information
- ❌ Hardcode token limits (use adaptive limits)
- ❌ Skip validation
- ❌ Forget to update seed rules

---

## Common Patterns

### Pattern: Full Stack Feature

**Scenario**: Add complete feature (API + database + frontend)

**Engineering**:
```python
task_context = {
    "relevant_seeds": {
        "api_design": {...},
        "database": {...},
        "frontend": {...}  # If applicable
    },
    "files_to_read": [
        # API files
        # Model files
        # Frontend files (if applicable)
    ]
}
```

### Pattern: Bug Fix

**Scenario**: Fix specific bug in existing code

**Engineering**:
```python
task_context = {
    "relevant_seeds": {
        # ONLY the pattern related to buggy code
    },
    "files_to_read": [
        {"path": "buggy_file.py", "sections": ["buggy_function"]}
    ],
    "inline_context": "Fix: [description of bug]"
}
```

**Note**: Minimal context - just fix the bug

### Pattern: Refactoring

**Scenario**: Refactor code while maintaining behavior

**Engineering**:
```python
task_context = {
    "relevant_seeds": {
        # Pattern of code being refactored
    },
    "files_to_read": [
        # Files to refactor
        # Related test files
    ],
    "conventions": [
        # Code style conventions
        # Testing conventions
    ]
}
```

---

## Debugging Context Issues

### Problem: Context Too Large

**Symptoms**: Token limit exceeded

**Debug**:
```python
context = engineer.engineer(seed_rules, task)
tokens = estimate_tokens(context)
print(f"Total: {tokens} tokens")

# Check each component
for key in context:
    component_tokens = estimate_tokens(context[key])
    print(f"{key}: {component_tokens} tokens")
```

**Solution**: Reduce number of patterns, files, or conventions

### Problem: Missing Information

**Symptoms**: Agent says "not enough context"

**Debug**:
```python
# Check what patterns were selected
print("Selected patterns:", context["relevant_seeds"].keys())

# Check what files were included
print("Files:", [f["path"] for f in context["files_to_read"]])
```

**Solution**: Improve keyword matching or manually add pattern

### Problem: Irrelevant Information

**Symptoms**: Context includes unrelated patterns

**Debug**:
```python
# Check keyword matching
task_keywords = extract_keywords(task["action"])
for pattern in context["relevant_seeds"]:
    print(f"Pattern '{pattern}' matched keywords: {task_keywords}")
```

**Solution**: Improve keyword extraction or pattern naming

---

## Integration Example

### Full Workflow

```python
from fractal_memory import FractalMemory
from context_distiller import (
    distill_user_to_opus,
    distill_opus_to_sonnet,
    distill_sonnet_to_haiku
)

# Initialize
memory = FractalMemory()

# 1. Store full context (User level)
full_context = load_project("peti")
memory.store_project("peti", full_context)

# 2. Extract seed rules (Opus level)
seed_rules = memory.distill_to_opus("peti", distill_user_to_opus)
print(f"Seed rules: {estimate_tokens(seed_rules)} tokens")

# 3. Engineer task context (Sonnet level)
task = {
    "task_id": "1.2",
    "action": "Add password reset endpoint"
}
task_context = memory.distill_to_sonnet("peti", task, distill_opus_to_sonnet)
print(f"Task context: {estimate_tokens(task_context)} tokens")

# 4. Extract step context (Haiku level)
step = {
    "step_id": "1.2.1",
    "action": "Create email template"
}
step_context = memory.distill_to_haiku("1.2", step, distill_sonnet_to_haiku)
print(f"Step context: {estimate_tokens(step_context)} tokens")

# Agents use contexts
# OpusPlanner: Uses seed_rules
# SonnetCoder: Uses task_context
# HaikuExecutor: Uses step_context
```

---

**Status**: ✅ Foundational Process
**Used By**: All context operations
**Maintained**: Fractal infrastructure
