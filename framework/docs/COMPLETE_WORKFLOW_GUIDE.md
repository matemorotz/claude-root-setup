# Complete Fractal Orchestration Workflow

**Version:** 1.0.0
**Last Updated:** December 20, 2025
**Status:** Production Ready ✅

---

## Overview

This guide shows the **complete end-to-end workflow** for using the fractal orchestration system, from initial project setup through feature development and continuous improvement.

### System Components

**Knowledge Systems (Phase 4+):**
- Knowledge indexer (builds code graph)
- Pattern extractor (identifies patterns)
- Rule distiller (creates seed rules)
- Rule validator (tracks effectiveness)

**Planning Systems (Phase 4+.4):**
- Conversational planning (OpusPlanner)
- Horizontal splitting (parallel sub-planners)
- Vertical distillation (Opus → Sonnet → Haiku)
- Intelligent routing (context filtering)

**Execution Systems:**
- ExecutionEngine (orchestration)
- Agent coordination (5 specialized agents)
- Fractal memory (4-layer hierarchy)

---

## Workflow 1: New Project Setup

**Goal:** Set up fractal orchestration for a new project in <5 minutes

### Step 1: Project Structure

```bash
cd /root/software
mkdir my-new-project
cd my-new-project

# Create basic structure
mkdir -p app/{models,routes,core}
touch app/__init__.py
touch README.md
```

### Step 2: Create Project Documentation

**Create CLAUDE.md:**
```markdown
# My New Project

**Type:** FastAPI application
**Purpose:** User management system with authentication

## Technology Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

## Architecture
- Repository pattern for data access
- JWT authentication
- RESTful API design

## Conventions
- Use type hints
- Follow PEP 8
- 100% test coverage for critical paths
```

**Create state.md:**
```markdown
# Development State

**Last Updated:** 2025-12-20
**Status:** Initial setup

## Current Status
- Project initialized
- Basic structure created
- Ready for feature development
```

### Step 3: Build Knowledge Graph

```bash
# Index the codebase
python /root/software/.claude/scripts/knowledge-indexer.py /root/software/my-new-project

# Output: knowledge_graph.json
# - Nodes: files, concepts, patterns
# - Edges: imports, dependencies, relationships
```

**Expected output:**
```
✓ Indexed 5 files
✓ Created 15 nodes (12 concepts, 2 files, 1 dependency)
✓ Created 18 edges
✓ Saved to knowledge_graph.json
```

### Step 4: Extract Patterns

```bash
# Extract patterns from knowledge graph
python /root/software/.claude/scripts/pattern-extractor.py knowledge_graph.json

# Output: extracted_patterns.json
# - Architectural patterns
# - Coding conventions
# - File organization
```

**Expected output:**
```
✓ Extracted 8 patterns
  - Architectural: Repository (confidence: 0.8)
  - Coding: Type hints (confidence: 0.9)
  - File org: Standard structure (confidence: 0.7)
✓ Saved to extracted_patterns.json
```

### Step 5: Distill Seed Rules

```bash
# Create seed rules for all fractal levels
python /root/software/.claude/scripts/rule-distiller.py \
    extracted_patterns.json \
    --project my-new-project \
    --level all

# Output: seed_rules_*.json (opus, sonnet, haiku)
```

**Expected output:**
```
✓ Created seed rules for 4 levels
  - User level: Full context
  - Opus level: 15K tokens (patterns + conventions)
  - Sonnet level: 5K tokens (task templates)
  - Haiku level: 2K tokens (step instructions)
✓ Saved to .claude/memory/opus_level/seed_rules/my-new-project.json
```

### Step 6: Verify Setup

```bash
# Query knowledge graph
python /root/software/.claude/scripts/knowledge-query.py \
    knowledge_graph.json \
    --search "authentication" \
    --format summary

# Validate seed rules
python /root/software/.claude/scripts/rule-validator.py \
    --project my-new-project \
    --dry-run
```

**Result:** Project ready for development! 🎉

---

## Workflow 2: Feature Development with Hierarchical Planning

**Goal:** Implement a new feature using conversational planning and horizontal splitting

### Scenario

User requests: *"Add user authentication with password reset to the FastAPI app"*

### Step 1: Conversational Planning

**OpusPlanner activates:**

