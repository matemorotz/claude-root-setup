# What Is Fractal

**Source:** ORCHESTRATOR_SEPARATION_PRINCIPLE.md
**Section:** Core Concept

---

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

---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: ORCHESTRATOR_SEPARATION_PRINCIPLE.md](../ORCHESTRATOR_SEPARATION_PRINCIPLE.md)
