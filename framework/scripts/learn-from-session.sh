#!/bin/bash
# learn-from-session.sh — Run the full learning pipeline for one session.
# Version: 1.0.0
#
# Usage:
#   learn-from-session.sh <project_path> <workflow> [session_id]
#
# Finds the session JSONL, runs session-analyzer + analyze-prompt-effectiveness,
# distills seed rules, validates for conflicts, and logs results.
#
# Environment:
#   WORKSPACE_ROOT  — workspace root (default: $HOME/software)
#   ANTHROPIC_API_KEY — required for prompt effectiveness analysis

set -euo pipefail

PROJECT_PATH="${1:-}"
WORKFLOW="${2:-general}"
SESSION_ID="${3:-}"

if [ -z "$PROJECT_PATH" ]; then
    echo '{"learned":false,"reason":"project_path required as first argument"}' >&2
    exit 1
fi

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/software}"
SCRIPTS_DIR="$WORKSPACE_ROOT/.claude/scripts"
AGENTS_DIR="$WORKSPACE_ROOT/.claude/agents"
MEMORY_DIR="$PROJECT_PATH/.claude/memory"
RULES_DIR="$PROJECT_PATH/seeds/workflows/$WORKFLOW"
PROJECT_NAME=$(basename "$PROJECT_PATH")

# ── Read learning config ──────────────────────────────────────────────────────
LEARNING_CONFIG=$(find "$PROJECT_PATH" -maxdepth 2 -name "learning.json" 2>/dev/null | head -1 || echo "")

MIN_TURNS=3
REVIEW_MODE=true
PROMPT_EFFECTIVENESS_ENABLED=true
AUTO_APPLY_IMPROVEMENTS=false

