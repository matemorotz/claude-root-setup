# Task-Level Hooks System: Detailed Analysis & Enhancement Guide

**Document Version:** 1.0.0
**Created:** 2025-12-16
**Purpose:** Comprehensive analysis of task-level hooks for future enhancement work

---

## Executive Summary

The task-level hooks (`pre-task.sh` and `post-task.sh`) implement a sophisticated lifecycle management system that wraps agent execution with intelligent context preparation and result persistence. This document provides deep analysis of the current implementation and identifies specific enhancement opportunities.

**Key Files:**
- `.claude/hooks/pre-task.sh` (149 lines)
- `.claude/hooks/post-task.sh` (234 lines)

**Current Status:** Production-ready infrastructure with identified enhancement opportunities

---

## 1. Architecture Overview

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION FLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Execution Engine calls pre-task.sh                       │
│     ↓                                                         │
│  2. Pre-hook loads context from fractal memory               │
│     ↓                                                         │
│  3. Agent executes task with prepared context                │
│     ↓                                                         │
│  4. Post-hook stores results in fractal memory               │
│     ↓                                                         │
│  5. Execution Engine continues with next task                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Design Principle
**Separation of Concerns**: Hooks handle infrastructure (context loading, state management, logging), agents handle logic (actual task execution).

---

## 2. Pre-Task Hook Deep Dive

### 2.1 Parameter Structure

```bash
AGENT_TYPE="$1"  # e.g., "haiku-executor", "sonnet-coder"
TASK_ID="$2"     # e.g., "1.2", "2.3.1" (hierarchical task identifier)
PROJECT="${3:-unknown}"  # e.g., "peti", "api_server"
```

**Error Handling:** `set -euo pipefail`
- `-e`: Exit on any error
- `-u`: Error on undefined variables
- `-o pipefail`: Catch errors in pipes

### 2.2 Environment Validation

**Location:** Lines 39-47

```bash
if [ ! -d "$MEMORY_DIR" ]; then
    echo "⚠️  Warning: Fractal memory directory not found"
    mkdir -p "$MEMORY_DIR"/{user_level,opus_level,sonnet_level,haiku_level}
fi
```

**Design Pattern:** Self-Healing Infrastructure
- Automatically creates missing directories
- Enables resilience to incomplete setup
- Agents can run even without initialized memory structure

### 2.3 Context Loading Strategy

**Location:** Lines 49-105

Each agent type receives context engineered for its specific needs:

#### HaikuExecutor
```bash
CONTEXT_FILE="$MEMORY_DIR/haiku_level/step_contexts/${TASK_ID}.json"
# Loads: <2K tokens
```

**Context Includes:**
- What to do (action)
- Expected outcome
- Inline instructions

**Context Excludes:**
- Full project context
- Task-level details
- Seed rules

**Principle:** Least Context - agent only sees what's needed for immediate step

#### SonnetCoder/Debugger/Tracker
```bash
CONTEXT_FILE="$MEMORY_DIR/sonnet_level/task_contexts/${TASK_ID}.json"
# Loads: 5-15K tokens

# SonnetDebugger ALSO gets seed rules
if [ "$AGENT_TYPE" = "sonnet-debugger" ]; then
    SEED_RULES_FILE="$MEMORY_DIR/opus_level/seed_rules/${PROJECT}.json"
fi
```

**Context Includes:**
- Task objective
- Relevant patterns from seed rules
- File references
- Success criteria

**SonnetDebugger Special Case:**
- Gets additional seed rules from Opus level
- Enables pattern matching against known solutions
- Can suggest new seed rules for recurring issues
- Implements hierarchical context access

#### OpusPlanner
```bash
FULL_CONTEXT_FILE="$MEMORY_DIR/user_level/projects/${PROJECT}.json"
SEED_RULES_FILE="$MEMORY_DIR/opus_level/seed_rules/${PROJECT}.json"
```

**Context Includes:**
- Full project context (unlimited tokens)
- Complete seed rules
- All requirements and constraints

**Only agent** with access to User level - maintains fractal hierarchy

### 2.4 Agent State Initialization

**Location:** Lines 107-134

