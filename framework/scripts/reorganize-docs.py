#!/usr/bin/env python3
"""
Documentation Reorganization - Create Fractal Structure

Transforms large monolithic docs into hierarchical graph:
- Small focused files (<1000 words)
- Cross-referenced index files
- Bidirectional links
- Category-based organization
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

DOCS_ROOT = Path(".claude/docs")

# Target structure
CATEGORIES = {
    "overview": ["WHAT_IS_FRACTAL", "WHY_FRACTAL", "TERMINOLOGY"],
    "architecture": ["INDEX", "ORCHESTRATOR_PATTERN", "MEMORY_HIERARCHY",
                     "CONTEXT_ENGINEERING", "AGENT_COORDINATION"],
    "guides": ["QUICK_START", "CREATING_PLANS", "RUNNING_EXECUTION", "DEBUGGING"],
    "agents": ["INDEX"],  # Subdirs per agent
    "memory": ["INDEX", "USER_LEVEL", "OPUS_LEVEL", "SONNET_LEVEL", "HAIKU_LEVEL"],
    "hooks": ["INDEX", "PRE_TASK", "POST_TASK", "ENHANCEMENTS"],
    "patterns": ["INDEX", "VERIFICATION_LOOP", "DELEGATION",
                 "DEPENDENCY_GRAPH", "ANTI_PATTERNS"],
    "integration": ["INDEX", "CLI", "REPLANNING", "TESTING"]
}

# Mapping from large files to new structure
REORGANIZATION_MAP = {
    "ORCHESTRATOR_SEPARATION_PRINCIPLE.md": {
        "overview/WHAT_IS_FRACTAL.md": {
            "section": "Core Concept",
            "extract": "lines:1-50"
        },
        "architecture/ORCHESTRATOR_PATTERN.md": {
            "section": "Orchestration Workflow Pattern",
            "extract": "heading:Orchestration Workflow Pattern"
        },
        "architecture/MEMORY_HIERARCHY.md": {
            "section": "Memory stores details",
            "extract": "heading:Memory System"
        },
        "patterns/VERIFICATION_LOOP.md": {
            "section": "Verification Patterns",
            "extract": "heading:Verification Patterns"
        },
        "patterns/DELEGATION.md": {
            "section": "Orchestrator Never Loads Details",
            "extract": "heading:Key Principles"
        },
        "patterns/ANTI_PATTERNS.md": {
            "section": "Anti-Patterns to Avoid",
            "extract": "heading:Anti-Patterns to Avoid"
        }
    },

    "CONTEXT_ENGINEERING_DELEGATION.md": {
        "architecture/CONTEXT_ENGINEERING.md": {
            "section": "Context Engineering Delegation",
            "extract": "all"
        },
        "agents/opus-planner/DELEGATION.md": {
            "section": "OpusPlanner Delegation",
            "extract": "heading:OpusPlanner"
        },
        "agents/context-engineer/README.md": {
            "section": "ContextEngineer Agent",
            "extract": "heading:ContextEngineer"
        }
    },

    "AGENT_COORDINATION_PATTERN.md": {
        "architecture/AGENT_COORDINATION.md": {
            "section": "I/O Style Coordination",
            "extract": "all"
        },
        "patterns/VERIFICATION_LOOP.md": {
            "section": "Parent Verifies Child",
            "extract": "heading:Parent-Verifies-Child"
        }
    },

    "TASK_HOOKS_ANALYSIS.md": {
        "hooks/INDEX.md": {
            "section": "Hooks Overview",
            "extract": "lines:1-100"
        },
        "hooks/PRE_TASK.md": {
            "section": "Pre-task Hook",
            "extract": "heading:Pre-task"
        },
        "hooks/POST_TASK.md": {
            "section": "Post-task Hook",
            "extract": "heading:Post-task"
        },
        "hooks/ENHANCEMENTS.md": {
            "section": "Enhancement Opportunities",
            "extract": "heading:Enhancement Opportunities"
        },
        "integration/TESTING.md": {
            "section": "Testing Strategy",
            "extract": "heading:Testing Strategy"
        }
    }
}


def create_directory_structure():
    """Create category directories"""
    print("Creating directory structure...")

    for category in CATEGORIES:
        category_dir = DOCS_ROOT / category
        category_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {category}/")


def create_index_file(category: str, files: List[str]) -> str:
    """Generate index file for category"""

    content = f"""# {category.title()} Documentation