if [ -n "$LEARNING_CONFIG" ] && [ -f "$LEARNING_CONFIG" ]; then
    MIN_TURNS=$(python3 -c "
import json
c=json.load(open('$LEARNING_CONFIG'))
print(c.get('min_session_turns',3))
" 2>/dev/null || echo "3")

    REVIEW_MODE=$(python3 -c "
import json
c=json.load(open('$LEARNING_CONFIG'))
print(str(c.get('review_mode',True)).lower())
" 2>/dev/null || echo "true")

    PROMPT_EFFECTIVENESS_ENABLED=$(python3 -c "
import json
c=json.load(open('$LEARNING_CONFIG'))
print(str(c.get('prompt_effectiveness',{}).get('enabled',True)).lower())
" 2>/dev/null || echo "true")

    AUTO_APPLY_IMPROVEMENTS=$(python3 -c "
import json
c=json.load(open('$LEARNING_CONFIG'))
print(str(c.get('prompt_effectiveness',{}).get('auto_apply_improvements',False)).lower())
" 2>/dev/null || echo "false")
fi

# ── Find session JSONL ────────────────────────────────────────────────────────
# Claude encodes the project path as: replace all / with -
# e.g. /root/software → -root-software
ENCODED_PATH=$(echo "$PROJECT_PATH" | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/$ENCODED_PATH"

JSONL_FILE=""
if [ -n "$SESSION_ID" ]; then
    # Specific session requested
    if [ -f "$SESSIONS_DIR/$SESSION_ID.jsonl" ]; then
        JSONL_FILE="$SESSIONS_DIR/$SESSION_ID.jsonl"
    else
        JSONL_FILE=$(find "$SESSIONS_DIR" -name "${SESSION_ID}.jsonl" 2>/dev/null | head -1 || echo "")
    fi
else
    # Most recent session by mtime
    JSONL_FILE=$(find "$SESSIONS_DIR" -name "*.jsonl" -type f 2>/dev/null \
        | xargs ls -t 2>/dev/null \
        | head -1 || echo "")
fi

if [ -z "$JSONL_FILE" ] || [ ! -f "$JSONL_FILE" ]; then
    echo "{\"learned\":false,\"reason\":\"no session JSONL found at $SESSIONS_DIR\"}"
    exit 0
fi

SESSION_UUID=$(basename "$JSONL_FILE" .jsonl)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TMP_PATTERNS="/tmp/learn_patterns_${SESSION_UUID}.json"
TMP_EFFECTIVENESS="/tmp/learn_effectiveness_${SESSION_UUID}.json"
TMP_IMPROVEMENTS="/tmp/learn_improvements_${SESSION_UUID}.json"

mkdir -p "$MEMORY_DIR/prompt_effectiveness"
mkdir -p "$RULES_DIR"
[ "$REVIEW_MODE" = "true" ] && mkdir -p "$RULES_DIR/pending"

# ── Step 1: Session analyzer ──────────────────────────────────────────────────
echo "  [learning 1/4] Analyzing session patterns..." >&2

NEW_PATTERNS=0
SESSION_SKIPPED=false

if python3 "$SCRIPTS_DIR/session-analyzer.py" "$JSONL_FILE" \
    --output "$TMP_PATTERNS" \
    --min-turns "$MIN_TURNS" 2>/dev/null; then

    SESSION_SKIPPED=$(python3 -c "
import json
d=json.load(open('$TMP_PATTERNS'))
print(str(d.get('statistics',{}).get('skipped',False)).lower())
" 2>/dev/null || echo "false")

    if [ "$SESSION_SKIPPED" = "true" ]; then
        echo "{\"learned\":false,\"reason\":\"session too short (< $MIN_TURNS turns)\"}"
        rm -f "$TMP_PATTERNS" 2>/dev/null || true
        exit 0
    fi

    NEW_PATTERNS=$(python3 -c "
import json
d=json.load(open('$TMP_PATTERNS'))
print(d.get('statistics',{}).get('total_patterns',0))
" 2>/dev/null || echo "0")
    echo "  [learning 1/4] ok — $NEW_PATTERNS patterns extracted" >&2
else
    echo "  [learning 1/4] warn — session-analyzer failed, continuing" >&2
fi

# ── Step 2: Prompt effectiveness analysis ─────────────────────────────────────
echo "  [learning 2/4] Analyzing prompt effectiveness..." >&2

RULES_USED=0
RULES_IGNORED=0
CONTRADICTIONS=0

if [ "$PROMPT_EFFECTIVENESS_ENABLED" = "true" ] \
   && [ -f "$SCRIPTS_DIR/analyze-prompt-effectiveness.py" ]; then

    python3 "$SCRIPTS_DIR/analyze-prompt-effectiveness.py" "$JSONL_FILE" \
        --rules-dir "$RULES_DIR" \
        --agents-dir "$AGENTS_DIR" \
        --output "$TMP_EFFECTIVENESS" 2>/dev/null || true

    if [ -f "$TMP_EFFECTIVENESS" ]; then
        cp "$TMP_EFFECTIVENESS" "$MEMORY_DIR/prompt_effectiveness/${SESSION_UUID}.json"

        RULES_USED=$(python3 -c "
import json
d=json.load(open('$TMP_EFFECTIVENESS'))
print(len(d.get('seed_rules_analysis',{}).get('used_useful',[])))
" 2>/dev/null || echo "0")

        RULES_IGNORED=$(python3 -c "
import json
d=json.load(open('$TMP_EFFECTIVENESS'))
print(len(d.get('seed_rules_analysis',{}).get('ignored',[])))
" 2>/dev/null || echo "0")

        CONTRADICTIONS=$(python3 -c "
import json
d=json.load(open('$TMP_EFFECTIVENESS'))
print(len(d.get('seed_rules_analysis',{}).get('contradicting',[])))
" 2>/dev/null || echo "0")

        echo "  [learning 2/4] ok — used:$RULES_USED ignored:$RULES_IGNORED contradictions:$CONTRADICTIONS" >&2
    else
        echo "  [learning 2/4] warn — effectiveness analysis produced no output" >&2
    fi
else
    echo "  [learning 2/4] skipped (prompt_effectiveness disabled or API key missing)" >&2
fi

# ── Step 3: Rule distiller ────────────────────────────────────────────────────
echo "  [learning 3/4] Distilling seed rules..." >&2

NEW_RULES=0
UPDATED_RULES=0

if [ -f "$TMP_PATTERNS" ] && [ "$NEW_PATTERNS" -gt 0 ]; then
    python3 "$SCRIPTS_DIR/rule-distiller.py" \
        "$TMP_PATTERNS" \
        --project "$PROJECT_NAME" \
        --workflow "$WORKFLOW" \
        --output-dir "$PROJECT_PATH" 2>/dev/null || true

    # Move newly written rules to pending/ if review_mode is on
    if [ "$REVIEW_MODE" = "true" ]; then
        for f in "$RULES_DIR"/*.json; do
            [ -f "$f" ] || continue
            mv "$f" "$RULES_DIR/pending/" 2>/dev/null && NEW_RULES=$((NEW_RULES + 1)) || true
        done
    fi
    echo "  [learning 3/4] ok — $NEW_RULES rules staged" >&2
fi

# Apply prompt improvements if auto_apply is on and improvements file exists
if [ "$AUTO_APPLY_IMPROVEMENTS" = "true" ] \
   && [ -f "$TMP_IMPROVEMENTS" ]; then
    python3 "$SCRIPTS_DIR/rule-distiller.py" \
        "$TMP_IMPROVEMENTS" \
        --project "$PROJECT_NAME" \
        --workflow "$WORKFLOW" \
        --output-dir "$PROJECT_PATH" \
        --update 2>/dev/null || true

    UPDATED_RULES=$(python3 -c "
import json
d=json.load(open('$TMP_IMPROVEMENTS'))
print(d.get('statistics',{}).get('total_patterns',0))
" 2>/dev/null || echo "0")
    echo "  [learning 3/4] ok — $UPDATED_RULES rules updated from effectiveness analysis" >&2
fi

# ── Step 4: Rule validator ────────────────────────────────────────────────────
echo "  [learning 4/4] Validating rules..." >&2

VALIDATOR_CONFLICTS=false
if [ -f "$SCRIPTS_DIR/rule-validator.py" ]; then
    conflicts=$(python3 "$SCRIPTS_DIR/rule-validator.py" \
        --project "$PROJECT_NAME" \
        --memory-dir "$MEMORY_DIR" \
        --find-conflicts 2>/dev/null || echo "")
    if echo "$conflicts" | grep -q "Found.*conflicts"; then
        VALIDATOR_CONFLICTS=true
        echo "  [learning 4/4] warn — conflicts found in seed rules" >&2
    else
        echo "  [learning 4/4] ok — no conflicts" >&2
    fi
fi

# ── Log ───────────────────────────────────────────────────────────────────────
LOG_FILE="$MEMORY_DIR/learning.log"
mkdir -p "$(dirname "$LOG_FILE")"
LOG_ENTRY=$(python3 -c "
import json
print(json.dumps({
    'timestamp': '$TIMESTAMP',
    'session_id': '$SESSION_UUID',
    'project': '$PROJECT_NAME',
    'workflow': '$WORKFLOW',
    'new_rules': $NEW_RULES,
    'updated_rules': $UPDATED_RULES,
    'rules_used_useful': $RULES_USED,
    'rules_ignored': $RULES_IGNORED,
    'contradictions': $CONTRADICTIONS,
    'review_mode': '$REVIEW_MODE' == 'true',
    'validator_conflicts': $VALIDATOR_CONFLICTS
}))" 2>/dev/null || echo "{}")
echo "$LOG_ENTRY" >> "$LOG_FILE"

# ── Cleanup ───────────────────────────────────────────────────────────────────
rm -f "$TMP_PATTERNS" "$TMP_EFFECTIVENESS" "$TMP_IMPROVEMENTS" 2>/dev/null || true

# ── Output ────────────────────────────────────────────────────────────────────
python3 -c "
import json
print(json.dumps({
    'learned': True,
    'session_id': '$SESSION_UUID',
    'new_rules': $NEW_RULES,
    'updated_rules': $UPDATED_RULES,
    'pending_review': $NEW_RULES,
    'rules_used_useful': $RULES_USED,
    'rules_ignored': $RULES_IGNORED,
    'contradictions': $CONTRADICTIONS,
    'review_mode': '$REVIEW_MODE' == 'true'
}))"