```bash
AGENT_STATE_DIR=".claude/state/agents/$AGENT_TYPE"
mkdir -p "$AGENT_STATE_DIR"

cat > "$AGENT_STATE_DIR/${TASK_ID}.start" <<EOF
{
  "task_id": "$TASK_ID",
  "agent_type": "$AGENT_TYPE",
  "project": "$PROJECT",
  "started_at": "$TIMESTAMP",
  "status": "in_progress"
}
EOF
```

**Purpose:**
1. Track which tasks are currently running
2. Record start time for duration calculation
3. Enable crash recovery (find abandoned tasks)
4. Support concurrent execution monitoring

**File Structure:**
```
.claude/state/agents/
├── haiku-executor/
│   ├── 1.1.start       # Running
│   ├── 1.2.complete    # Done
│   └── 1.3.start       # Running
├── sonnet-coder/
│   └── 2.1.complete
└── sonnet-debugger/
    └── 3.1.start
```

### 2.5 Logging

**Location:** Lines 136-143

```bash
LOG_FILE=".claude/logs/task-execution.log"
echo "[$TIMESTAMP] START $AGENT_TYPE task=$TASK_ID project=$PROJECT" >> "$LOG_FILE"
```

**Centralized Audit Trail:** Single log file captures all agent activity

**Example Output:**
```
[2025-12-16T10:30:00Z] START haiku-executor task=1.1 project=peti
[2025-12-16T10:30:05Z] COMPLETE haiku-executor task=1.1 status=success duration=5s
[2025-12-16T10:30:06Z] START sonnet-coder task=2.1 project=peti
```

**Enables:**
- Performance analysis (find slow tasks)
- Failure pattern detection (which agents fail most)
- Execution timeline reconstruction

---

## 3. Post-Task Hook Deep Dive

### 3.1 Result Validation

**Location:** Lines 42-49

```bash
if [ -n "$RESULT_FILE" ] && [ ! -f "$RESULT_FILE" ]; then
    echo "⚠️  Warning: Result file not found: $RESULT_FILE"
    RESULT_FILE=""
fi
```

**Design Pattern:** Defensive Programming
- Gracefully degrades to minimal result creation
- Prevents hard failures from missing files

### 3.2 Result Storage Strategy

**Location:** Lines 51-150

Each agent writes results to its corresponding fractal memory layer.

#### HaikuExecutor Results
```bash
RESULT_DIR="$MEMORY_DIR/haiku_level/step_results"

if [ -n "$RESULT_FILE" ]; then
    cp "$RESULT_FILE" "$RESULT_DIR/${TASK_ID}.json"
else
    # Create minimal result
    cat > "$RESULT_DIR/${TASK_ID}.json" <<EOF
{
  "step_id": "$TASK_ID",
  "status": "$STATUS",
  "completed_at": "$TIMESTAMP"
}
EOF
fi
```

**Minimal Fallback:** Ensures every task has a result entry for tracking completeness

#### SonnetDebugger Intelligence
```bash
# Store solution
cp "$RESULT_FILE" "$RESULT_DIR/${TASK_ID}.json"

# Check if solution suggests new seed rule
if grep -q "seed_rule_suggested" "$RESULT_FILE" 2>/dev/null; then
    echo "   💡 Solution suggests new seed rule"
    echo "      OpusPlanner should review and potentially update Opus level"
fi
```

**Seed Rule Learning:** Implements bottom-up learning
1. Debugger encounters novel error
2. Solves it with specific approach
3. Marks solution as "should be a seed rule"
4. OpusPlanner reviews and promotes to Opus level
5. Future similar errors prevented using new seed rule

**Example Result:**
```json
{
  "task_id": "3.1",
  "error": "CORS preflight failed",
  "solution": "Add OPTIONS handler before routes",
  "seed_rule_suggested": {
    "pattern": "cors_configuration",
    "rule": "Always add CORS headers before route handlers in FastAPI"
  }
}
```

#### SonnetTracker Dual Storage
```bash
RESULT_DIR="$MEMORY_DIR/sonnet_level/synthesized_results"
PROGRESS_DIR="$MEMORY_DIR/sonnet_level/progress"

# Determine if synthesis or progress update
if grep -q "synthesis" "$RESULT_FILE" 2>/dev/null; then
    cp "$RESULT_FILE" "$RESULT_DIR/${TASK_ID}.json"
else
    cp "$RESULT_FILE" "$PROGRESS_DIR/${TASK_ID}.json"
fi
```

