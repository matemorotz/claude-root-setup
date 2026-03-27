# Fractal Orchestration Documentation

**Structure:** Hierarchical graph of small, cross-referenced files
**Philosophy:** Apply fractal principles to documentation itself

---

## Documentation Principles

### 1. Context-Engineered File Sizes
Each file is a complete logical unit optimized for agent context windows.

**Not too small:** Avoid needing to read 10 files for one concept
**Not too large:** Avoid overwhelming agent context windows

**Target sizes:**
- **Quick Reference (Level 1):** <2K tokens (~500 words) - HaikuExecutor optimized
- **Conceptual Docs (Level 2):** 5-15K tokens (~1,500-4,000 words) - SonnetCoder optimized
- **Implementation (Level 3):** 5-15K tokens - Complete practical guide
- **API Reference (Level 4):** 10-50K tokens - OpusPlanner strategic reference

**Benefits:**
- Complete logical units (one file = one complete concept)
- Agent-optimized (matches model context limits)
- Efficient context engineering (no need to assemble from multiple files)
- Fast loading (read once, have full context)

### 2. Hierarchical Organization
```
docs/
├── INDEX.md (navigation root)
├── overview/ (concepts)
├── architecture/ (design)
├── guides/ (how-to)
├── agents/ (implementations)
├── memory/ (storage)
├── hooks/ (lifecycle)
├── patterns/ (reusable)
└── integration/ (external)
```

### 3. Cross-References
Every file links to:
- Parent category index
- Related concepts
- Source documents (if extracted)
- Implementation details

### 4. Bidirectional Links
If A references B, B should reference A back.

**Example:**
- `architecture/ORCHESTRATOR_PATTERN.md` → links to `patterns/DELEGATION.md`
- `patterns/DELEGATION.md` → links back to `architecture/ORCHESTRATOR_PATTERN.md`

---

## Navigation

**Start here:**
1. Read [INDEX.md](INDEX.md) - Main navigation
2. Choose category (overview/architecture/guides)
3. Read category INDEX.md
4. Follow links to detailed topics

**Quick access:**
- New users → [overview/WHAT_IS_FRACTAL.md](overview/WHAT_IS_FRACTAL.md)
- Implementers → [architecture/INDEX.md](architecture/INDEX.md)
- Integration → [integration/INDEX.md](integration/INDEX.md)

---

## File Naming Convention

**Pattern:** `CATEGORY/TOPIC_NAME.md`

**Examples:**
- `overview/WHAT_IS_FRACTAL.md` - Core concept
- `architecture/ORCHESTRATOR_PATTERN.md` - Design pattern
- `guides/QUICK_START.md` - Practical guide
- `patterns/ANTI_PATTERNS.md` - What NOT to do

**INDEX.md:**
Every category has `INDEX.md` with:
- Category overview (1-2 paragraphs)
- List of files in category
- Links to related categories

---

## Size Guidelines (Context-Engineered)

| File Type | Target Tokens | Target Words | Agent | Purpose |
|-----------|---------------|--------------|-------|---------|
| Quick Ref | <2K | ~500 | Haiku | Fast lookup |
| Concept | 5-15K | 1,500-4,000 | Sonnet | Complete idea |
| Guide | 5-15K | 1,500-4,000 | Sonnet | Full tutorial |
| API Ref | 10-50K | 3,000-12,000 | Opus | Strategic reference |
| INDEX.md | <500 | ~150 | All | Navigation |

**Principle:** One file = one complete logical unit

**Examples:**
- "What is Fractal?" → 2K tokens (complete overview)
- "How Memory Works" → 8K tokens (complete conceptual model)
- "Memory Implementation" → 12K tokens (complete code guide)
- "Memory API Reference" → 35K tokens (all methods documented)

**If file grows beyond upper limit:**
1. Check: Is this really one logical unit?
2. If yes: Keep it (completeness > arbitrary size)
3. If no: Split into separate logical units
4. Create index linking sub-units

---

## Graph Visualization

```
┌─────────────────┐
│   INDEX.md      │ ← Entry point
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
 overview  architecture guides  patterns
    │         │         │          │
    ├── WHAT  ├── ORCH  ├── QUICK  ├── VERIFY
    ├── WHY   ├── MEM   ├── PLAN   ├── DELEG
    └── TERM  └── CTX   └── DEBUG  └── ANTI
```

**Each node:**
- Small focused file
- Links to related nodes
- Part of hierarchical graph

---

## Maintenance

### Adding New Documentation

1. **Choose category** - Where does it belong?
2. **Create focused file** - One topic, <1000 words
3. **Add to category INDEX.md** - Update file list
4. **Cross-reference** - Link to/from related docs
5. **Validate links** - Ensure no broken references

### Updating Existing Documentation

1. **Read current file** - Understand context
2. **Make focused changes** - Keep scope small
3. **Update cross-references** - Fix affected links
4. **Check file size** - Split if growing too large

### Splitting Large Files

```bash
# Use reorganization script
python .claude/scripts/reorganize-docs.py

# Or manually:
# 1. Identify sections
# 2. Create new category/file
# 3. Move section content
# 4. Add cross-references
# 5. Archive original
```

---

## Migration Status

**Completed:**
- ✅ Created directory structure (8 categories)
- ✅ Generated category INDEX files
- ✅ Split ORCHESTRATOR_SEPARATION_PRINCIPLE.md → 6 files
- ✅ Split CONTEXT_ENGINEERING_DELEGATION.md → 3 files
- ✅ Split AGENT_COORDINATION_PATTERN.md → 2 files
- ✅ Split TASK_HOOKS_ANALYSIS.md → 5 files

**Original files:** Kept in `.claude/docs/` root for reference

**Total:** 20 focused documentation files created

---

## Benefits Achieved

**Before:**
- 6 large files (12K-31K words)
- Hard to navigate
- Overwhelming to read
- Difficult to maintain

**After:**
- 20 focused files (<1000 words each)
- Easy navigation via indexes
- Quick to find specific topics
- Simple to update individual concepts

**Fractal graph:**
- Hierarchical organization
- Cross-referenced knowledge
- Scalable structure
- Self-documenting

---

## Next Steps

1. **Fill remaining files** - Create content for empty guides
2. **Add examples** - Code samples for each pattern
3. **Generate graph** - Visual navigation diagram
4. **Validate links** - Automated link checker
5. **Index search** - Quick topic finder

---

**Structure:** Fractal documentation mirrors fractal code architecture
**Result:** Knowledge organized like memory - hierarchical and cross-referenced
