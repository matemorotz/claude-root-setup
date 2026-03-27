#!/bin/bash
# Claude Root Setup — Bootstrap Script
# Usage: bash install.sh [WORKSPACE_ROOT]
# Default WORKSPACE_ROOT: $HOME/software
#
# What this does:
#   1. Installs global Claude config → ~/.claude/
#   2. Creates workspace directory with domain config → $WORKSPACE_ROOT/
#   3. Installs framework → $WORKSPACE_ROOT/claude-code-framework/
#   4. Creates symlinks: .claude/hooks, .claude/scripts, .claude/fractal
#   5. Patches all {{WORKSPACE_ROOT}} placeholders with the actual path

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
WORKSPACE_ROOT="${1:-$HOME/software}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colors ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[ok]${NC}  $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
info() { echo -e "      $*"; }

echo ""
echo "Claude Root Setup — Install"
echo "==========================="
echo "  WORKSPACE_ROOT : $WORKSPACE_ROOT"
echo "  Source         : $REPO_DIR"
echo ""

# ── Step 1: Global ~/.claude/ ────────────────────────────────────────────────
echo "1/5  Installing global config → ~/.claude/"

mkdir -p ~/.claude

# CLAUDE.md — only install if none exists (don't overwrite personal config)
if [ ! -f ~/.claude/CLAUDE.md ]; then
    cp "$REPO_DIR/global/CLAUDE.md" ~/.claude/CLAUDE.md
    ok "Installed ~/.claude/CLAUDE.md"
else
    warn "~/.claude/CLAUDE.md already exists — skipping (edit manually to merge)"
fi

# settings.json — merge if exists, install fresh if not
if [ ! -f ~/.claude/settings.json ]; then
    cp "$REPO_DIR/global/settings.json" ~/.claude/settings.json
    ok "Installed ~/.claude/settings.json"
else
    warn "~/.claude/settings.json already exists — skipping (edit manually to merge)"
fi

# ── Step 2: Workspace directory ───────────────────────────────────────────────
echo ""
echo "2/5  Creating workspace → $WORKSPACE_ROOT/"

mkdir -p \
    "$WORKSPACE_ROOT/.claude/agents" \
    "$WORKSPACE_ROOT/.claude/docs" \
    "$WORKSPACE_ROOT/.claude/schemas" \
    "$WORKSPACE_ROOT/.claude/skills" \
    "$WORKSPACE_ROOT/.claude/knowledge/graph" \
    "$WORKSPACE_ROOT/.claude/memory/user_level" \
    "$WORKSPACE_ROOT/.claude/memory/opus_level/seed_rules" \
    "$WORKSPACE_ROOT/.claude/memory/sonnet_level/task_contexts" \
    "$WORKSPACE_ROOT/.claude/memory/haiku_level/step_contexts"
ok "Created directory structure"

# Workspace CLAUDE.md
if [ ! -f "$WORKSPACE_ROOT/CLAUDE.md" ]; then
    cp "$REPO_DIR/workspace/CLAUDE.md" "$WORKSPACE_ROOT/CLAUDE.md"
    ok "Installed $WORKSPACE_ROOT/CLAUDE.md"
else
    warn "$WORKSPACE_ROOT/CLAUDE.md already exists — skipping"
fi

# Agents, schemas, skills, docs
cp -rn "$REPO_DIR/workspace/.claude/agents/." "$WORKSPACE_ROOT/.claude/agents/" 2>/dev/null || true
cp -rn "$REPO_DIR/workspace/.claude/schemas/." "$WORKSPACE_ROOT/.claude/schemas/" 2>/dev/null || true
cp -rn "$REPO_DIR/workspace/.claude/skills/." "$WORKSPACE_ROOT/.claude/skills/" 2>/dev/null || true
cp -rn "$REPO_DIR/workspace/.claude/docs/." "$WORKSPACE_ROOT/.claude/docs/" 2>/dev/null || true
ok "Installed agents, schemas, skills, docs"

# settings.json with placeholder replaced
SETTINGS_DST="$WORKSPACE_ROOT/.claude/settings.json"
if [ ! -f "$SETTINGS_DST" ]; then
    sed "s|{{WORKSPACE_ROOT}}|$WORKSPACE_ROOT|g" \
        "$REPO_DIR/workspace/.claude/settings.json" > "$SETTINGS_DST"
    ok "Installed $SETTINGS_DST (paths resolved)"