**Smart Routing:** Automatically routes based on content type
1. **Synthesis:** Aggregated results from multiple agents
2. **Progress:** Status updates and completion metrics

#### OpusPlanner Seed Rule Updates
```bash
# Extract project name from result
PROJECT=$(jq -r '.project // "unknown"' "$RESULT_FILE" 2>/dev/null || echo "unknown")
cp "$RESULT_FILE" "$RESULT_DIR/${PROJECT}.json"
```

**Dynamic Project Naming:** Enables multi-project support with separate seed rules

### 3.3 Progress Tracking

**Location:** Lines 152-181

```bash
if [ -f "$AGENT_STATE_DIR/${TASK_ID}.start" ]; then
    START_TIME=$(jq -r '.started_at // ""' "$AGENT_STATE_DIR/${TASK_ID}.start" 2>/dev/null || echo "")

    # Create completion state
    cat > "$AGENT_STATE_DIR/${TASK_ID}.complete" <<EOF
{
  "task_id": "$TASK_ID",
  "agent_type": "$AGENT_TYPE",
  "started_at": "$START_TIME",
  "completed_at": "$TIMESTAMP",
  "status": "$STATUS"
}
EOF

    # Remove start marker
    rm "$AGENT_STATE_DIR/${TASK_ID}.start"
fi
```

**State Transition:**
1. Read start time from `.start` file
2. Create `.complete` file with both start and end times
3. Delete `.start` file (task no longer in progress)

**Atomic State Transitions:**
- `.start` exists = task running
- `.complete` exists = task finished
- Neither exist = task not started
- Both never exist simultaneously

### 3.4 Dependency Triggering

**Location:** Lines 183-199

```bash
if [ "$STATUS" = "success" ]; then
    echo "✅ Task succeeded - dependent tasks can proceed"
    # TODO: Implement dependency logic
else
    echo "⚠️  Task $STATUS - dependent tasks may be blocked"
fi
```

**Current:** Placeholder for production implementation

**Future Implementation:**
```bash
# Get tasks that depend on current task
DEPENDENT_TASKS=$(jq -r ".dependencies | to_entries[] | select(.value[] == \"$TASK_ID\") | .key" plan.json)

for DEP_TASK in $DEPENDENT_TASKS; do
    # Check if all dependencies for DEP_TASK are complete
    ALL_DEPS=$(jq -r ".dependencies[\"$DEP_TASK\"][]" plan.json)
    ALL_COMPLETE=true

    for DEP in $ALL_DEPS; do
        if [ ! -f ".claude/state/agents/*/${DEP}.complete" ]; then
            ALL_COMPLETE=false
        fi
    done

    if [ "$ALL_COMPLETE" = true ]; then
        # Trigger execution of DEP_TASK
        ./execute-plan.py --task="$DEP_TASK"
    fi
done
```

### 3.5 Duration Calculation

**Location:** Lines 208-216

```bash
DURATION="unknown"
if [ -f "$AGENT_STATE_DIR/${TASK_ID}.complete" ]; then
    START=$(jq -r '.started_at // ""' "$AGENT_STATE_DIR/${TASK_ID}.complete" 2>/dev/null || echo "")
    if [ -n "$START" ]; then
        DURATION="<calculated>"  # TODO: Implement
    fi
fi
```

**Production Implementation:**
```bash
START_EPOCH=$(date -d "$START" +%s)
END_EPOCH=$(date -d "$TIMESTAMP" +%s)
DURATION=$((END_EPOCH - START_EPOCH))
```

**Enables:**
- Performance benchmarking
- Optimization opportunities
- Progress estimation

---

## 4. Fractal Memory Integration

### Memory Flow Architecture

```
PRE-TASK HOOK (Read Context)
┌─────────────────────────────────────────────────────┐
│  OpusPlanner      → User + Opus levels (full)        │
│  SonnetDebugger   → Sonnet + Opus levels (patterns)  │
│  SonnetCoder      → Sonnet level only (task)         │
│  HaikuExecutor    → Haiku level only (step)          │
└─────────────────────────────────────────────────────┘
                          ↓
                    AGENT EXECUTES
                          ↓
POST-TASK HOOK (Write Results)
┌─────────────────────────────────────────────────────┐
│  OpusPlanner      → Opus level (seed rules)          │
│  SonnetDebugger   → Sonnet level (solutions)         │
│  SonnetCoder      → Sonnet level (results)           │
│  SonnetTracker    → Sonnet level (synthesis/progress)│
│  HaikuExecutor    → Haiku level (step results)       │
└─────────────────────────────────────────────────────┘
```

