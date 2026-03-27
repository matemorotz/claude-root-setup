#!/bin/bash
# Session Stop Hook - Validate rules and log session summary
# Version: 1.0.0

set -euo pipefail

CURRENT_DIR="${PWD}"
MAX_DEPTH=5
# Resolve SCRIPTS_DIR: prefer env var WORKSPACE_ROOT, fallback to $HOME/software
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/software}"
SCRIPTS_DIR="$WORKSPACE_ROOT/.claude/scripts"

# Find file walking up directory tree
find_file() {
    local file="$1"
    local dir="$CURRENT_DIR"
    local depth=0

    while [ "$depth" -lt "$MAX_DEPTH" ]; do
        if [ -f "$dir/$file" ]; then
            echo "$dir/$file"
            return 0
        fi
        local parent=$(dirname "$dir")
        [ "$parent" = "$dir" ] && break
        dir="$parent"
        ((depth++))
    done
    return 1
}

# Find project
claude_md=$(find_file "CLAUDE.md" || echo "")
if [ -z "$claude_md" ]; then
    echo '{"session_end": true, "rules_validated": false, "reason": "no project found"}'
    exit 0
fi

project_path=$(dirname "$claude_md")
project_name=$(basename "$project_path")
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
memory_dir="$project_path/.claude/memory"
rules_file="$memory_dir/opus_level/seed_rules/$project_name.json"

# Skip if no seed rules exist
if [ ! -f "$rules_file" ]; then
    echo "{\"session_end\": \"$timestamp\", \"project\": \"$project_name\", \"rules_validated\": false, \"reason\": \"no seed rules\"}"
    exit 0
fi

# Run rule validator report (append to session log)
log_file="$memory_dir/session_reports.log"
mkdir -p "$(dirname "$log_file")"

if [ -f "$SCRIPTS_DIR/rule-validator.py" ]; then
    # Generate report
    report=$(python3 "$SCRIPTS_DIR/rule-validator.py" \
        --project "$project_name" \
        --memory-dir "$memory_dir" \
        --report 2>/dev/null || echo "No metrics data yet")

    echo "[$timestamp] $report" >> "$log_file"

    # Check for conflicts
    conflicts=$(python3 "$SCRIPTS_DIR/rule-validator.py" \
        --project "$project_name" \
        --memory-dir "$memory_dir" \
        --find-conflicts 2>/dev/null || echo "")

    has_conflicts=false
    if echo "$conflicts" | grep -q "Found.*conflicts"; then
        has_conflicts=true
    fi
fi

echo "{\"session_end\": \"$timestamp\", \"project\": \"$project_name\", \"rules_validated\": true, \"has_conflicts\": $has_conflicts}"
exit 0