else
    warn "$SETTINGS_DST already exists — skipping"
fi

# ── Step 3: Framework ─────────────────────────────────────────────────────────
echo ""
echo "3/5  Installing framework → $WORKSPACE_ROOT/claude-code-framework/"

FRAMEWORK_DST="$WORKSPACE_ROOT/claude-code-framework"
if [ -d "$FRAMEWORK_DST" ]; then
    warn "Framework already exists at $FRAMEWORK_DST — skipping (delete it first to reinstall)"
else
    cp -r "$REPO_DIR/framework" "$FRAMEWORK_DST"
    ok "Copied framework"

    # Patch WORKSPACE_ROOT in hooks
    sed -i "s|WORKSPACE_ROOT=\"\${WORKSPACE_ROOT:-\$HOME/software}\"|WORKSPACE_ROOT=\"\${WORKSPACE_ROOT:-$WORKSPACE_ROOT}\"|g" \
        "$FRAMEWORK_DST/hooks/session-start.sh" \
        "$FRAMEWORK_DST/hooks/session-stop.sh"
    ok "Patched hook paths (default WORKSPACE_ROOT=$WORKSPACE_ROOT)"
fi

# ── Step 4: Symlinks ─────────────────────────────────────────────────────────
echo ""
echo "4/5  Creating symlinks"

CLAUDE_DIR="$WORKSPACE_ROOT/.claude"
FRAMEWORK_DIR="$WORKSPACE_ROOT/claude-code-framework"

create_symlink() {
    local link="$1"
    local target="$2"
    if [ -L "$link" ]; then
        warn "$link already a symlink — skipping"
    elif [ -d "$link" ]; then
        warn "$link is a real directory — skipping (remove it manually to create symlink)"
    else
        ln -s "$target" "$link"
        ok "Symlink: $link → $target"
    fi
}

create_symlink "$CLAUDE_DIR/hooks"   "../claude-code-framework/hooks"
create_symlink "$CLAUDE_DIR/scripts" "../claude-code-framework/scripts"
create_symlink "$CLAUDE_DIR/fractal" "../claude-code-framework/docs"

# ── Step 5: Permissions ───────────────────────────────────────────────────────
echo ""
echo "5/5  Setting executable permissions"

chmod +x "$FRAMEWORK_DIR/hooks/"*.sh 2>/dev/null || true
chmod +x "$FRAMEWORK_DIR/scripts/"*.py 2>/dev/null || true
chmod +x "$FRAMEWORK_DIR/scripts/orchestrate" 2>/dev/null || true
chmod +x "$FRAMEWORK_DIR/scripts/health-check.sh" 2>/dev/null || true
ok "Permissions set"

# ── Verification ──────────────────────────────────────────────────────────────
echo ""
echo "==========================="
echo "Verification"
echo "==========================="

check() {
    local label="$1"
    local path="$2"
    if [ -e "$path" ]; then
        echo -e "${GREEN}✓${NC} $label"
    else
        echo -e "${RED}✗${NC} $label  ← MISSING: $path"
    fi
}

check "~/.claude/CLAUDE.md"                          ~/.claude/CLAUDE.md
check "~/.claude/settings.json"                      ~/.claude/settings.json
check "$WORKSPACE_ROOT/CLAUDE.md"                    "$WORKSPACE_ROOT/CLAUDE.md"
check "$WORKSPACE_ROOT/.claude/settings.json"        "$WORKSPACE_ROOT/.claude/settings.json"
check "$WORKSPACE_ROOT/.claude/hooks (symlink)"      "$WORKSPACE_ROOT/.claude/hooks"
check "$WORKSPACE_ROOT/.claude/scripts (symlink)"    "$WORKSPACE_ROOT/.claude/scripts"
check "$WORKSPACE_ROOT/claude-code-framework/hooks/" "$WORKSPACE_ROOT/claude-code-framework/hooks/session-start.sh"
check "Agents installed"                             "$WORKSPACE_ROOT/.claude/agents/execution/haiku-executor.md"

echo ""
echo -e "${GREEN}Done!${NC} Start a Claude Code session in $WORKSPACE_ROOT to trigger auto-initialization."
echo ""
echo "  cd $WORKSPACE_ROOT"
echo "  claude"
echo ""
echo "On first session, the hook will index your projects and generate seed rules."
echo ""
