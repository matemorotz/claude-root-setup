# Fractal Orchestration - Documentation Index

**Purpose:** Hierarchical navigation of all system documentation
**Structure:** Fractal graph - small focused files with cross-references

---

## Quick Navigation

**New user?** Start here:
- [System Overview](overview/WHAT_IS_FRACTAL.md) - Core concepts (5min read)
- [Quick Start](guides/QUICK_START.md) - Get running (10min)

**Implementing?** Core references:
- [Architecture](architecture/INDEX.md) - System design patterns
- [Agents](agents/INDEX.md) - Agent specifications
- [Memory](memory/INDEX.md) - Fractal memory system
- [Hooks](hooks/INDEX.md) - Lifecycle management

**Advanced topics:**
- [Patterns](patterns/INDEX.md) - Design patterns library
- [Integration](integration/INDEX.md) - External systems

---

## Documentation Hierarchy

```
.claude/docs/
├── INDEX.md (this file)
│
├── overview/
│   ├── WHAT_IS_FRACTAL.md          ← Core concept (500 words)
│   ├── WHY_FRACTAL.md              ← Benefits & rationale
│   └── TERMINOLOGY.md              ← Glossary
│
├── architecture/
│   ├── INDEX.md                    ← Architecture overview
│   ├── ORCHESTRATOR_PATTERN.md     ← Lightweight orchestrator
│   ├── MEMORY_HIERARCHY.md         ← 4-layer memory
│   ├── CONTEXT_ENGINEERING.md      ← Context distillation
│   └── AGENT_COORDINATION.md       ← Parent-verifies-child
│
├── guides/
│   ├── QUICK_START.md              ← Get started fast
│   ├── CREATING_PLANS.md           ← Plan structure
│   ├── RUNNING_EXECUTION.md        ← Execute plans
│   └── DEBUGGING.md                ← Troubleshooting
│
├── agents/
│   ├── INDEX.md                    ← Agent catalog
│   ├── opus-planner/               ← Per-agent details
│   ├── sonnet-coder/
│   ├── haiku-executor/
│   └── patterns/                   ← Reusable agent patterns
│
├── memory/
│   ├── INDEX.md                    ← Memory system overview
│   ├── USER_LEVEL.md               ← Full context storage
│   ├── OPUS_LEVEL.md               ← Seed rules
│   ├── SONNET_LEVEL.md             ← Task contexts
│   └── HAIKU_LEVEL.md              ← Step contexts
│
├── hooks/
│   ├── INDEX.md                    ← Hooks overview
│   ├── PRE_TASK.md                 ← Pre-task lifecycle
│   ├── POST_TASK.md                ← Post-task lifecycle
│   └── ENHANCEMENTS.md             ← Production features
│
├── patterns/
│   ├── INDEX.md                    ← Pattern library
│   ├── VERIFICATION_LOOP.md        ← Verify→Execute→Verify
│   ├── DELEGATION.md               ← Delegate heavy work
│   ├── DEPENDENCY_GRAPH.md         ← Task dependencies
│   └── ANTI_PATTERNS.md            ← What NOT to do
│
└── integration/
    ├── INDEX.md                    ← Integration guide
    ├── CLI.md                      ← orchestrate command
    ├── REPLANNING.md               ← Dynamic re-planning
    └── TESTING.md                  ← Test strategies
```

---

## Document Size Guidelines

**Index files:** <200 words (navigation only)
**Concept files:** 200-500 words (one idea)
**Guide files:** 500-1000 words (practical steps)
**Reference files:** 1000-2000 words (complete API)

**Large files → Split into:**
- Index (short overview + links)
- Concepts (individual topics)
- Examples (code samples)
- Deep dives (implementation details)

---

## Cross-Reference Format

**Link to related docs:**
```markdown
See also:
- [Context Engineering](../architecture/CONTEXT_ENGINEERING.md)
- [OpusPlanner Agent](../agents/opus-planner/README.md)
- [Memory Hierarchy](../memory/INDEX.md)
```

**Bidirectional linking:**
Every referenced document should link back to referrer

---

## Status

- [ ] Reorganize large files (>2000 words)
- [ ] Create index files for each category
- [ ] Add cross-references
- [ ] Validate all links
- [ ] Generate graph visualization

---

**Next:** Run reorganization script to create structure
