#!/bin/bash
# Validate skill structure and content
# Usage: ./validate-skill.sh <skill-directory>

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SKILL_DIR=$1

if [ -z "$SKILL_DIR" ]; then
    echo -e "${RED}Usage: $0 <skill-directory>${NC}"
    echo "Example: $0 .claude/skills/my-skill"
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}✗ Directory not found: $SKILL_DIR${NC}"
    exit 1
fi

ERRORS=0
WARNINGS=0

echo "═══════════════════════════════════════"
echo "  Skill Validation"
echo "═══════════════════════════════════════"
echo "Skill: $SKILL_DIR"
echo ""

# Check SKILL.md exists
echo "Checking SKILL.md..."
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo -e "${RED}✗ SKILL.md not found${NC}"
    ((ERRORS++))
    exit 1
else
    echo -e "${GREEN}✓ SKILL.md exists${NC}"
fi

# Check YAML frontmatter
echo ""
echo "Checking YAML frontmatter..."
if ! head -n 1 "$SKILL_DIR/SKILL.md" | grep -q "^---$"; then
    echo -e "${RED}✗ Missing YAML frontmatter (must start with ---)${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ YAML frontmatter found${NC}"
fi

# Check required fields
echo ""
echo "Checking required fields..."

# Check name field
if ! grep -q "^name:" "$SKILL_DIR/SKILL.md"; then
    echo -e "${RED}✗ Missing 'name' field in frontmatter${NC}"
    ((ERRORS++))
else
    NAME=$(grep "^name:" "$SKILL_DIR/SKILL.md" | head -1 | cut -d: -f2 | xargs)
    echo -e "${GREEN}✓ Name field found: $NAME${NC}"

    # Validate name format
    if ! echo "$NAME" | grep -qE "^[a-z0-9]+(-[a-z0-9]+)*$"; then
        echo -e "${RED}✗ Name '$NAME' not in hyphen-case format${NC}"
        echo "  Must be lowercase-with-hyphens"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓ Name format valid (hyphen-case)${NC}"
    fi

    # Check name length
    NAME_LEN=${#NAME}
    if [ $NAME_LEN -gt 64 ]; then
        echo -e "${RED}✗ Name is $NAME_LEN chars (max 64)${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓ Name length: $NAME_LEN chars${NC}"
    fi

    # Check if directory name matches skill name
    DIR_NAME=$(basename "$SKILL_DIR")
    if [ "$DIR_NAME" != "$NAME" ]; then
        echo -e "${YELLOW}⚠ Directory name '$DIR_NAME' doesn't match skill name '$NAME'${NC}"
        ((WARNINGS++))
    fi
fi

# Check description field
if ! grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
    echo -e "${RED}✗ Missing 'description' field in frontmatter${NC}"
    ((ERRORS++))
else
    DESC=$(grep "^description:" "$SKILL_DIR/SKILL.md" | head -1 | cut -d: -f2-)
    DESC_LEN=${#DESC}
    echo -e "${GREEN}✓ Description field found${NC}"

    if [ $DESC_LEN -eq 0 ]; then
        echo -e "${RED}✗ Description is empty${NC}"
        ((ERRORS++))
    elif [ $DESC_LEN -gt 1024 ]; then
        echo -e "${RED}✗ Description is $DESC_LEN chars (max 1024)${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓ Description length: $DESC_LEN chars${NC}"
    fi
fi

# Check line count
echo ""
echo "Checking SKILL.md line count..."
LINES=$(wc -l < "$SKILL_DIR/SKILL.md")
if [ $LINES -gt 500 ]; then
    echo -e "${YELLOW}⚠ SKILL.md is $LINES lines (recommend <500)${NC}"
    echo "  Consider splitting content using progressive disclosure:"
    echo "  - Extract examples to examples.md"
    echo "  - Extract advanced content to advanced.md"
    echo "  - Extract reference to reference.md"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ SKILL.md line count: $LINES${NC}"
fi

# Check @ imports resolve
echo ""
echo "Checking @ imports..."
IMPORTS_FOUND=0
IMPORTS_MISSING=0

while IFS= read -r line; do
    # Extract @filename pattern (not @http://, not inside code blocks)
    if echo "$line" | grep -q "@[a-zA-Z]"; then
        FILE=$(echo "$line" | grep -oP '@\K[a-zA-Z0-9_\-/.]+\.md' | head -1)
        if [ -n "$FILE" ]; then
            ((IMPORTS_FOUND++))

            # Check if file exists (relative to SKILL_DIR)
            if [ -f "$SKILL_DIR/$FILE" ]; then
                echo -e "${GREEN}✓ Import found: $FILE${NC}"
            else
                echo -e "${YELLOW}⚠ Referenced file not found: $FILE${NC}"
                ((IMPORTS_MISSING++))
                ((WARNINGS++))
            fi
        fi
    fi
done < "$SKILL_DIR/SKILL.md"

if [ $IMPORTS_FOUND -eq 0 ]; then
    echo "  No @ imports found (OK for simple skills)"
fi

# Check for XML tags in name/description
echo ""
echo "Checking for XML tags..."
if grep -E "^(name|description):" "$SKILL_DIR/SKILL.md" | grep -q "<"; then
    echo -e "${RED}✗ XML tags found in name or description${NC}"
    echo "  Name and description cannot contain < or > characters"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ No XML tags in name/description${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Skill is valid and ready to use."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
    echo ""
    echo "Skill is functional but has minor issues."
    echo "Review warnings above for improvements."
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo ""
    echo "Skill has errors that must be fixed."
    echo "Review errors above and correct them."
    exit 1
fi
