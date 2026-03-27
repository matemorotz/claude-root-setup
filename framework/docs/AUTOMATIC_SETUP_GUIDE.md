# Automatic Project Setup Guide

**Version:** 2.0.0
**Date:** December 20, 2025
**Status:** Production Ready ✅

---

## Overview

The fractal orchestration system now **automatically initializes** new projects when you start a session. No manual setup required!

### What Happens Automatically

When you start a Claude session in a project directory:

1. **Detection:** System checks if project has CLAUDE.md (indicates Claude-managed project)
2. **Initialization Check:** Looks for `knowledge_graph.json` and seed rules
3. **Auto-Setup (if needed):** Runs the complete knowledge pipeline automatically
4. **Ready to Use:** Your project is now ready for hierarchical planning

**Time:** <5 minutes for first-time setup, instant for already-initialized projects

---

## How It Works

### Session Start Flow

```
User starts session in project directory
    ↓
session-start.sh hook runs automatically
    ↓
Looks for CLAUDE.md
    ↓
Project Found → Check initialization status
    ↓
┌─────────────┴───────────────┐
│                             │
NOT Initialized         Already Initialized
│                             │
↓                             ↓
Run Auto-Setup            Skip setup
[1/3] Build knowledge     Load seed rules
[2/3] Extract patterns    Return status JSON
[3/3] Distill seed rules
↓
✅ Initialization complete
```

### What Gets Created

**During automatic setup:**

1. **knowledge_graph.json** (Project root)
   - Complete code structure mapping
   - AST-based concept extraction
   - Dependency relationships

2. **extracted_patterns.json** (Project root)
   - 15+ pattern types detected
   - Architectural patterns
   - Coding conventions
   - File organization

3. **Seed Rules** (`.claude/memory/opus_level/seed_rules/[project-name].json`)
   - 4-level hierarchical rules
   - User/Opus/Sonnet/Haiku distillation
   - Ready for OpusPlanner

---

## User Experience

### First Session (New Project)

```bash
cd /path/to/my-new-project
# Session starts...
```

**You'll see:**
```
🚀 Detected new project - initializing fractal orchestration...
   This will take <5 minutes for the first-time setup...

   [1/3] Building knowledge graph...
   ✓ Knowledge graph created

   [2/3] Extracting patterns...
   ✓ Patterns extracted

   [3/3] Distilling seed rules...
   ✓ Seed rules created

✅ Fractal orchestration initialized for: my-new-project
   📁 Seed rules: .claude/memory/opus_level/seed_rules/my-new-project.json
```

### Subsequent Sessions (Already Initialized)

```bash
cd /path/to/my-new-project
# Session starts...
```

**You'll see:**
```
(Silent - no initialization needed)
```

**JSON Output:**
```json
{
  "project": {
    "name": "my-new-project",
    "initialized": true,
    "auto_setup_ran": false
  },
  "fractal": {
    "knowledge_graph": true,
    "seed_rules": true
  }
}
```

---

## Detection Logic

### Project is Considered "Uninitialized" if:

✓ Has `CLAUDE.md` (Claude-managed project)
AND
✗ Missing `knowledge_graph.json`
OR
✗ Missing `.claude/memory/opus_level/seed_rules/[project-name].json`

### Project is Considered "Initialized" if:

✓ Has `knowledge_graph.json`
✓ Has seed rules in `.claude/memory/opus_level/seed_rules/`

---

## Verification

### Check if Your Project is Initialized

```bash
# From project root:

# Check for knowledge graph
ls -lh knowledge_graph.json

# Check for patterns
ls -lh extracted_patterns.json

# Check for seed rules (replace [project-name])
ls -lh .claude/memory/opus_level/seed_rules/[project-name].json
```

### Query Your Knowledge Graph

```bash
python /root/software/.claude/scripts/knowledge-query.py \
    knowledge_graph.json \
    --search "authentication" \
    --format summary
```

### Validate Seed Rules

```bash
PROJECT_NAME=$(basename "$PWD")
python /root/software/.claude/scripts/rule-validator.py \
    --project "$PROJECT_NAME" \
    --dry-run
```

---

## Manual Re-initialization

If you want to force re-initialization (e.g., after major code changes):

### Option 1: Delete Artifacts

```bash
# Delete generated files
rm knowledge_graph.json
rm extracted_patterns.json
rm .claude/memory/opus_level/seed_rules/[project-name].json

# Next session will auto-initialize
```

### Option 2: Run Scripts Manually

