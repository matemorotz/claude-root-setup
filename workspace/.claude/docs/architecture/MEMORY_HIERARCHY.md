# Memory Hierarchy

**Source:** ORCHESTRATOR_SEPARATION_PRINCIPLE.md
**Section:** Memory stores details

---

### Memory System (Knowledge Repository)
**Role:** Store detailed context, plans, and execution state
**Storage:** File-based hierarchy (`.claude/memory/`)

```
Memory Hierarchy:
┌─────────────────────────────────────────────┐
│ user_level/                                 │
│   └── Full project context (unlimited)      │
│                                             │
│ opus_level/                                 │
│   └── Seed rules (10-50K tokens)            │
│                                             │
│ sonnet_level/                               │
│   └── Task contexts (5-15K tokens each)     │
│                                             │
│ haiku_level/                                │
│   └── Step contexts (<2K tokens each)       │
└─────────────────────────────────────────────┘

Execution agents READ from memory directly
OpusPlanner does NOT pass context
```



---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: ORCHESTRATOR_SEPARATION_PRINCIPLE.md](../ORCHESTRATOR_SEPARATION_PRINCIPLE.md)