**Category:** {category}
**Files:** {len(files)}

---

## Contents

"""

    for file in files:
        if file != "INDEX":
            name = file.replace("_", " ").title()
            link = f"{file}.md"
            content += f"- [{name}]({link})\n"

    content += f"""

---

**Navigation:**
- [← Documentation Index](../INDEX.md)
"""

    return content


def extract_section(source_file: Path, extract_spec: str) -> str:
    """Extract section from source file"""

    if not source_file.exists():
        return f"<!-- Source file not found: {source_file} -->\n"

    with open(source_file) as f:
        content = f.read()

    if extract_spec == "all":
        return content

    elif extract_spec.startswith("lines:"):
        # Extract specific line range
        start, end = map(int, extract_spec.split(":")[1].split("-"))
        lines = content.split("\n")
        return "\n".join(lines[start-1:end])

    elif extract_spec.startswith("heading:"):
        # Extract section starting with heading
        heading = extract_spec.split(":", 1)[1]

        # Find heading and extract until next same-level heading
        pattern = rf"^(#+)\s+{re.escape(heading)}"
        match = re.search(pattern, content, re.MULTILINE)

        if not match:
            return f"<!-- Heading not found: {heading} -->\n"

        level = len(match.group(1))
        start_pos = match.start()

        # Find next same-level heading
        next_heading = rf"^#{{{level}}}\s+"
        next_match = re.search(next_heading, content[start_pos+len(match.group(0)):], re.MULTILINE)

        if next_match:
            end_pos = start_pos + len(match.group(0)) + next_match.start()
            return content[start_pos:end_pos]
        else:
            return content[start_pos:]

    return content


def create_reorganized_docs():
    """Create reorganized documentation structure"""
    print("\nReorganizing documentation...")

    for source_file, mapping in REORGANIZATION_MAP.items():
        source_path = DOCS_ROOT / source_file

        if not source_path.exists():
            print(f"  ⚠️  Source not found: {source_file}")
            continue

        print(f"\n  Processing: {source_file}")

        for target_file, spec in mapping.items():
            target_path = DOCS_ROOT / target_file
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract section
            section_content = extract_section(source_path, spec["extract"])

            # Add header
            file_name = target_path.stem.replace("_", " ").title()
            header = f"""# {file_name}

**Source:** {source_file}
**Section:** {spec['section']}

---

"""

            # Add navigation footer
            footer = f"""

---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: {source_file}](../{source_file})
"""

            content = header + section_content + footer

            with open(target_path, 'w') as f:
                f.write(content)

            print(f"    → {target_file}")


def create_category_indexes():
    """Create index file for each category"""
    print("\nCreating category indexes...")

    for category, files in CATEGORIES.items():
        index_content = create_index_file(category, files)
        index_path = DOCS_ROOT / category / "INDEX.md"

        with open(index_path, 'w') as f:
            f.write(index_content)

        print(f"  ✓ {category}/INDEX.md")


def generate_summary():
    """Generate reorganization summary"""
    print("\n" + "="*60)
    print("REORGANIZATION SUMMARY")
    print("="*60)

    total_files = 0
    for category, files in CATEGORIES.items():
        count = len([f for f in (DOCS_ROOT / category).glob("*.md") if f.exists()])
        total_files += count
        print(f"  {category:20s} {count:3d} files")

    print(f"\n  TOTAL: {total_files} documentation files")
    print("\n" + "="*60)


if __name__ == "__main__":
    print("Fractal Documentation Reorganization")
    print("="*60)

    # Create structure
    create_directory_structure()

    # Create category indexes
    create_category_indexes()

    # Reorganize large files
    create_reorganized_docs()

    # Summary
    generate_summary()

    print("\n✅ Reorganization complete!")
    print("\nNext steps:")
    print("  1. Review generated files")
    print("  2. Validate cross-references")
    print("  3. Archive original large files")
    print("  4. Update agent documentation")