```bash
PROJECT_NAME=$(basename "$PWD")

# Run knowledge pipeline
python /root/software/.claude/scripts/knowledge-indexer.py .
python /root/software/.claude/scripts/pattern-extractor.py knowledge_graph.json
python /root/software/.claude/scripts/rule-distiller.py \
    extracted_patterns.json \
    --project "$PROJECT_NAME" \
    --level all
```

---

## Error Handling

### Automatic Recovery

The setup script is **resilient** and continues even if individual steps fail:

```
[1/3] Building knowledge graph...
⚠ Knowledge graph creation failed (continuing anyway)

[2/3] Extracting patterns...
⚠ Pattern extraction failed (continuing anyway)

[3/3] Distilling seed rules...
⚠ Seed rule distillation failed
```

**Result:** Session still starts, but project may have partial initialization

### Common Issues

**Issue:** Knowledge graph creation fails
**Cause:** No Python files in project (empty project)
**Fix:** Add some code files, then delete `knowledge_graph.json` to trigger re-init

**Issue:** Pattern extraction fails
**Cause:** knowledge_graph.json missing or corrupt
**Fix:** Delete all artifacts and re-initialize

**Issue:** Seed rule distillation fails
**Cause:** extracted_patterns.json missing or corrupt
**Fix:** Delete all artifacts and re-initialize

---

## Configuration

### Hook Location

**File:** `/root/software/.claude/hooks/session-start.sh`
**Version:** 2.0.0
**Mode:** Automatic (runs on every session start)

### Scripts Used

Located in `/root/software/.claude/scripts/`:

1. `knowledge-indexer.py` (450 lines)
2. `pattern-extractor.py` (900+ lines)
3. `rule-distiller.py` (850+ lines)

### Output Locations

- **Knowledge Graph:** `knowledge_graph.json` (project root)
- **Patterns:** `extracted_patterns.json` (project root)
- **Seed Rules:** `.claude/memory/opus_level/seed_rules/[project-name].json`

---

## Performance

**First-Time Setup:**
- Small project (<100 files): <30 seconds
- Medium project (100-1000 files): 1-3 minutes
- Large project (>1000 files): 3-5 minutes

**Already Initialized:**
- Instant (just JSON status check)

---

## Benefits

✅ **Zero-friction onboarding** - New projects "just work"
✅ **Consistent behavior** - Every project gets the same setup
✅ **Idempotent** - Safe to run multiple times
✅ **Fast for existing projects** - Only runs once
✅ **Informative** - Clear progress indicators
✅ **Resilient** - Continues even if individual steps fail
✅ **Automatic** - No manual intervention needed

---

## Advanced Usage

### Disable Auto-Setup (if needed)

Edit `/root/software/.claude/hooks/session-start.sh` and comment out the auto-setup call:

```bash
# Auto-setup if needed (returns "true" or "false")
# auto_setup_ran=$(auto_setup_project "$project_path" "$project_name")
auto_setup_ran="false"  # Disabled
```

### Customize Setup Steps

Edit the `auto_setup_project()` function in `session-start.sh` to:
- Add custom pre/post-processing
- Change progress messages
- Add project-specific logic

---

## JSON Output Reference

The hook returns JSON with initialization status:

```json
{
  "version": "2.0.0",
  "timestamp": "2025-12-20T12:34:56Z",
  "project": {
    "name": "my-project",
    "path": "/root/software/my-project",
    "initialized": true,        // ← Project has full setup
    "auto_setup_ran": false     // ← Setup ran this session
  },
  "status": "Active Development",
  "pending_todos": 5,
  "fractal": {
    "knowledge_graph": true,    // ← knowledge_graph.json exists
    "seed_rules": true          // ← Seed rules exist
  },
  "files": {
    "claude_md": "/root/software/my-project/CLAUDE.md",
    "state_md": "/root/software/my-project/state.md",
    "todo_md": "/root/software/my-project/todo.md"
  },
  "context_loaded": true
}
```

---

## Related Documentation

- **Manual Setup Guide:** `/root/.claude/plans/whimsical-conjuring-hippo.md`
- **Complete Workflows:** `/root/software/.claude/fractal/COMPLETE_WORKFLOW_GUIDE.md`
- **Hierarchical Planning:** `/root/software/.claude/fractal/HIERARCHICAL_PLANNING_GUIDE.md`
- **Fractal Architecture:** `/root/software/.claude/fractal/README.md`

---

## Summary

**Automatic setup is now the default behavior.** Just create a project with CLAUDE.md and start a session - the system handles the rest!

**First session:** 3-5 minute setup
**All other sessions:** Instant

**No manual intervention required.**
