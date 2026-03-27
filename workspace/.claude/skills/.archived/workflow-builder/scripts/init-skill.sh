#!/bin/bash
# Initialize new skill from template
# Usage: ./init-skill.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════"
echo "  Skill Initialization Tool"
echo "═══════════════════════════════════════"
echo ""

# Get skill name
while true; do
    read -p "Skill name (lowercase-with-hyphens): " skill_name

    # Validate hyphen-case format
    if [[ $skill_name =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] && [ ${#skill_name} -le 64 ]; then
        break
    else
        echo -e "${RED}✗ Invalid name. Must be hyphen-case, lowercase, under 64 chars${NC}"
        echo "  Examples: managing-databases, analyzing-data, deploying-agents"
    fi
done

# Get description
while true; do
    read -p "Description (max 1024 chars): " description

    if [ ${#description} -le 1024 ] && [ ${#description} -gt 0 ]; then
        break
    else
        echo -e "${RED}✗ Description must be 1-1024 characters${NC}"
    fi
done

# Get template choice
echo ""
echo "Available templates:"
echo "  1) minimal   - Simple skill (~100-300 lines)"
echo "  2) standard  - Standard workflow skill (~300-500 lines)"
echo "  3) complex   - Progressive disclosure skill (500+ lines split)"
echo ""

while true; do
    read -p "Choose template (1-3): " template_choice

    case $template_choice in
        1) template="minimal"; break;;
        2) template="standard"; break;;
        3) template="complex"; break;;
        *) echo -e "${RED}✗ Invalid choice. Enter 1, 2, or 3${NC}";;
    esac
done

# Determine skill directory
skill_dir=".claude/skills/$skill_name"

# Check if skill already exists
if [ -d "$skill_dir" ]; then
    echo -e "${RED}✗ Skill directory already exists: $skill_dir${NC}"
    read -p "Overwrite? (yes/no): " overwrite
    if [ "$overwrite" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf "$skill_dir"
fi

# Create skill directory
mkdir -p "$skill_dir"

# Copy template
template_file="../building-skills/templates/${template}-skill.md"
if [ ! -f "$template_file" ]; then
    # Try absolute path from script location
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    template_file="$script_dir/../templates/${template}-skill.md"
fi

if [ -f "$template_file" ]; then
    cp "$template_file" "$skill_dir/SKILL.md"
else
    echo -e "${YELLOW}⚠ Template not found, creating basic structure${NC}"
    cat > "$skill_dir/SKILL.md" <<EOF
---
name: $skill_name
description: $description
---

# ${skill_name}

## Overview

## Workflow

## Examples

## References
EOF
fi

# Replace placeholders
sed -i "s/skill-name/$skill_name/g" "$skill_dir/SKILL.md"
sed -i "s/Skill Name/$(echo $skill_name | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')/g" "$skill_dir/SKILL.md"
sed -i "s/Brief description of what this skill does and when to use it/$description/g" "$skill_dir/SKILL.md"
sed -i "s/Detailed description of what this skill does, when to use it, and key capabilities it provides/$description/g" "$skill_dir/SKILL.md"
sed -i "s/Comprehensive description of what this skill does, when to use it, key capabilities, and the types of complex workflows it supports/$description/g" "$skill_dir/SKILL.md"

# Create additional directories based on template
if [ "$template" == "complex" ]; then
    touch "$skill_dir/examples.md"
    touch "$skill_dir/advanced.md"
    touch "$skill_dir/reference.md"
    touch "$skill_dir/troubleshooting.md"
    echo -e "${GREEN}✓ Created supporting files for progressive disclosure${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Skill created successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "Location: $skill_dir/"
echo "Template: $template"
echo ""
echo "Next steps:"
echo "  1. Edit $skill_dir/SKILL.md"
echo "  2. Add your workflows and examples"
echo "  3. Test activation: 'use $skill_name'"
echo "  4. Validate: ./scripts/validate-skill.sh $skill_dir"
echo ""