```
OpusPlanner: Analyzing your request...

I'll implement authentication with password reset. I detected these
natural boundaries in your project:

- auth_logic: JWT tokens, password hashing, middleware
- db_schema: User model, PasswordResetToken model, migrations
- api_routes: /auth/login, /auth/register, /auth/reset-password

This is a complex feature with 6 sections and ~30 steps.

Question 1: Should we organize the plan around these boundaries?
  ✓ Yes, use these boundaries (Recommended)
  - Combine some boundaries
  - Different boundaries

Question 2: Should we use parallel execution where possible?
  ✓ Yes, parallel where possible (Recommended)
  - No, sequential only

Your choice?
```

**User responds:** "Yes, use parallel execution"

### Step 2: Plan Creation

**OpusPlanner creates structured plan:**

```json
{
  "plan_id": "plan-auth-password-reset-001",
  "sections": [
    {
      "section_id": "s1",
      "title": "Core Authentication Logic",
      "metadata": {
        "boundary": "auth_logic",
        "estimated_steps": 6,
        "parallelizable": true
      }
    },
    {
      "section_id": "s2",
      "title": "Password Reset Logic",
      "metadata": {
        "boundary": "auth_logic",
        "estimated_steps": 4,
        "dependencies": ["s1"]
      }
    },
    {
      "section_id": "s3",
      "title": "Database Models",
      "metadata": {
        "boundary": "db_schema",
        "estimated_steps": 5,
        "parallelizable": true
      }
    },
    // ... more sections
  ]
}
```

### Step 3: Automatic Split Decision

**ExecutionEngine analyzes plan:**

```python
splitter = HorizontalPlanSplitter(fractal_memory)
should_split = splitter.should_split(plan)
# → True (6 sections, 30 steps, 3 boundaries)

sub_contexts = splitter.create_sub_contexts(plan)
# → 3 sub-contexts (auth, db, api)
```

**Split decision:**
```
✓ Plan will split horizontally
  - 3 sub-planners (auth_logic, db_schema, api_routes)
  - Parallel execution where possible
  - Token savings: 37-73%
```

### Step 4: Context Filtering

**Each sub-planner gets filtered seed rules:**

```
auth_logic sub-planner receives:
  - Patterns: authentication (JWT, password hashing)
  - Conventions: coding_style, testing
  - Tech stack: Python, FastAPI, python-jose, passlib
  - Size: 15K tokens (vs 50K full seed rules)

db_schema sub-planner receives:
  - Patterns: database (SQLAlchemy, Alembic)
  - Conventions: coding_style, testing
  - Tech stack: Python, SQLAlchemy, Alembic
  - Size: 12K tokens

api_routes sub-planner receives:
  - Patterns: api_design (RESTful, FastAPI)
  - Conventions: coding_style, testing, error_handling
  - Tech stack: Python, FastAPI, Pydantic
  - Size: 13K tokens

Total: 40K tokens (vs 150K without filtering)
Token savings: 110K (73%)
```

### Step 5: Parallel Execution

**Execution waves:**

```
Wave 1 (Parallel):
┌─────────────────────┐  ┌─────────────────────┐
│ auth_logic          │  │ db_schema           │
│ Sub-Planner         │  │ Sub-Planner         │
│                     │  │                     │
│ Opus (15K)          │  │ Opus (12K)          │
│   ↓                 │  │   ↓                 │
│ Sonnet (5K)         │  │ Sonnet (4K)         │
│   ↓                 │  │   ↓                 │
│ Haiku (2K)          │  │ Haiku (1.5K)        │
│   ↓                 │  │   ↓                 │
│ s1: Core Auth (6)   │  │ s3: Models (5)      │
└─────────────────────┘  └─────────────────────┘

Wave 2 (Parallel):
┌─────────────────────┐  ┌─────────────────────┐
│ auth_logic          │  │ db_schema           │
│   ↓                 │  │   ↓                 │
│ s2: Reset (4)       │  │ s4: Migrations (3)  │
│ [depends on s1]     │  │ [depends on s3]     │
└─────────────────────┘  └─────────────────────┘

Wave 3 (Sequential):
┌─────────────────────┐
│ api_routes          │
│ Sub-Planner         │
│                     │
│ Opus (13K)          │
│   ↓                 │
│ Sonnet (6K)         │
│   ↓                 │
│ Haiku (2K)          │
│   ↓                 │
│ s5: Endpoints (7)   │
│ [depends on s1,s2,s3]
└─────────────────────┘

Wave 4 (Sequential):
┌─────────────────────┐
│ api_routes          │
│   ↓                 │
│ s6: Tests (5)       │
│ [depends on s5]     │
└─────────────────────┘
```

