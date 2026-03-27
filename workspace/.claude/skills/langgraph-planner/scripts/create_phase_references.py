#!/usr/bin/env python3
"""
Extract phase content from SKILL.md and create 11 phase-specific reference files.

Why this solution:
- Automates extraction of 1,088 lines into organized phase files
- Ensures consistent structure across all phase references
- Preserves all detailed content while enabling progressive disclosure
- Creates navigation links between phases for sequential workflow
"""

import re
from pathlib import Path
from typing import List, Tuple

# Phase definitions with target names
PHASES = [
    (1, "complexity_analysis", "Graph Complexity Analysis"),
    (2, "nodes_edges_state", "Nodes, Edges, and State Objects"),
    (3, "node_io", "I/O for Every Node"),
    (4, "conditional_edges", "Conditional Edges Planning"),
    (5, "llm_prompts", "LLM Call Planning"),
    (6, "state_evolution", "State Evolution Example"),
    (7, "archetypes", "Archetype Generation"),
    (8, "code_generation", "Code Generation"),
    (9, "structure_check", "Final Structure Check & Logic Control"),
    (10, "safety_analysis", "Safety Analysis"),
    (11, "mock_testing", "Mock Testing"),
]


def extract_phase_content(skill_md_path: Path) -> List[Tuple[int, str, str]]:
    """
    Extract content for each phase from SKILL.md.

    Returns: List of (phase_number, phase_title, content) tuples
    """
    content = skill_md_path.read_text()
    phase_sections = []

    # Find all phase sections
    phase_pattern = r'## Phase (\d+): (.+?)\n(.*?)(?=\n## Phase |\n## Enforcement Features|\Z)'
    matches = re.finditer(phase_pattern, content, re.DOTALL)

    for match in matches:
        phase_num = int(match.group(1))
        phase_title = match.group(2).strip()
        phase_content = match.group(3).strip()
        phase_sections.append((phase_num, phase_title, phase_content))

    return phase_sections


def create_phase_reference(
    phase_num: int,
    phase_slug: str,
    phase_title: str,
    content: str,
    output_dir: Path
) -> None:
    """
    Create a phase-specific reference file with consistent structure.
    """
    filename = f"phase{phase_num}_{phase_slug}.md"
    filepath = output_dir / filename

    # Determine next and previous phases
    prev_phase = None
    next_phase = None

    for i, (num, slug, title) in enumerate(PHASES):
        if num == phase_num:
            if i > 0:
                prev_phase = PHASES[i - 1]
            if i < len(PHASES) - 1:
                next_phase = PHASES[i + 1]
            break

    # Build navigation
    navigation = "## Navigation\n\n"
    if prev_phase:
        navigation += f"**Previous:** [`Phase {prev_phase[0]}: {prev_phase[2]}`](@phase{prev_phase[0]}_{prev_phase[1]}.md)\n\n"
    else:
        navigation += "**Previous:** (First phase)\n\n"

    if next_phase:
        navigation += f"**Next:** [`Phase {next_phase[0]}: {next_phase[2]}`](@phase{next_phase[0]}_{next_phase[1]}.md)\n\n"
    else:
        navigation += "**Next:** (Final phase - proceed to implementation)\n\n"

    # Build file content
    file_content = f"""# Phase {phase_num}: {phase_title}

## Essential Context (Load First)

**Goal:** Extract key purpose from phase content below

**Prerequisites:**
- Completed Phase {phase_num - 1 if phase_num > 1 else 'None'}
- Have graph structure from previous phases
- Ready to proceed with detailed planning

**Expected Duration:** 15-30 minutes (depends on graph complexity)

---

{navigation}---

## Detailed Process

{content}

---

## Common Pitfalls

Phase {phase_num} common mistakes:
- Rushing through without proper consideration
- Skipping validation steps
- Not documenting decisions for later reference
- Not getting user feedback when uncertain

---

## Validation Checklist

Before moving to Phase {phase_num + 1 if phase_num < 11 else 'implementation'}:
- [ ] Phase {phase_num} deliverables are complete
- [ ] User has reviewed and approved (if needed)
- [ ] All questions answered
- [ ] Documentation updated

---

{navigation}
"""

    filepath.write_text(file_content)
    print(f"✓ Created {filename} ({len(file_content)} chars)")


def main():
    """Main execution"""
    # Paths
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    references_dir = skill_dir / "references"

    print(f"Extracting phase content from {skill_md}...")
    print(f"Creating phase references in {references_dir}/\n")

    # Extract phases
    phase_sections = extract_phase_content(skill_md)
    print(f"Found {len(phase_sections)} phase sections\n")

    # Create reference files
    for phase_num, phase_title, content in phase_sections:
        # Find matching phase slug
        phase_slug = None
        for num, slug, title in PHASES:
            if num == phase_num:
                phase_slug = slug
                break

        if phase_slug:
            create_phase_reference(
                phase_num, phase_slug, phase_title, content, references_dir
            )

    print(f"\n✓ Successfully created {len(phase_sections)} phase reference files")
    print(f"✓ Total content extracted: ~{sum(len(c) for _, _, c in phase_sections)} characters")
    print(f"\nNext steps:")
    print(f"1. Review generated files in {references_dir}/")
    print(f"2. Rewrite SKILL.md to <500 lines with brief phase overviews")
    print(f"3. Update SKILL.md to reference these phase files")


if __name__ == "__main__":
    main()
