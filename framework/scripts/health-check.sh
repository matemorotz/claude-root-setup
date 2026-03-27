#!/bin/bash
# Health Check Script for Claude Code Initialization System
# Version: 1.0.0

set -uo pipefail

PASS=0
FAIL=0
WARN=0

check() {
    local label="$1"
    local result="$2"
    if [ "$result" = "ok" ]; then
        echo "  [OK]   $label"
        ((PASS++))
    elif [ "$result" = "warn" ]; then
        echo "  [WARN] $label"
        ((WARN++))
    else
        echo "  [FAIL] $label"
        ((FAIL++))
    fi
}

echo "=== Claude Code Health Check ==="
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# 1. Context files
echo "--- Context Files ---"
check "CLAUDE.md (global)" "$([ -f /root/.claude/CLAUDE.md ] && echo ok || echo fail)"
check "CLAUDE.md (root)" "$([ -f /root/CLAUDE.md ] && echo ok || echo fail)"
check "CLAUDE.md (software)" "$([ -f /root/software/CLAUDE.md ] && echo ok || echo fail)"
check "CLAUDE_MASTER_RULES.md" "$([ -f /root/software/CLAUDE_MASTER_RULES.md ] && echo ok || echo fail)"
check "ENVIRONMENT_STRUCTURE.md" "$([ -f /root/software/ENVIRONMENT_STRUCTURE.md ] && echo ok || echo fail)"
check "project.md" "$([ -f /root/software/project.md ] && echo ok || echo fail)"
echo ""

# 2. Hook executable
echo "--- Hooks ---"
check "session-start.sh exists" "$([ -f /root/software/.claude/hooks/session-start.sh ] && echo ok || echo fail)"
check "session-start.sh executable" "$([ -x /root/software/.claude/hooks/session-start.sh ] && echo ok || echo warn)"
echo ""

# 3. Fractal pipeline scripts
echo "--- Fractal Pipeline ---"
check "knowledge-indexer.py" "$([ -f /root/software/.claude/scripts/knowledge-indexer.py ] && echo ok || echo fail)"
check "pattern-extractor.py" "$([ -f /root/software/.claude/scripts/pattern-extractor.py ] && echo ok || echo fail)"
check "rule-distiller.py" "$([ -f /root/software/.claude/scripts/rule-distiller.py ] && echo ok || echo fail)"
check "knowledge graph (software)" "$([ -f /root/software/.claude/knowledge/graph/software_nodes.json ] && echo ok || echo warn)"
check "seed rules exist" "$([ -f /root/software/.claude/memory/opus_level/seed_rules/software.json ] && echo ok || echo warn)"
echo ""

# 4. No malformed brace directories
echo "--- Directory Health ---"
brace_dirs=$(find /root/software/.claude/memory -name "{*" -type d 2>/dev/null | wc -l)
check "No malformed brace dirs" "$([ "$brace_dirs" -eq 0 ] && echo ok || echo fail)"
check "opus_level/seed_rules dir" "$([ -d /root/software/.claude/memory/opus_level/seed_rules ] && echo ok || echo fail)"
check "sonnet_level/task_contexts dir" "$([ -d /root/software/.claude/memory/sonnet_level/task_contexts ] && echo ok || echo fail)"
check "haiku_level/step_contexts dir" "$([ -d /root/software/.claude/memory/haiku_level/step_contexts ] && echo ok || echo fail)"
echo ""

# 5. Settings health
echo "--- Settings ---"
check "settings.json (global)" "$([ -f /root/.claude/settings.json ] && echo ok || echo fail)"
check "settings.json (project)" "$([ -f /root/software/.claude/settings.json ] && echo ok || echo fail)"
check "No dual hook" "$(python3 -c "
import json
with open('/root/.claude/settings.json') as f:
    d = json.load(f)
print('ok' if 'hooks' not in d else 'fail')
" 2>/dev/null || echo fail)"
check "Model config = sonnet" "$(python3 -c "
import json
with open('/root/software/.claude/settings.json') as f:
    d = json.load(f)
print('ok' if d.get('models',{}).get('execution') == 'sonnet' else 'fail')
" 2>/dev/null || echo fail)"
echo ""

# 6. Skill duplication check
echo "--- Skills ---"
root_skills=$(ls -d /root/.claude/skills/*/ 2>/dev/null | wc -l)
sw_skills=$(ls -d /root/software/.claude/skills/*/ 2>/dev/null | wc -l)
dupes=0
for skill in /root/.claude/skills/*/; do
    name=$(basename "$skill")
    if [ -d "/root/software/.claude/skills/$name" ]; then
        ((dupes++))
    fi
done
check "Root skills: $root_skills" "ok"
check "Software skills: $sw_skills" "ok"
check "Duplicate skills: $dupes" "$([ "$dupes" -eq 0 ] && echo ok || echo warn)"
echo ""

# 7. Plugin count
echo "--- Plugins ---"
enabled=$(python3 -c "
import json
with open('/root/.claude/settings.json') as f:
    d = json.load(f)
count = sum(1 for v in d.get('enabledPlugins', {}).values() if v)
print(count)
" 2>/dev/null || echo "?")
disabled=$(python3 -c "
import json
with open('/root/.claude/settings.json') as f:
    d = json.load(f)
count = sum(1 for v in d.get('enabledPlugins', {}).values() if not v)
print(count)
" 2>/dev/null || echo "?")
check "Enabled plugins: $enabled" "ok"
check "Disabled plugins: $disabled" "ok"
echo ""

# 8. Credentials check
echo "--- Security ---"
cred_in_autoload=$(grep -l "zgThA8skq" /root/software/CLAUDE.md /root/software/ENVIRONMENT_STRUCTURE.md 2>/dev/null | wc -l)
check "No credentials in auto-loaded files" "$([ "$cred_in_autoload" -eq 0 ] && echo ok || echo fail)"
cred_in_project=$(grep -c "zgThA8skq" /root/software/project.md 2>/dev/null || true)
check "No credentials in project.md" "$([ "${cred_in_project:-0}" -eq 0 ] && echo ok || echo fail)"
echo ""

# 9. Logs
echo "--- Logging ---"
check "Log directory exists" "$([ -d /root/software/.claude/logs ] && echo ok || echo warn)"
latest_log=$(ls -t /root/software/.claude/logs/session-start-*.log 2>/dev/null | head -1)
check "Recent session log" "$([ -n "$latest_log" ] && echo ok || echo warn)"
echo ""

# Summary
echo "=== Summary ==="
echo "  PASS: $PASS"
echo "  WARN: $WARN"
echo "  FAIL: $FAIL"
total=$((PASS + WARN + FAIL))
if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
    echo "  Status: ALL OK"
elif [ "$FAIL" -eq 0 ]; then
    echo "  Status: OK with warnings"
else
    echo "  Status: ISSUES FOUND"
fi
