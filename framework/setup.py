#!/usr/bin/env python3
"""
Claude Code Framework - Installation Script

Usage:
    python setup.py install [--project-dir /path/to/project]
    python setup.py link    # Create symlinks to this framework
"""

import argparse
import os
import shutil
import json
from pathlib import Path


FRAMEWORK_DIR = Path(__file__).parent.resolve()


def install_to_project(project_dir: Path, overwrite: bool = False):
    """Install framework components to a project directory."""

    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # Copy hooks
    hooks_src = FRAMEWORK_DIR / "hooks"
    hooks_dst = claude_dir / "hooks"
    if hooks_dst.exists() and not overwrite:
        print(f"⚠️  Hooks already exist at {hooks_dst}, skipping (use --overwrite to replace)")
    else:
        if hooks_dst.exists():
            shutil.rmtree(hooks_dst)
        shutil.copytree(hooks_src, hooks_dst)
        print(f"✅ Installed hooks to {hooks_dst}")

    # Copy scripts
    scripts_src = FRAMEWORK_DIR / "scripts"
    scripts_dst = claude_dir / "scripts"
    if scripts_dst.exists() and not overwrite:
        print(f"⚠️  Scripts already exist at {scripts_dst}, skipping (use --overwrite to replace)")
    else:
        if scripts_dst.exists():
            shutil.rmtree(scripts_dst)
        shutil.copytree(scripts_src, scripts_dst)
        print(f"✅ Installed scripts to {scripts_dst}")

    # Create memory directories
    memory_dirs = [
        claude_dir / "memory" / "user_level" / "projects",
        claude_dir / "memory" / "opus_level" / "seed_rules",
        claude_dir / "memory" / "sonnet_level" / "task_contexts",
        claude_dir / "memory" / "sonnet_level" / "results",
        claude_dir / "memory" / "haiku_level" / "step_contexts",
        claude_dir / "memory" / "haiku_level" / "step_results",
    ]

    for d in memory_dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created memory directories")

    # Create CLAUDE.md if not exists
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        template = FRAMEWORK_DIR / "templates" / "CLAUDE.md.template"
        if template.exists():
            shutil.copy(template, claude_md)
            print(f"✅ Created CLAUDE.md from template")
        else:
            claude_md.write_text(f"""# {project_dir.name}

**Type:** Python/TypeScript
**Status:** Active

## Quick Start

```bash
# Add your quick start commands here
```

## Project Structure

```
{project_dir.name}/
├── CLAUDE.md       # This file
├── src/            # Source code
└── tests/          # Tests
```

## Development Rules

1. Follow existing patterns
2. Add type hints
3. Write tests

---

**Fractal orchestration initialized.**
""")
            print(f"✅ Created default CLAUDE.md")
    else:
        print(f"ℹ️  CLAUDE.md already exists, skipping")

    print(f"\n🎉 Framework installed to {project_dir}")
    print(f"   Run 'claude' in project directory to auto-initialize")


def create_symlinks():
    """Create symlinks from /root/software/.claude to framework components."""

    software_claude = Path("/root/software/.claude")
    software_claude.mkdir(exist_ok=True)

    # Link hooks
    hooks_link = software_claude / "hooks"
    if hooks_link.is_symlink():
        hooks_link.unlink()
    elif hooks_link.exists():
        print(f"⚠️  {hooks_link} exists and is not a symlink, backing up")
        shutil.move(hooks_link, hooks_link.with_suffix(".backup"))

    hooks_link.symlink_to(FRAMEWORK_DIR / "hooks")
    print(f"✅ Linked hooks: {hooks_link} -> {FRAMEWORK_DIR / 'hooks'}")

    # Link scripts
    scripts_link = software_claude / "scripts"
    if scripts_link.is_symlink():
        scripts_link.unlink()
    elif scripts_link.exists():
        print(f"⚠️  {scripts_link} exists and is not a symlink, backing up")
        shutil.move(scripts_link, scripts_link.with_suffix(".backup"))

    scripts_link.symlink_to(FRAMEWORK_DIR / "scripts")
    print(f"✅ Linked scripts: {scripts_link} -> {FRAMEWORK_DIR / 'scripts'}")

    # Link docs as fractal
    fractal_link = software_claude / "fractal"
    if fractal_link.is_symlink():
        fractal_link.unlink()
    elif fractal_link.exists():
        print(f"⚠️  {fractal_link} exists and is not a symlink, backing up")
        shutil.move(fractal_link, fractal_link.with_suffix(".backup"))

    fractal_link.symlink_to(FRAMEWORK_DIR / "docs")
    print(f"✅ Linked fractal: {fractal_link} -> {FRAMEWORK_DIR / 'docs'}")

    print(f"\n🎉 Framework linked from /root/software/.claude")


