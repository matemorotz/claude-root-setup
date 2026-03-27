# Claude Root Setup

Portable bootstrap for a Claude Code orchestration environment on a fresh VPS or machine.

Installs in one command:

```bash
bash install.sh [WORKSPACE_ROOT]
```

Default `WORKSPACE_ROOT` is `$HOME/software`. Pass a custom path to install elsewhere:

```bash
bash install.sh /home/ubuntu/workspace
```

---

## What Gets Installed

```
~/.claude/
├── CLAUDE.md          ← Global preferences and agent strategy
└── settings.json      ← Permissions, plugins, model defaults

$WORKSPACE_ROOT/
├── CLAUDE.md          ← Workspace routing instructions (root agent)
├── claude-code-framework/
│   ├── hooks/         ← session-start.sh, session-stop.sh
│   ├── scripts/       ← knowledge-indexer, pattern-extractor, rule-distiller, ...
│   ├── docs/          ← fractal architecture docs
│   ├── templates/     ← CLAUDE.md.template, governor-domain/
│   └── seeds/         ← default seed rule JSONs
└── .claude/
    ├── settings.json  ← Domain hooks + model config
    ├── hooks/         → symlink → ../claude-code-framework/hooks/
    ├── scripts/       → symlink → ../claude-code-framework/scripts/
    ├── fractal/       → symlink → ../claude-code-framework/docs/
    ├── agents/        ← execution, orchestration, research agents
    ├── schemas/       ← JSON schemas for plans and contexts
    ├── skills/        ← reusable skill plugins
    └── docs/          ← architecture documentation
```

---

## How It Works

### Session auto-initialization

When you open Claude Code anywhere inside `$WORKSPACE_ROOT`, the `SessionStart` hook fires:

1. Walks up the directory tree to find the nearest `CLAUDE.md`
2. Extracts the `## Workflow: <name>` from the project's `CLAUDE.md`
3. Runs the 4-step pipeline on first encounter:
   - `knowledge-indexer.py` — builds a knowledge graph of the project
   - `pattern-extractor.py` — extracts architectural patterns
   - `pattern-adapter.py` — adapts patterns for distillation
   - `rule-distiller.py` — generates seed rules → `seeds/workflows/<workflow>/*.json`
4. On subsequent sessions: loads seed rules into prompt context silently

### Agent tiers

| Agent | Model | Role |
|-------|-------|------|
| `opus-planner` | Opus | Strategic planning and decomposition |
| `maestro-planner` | Opus | Multi-domain orchestration |
| `phase-conductor` | Sonnet | Phase execution coordination |
| `sonnet-coder` | Sonnet | Code generation |
| `sonnet-debugger` | Sonnet | Bug analysis |
| `haiku-executor` | Haiku | Fast atomic step execution |

### Fractal memory (4-layer token optimization)

```
user_level/     ← Full project context (unlimited)
opus_level/     ← Distilled seed rules (10-50K tokens)
sonnet_level/   ← Task-specific context (5-15K tokens)
haiku_level/    ← Step context (<2K tokens)
```

Each layer is populated progressively. New projects start with just `user_level` until the first session completes indexing.

---

## Adding a New Project

1. Create a directory under `$WORKSPACE_ROOT`:
   ```bash
   mkdir $WORKSPACE_ROOT/my-project
   ```

2. Copy the CLAUDE.md template and customize it:
   ```bash
   cp $WORKSPACE_ROOT/claude-code-framework/templates/CLAUDE.md.template \
      $WORKSPACE_ROOT/my-project/CLAUDE.md
   # Edit: replace {{PROJECT_NAME}}, set ## Workflow: general
   ```

3. Open Claude Code in that directory — the hook auto-initializes on first session.

---

## Requirements

- Claude Code CLI installed (`claude --version`)
- Python 3.9+
- Bash
- Git

---

## Repository Structure

```
claude-root-setup/
├── install.sh          ← Bootstrap script (run this)
├── .gitignore
├── README.md
├── global/             ← Installs to ~/.claude/
│   ├── CLAUDE.md
│   └── settings.json
├── workspace/          ← Installs to $WORKSPACE_ROOT/
│   ├── CLAUDE.md
│   └── .claude/
│       ├── settings.json   ({{WORKSPACE_ROOT}} placeholder, resolved at install time)
│       ├── agents/
│       ├── docs/
│       ├── schemas/
│       └── skills/
└── framework/          ← Installs to $WORKSPACE_ROOT/claude-code-framework/
    ├── hooks/
    ├── scripts/
    ├── docs/
    ├── templates/
    ├── seeds/
    └── setup.py
```

---

## Idempotent

Running `install.sh` multiple times is safe — existing files are skipped, not overwritten. To reinstall a component, delete it first and re-run.
