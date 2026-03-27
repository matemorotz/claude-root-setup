# Dynamic Re-planning Module

**Purpose:** Adaptive orchestration - adjust plans based on execution progress
**Version:** 1.0.0
**Agent:** OpusPlanner extension

---

## Core Concept

Monitor execution → Detect blockers → Regenerate affected sections → Resume

**Lightweight:** Orchestrator monitors state files, delegates re-planning to fresh agents

---

## Blocker Detection

```python
# Check .claude/state/agents/*/*.start files
# If task.start older than 5min → blocker detected
```

**Triggers:**
- Task stuck >5min
- Dependency failed
- Tests failing repeatedly
- Resource exhaustion

---

## Re-planning Process

1. **Detect:** Read state markers (lightweight)
2. **Analyze:** Identify affected tasks (lightweight)
3. **Delegate:** Spawn fresh OpusPlanner for re-plan
4. **Merge:** Update plan in memory (file operation)
5. **Resume:** Continue execution

**OpusPlanner stays lightweight - never loads full context for debugging**

---

## Implementation

### Monitor Progress
```bash
# Read state files
for start_file in .claude/state/agents/*/*.start; do
  started=$(jq -r '.started_at' "$start_file")
  now=$(date -u +%s)
  elapsed=$((now - started))
  if [ $elapsed -gt 300 ]; then
    echo "BLOCKER: $start_file stuck for ${elapsed}s"
  fi
done
```

### Regenerate Section
```python
# Spawn fresh planner
Task(
    subagent_type="opus-planner",
    prompt=f"Re-plan section {section_id} due to blocker",
    run_in_background=True
)
```

### Merge Updated Plan
```bash
# Replace section in plan
jq ".sections[] |= if .section_id == \"s2\" then $new_section else . end" \
  .claude/memory/opus_level/plans/plan-001.json > temp.json
mv temp.json .claude/memory/opus_level/plans/plan-001.json
```

---

## Storage

**Re-planning log:** `.claude/memory/opus_level/re-planning-log.jsonl`

```jsonl
{"timestamp": "2025-12-16T20:00:00Z", "plan_id": "p1", "section": "s2", "reason": "dependency_failed"}
```

**Plan versions:** `.claude/memory/opus_level/plans/{plan_id}/versions/`

---

**Status:** ✅ Specification complete
**Next:** Implement in execute-plan.py
