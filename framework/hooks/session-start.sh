#!/bin/bash
# SessionStart Hook - Auto-load context files + Auto-initialize projects
# Version: 2.1.0 - Workflow-scoped seed rules

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

# Extract first heading
get_heading() {
    grep -m 1 "^# " "$1" 2>/dev/null | sed 's/^# //' || echo ""
}

# Extract status
get_status() {
    grep -i "^\*\*Status:\*\*" "$1" 2>/dev/null | sed 's/.*: //' | sed 's/\*\*//' || echo "Unknown"
}

# Count pending todos
count_todos() {
    grep -c "^- \[ \]" "$1" 2>/dev/null || echo "0"
}

# Extract workflow name from CLAUDE.md (looks for "## Workflow: <name>")
get_workflow() {
    grep -m 1 "^## Workflow:" "$1" 2>/dev/null | sed 's/^## Workflow: *//' | tr -d '[:space:]' || echo "general"
}

# Auto-setup project with fractal orchestration
auto_setup_project() {
    local project_path="$1"
    local project_name="$2"
    local workflow="${3:-general}"

    # Knowledge graph lives in the framework's knowledge dir
    local GRAPH_DIR="$SCRIPTS_DIR/../knowledge/graph"
    mkdir -p "$GRAPH_DIR"
    local GRAPH_FILE="$GRAPH_DIR/${project_name}_nodes.json"

    # Check if already initialized (new format: seeds/workflows/{workflow}/)
    local has_graph=false
    local has_rules=false

    if [ -f "$GRAPH_FILE" ]; then
        has_graph=true
    fi

    local workflow_dir="$project_path/seeds/workflows/$workflow"
    if [ -d "$workflow_dir" ] && ls "$workflow_dir"/*.json 2>/dev/null | head -1 > /dev/null 2>&1; then
        has_rules=true
    fi

    # If both exist, already initialized
    if [ "$has_graph" = true ] && [ "$has_rules" = true ]; then
        echo "false" # Did not run setup
        return 0
    fi

    # Scope guard: skip projects that are too large
    local FILE_COUNT
    FILE_COUNT=$(find "$project_path" -type f \
        -not -path '*/.git/*' -not -path '*/node_modules/*' \
        -not -path '*/venv/*' -not -path '*/__pycache__/*' \
        -not -path '*/.claude/*' 2>/dev/null | wc -l)
    if [ "$FILE_COUNT" -gt 10000 ]; then
        echo "   Skipping auto-index: project too large ($FILE_COUNT files)" >&2
        echo "false"
        return 0
    fi

    # Run automatic setup
    echo "   Detected new project - initializing fractal orchestration..." >&2
    echo "   This will take <5 minutes for the first-time setup..." >&2
    echo "" >&2

    # Step 1: Build knowledge graph
    echo "   [1/4] Building knowledge graph..." >&2
    if python3 "$SCRIPTS_DIR/knowledge-indexer.py" "$project_path" --output "$GRAPH_FILE" >/dev/null 2>&1; then
        echo "   [ok] Knowledge graph created" >&2
    else
        echo "   [warn] Knowledge graph creation failed (continuing anyway)" >&2
    fi

    # Step 2: Extract patterns
    local PATTERNS_FILE="/tmp/fractal_patterns_${project_name}.json"
    local ADAPTED_FILE="/tmp/fractal_adapted_${project_name}.json"
    echo "   [2/4] Extracting patterns..." >&2
    if [ -f "$GRAPH_FILE" ] && python3 "$SCRIPTS_DIR/pattern-extractor.py" "$GRAPH_FILE" "$PATTERNS_FILE" >/dev/null 2>&1; then
        echo "   [ok] Patterns extracted" >&2
    else
        echo "   [warn] Pattern extraction failed (continuing anyway)" >&2
    fi

    # Step 3: Adapt pattern format for rule distiller
    echo "   [3/4] Adapting patterns..." >&2
    if [ -f "$PATTERNS_FILE" ] && python3 "$SCRIPTS_DIR/pattern-adapter.py" "$PATTERNS_FILE" "$ADAPTED_FILE" >/dev/null 2>&1; then
        echo "   [ok] Patterns adapted" >&2
    else
        echo "   [warn] Pattern adaptation failed (continuing anyway)" >&2
    fi

    # Step 4: Distill seed rules into seeds/workflows/{workflow}/
    echo "   [4/4] Distilling seed rules..." >&2
    if [ -f "$ADAPTED_FILE" ] && python3 "$SCRIPTS_DIR/rule-distiller.py" \
        "$ADAPTED_FILE" \
        --project "$project_name" \
        --level opus \
        --workflow "$workflow" \
        --output-dir "$project_path" >/dev/null 2>&1; then
        echo "   [ok] Seed rules created" >&2
    else
        echo "   [warn] Seed rule distillation failed" >&2
    fi

    # Cleanup temp files
    rm -f "$PATTERNS_FILE" "$ADAPTED_FILE" 2>/dev/null

    echo "" >&2
    echo "   Fractal orchestration initialized for: $project_name" >&2
    echo "   Seed rules: seeds/workflows/$workflow/*.json" >&2
    echo "" >&2

    echo "true" # Did run setup
}

# Find context files
claude_md=$(find_file "CLAUDE.md" || echo "")
state_md=$(find_file "state.md" || echo "")
todo_md=$(find_file "todo.md" || echo "")

# Exit if no CLAUDE.md
if [ -z "$claude_md" ]; then
    echo '{"error": "No CLAUDE.md found", "context_loaded": false}'
    exit 1
fi

# Extract info
project_path=$(dirname "$claude_md")
project_name=$(basename "$project_path")
workflow=$(get_workflow "$claude_md")
status=$([ -n "$state_md" ] && get_status "$state_md" || echo "Unknown")
pending=$([ -n "$todo_md" ] && count_todos "$todo_md" || echo "0")
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Auto-setup if needed (returns "true" or "false")
auto_setup_ran=$(auto_setup_project "$project_path" "$project_name" "$workflow")

# Check initialization status
has_knowledge_graph=false
has_seed_rules=false

GRAPH_DIR="$SCRIPTS_DIR/../knowledge/graph"
if [ -f "$GRAPH_DIR/${project_name}_nodes.json" ]; then
    has_knowledge_graph=true
fi

if [ -d "$project_path/seeds/workflows/$workflow" ] && \
   ls "$project_path/seeds/workflows/$workflow/"*.json 2>/dev/null | head -1 > /dev/null 2>&1; then
    has_seed_rules=true
fi

# Determine if fully initialized
if [ "$has_knowledge_graph" = true ] && [ "$has_seed_rules" = true ]; then
    is_initialized=true
else
    is_initialized=false
fi

# Assemble prompt rules for this workflow (JSON array of rule strings)
prompt_rules_json="[]"
if [ "$has_seed_rules" = true ]; then
    prompt_rules_json=$(python3 "$SCRIPTS_DIR/assemble-prompt.py" \
        --project-dir "$project_path" \
        --workflow "$workflow" \
        --json 2>/dev/null || echo "[]")
fi

# Output JSON
cat <<EOF
{
  "version": "2.1.0",
  "timestamp": "$timestamp",
  "project": {
    "name": "$project_name",
    "path": "$project_path",
    "workflow": "$workflow",
    "initialized": $is_initialized,
    "auto_setup_ran": $auto_setup_ran
  },
  "status": "$status",
  "pending_todos": $pending,
  "fractal": {
    "knowledge_graph": $has_knowledge_graph,
    "seed_rules": $has_seed_rules
  },
  "prompt_rules": $prompt_rules_json,
  "files": {
    "claude_md": "$claude_md",
    "state_md": "${state_md:-null}",
    "todo_md": "${todo_md:-null}"
  },
  "context_loaded": true
}
EOF