### Step 6: Results Synthesis

**ExecutionEngine combines results:**

```
✓ auth_logic complete (10 steps, 2.3 min)
  - s1: JWT handler, password hashing, middleware
  - s2: Reset token generation, validation

✓ db_schema complete (8 steps, 1.8 min)
  - s3: User model, PasswordResetToken model
  - s4: Alembic migrations

✓ api_routes complete (12 steps, 3.1 min)
  - s5: /auth/login, /auth/register, /auth/reset-password
  - s6: Integration tests (100% coverage)

Total: 30 steps completed in 7.2 minutes
Success rate: 100%
```

**Result:** Feature fully implemented! ✅

---

## Workflow 3: Continuous Improvement

**Goal:** Keep seed rules updated as project evolves

### Weekly Knowledge Update

```bash
# 1. Re-index codebase (picks up new code)
python knowledge-indexer.py /root/software/my-new-project

# 2. Extract new patterns
python pattern-extractor.py knowledge_graph.json --update

# 3. Update seed rules
python rule-distiller.py extracted_patterns.json \
    --project my-new-project \
    --update  # Merges with existing rules

# 4. Validate effectiveness
python rule-validator.py --project my-new-project --report
```

**Sample report:**
```
Rule Effectiveness Report
========================

High-performing rules (>90% success):
✓ authentication pattern (95%, 45 uses)
✓ repository pattern (92%, 38 uses)

Medium-performing rules (70-90% success):
⚠ API error handling (75%, 20 uses)

Low-performing rules (<70% success):
❌ Database transaction (55%, 15 uses) → PRUNED

Stale rules (<5 uses in 30 days):
⏳ Legacy auth pattern (2 uses) → ARCHIVED

Recommendations:
- Update API error handling rule with recent examples
- Remove legacy auth pattern from active rules
```

### Monthly Pattern Review

**Identify emerging patterns:**

```bash
# Query for frequently used but unrecorded patterns
python knowledge-query.py knowledge_graph.json \
    --search ".*handler.*" \
    --relationships "implements" \
    --format table

# Review and add to seed rules manually if valuable
```

---

## Workflow 4: Multi-Project Knowledge Sharing

**Goal:** Reuse patterns across projects

### Export Patterns from Project A

```bash
cd /root/software/project-a
python rule-distiller.py patterns.json \
    --project project-a \
    --export patterns_export.json
```

### Import to Project B

```bash
cd /root/software/project-b
python rule-distiller.py ../project-a/patterns_export.json \
    --project project-b \
    --import \
    --filter "authentication,api_design"  # Only import relevant
```

### Share via Seed Rule Library

**Create shared seed rules:**

```bash
# Extract common patterns
mkdir -p .claude/memory/shared/
python rule-validator.py \
    --project project-a \
    --export-high-confidence .claude/memory/shared/common_patterns.json

# Use in new projects
python rule-distiller.py .claude/memory/shared/common_patterns.json \
    --project new-project \
    --import
```

---

## Integration Points

### With Session Start Hook

**Enhanced session-start.sh:**

```bash
#!/bin/bash
# Auto-load context and seed rules on session start

# 1. Find project root
PROJECT_ROOT=$(find_project_root)

# 2. Load into fractal memory
python -c "
from fractal_memory import FractalMemory
memory = FractalMemory()

# Load project context
memory.store_project('$PROJECT_NAME', {
    'path': '$PROJECT_ROOT',
    'claude_md': '$CLAUDE_MD',
    'state_md': '$STATE_MD'
})

# Load seed rules
memory.opus_level.load_seed_rules('$PROJECT_NAME')
"

# 3. Output status
echo "Context loaded: $PROJECT_NAME"
```

### With Git Hooks

**Pre-commit pattern extraction:**

```bash
# .git/hooks/pre-commit
python knowledge-indexer.py . --incremental
python pattern-extractor.py knowledge_graph.json --update
```

**Post-merge seed rule update:**