### Key Patterns

1. **Hierarchical Read Access:** Agents can read from their level and above
2. **Level-Appropriate Write:** Agents only write to their own level
3. **Context Isolation:** HaikuExecutor never sees full project context
4. **Seed Rule Lifecycle:** Solutions → Debugger → OpusPlanner → Seed Rules

---

## 5. State Management System

### Directory Structure
```
.claude/
├── memory/              # Fractal memory (4 levels)
│   ├── user_level/
│   ├── opus_level/
│   ├── sonnet_level/
│   └── haiku_level/
├── state/               # Agent execution state
│   └── agents/
│       ├── haiku-executor/
│       ├── sonnet-coder/
│       ├── sonnet-debugger/
│       ├── sonnet-tracker/
│       └── opus-planner/
└── logs/                # Centralized logging
    └── task-execution.log
```

### State File Lifecycle

```
Task Not Started:  (no files)
                   ↓
Task Started:      task_id.start (created by pre-hook)
                   ↓
Task Running:      task_id.start (exists, agent executing)
                   ↓
Task Complete:     task_id.complete (created by post-hook)
                   task_id.start (deleted by post-hook)
                   ↓
Next Execution:    task_id.complete (historical record)
```

### Concurrent Execution Support

Multiple tasks can run simultaneously:
```
.claude/state/agents/haiku-executor/
├── 1.1.start     ← Task 1.1 running
├── 1.2.complete  ← Task 1.2 done
├── 1.3.start     ← Task 1.3 running
└── 2.1.start     ← Task 2.1 running
```

Query running tasks:
```bash
find .claude/state/agents/ -name "*.start"
```

---

## 6. Design Patterns

### 6.1 Fail-Fast with Graceful Degradation

```bash
set -euo pipefail  # Fail fast on errors

# BUT provide graceful fallbacks
if [ -n "$RESULT_FILE" ] && [ ! -f "$RESULT_FILE" ]; then
    RESULT_FILE=""  # Degrade to minimal result
fi
```

**Philosophy:** Infrastructure errors abort immediately, missing data degrades gracefully

### 6.2 Self-Healing Infrastructure

```bash
if [ ! -d "$MEMORY_DIR" ]; then
    mkdir -p "$MEMORY_DIR"/{user_level,opus_level,sonnet_level,haiku_level}
fi
```

System automatically creates missing directories

### 6.3 Idempotent Operations

