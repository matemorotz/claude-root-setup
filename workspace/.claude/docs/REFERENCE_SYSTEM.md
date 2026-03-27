# On-Demand Reference System

**Principle:** Keep core files small, reference details on-demand
**Mirrors:** Fractal memory architecture (orchestrator + memory)

---

## Core Concept

**Like fractal orchestration:**
```
Core files (small)      ↔  OpusPlanner (lightweight)
Referenced details      ↔  Memory system (stores details)
Read on-demand          ↔  Agents read when needed
```

**Files stay small, context loaded as needed**

---

## Core Files (Always Small)

### CLAUDE.md
```markdown
# Project Configuration

Quick overview (500 words max)

**Detailed references:**
- Architecture: @.claude/docs/architecture/
- Agents: @.claude/agents/
- Memory: @.claude/fractal/README.md
- Hooks: @.claude/docs/hooks/
```

**Size:** <2K tokens
**Load:** Always read at session start
**Details:** Referenced, not included

### project.md
```markdown
# Project Context

Goals, current state (1000 words max)

**Technical details:**
- Architecture: See @.claude/docs/architecture/ORCHESTRATOR_PATTERN.md
- Implementation: See @.claude/fractal/
- Patterns: See @.claude/docs/patterns/
```

**Size:** <3K tokens
**Load:** Read when needed
**Details:** Referenced with @file syntax

### state.md
```markdown
# Current State

Recent changes (summary only)

**Phase 1:** Complete ✅ (details: @.claude/docs/PHASE_1_SUMMARY.md)
**Phase 2:** Complete ✅ (details: @.claude/docs/PHASE_2_SUMMARY.md)
**Phase 3:** Complete ✅ (details: @state.md#phase-3-section)
```

**Size:** <5K tokens
**Load:** Read at session start
**Details:** Summarized, reference for full details

### todo.md
```markdown
# Current Tasks

Active items only (not history)

**Completed archive:**
See @.claude/docs/COMPLETED_TASKS.md
```

**Size:** <2K tokens
**Load:** Read when planning work
**Details:** Archive completed items

---

## Reference Patterns

### Pattern 1: @file Reference (Explicit)
```markdown
**Architecture details:**
See @.claude/docs/architecture/ORCHESTRATOR_PATTERN.md

When to read:
- Implementing orchestrator
- Understanding coordination
- Debugging orchestration flow
```

**Benefits:**
- Exact file path
- Agent can read when needed
- Core file stays small

### Pattern 2: Category Reference (Discovery)
```markdown
**All patterns:**
See @.claude/docs/patterns/

Files:
- DELEGATION.md
- VERIFICATION_LOOP.md
- ANTI_PATTERNS.md
```

**Benefits:**
- Explore multiple options
- Discover related concepts
- Flexible navigation

### Pattern 3: Inline Brief + Reference (Context)
```markdown
**Dependency triggering:** Post-task hook checks dependency graph
after task completion and marks dependent tasks as ready.

**Complete implementation:**
See @.claude/hooks/post-task.sh:191-226
See @.claude/docs/hooks/POST_TASK.md (detailed analysis)
```

**Benefits:**
- Enough context to understand
- Reference for implementation
- Reference for deep dive

### Pattern 4: Research Archive (Historical)
```markdown
**Broker comparison research:**
Archived: @research/mt5-trading/old-mt5-project/docs/EXTENDED_BROKER_COMPARISON.md

Read if: Re-evaluating broker choice
Skip if: Just using current system
```

**Benefits:**
- Available but not required
- Clear when to read
- Doesn't clutter core docs

---

## Reading Strategies

### Session Start (Load Core)
```
Read automatically:
├─ CLAUDE.md (project rules)
├─ state.md (current status)
└─ todo.md (active tasks)

Total: ~10K tokens

Don't load:
├─ Architecture docs (50K+ tokens)
├─ Research files (100K+ tokens)
└─ Implementation details
```

### Task Planning (Load Relevant)
```
Task: Implement new feature

Read on-demand:
├─ @.claude/docs/patterns/VERIFICATION_LOOP.md (pattern)
├─ @.claude/agents/sonnet-coder.md (agent spec)
└─ @.claude/fractal/CONTEXT_ENGINEERING.md (how to engineer context)

Total: ~20K tokens (task-specific)
```

### Debugging (Load Specific)
```
Issue: Hook not triggering dependencies

Read:
├─ @.claude/hooks/post-task.sh:191-226 (exact implementation)
├─ @.claude/docs/hooks/POST_TASK.md (detailed analysis)
└─ @.claude/docs/hooks/ENHANCEMENTS.md (known issues)

Total: ~15K tokens (problem-focused)
```

---

## Evolution Pattern

### Start: Simple References
```markdown
**Memory system:**
See @.claude/fractal/README.md
```

### Evolve: Categorized References
```markdown
**Memory system:**
- Overview: @.claude/fractal/README.md
- Implementation: @.claude/fractal/fractal_memory.py
- Testing: @.claude/fractal/test_fractal_flow.py
```

### Evolve: Contextual References
```markdown
**Memory system:**

Quick start:
@.claude/fractal/README.md#quick-start

Debugging:
@.claude/fractal/README.md#troubleshooting

API reference:
@.claude/fractal/fractal_memory.py (complete class)
```

### Evolve: Intelligent References
```markdown
**Memory system:**

For: Understanding concepts
Read: @.claude/docs/architecture/MEMORY_HIERARCHY.md

For: Implementing storage
Read: @.claude/fractal/fractal_memory.py

For: Debugging issues
Read: @.claude/docs/hooks/POST_TASK.md#memory-storage
```

---

## File Size Guidelines

| File Type | Max Size | Rationale |
|-----------|----------|-----------|
| CLAUDE.md | 2K tokens | Session start overhead |
| project.md | 3K tokens | Context overview |
| state.md | 5K tokens | Recent changes only |
| todo.md | 2K tokens | Active tasks only |
| Research | Unlimited | Read on-demand only |
| Architecture | 15K tokens | Complete logical unit |
| Patterns | 10K tokens | Reusable reference |
| Implementation | 15K tokens | Complete code guide |

**Principle:** If file grows too large:
1. Check: Is all content essential?
2. If no: Move details to referenced file
3. If yes: Keep it (completeness > size)

---

## Current Status

**Core files:** ✅ All small (<5K tokens)
**References:** ⚠️  Need to add more cross-references
**Orphans:** 14 large files not yet linked (ok for now)
**System:** Ready to evolve references as needed

---

## Benefits

**Like fractal orchestration:**
- Core stays lightweight (orchestrator)
- Details stored separately (memory)
- Load on-demand (agents read when needed)
- Scales infinitely (add references, not content)

**Practical:**
- Fast session starts
- Focused context loading
- No overwhelming files
- Easy to maintain

**Flexible:**
- Add references as needed
- No need to link everything immediately
- Evolve structure organically
- Support different use cases

---

## Summary

**Reference system = Memory system for documentation**

- Core files small (like OpusPlanner)
- Details separate (like memory levels)
- Read on-demand (like agent context loading)
- Evolve as needed (like seed rules learning)

**Result:** Scalable documentation that mirrors fractal code architecture