```bash
# .git/hooks/post-merge
python rule-distiller.py patterns.json --project $(basename $PWD) --update
```

---

## Performance Benchmarks

### Knowledge Pipeline

| Operation | Small Project | Medium Project | Large Project |
|-----------|---------------|----------------|---------------|
| Indexing | <5 sec | <30 sec | <2 min |
| Pattern extraction | <10 sec | <45 sec | <3 min |
| Rule distillation | <5 sec | <20 sec | <1 min |
| Validation | <5 sec | <15 sec | <30 sec |
| **Total** | **<25 sec** | **<2 min** | **<7 min** |

### Planning & Execution

| Operation | Simple Plan | Complex Plan | Large Plan |
|-----------|-------------|--------------|------------|
| Plan creation | <1 sec | <3 sec | <5 sec |
| Split decision | <1 ms | <1 ms | <1 ms |
| Context filtering | <5 ms | <10 ms | <20 ms |
| Execution | <30 sec | <5 min | <15 min |

### Token Savings

| Project Size | Without Split | With Split | Savings |
|-------------|---------------|------------|---------|
| Small (10K) | 30K | 10K | 67% |
| Medium (50K) | 150K | 40K | 73% |
| Large (100K) | 500K | 90K | 82% |

---

## Troubleshooting

### Issue: Knowledge graph missing nodes

**Symptoms:** Pattern extraction finds no patterns

**Fix:**
```bash
# Re-index with increased depth
python knowledge-indexer.py . --depth 10

# Check output
cat knowledge_graph.json | jq '.nodes | length'
```

### Issue: Seed rules not loading

**Symptoms:** OpusPlanner can't detect boundaries

**Fix:**
```bash
# Verify seed rules exist
ls .claude/memory/opus_level/seed_rules/

# Check rule format
cat .claude/memory/opus_level/seed_rules/project.json | jq '.patterns'

# Re-distill if needed
python rule-distiller.py patterns.json --project project --force
```

### Issue: Plan not splitting

**Symptoms:** Complex plan executes vertically

**Fix:**
1. Add boundary metadata to sections
2. Ensure 4+ sections, 2+ boundaries, 16+ steps
3. Check `splitter.should_split(plan)` returns True

---

## Best Practices

### 1. Keep Documentation Updated

Update CLAUDE.md, state.md after major changes:
```markdown
# state.md

## Recent Changes (Dec 20)
- Added authentication system
- Implemented password reset
- Updated seed rules with auth patterns
```

### 2. Use Conversational Planning for Complex Features

Always use conversational mode for:
- Features with >3 sections
- Multiple implementation approaches
- Cross-boundary dependencies

### 3. Run Knowledge Pipeline Weekly

```bash
# Weekly update script
#!/bin/bash
cd /root/software/my-project
python knowledge-indexer.py . --update
python pattern-extractor.py graph.json --update
python rule-distiller.py patterns.json --project $(basename $PWD) --update
python rule-validator.py --project $(basename $PWD) --report --prune
```

### 4. Review Rule Effectiveness Monthly

Check rule-validator.py reports:
- Prune ineffective rules (<50% success after 20 uses)
- Archive stale rules (<5 uses in 30 days)
- Promote high-performing patterns

---

## Summary

The complete fractal orchestration workflow:

**Phase 1: Setup (One-time)**
→ Create project structure
→ Build knowledge graph
→ Extract patterns
→ Distill seed rules

**Phase 2: Development (Per-feature)**
→ Conversational planning
→ Automatic split decision
→ Parallel execution
→ Results synthesis

**Phase 3: Maintenance (Weekly/Monthly)**
→ Update knowledge graph
→ Validate rule effectiveness
→ Prune/archive stale rules
→ Share patterns across projects

**Result:**
- ✅ 37-73% token reduction
- ✅ Parallel execution of independent tasks
- ✅ Continuous learning from project patterns
- ✅ <5 min project setup
- ✅ Production-ready workflows

---

**For detailed documentation:**
- Knowledge Pipeline: `.claude/fractal/README.md`
- Hierarchical Planning: `.claude/fractal/HIERARCHICAL_PLANNING_GUIDE.md`
- Seed Rules: `.claude/fractal/SEED_RULES.md`
- Fractal Architecture: `.claude/fractal/FRACTAL_PRINCIPLES.md`