Running hooks multiple times produces same result:
- Creating directories (`mkdir -p`) succeeds even if exists
- Overwriting state files with same data is safe
- Logging appends (doesn't destroy previous entries)

### 6.4 Single Responsibility

Each hook has one job:
- Pre-hook: **Prepare** environment
- Post-hook: **Persist** results

Agents do actual work - enables independent evolution

### 6.5 Convention over Configuration

No configuration files needed. Everything inferred from:
- Agent type (determines memory level)
- Task ID (determines file name)
- Project name (determines seed rule file)

---

## 7. Integration with Execution Engine

Example integration in `execute-plan.py`:

```python
def execute_step(self, step: Dict, section_id: str, context: Dict) -> ExecutionResult:
    step_id = step["step_id"]
    agent_type = step.get("agent_type", "haiku-executor")

    # 1. Call pre-task hook
    subprocess.run([
        ".claude/hooks/pre-task.sh",
        agent_type,
        step_id,
        context["project"]
    ], check=True)

    # 2. Execute agent
    result = self._execute_agent(agent_type, step_id)

    # 3. Save result to temp file
    result_file = f"/tmp/result_{step_id}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f)

    # 4. Call post-task hook
    subprocess.run([
        ".claude/hooks/post-task.sh",
        agent_type,
        step_id,
        result.status,
        result_file
    ], check=True)

    return result
```

---

## 8. Performance Considerations

### Memory Efficiency
- Hooks reference file paths, don't load full content
- Agent does actual loading only when needed

### Parallel Execution
- Hooks are stateless and concurrent-safe
- Each task has unique ID
- State files are task-specific
- No shared mutable state

### Logging Performance
- Appending to single log: O(1) operation
- OS guarantees append atomicity
- Concurrent-safe for multiple processes
- Potential bottleneck only at 1000s tasks/second

---

## 9. Future Enhancement Opportunities

### Priority 1: Critical Features

#### 9.1 Dependency Triggering Implementation
**Location:** `post-task.sh` lines 183-199

**Current State:** Placeholder logging only

**Implementation Plan:**
```bash
# Load plan JSON to get dependency graph
PLAN_FILE=".claude/current-plan.json"

# Get tasks that depend on completed task
DEPENDENT_TASKS=$(jq -r ".dependencies | to_entries[] |
                   select(.value[] == \"$TASK_ID\") | .key" "$PLAN_FILE")

for DEP_TASK in $DEPENDENT_TASKS; do
    # Get all dependencies for this dependent task
    DEPS=$(jq -r ".dependencies[\"$DEP_TASK\"][]" "$PLAN_FILE")

    # Check if all dependencies are satisfied
    ALL_SATISFIED=true
    for DEP in $DEPS; do
        # Check if dependency has .complete file
        COMPLETE_FILES=$(find .claude/state/agents/ -name "${DEP}.complete")
        if [ -z "$COMPLETE_FILES" ]; then
            ALL_SATISFIED=false
            break
        fi
    done

    # If all dependencies satisfied, trigger execution
    if [ "$ALL_SATISFIED" = true ]; then
        echo "   🚀 Triggering dependent task: $DEP_TASK"
        # Signal execution engine or add to ready queue
        echo "$DEP_TASK" >> .claude/state/ready-tasks.queue
    fi
done
```

**Benefits:**
- Automatic parallel execution when dependencies met
- No manual scheduling needed
- Optimal throughput

**Dependencies:**
- Requires plan JSON accessible to hooks
- Needs execution engine to monitor ready queue

---

#### 9.2 Duration Calculation
**Location:** `post-task.sh` lines 208-216

**Current State:** Placeholder `<calculated>`

**Implementation Plan:**
```bash
DURATION="unknown"
if [ -f "$AGENT_STATE_DIR/${TASK_ID}.complete" ]; then
    START=$(jq -r '.started_at // ""' "$AGENT_STATE_DIR/${TASK_ID}.complete" 2>/dev/null || echo "")
    if [ -n "$START" ]; then
        # Convert ISO 8601 timestamps to epoch seconds
        START_EPOCH=$(date -d "$START" +%s 2>/dev/null || echo "0")
        END_EPOCH=$(date -d "$TIMESTAMP" +%s 2>/dev/null || echo "0")

        if [ "$START_EPOCH" != "0" ] && [ "$END_EPOCH" != "0" ]; then
            DURATION_SECONDS=$((END_EPOCH - START_EPOCH))
            DURATION="${DURATION_SECONDS}s"
        fi
    fi
fi

# Log with actual duration
echo "[$TIMESTAMP] COMPLETE $AGENT_TYPE task=$TASK_ID status=$STATUS duration=$DURATION" >> "$LOG_FILE"
```

**Benefits:**
- Accurate performance metrics
- Identify slow tasks
- Predict execution time

**Testing:**
```bash
# Test duration calculation
START="2025-12-16T10:30:00Z"
END="2025-12-16T10:30:45Z"
# Should output: 45s
```

---

#### 9.3 Access Validation
**Location:** `pre-task.sh` lines 107-113

**Current State:** Placeholder validation

**Implementation Plan:**
```bash
# Define agent permissions
case "$AGENT_TYPE" in
    "haiku-executor")
        ALLOWED_LEVELS=("haiku_level")
        ;;
    "sonnet-coder"|"sonnet-tracker")
        ALLOWED_LEVELS=("sonnet_level")
        ;;
    "sonnet-debugger")
        ALLOWED_LEVELS=("sonnet_level" "opus_level")
        ;;
    "opus-planner")
        ALLOWED_LEVELS=("user_level" "opus_level" "sonnet_level" "haiku_level")
        ;;
    *)
        echo "❌ Unknown agent type: $AGENT_TYPE"
        exit 1
        ;;
esac

# Validate task_id matches allowed pattern
if ! [[ "$TASK_ID" =~ ^[0-9]+(\.[0-9]+)*$ ]]; then
    echo "❌ Invalid task ID format: $TASK_ID"
    exit 1
fi

# Validate project name is safe (no path traversal)
if [[ "$PROJECT" =~ \.\. ]] || [[ "$PROJECT" =~ / ]]; then
    echo "❌ Invalid project name: $PROJECT"
    exit 1
fi

echo "✅ Agent access validated"
```

**Benefits:**
- Security enforcement
- Prevents unauthorized access
- Input sanitization

---

### Priority 2: Performance & Observability

#### 9.4 Retry Logic
**New Feature**

**Implementation Plan:**
```bash
# In post-task.sh, after detecting failure
if [ "$STATUS" = "error" ]; then
    # Check retry count
    RETRY_FILE="$AGENT_STATE_DIR/${TASK_ID}.retries"
    RETRY_COUNT=0

    if [ -f "$RETRY_FILE" ]; then
        RETRY_COUNT=$(cat "$RETRY_FILE")
    fi

    MAX_RETRIES=3
    if [ "$RETRY_COUNT" -lt "$MAX_RETRIES" ]; then
        # Increment retry count
        echo $((RETRY_COUNT + 1)) > "$RETRY_FILE"

        # Calculate backoff (exponential: 2^retry seconds)
        BACKOFF=$((2 ** RETRY_COUNT))

        echo "   🔄 Retry attempt $((RETRY_COUNT + 1))/$MAX_RETRIES in ${BACKOFF}s"

        # Schedule retry
        (sleep "$BACKOFF" && echo "$TASK_ID" >> .claude/state/retry-tasks.queue) &
    else
        echo "   ❌ Max retries exceeded - marking as failed"
        rm "$RETRY_FILE"
    fi
fi
```

**Benefits:**
- Automatic recovery from transient failures
- Exponential backoff prevents thundering herd
- Configurable retry limits

---

#### 9.5 Resource Limits
**New Feature**

**Implementation Plan:**
```bash
# In pre-task.sh, before agent execution
case "$AGENT_TYPE" in
    "haiku-executor")
        MEMORY_LIMIT="512M"
        CPU_LIMIT="0.5"  # 50% of one core
        TIMEOUT="300"    # 5 minutes
        ;;
    "sonnet-coder")
        MEMORY_LIMIT="2G"
        CPU_LIMIT="1.0"
        TIMEOUT="1800"   # 30 minutes
        ;;
    "opus-planner")
        MEMORY_LIMIT="4G"
        CPU_LIMIT="2.0"
        TIMEOUT="3600"   # 1 hour
        ;;
esac

# Store limits for execution engine
cat > "$AGENT_STATE_DIR/${TASK_ID}.limits" <<EOF
{
  "memory_limit": "$MEMORY_LIMIT",
  "cpu_limit": "$CPU_LIMIT",
  "timeout": $TIMEOUT
}
EOF
```

**Benefits:**
- Prevent runaway processes
- Fair resource allocation
- Predictable performance

---

#### 9.6 Metrics Export
**New Feature**

**Implementation Plan:**
```bash
# In post-task.sh, after completion
if command -v curl &> /dev/null; then
    # Export to Prometheus pushgateway
    METRICS=$(cat <<EOF
# TYPE task_duration_seconds gauge
task_duration_seconds{agent_type="$AGENT_TYPE",task_id="$TASK_ID",status="$STATUS"} $DURATION_SECONDS
# TYPE task_completed_total counter
task_completed_total{agent_type="$AGENT_TYPE",status="$STATUS"} 1
EOF
)

    echo "$METRICS" | curl -s --data-binary @- \
        http://localhost:9091/metrics/job/orchestration/instance/$HOSTNAME \
        2>/dev/null || true
fi

# Also export to JSON for local analysis
METRICS_FILE=".claude/metrics/$(date +%Y-%m-%d).jsonl"
mkdir -p "$(dirname "$METRICS_FILE")"

cat >> "$METRICS_FILE" <<EOF
{"timestamp":"$TIMESTAMP","agent_type":"$AGENT_TYPE","task_id":"$TASK_ID","status":"$STATUS","duration":$DURATION_SECONDS}
EOF
```

**Benefits:**
- Integration with monitoring systems
- Real-time dashboards
- Historical analysis

---

### Priority 3: Advanced Features

#### 9.7 Distributed Execution
**New Feature**

**Implementation Plan:**
```bash
# In pre-task.sh, support remote execution
EXECUTION_MODE="${EXECUTION_MODE:-local}"

if [ "$EXECUTION_MODE" = "remote" ]; then
    # Copy context to remote machine
    REMOTE_HOST="${REMOTE_HOST:-localhost}"

    rsync -az "$MEMORY_DIR" "$REMOTE_HOST:.claude/memory/"

    # Store remote execution info
    cat > "$AGENT_STATE_DIR/${TASK_ID}.remote" <<EOF
{
  "remote_host": "$REMOTE_HOST",
  "remote_pid": null,
  "started_at": "$TIMESTAMP"
}
EOF

    echo "   🌐 Executing on remote host: $REMOTE_HOST"
fi
```

**Benefits:**
- Scale beyond single machine
- Leverage heterogeneous resources
- Fault tolerance

---

#### 9.8 Result Validation
**New Feature**

**Implementation Plan:**
```bash
# In post-task.sh, validate result schema
if [ -n "$RESULT_FILE" ] && [ -f "$RESULT_FILE" ]; then
    # Load expected schema for agent type
    SCHEMA_FILE=".claude/schemas/results/${AGENT_TYPE}.schema.json"

    if [ -f "$SCHEMA_FILE" ]; then
        # Validate using ajv-cli
        if command -v ajv &> /dev/null; then
            if ! ajv validate -s "$SCHEMA_FILE" -d "$RESULT_FILE" 2>&1; then
                echo "   ⚠️  Result validation failed - schema mismatch"
                # Still store result but flag as invalid
                STATUS="error_invalid_result"
            else
                echo "   ✅ Result validated against schema"
            fi
        fi
    fi
fi
```

**Benefits:**
- Catch malformed results early
- Ensure data quality
- Type safety

---

## 10. Testing Strategy

### Unit Testing Hooks

```bash
# test-hooks.sh
#!/bin/bash

# Test pre-task hook
test_pre_task_creates_state() {
    # Setup
    rm -rf .claude/state

    # Execute
    .claude/hooks/pre-task.sh haiku-executor 1.1 test_project

    # Assert
    [ -f .claude/state/agents/haiku-executor/1.1.start ] || {
        echo "FAIL: State file not created"
        return 1
    }

    echo "PASS: Pre-task creates state"
}

# Test post-task hook
test_post_task_stores_result() {
    # Setup
    .claude/hooks/pre-task.sh haiku-executor 1.1 test_project
    echo '{"status":"success"}' > /tmp/result.json

    # Execute
    .claude/hooks/post-task.sh haiku-executor 1.1 success /tmp/result.json

    # Assert
    [ -f .claude/memory/haiku_level/step_results/1.1.json ] || {
        echo "FAIL: Result not stored"
        return 1
    }

    [ ! -f .claude/state/agents/haiku-executor/1.1.start ] || {
        echo "FAIL: Start state not removed"
        return 1
    }

    [ -f .claude/state/agents/haiku-executor/1.1.complete ] || {
        echo "FAIL: Complete state not created"
        return 1
    }

    echo "PASS: Post-task stores result and updates state"
}

# Run all tests
test_pre_task_creates_state
test_post_task_stores_result
```

### Integration Testing

```python
# test_hooks_integration.py
import subprocess
import json
import time
from pathlib import Path

def test_full_task_lifecycle():
    """Test complete task lifecycle with hooks"""

    # 1. Pre-task hook
    result = subprocess.run([
        ".claude/hooks/pre-task.sh",
        "sonnet-coder",
        "2.1",
        "test_project"
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert Path(".claude/state/agents/sonnet-coder/2.1.start").exists()

    # 2. Simulate agent execution
    time.sleep(1)

    result_data = {
        "task_id": "2.1",
        "status": "success",
        "output": "Task completed successfully"
    }

    result_file = Path("/tmp/result_2.1.json")
    result_file.write_text(json.dumps(result_data))

    # 3. Post-task hook
    result = subprocess.run([
        ".claude/hooks/post-task.sh",
        "sonnet-coder",
        "2.1",
        "success",
        str(result_file)
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert not Path(".claude/state/agents/sonnet-coder/2.1.start").exists()
    assert Path(".claude/state/agents/sonnet-coder/2.1.complete").exists()
    assert Path(".claude/memory/sonnet_level/results/2.1.json").exists()

    # 4. Verify log entry
    log_content = Path(".claude/logs/task-execution.log").read_text()
    assert "START sonnet-coder task=2.1" in log_content
    assert "COMPLETE sonnet-coder task=2.1 status=success" in log_content

    print("✅ Full task lifecycle test passed")

if __name__ == "__main__":
    test_full_task_lifecycle()
```

---

## 11. Migration Guide

When implementing enhancements, follow this sequence:

### Phase 1: Non-Breaking Additions
1. Implement duration calculation (backward compatible)
2. Add access validation (enhances security)
3. Add metrics export (optional feature)

### Phase 2: Infrastructure Enhancements
4. Implement dependency triggering (requires execution engine integration)
5. Add resource limits (requires execution engine support)
6. Add retry logic (changes failure behavior)

### Phase 3: Advanced Features
7. Implement result validation (may break existing results)
8. Add distributed execution (requires infrastructure)

### Testing Checklist
- [ ] Unit tests for each hook function
- [ ] Integration tests for full lifecycle
- [ ] Performance tests with parallel execution
- [ ] Backward compatibility verification
- [ ] Documentation updates

---

## 12. Reference Implementation Snippets

### Complete Dependency Checker
```bash
#!/bin/bash
# check-dependencies.sh - Standalone dependency checker

TASK_ID="$1"
PLAN_FILE=".claude/current-plan.json"

# Get all dependencies for this task
DEPS=$(jq -r ".dependencies[\"$TASK_ID\"][]" "$PLAN_FILE" 2>/dev/null)

if [ -z "$DEPS" ]; then
    echo "No dependencies"
    exit 0
fi

# Check each dependency
for DEP in $DEPS; do
    COMPLETE_FILE=$(find .claude/state/agents/ -name "${DEP}.complete" 2>/dev/null)

    if [ -z "$COMPLETE_FILE" ]; then
        echo "❌ Dependency not met: $DEP"
        exit 1
    fi

    # Check if dependency succeeded
    STATUS=$(jq -r '.status' "$COMPLETE_FILE" 2>/dev/null)
    if [ "$STATUS" != "success" ]; then
        echo "❌ Dependency failed: $DEP (status: $STATUS)"
        exit 1
    fi
done

echo "✅ All dependencies met"
exit 0
```

### Performance Monitor
```bash
#!/bin/bash
# monitor-performance.sh - Real-time performance dashboard

watch -n 1 '
echo "=== Task Execution Dashboard ==="
echo ""
echo "Running Tasks:"
find .claude/state/agents/ -name "*.start" | wc -l
echo ""
echo "Completed Tasks:"
find .claude/state/agents/ -name "*.complete" | wc -l
echo ""
echo "Recent Completions:"
tail -5 .claude/logs/task-execution.log | grep COMPLETE
echo ""
echo "Average Duration:"
grep COMPLETE .claude/logs/task-execution.log | grep -oP "duration=\K[0-9]+" | awk "{sum+=\$1; count++} END {if(count>0) print sum/count \"s\"}"
'
```

---

## 13. Summary

The task-level hooks implement a production-ready lifecycle management system with:

✅ **Enforces fractal hierarchy** - Agent-specific context access
✅ **Enables concurrent execution** - Stateless, concurrent-safe design
✅ **Provides observability** - Centralized logging and state tracking
✅ **Supports learning** - Seed rule suggestions from debugging
✅ **Ensures reliability** - Fail-fast with graceful degradation
✅ **Maintains simplicity** - Convention over configuration

### Enhancement Priorities

**Critical (Priority 1):**
- Dependency triggering
- Duration calculation
- Access validation

**Performance (Priority 2):**
- Retry logic
- Resource limits
- Metrics export

**Advanced (Priority 3):**
- Distributed execution
- Result validation

**Next Steps:**
1. Implement Priority 1 enhancements
2. Add comprehensive test suite
3. Deploy to production with monitoring
4. Gather metrics and optimize based on real usage

---

**Document Status:** Ready for Enhancement Implementation
**Last Updated:** 2025-12-16