def init_governor_domain(domain_dir: Path, domain_name: str):
    """Initialize a .governor folder for a domain."""

    governor_dir = domain_dir / ".governor"
    governor_dir.mkdir(exist_ok=True)

    # Copy templates
    template_dir = FRAMEWORK_DIR / "templates" / "governor-domain"
    if template_dir.exists():
        for template_file in template_dir.glob("*.md"):
            dst = governor_dir / template_file.name
            if not dst.exists():
                content = template_file.read_text()
                content = content.replace("{{DOMAIN_NAME}}", domain_name)
                dst.write_text(content)
                print(f"✅ Created {dst}")
    else:
        # Create default files
        (governor_dir / "Governor.md").write_text(f"""# {domain_name} Governor

**Domain:** {domain_name}
**Mission:** Handle tasks related to {domain_name}

## Routing Rules

See `Agents.md` for available specialists.

## Termination Logic

```
1. COUNT steps in plan where done:false
2. IF count is ZERO → return [TERMINATE]
3. ELSE → route to next uncompleted step
```
""")

        (governor_dir / "Agents.md").write_text(f"""# {domain_name} Agents

## Available Specialists

| Agent | Purpose | MCP Tools |
|-------|---------|-----------|
| TBD | TBD | TBD |

## Agent Capabilities

Add agent details as you create specialists.
""")

        (governor_dir / "MCP.md").write_text(f"""# {domain_name} MCP Services

## Available MCP Servers

| Server | Purpose | Tools |
|--------|---------|-------|
| TBD | TBD | TBD |

## Tool Reference

Add MCP tool documentation as you integrate services.
""")

        (governor_dir / "Rules.md").write_text(f"""# {domain_name} Rules

## Business Rules

1. Follow company policies
2. Escalate when needed
3. Document decisions

## Safety Rules

1. Never expose sensitive data
2. Validate all inputs
3. Log all operations
""")

        (governor_dir / "Examples.md").write_text(f"""# {domain_name} Examples

## Workflow Examples

### Example 1: Basic Task

**Input:** User request
**Processing:** Agent routing
**Output:** Response

Add real examples as you develop the domain.
""")

        print(f"✅ Created default governor files")

    # Create knowledge directory
    (governor_dir / "knowledge").mkdir(exist_ok=True)

    print(f"\n🎉 Governor domain initialized at {governor_dir}")


def main():
    parser = argparse.ArgumentParser(description="Claude Code Framework Setup")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install framework to project")
    install_parser.add_argument("--project-dir", "-p", type=Path, default=Path.cwd(),
                                help="Project directory (default: current)")
    install_parser.add_argument("--overwrite", "-o", action="store_true",
                                help="Overwrite existing files")

    # Link command
    link_parser = subparsers.add_parser("link", help="Create symlinks to framework")

    # Init-governor command
    governor_parser = subparsers.add_parser("init-governor", help="Initialize .governor folder")
    governor_parser.add_argument("--domain-dir", "-d", type=Path, default=Path.cwd(),
                                 help="Domain directory (default: current)")
    governor_parser.add_argument("--name", "-n", type=str, required=True,
                                 help="Domain name")

    args = parser.parse_args()

    if args.command == "install":
        install_to_project(args.project_dir.resolve(), args.overwrite)
    elif args.command == "link":
        create_symlinks()
    elif args.command == "init-governor":
        init_governor_domain(args.domain_dir.resolve(), args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
