---
name: worktree
description: Create new projects or set up git worktrees for existing projects. Use when starting a new project, setting up development worktrees, listing worktrees, or cleaning up stale worktrees.
---

# Worktree Management Skill

Manage git worktrees and create new projects following best practices for parallel AI development.

## Quick Commands

```bash
# Interactive menu
worktree-setup

# Create new project
worktree-setup --new

# Set up worktree for existing project
worktree-setup my_project

# List all worktrees
worktree-setup --list

# Clean up stale worktrees
worktree-setup --cleanup
```

## When to Use This Skill

Activate when user wants to:
- **Create a new project** with proper structure
- **Set up a development worktree** for an existing project
- **List all worktrees** across projects
- **Clean up stale worktrees**
- **Understand worktree best practices**

**Keywords:** new project, worktree, development environment, project setup, parallel development

## Creating a New Project

Run interactively:
```bash
worktree-setup --new
```

This will:
1. Prompt for project name, type (Python/Node), and description
2. Create `/root/software/project_name/` with full structure
3. Initialize git with proper `.gitignore`
4. Create Python venv or Node package.json
5. Set up dev worktree at `/root/.dev/project_name_dev/`
6. Generate CLAUDE.md, project.md, state.md, todo.md

## Setting Up Existing Project

From project directory:
```bash
cd /root/software/my_project
worktree-setup
```

Or by name:
```bash
worktree-setup my_project
```

This will:
1. Initialize git if needed
2. Add Claude Code exclusions to `.gitignore`
3. Create dev worktree at `/root/.dev/my_project_dev/`
4. Generate development documentation
5. Symlink IDE settings (.vscode, .idea)

## Directory Structure

```
/root/software/
├── project_name/              # Main repository (production)
│   ├── .git/                  # Git objects (shared)
│   ├── .gitignore             # Ignores .claude/, CLAUDE.md
│   ├── src/                   # Source code
│   └── [main branch]          # Clean, stable code only

/root/.dev/
├── project_name_dev/          # Development worktree
│   ├── .git → points to main  # Linked to main .git
│   ├── .claude/               # Claude Code settings (NOT in git)
│   ├── CLAUDE.md              # Dev instructions (NOT in git)
│   ├── project.md             # Project architecture
│   ├── state.md               # Current status
│   ├── todo.md                # Task list
│   └── [project_name_dev branch]
```

## AI Development Workflow

Follow **Explore → Plan → Code → Commit** in each worktree:

1. **Explore:** Run `/init` in Claude Code to orient with codebase
2. **Plan:** Create step-by-step plan before coding
3. **Code:** Implement incrementally, test as you go
4. **Commit:** Commit working changes with clear messages

### Parallel Development

Run multiple Claude Code instances in different worktrees:
```bash
# Terminal 1: Feature A
cd /root/.dev/project_dev
claude  # Works on feature A

# Terminal 2: Feature B (create another worktree)
cd /root/software/project
git worktree add /root/.dev/project_feature_b -b feature_b
cd /root/.dev/project_feature_b
claude  # Works on feature B independently
```

## Best Practices

1. **Keep Main Clean** - Never develop directly in main
2. **Commit Often** - Small, frequent commits in dev branch
3. **Rebase Regularly** - `git rebase main` to avoid conflicts
4. **Test Before Merging** - Run full test suite before merge
5. **Use Descriptive Messages** - Clear commits help future you

## Merging to Main

```bash
# Ensure dev branch is clean
cd /root/.dev/project_dev
git status  # Must be clean

# Run tests
pytest tests/ -v  # or npm test

# Switch to main
cd /root/software/project

# Merge dev branch
git merge project_dev

# Verify
git log --oneline -n 5
```

## Script Location

- **Script:** `/root/software/scripts/setup-worktree.sh`
- **Symlink:** `/usr/local/bin/worktree-setup`
- **Standards:** `/root/software/WORKTREE_STANDARDS.md`

## References

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Using Git Worktrees for Parallel AI Development](https://stevekinney.com/courses/ai-development/git-worktrees)
